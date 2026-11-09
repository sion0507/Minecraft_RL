"""Shared fixed prompt and provider adapters. Providers generate goals; Planning alone validates/adopts them."""

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from .rpc import EpisodeError
from .schema import AstraPlannerConfig, ErrorInfo, Goal, LocalPlannerConfig, Observation, PlannerSettings

PROMPT = Path(__file__).with_name("planner_prompt.txt").read_text(encoding="utf-8").strip()
PROMPT_HASH = hashlib.sha256(PROMPT.encode()).hexdigest()
Emit = Callable[[str, dict[str, Any]], None]


def messages(observation: Observation, task: Goal, feedback: str | None) -> list[dict[str, str]]:
    # Revalidate at the provider boundary: mutated model_copy objects cannot smuggle administrator fields.
    observation = Observation.model_validate(observation.model_dump())
    task = Goal.model_validate(task.model_dump())
    state = observation.model_dump(exclude={"episode_id", "attempt_id", "obs_id", "observed_map", "visited", "history"})
    surfaces = sorted((s for s in observation.observed_map if s.visible and s.block not in {"air", "cave_air", "void_air"}),
                      key=lambda s: (sum((a - b) ** 2 for a, b in zip(s.position, observation.position)), s.position, s.block))
    state.update(observed_surfaces=[s.model_dump() for s in surfaces[:64]], observed_surface_count=len(surfaces),
                 visited_count=len(observation.visited), recent_visited=observation.visited[-32:], recent_results=observation.history[-8:])
    payload = {"observation": state, "task": task.model_dump(exclude={"goal_id"}), "feedback": feedback,
               "knowledge": None}  # PLAN §5.5: retrieval is conditional, not silently added at connection time
    return [{"role": "system", "content": PROMPT}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False, allow_nan=False)}]


def failure(code: Literal["planner_error", "planner_unavailable", "permission_denied", "invalid_request"] = "planner_error") -> EpisodeError:
    # Provider exceptions/HTTP bodies may contain credentials; never copy them into logs.
    return EpisodeError(ErrorInfo(code=code, message=f"Planner {code}; inspect provider access/configuration"))


