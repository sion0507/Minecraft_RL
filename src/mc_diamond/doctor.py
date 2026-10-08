"""Real, bounded tool/computation probes; never substitute mock GPU evidence."""

import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Literal

from .schema import Contract


class Computation(Contract):
    expected: int = 10
    actual: int


class Probe(Contract):
    status: Literal["available", "missing", "error"]
    version: str | None = None
    computation: Computation | None = None
    detail: str | None = None


class DoctorReport(Contract):
    probes: dict[str, Probe]
    ready: bool
    minecraft_verified: Literal[False] = False
    model_verified: Literal[False] = False


def execute(command: list[str], *, expected: int | None = None, timeout: float = 15) -> Probe:
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
    except FileNotFoundError:
        return Probe(status="missing", detail="Executable not found")
    except (OSError, subprocess.TimeoutExpired):
        return Probe(status="error", detail="Tool could not run or timed out")
    if result.returncode:
        return Probe(status="error", detail=f"Tool exited with status {result.returncode}")
    output = (result.stdout or result.stderr).strip()
    if expected is not None:
        try:
            actual = int(output)
        except ValueError:
            return Probe(status="error", detail="Computation did not return an integer")
        if actual != expected:
            return Probe(status="error", detail="Computation returned the wrong result")
        return Probe(status="available", computation=Computation(expected=expected, actual=actual))
    return Probe(status="available", version=output[:1024])


def doctor() -> DoctorReport:
    python = execute([sys.executable, "-c", "print(sum(range(5)))"], expected=10)
    python.version = sys.version.split()[0]
    uv = shutil.which("uv")
    if uv is None and Path(".tools/uv").is_file():
        uv = str(Path(".tools/uv").resolve())
    probes = {
        "python": python,
        "uv": execute([uv or "uv", "--version"]),
        "node": execute(["node", "--version"]),
        "npm": execute(["npm", "--version"]),
        "java": execute(["java", "-version"]),
        "cuda": execute(["nvcc", "--version"]),
        "gpu": execute(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]),
    }
    if probes["node"].status == "available":
        calculation = execute(["node", "-e", "console.log([0,1,2,3,4].reduce((a,b)=>a+b,0))"], expected=10)
        probes["node"].computation = calculation.computation
        if calculation.status != "available":
            probes["node"] = calculation
    probes["mineflayer"] = execute([
        "node", "-e", 'const m=require("./bridge/node_modules/mineflayer");'
        'if(typeof m.createBot!=="function") process.exit(1);'
        'console.log(require("./bridge/node_modules/mineflayer/package.json").version)',
    ]) if Path("bridge/node_modules/mineflayer/package.json").is_file() else Probe(
        status="missing", detail="Run npm --prefix bridge ci")
    with tempfile.TemporaryDirectory(prefix="mc-diamond-doctor-") as directory:
        root = Path(directory)
        if probes["java"].status == "available":
            source = root / "DoctorArithmetic.java"
            source.write_text(
                "class DoctorArithmetic { public static void main(String[] args) {"
                "int sum=0; for(int i=0;i<5;i++) sum+=i; System.out.println(sum); } }", encoding="utf-8")
            calculation = execute(["java", str(source)], expected=10)
            probes["java"].computation = calculation.computation
            if calculation.status != "available":
                probes["java"] = calculation
    probes["gpu_compute"] = (execute([sys.executable, "-m", "mc_diamond.gpu_probe"], expected=10)
                              if probes["gpu"].status == "available" else Probe(
                                  status="missing", detail="GPU calculation not run: working GPU driver required"))
    for package in ["pydantic", "PyYAML", "pytest", "mypy"]:
        try:
            probes[package] = Probe(status="available", version=version(package))
        except PackageNotFoundError:
            probes[package] = Probe(status="missing", detail="Package is not installed")
    return DoctorReport(probes=probes, ready=all(probe.status == "available" for probe in probes.values()))
