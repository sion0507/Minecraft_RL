"""Build the own 1.16.5 pause extension using the already installed server jars."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

source = Path(__file__).resolve().parent
server = source.parents[1] / "worlds/server"
libraries = server / "libraries"
classpath = [
    server / "mods/fabric-carpet-1.16.5-1.4.44+v210714.jar",
    libraries / "net/fabricmc/fabric-loader/0.16.14/fabric-loader-0.16.14.jar",
    libraries / "net/fabricmc/sponge-mixin/0.15.5+mixin.0.8.7/sponge-mixin-0.15.5+mixin.0.8.7.jar",
    server / ".fabric/remappedJars/minecraft-1.16.5-0.16.14/server-intermediary.jar",
]
if not all(item.is_file() for item in classpath):
    raise SystemExit("Start the approved Fabric server once before building the pause extension")
target = server / "mods/mc-diamond-pause.jar"
with tempfile.TemporaryDirectory() as directory:
    subprocess.run(["javac", "-proc:none", "-Xlint:-options", "--release", "8", "-cp", os.pathsep.join(map(str, classpath)),
                    "-d", directory, *map(str, sorted((source / "src").glob("*.java")))], check=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        files = [(item.relative_to(directory).as_posix(), item) for item in Path(directory).rglob("*.class")]
        files.extend((item.name, item) for item in source.glob("*.json"))
        for name, item in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, item.read_bytes())
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    assert "mcdiamond/mixin/PlayerPause.class" in archive.namelist()
    assert "mcdiamond/mixin/MovementPause.class" in archive.namelist()
    assert "mcdiamond/mixin/TickReceipt.class" in archive.namelist()
    assert "mcdiamond/mixin/AdminStep.class" in archive.namelist()
print(f"{hashlib.sha256(target.read_bytes()).hexdigest()}  {target}")