class LocalPlanner:
    def __init__(self, config: LocalPlannerConfig, root: Path, emit: Emit) -> None:
        import torch
        import bitsandbytes
        import transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        started = time.monotonic()
        manifest = json.loads(Path(__file__).with_name("qwen_files.json").read_text())
        if manifest["model"] != config.model or manifest["revision"] != config.version:
            raise ValueError("Qwen revision mismatch")
        for name, expected in manifest["files_sha256"].items():
            with (root / name).open("rb") as handle:
                if hashlib.file_digest(handle, "sha256").hexdigest() != expected:
                    raise ValueError("Qwen file hash mismatch")
        if not torch.cuda.is_available():
            raise ValueError("Qwen smoke requires actual CUDA")
        torch.cuda.reset_peak_memory_stats()
        self.tokenizer: Any = AutoTokenizer.from_pretrained(root, local_files_only=True, trust_remote_code=False)
        quantize: Any = BitsAndBytesConfig  # Transformers' quantizer/generation annotations are incomplete.
        self.model: Any = AutoModelForCausalLM.from_pretrained(root, local_files_only=True, trust_remote_code=False,
            device_map={"": 0}, dtype=torch.bfloat16, attn_implementation="sdpa",
            quantization_config=quantize(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16))
        self.model.eval()  # type: ignore[no-untyped-call]
        self.model.requires_grad_(False)
        if not self.model.is_loaded_in_4bit or any(p.requires_grad for p in self.model.parameters()):
            raise ValueError("Planner must be frozen and actually loaded in 4-bit")
        self.config, self.emit = config, emit
        emit("planner_loaded", {"backend": "local_7b", "model": config.model, "version": config.version,
            "files_sha256": manifest["files_sha256"], "prompt_sha256": PROMPT_HASH,
            "quantization": "nf4_double_quant_bf16", "temperature": 0, "decoding": "greedy", "do_sample": False,
            "max_new_tokens": config.max_new_tokens, "context_limit": 8192,
            "device": torch.cuda.get_device_name(), "torch": torch.__version__, "cuda": torch.version.cuda,
            "transformers": transformers.__version__, "bitsandbytes": bitsandbytes.__version__,
            "load_seconds": time.monotonic() - started, "allocated_bytes": torch.cuda.memory_allocated(),
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(), "training": False})

    def __call__(self, observation: Observation, task: Goal, feedback: str | None) -> str:
        import torch

        prompt = messages(observation, task, feedback)
        inputs = self.tokenizer.apply_chat_template(prompt, add_generation_prompt=True, tokenize=True,
            return_dict=True, return_tensors="pt").to(self.model.device)
        length = inputs["input_ids"].shape[-1]
        if length + self.config.max_new_tokens > 8192:
            raise failure("invalid_request")
        started = time.monotonic()
        try:
            with torch.inference_mode():
                output = self.model.generate(**inputs, do_sample=False, temperature=None, top_p=None, top_k=None,
                    max_new_tokens=self.config.max_new_tokens, pad_token_id=self.tokenizer.eos_token_id)
            reply: str = self.tokenizer.decode(output[0, length:], skip_special_tokens=True)
        except (RuntimeError, ValueError, OSError):
            self.emit("planner_call", {"backend": "local_7b", "model": self.config.model, "version": self.config.version,
                "prompt_sha256": PROMPT_HASH, "error": "inference_failed", "regeneration": feedback is not None,
                "latency_seconds": time.monotonic() - started, "cost_usd": 0.0})
            raise failure() from None
        self.emit("planner_call", {"backend": "local_7b", "model": self.config.model, "version": self.config.version,
            "prompt_sha256": PROMPT_HASH, "input_sha256": hashlib.sha256(json.dumps(prompt).encode()).hexdigest(),
            "input_tokens": length, "output_tokens": output.shape[-1] - length,
            "latency_seconds": time.monotonic() - started, "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "cost_usd": 0.0, "regeneration": feedback is not None, "reply": reply})
        return reply


class AstraPlanner:
    def __init__(self, config: AstraPlannerConfig, budget_file: Path, emit: Emit) -> None:
        endpoint = urllib.parse.urlsplit(config.endpoint)
        if (endpoint.scheme != "https" or not endpoint.hostname or endpoint.username or endpoint.password
                or endpoint.query or endpoint.fragment):
            raise ValueError("Astra endpoint needs HTTPS without credentials/query")
        if set(config.supported_settings) - {"temperature", "top_p", "reasoning_effort"}:
            raise ValueError("Unsupported Astra generation setting")
        self.config, self.budget_file, self.emit = config, budget_file, emit
        emit("planner_loaded", {"backend": "astra", "provider": config.provider, "model": config.model, "version": config.version,
            "endpoint": config.endpoint, "protocol": "chat_completions", "supported_settings": config.supported_settings,
            "prompt_sha256": PROMPT_HASH, "rates_checked_on": config.rates_checked_on,
            "input_usd_per_million": config.input_usd_per_million, "output_usd_per_million": config.output_usd_per_million,
            "max_calls": config.max_calls, "max_usd": config.max_usd, "request_usd_ceiling": config.request_usd_ceiling,
            "approved": config.approved, "access_verified": False})

    def __call__(self, observation: Observation, task: Goal, feedback: str | None) -> str:
        from .planner_budget import record_cost, reserve

        if not self.config.approved or not self.config.approval_reference:
            raise failure("permission_denied")
        key = os.environ.get("ASTRA_API_KEY")
        if not key:
            raise failure("permission_denied")
        payload = {"model": self.config.model, "messages": messages(observation, task, feedback),
                   "max_tokens": self.config.max_new_tokens, **self.config.supported_settings}
        request = urllib.request.Request(self.config.endpoint, data=json.dumps(payload, allow_nan=False).encode(),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
        reserve(self.config, self.budget_file)
        started = time.monotonic()
        report: dict[str, Any] = {"backend": "astra", "provider": self.config.provider, "model": self.config.model,
            "version": self.config.version, "prompt_sha256": PROMPT_HASH, "regeneration": feedback is not None,
            "reserved_usd": self.config.request_usd_ceiling, "usage": None, "cost_usd": None}
        try:
            opener = urllib.request.build_opener(NoRedirect())
            with opener.open(request, timeout=self.config.timeout_seconds) as response:
                body = json.loads(response.read(1024 * 1024 + 1))
            if body.get("model") != self.config.model:
                raise ValueError("Provider model mismatch")
            reply = body["choices"][0]["message"]["content"]
            if not isinstance(reply, str):
                raise ValueError("Missing text content")
            usage = body["usage"]
            if any(type(usage.get(k)) is not int or usage[k] < 0 for k in ("prompt_tokens", "completion_tokens")):
                raise ValueError("Missing token usage")
            cost = (usage["prompt_tokens"] * self.config.input_usd_per_million
                    + usage["completion_tokens"] * self.config.output_usd_per_million) / 1_000_000
            report.update(usage={k: usage[k] for k in ("prompt_tokens", "completion_tokens")}, cost_usd=cost,
                          response_model=body["model"], reply=reply.replace(key, "[REDACTED]"))
            record_cost(self.config, self.budget_file, cost)
            if cost > self.config.request_usd_ceiling:
                raise ValueError("Provider violated the approved request ceiling")
            return str(report["reply"])
        except urllib.error.HTTPError as error:
            report["http_status"] = error.code
            unavailable = error.code in {401, 402, 403, 404, 408, 429} or error.code >= 500
            report["error"] = "access_unavailable" if unavailable else "request_error"
            raise failure("planner_unavailable" if unavailable else "planner_error") from None
        except (urllib.error.URLError, TimeoutError):
            report["error"] = "access_unavailable"
            raise failure("planner_unavailable") from None
        except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError):
            report["error"] = "provider_error"
            raise failure() from None
        finally:
            report["latency_seconds"] = time.monotonic() - started
            self.emit("planner_call", report)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        # Credentials stay on the explicitly approved endpoint.
        return None


def load_planner(config: PlannerSettings, config_path: Path, emit: Emit) -> Callable[[Observation, Goal, str | None], str]:
    if config.backend == "scripted":
        replies = iter(config.outputs)
        return lambda _observation, _task, _feedback: next(replies, "")
    try:
        if config.backend == "local_7b":
            return LocalPlanner(config, (config_path.parent / config.checkpoint).resolve(), emit)
        return AstraPlanner(config, (config_path.parent / config.budget_file).resolve(), emit)
    except (ImportError, OSError, ValueError, RuntimeError):
        raise failure() from None
