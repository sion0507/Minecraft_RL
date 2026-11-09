"""Trainable public Choice over frozen EOS features; no predict()/inference tensors in the learning path.

Choice and tokenization adapted from NanoJev unified-games-v1 (MIT, OpenJev contributors 2026).
See third_party/nanojev-LICENSE.txt and third_party/README.md for provenance and changes.
"""

import hashlib
import importlib.util
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal, Self, cast

import torch
from torch import Tensor, nn
from safetensors import safe_open
from safetensors.torch import load_file, save_file

from .model_input import ChoiceInput, choice_input
from .schema import CandidateSet, Goal, Observation, SelectionResult
from .selectors import result

REVISION = "047b927b30882a1138fc504821b82ac145a4b81a"
WEIGHTS_SHA256 = "f68c47d66998231b86b7e91b4ed5e82ae23acf104c8b7cd6d165c3ac7b7ffe1b"
FILES = {
    "best.safetensors": WEIGHTS_SHA256,
    "config.json": "901038b5f1785c748c3fb4d35131e910951f2178f9a8bf024ff57aca556a30e9",
    "backbone_config/config.json": "30c011854471509747858ac07ffb8a4dab2bc6c04035b184729b69500c557c54",
    "source/LICENSE": "c69c1bb0b33112f68f9e8ef7e91dd38ec59066fcba3f62f70cbc8c9c83cf6a8e",
    "source/scripts/predict_toy_decisions.py": "6eedc49aaf9a81763677e3cff4e87fc4e499bfc5decf0bb4678f452f578dd92b",
    "source/scripts/train_toy_decisions.py": "4f39babd5575e43d7acf3eca357329a93c60041f334bc2bd7424929bf9c0da86",
    "tokenizer/tokenizer.json": "be75606093db2094d7cd20f3c2f385c212750648bd6ea4fb2bf507a6a4c55506",
    "tokenizer/tokenizer_config.json": "1cc816812993bff176eb4f7495433b736f06fba9b6e7b05cac7b4a1780650c95",
    "tokenizer/chat_template.jinja": "a55ee1b1660128b7098723e0abcd92caa0788061051c62d51cbe87d9cf1974d8",
}


def verify_bundle(root: Path) -> dict[str, str]:
    for name, expected in FILES.items():
        with (root / name).open("rb") as handle:
            if hashlib.file_digest(handle, "sha256").hexdigest() != expected:
                raise ValueError(f"Public NanoJev file hash mismatch: {name}")
    return dict(FILES)


def reference_module(root: Path, name: str) -> Any:
    """Only execute the two hash-pinned MIT sources, after verify_bundle()."""
    if name not in {"train_toy_decisions", "predict_toy_decisions"}:
        raise ValueError("Unknown reference module")
    path = root / "source/scripts" / f"{name}.py"
    with path.open("rb") as handle:
        if hashlib.file_digest(handle, "sha256").hexdigest() != FILES[f"source/scripts/{name}.py"]:
            raise ValueError("Reference source hash mismatch")
    spec = importlib.util.spec_from_file_location(f"nanojev_reference_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parameter_hash(module: nn.Module) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(module.state_dict().items()):
        digest.update(f"{name}:{tensor.dtype}:{list(tensor.shape)}".encode())
        digest.update(tensor.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def tokenize(encoded: ChoiceInput, tokenizer: Any, max_length: int) -> list[list[int]]:
    row = encoded.payload["states"][0]
    question = row["questions"]["action"]
    prefix = tokenizer.encode(f"State:\n{row['state']}\n", add_special_tokens=False)
    prefix += tokenizer.encode(f"Question type: choice\nQuestion:\n{question['instructions']}\n", add_special_tokens=False)
    paths = [prefix + tokenizer.encode(f"Candidate:\n{key}: {value}\nDecision:", add_special_tokens=False)
             + [tokenizer.eos_token_id] for key, value in question["criteria"].items()]
    if any(len(path) > max_length for path in paths):
        raise ValueError("NanoJev candidate path exceeds max_length; input was not truncated")
    return paths


class ChoiceHead(nn.Module):
    def __init__(self, hidden: int) -> None:
        super().__init__()
        self.norm = nn.LayerNorm(hidden)
        self.scalar = nn.Linear(hidden, 1)
        self.set_project = nn.Linear(hidden + 1, 128)
        self.set_attention = nn.MultiheadAttention(128, 4, dropout=0, batch_first=True)
        self.set_output = nn.Linear(128, 1)

    def forward(self, features: Tensor, mask: Tensor) -> Tensor:
        h = self.norm(features.unsqueeze(0))
        log_k = mask.sum().float().log().expand(1, len(mask), 1)
        u = self.set_project(torch.cat([h, log_k.to(h.dtype)], dim=-1))
        mixed, _ = self.set_attention(u, u, u, key_padding_mask=~mask.unsqueeze(0), need_weights=False)
        delta = self.set_output(torch.tanh(u + mixed)).squeeze(-1).float()
        z = self.scalar(h).squeeze(-1).float() + delta
        return cast(Tensor, z[0].masked_fill(~mask, -torch.inf))


class NanoJevAdapter(nn.Module):
    def __init__(self, backbone: nn.Module) -> None:
        super().__init__()
        self.backbone = backbone.requires_grad_(False)
        config: Any = backbone.config
        hidden = int(config.hidden_size)
        self.choice = ChoiceHead(hidden)
        self.critics = nn.ModuleDict({kind: nn.Sequential(nn.Linear(hidden + 4, 256), nn.GELU(), nn.Linear(256, 1))
                                     for kind in ("local", "full")})
        self.tokenizer: Any = None
        self.max_length = 8192
        self.bf16 = False
        self.train(False)

    def train(self, mode: bool = True) -> Self:
        super().train(mode)
        for module in self.modules():
            if isinstance(module, nn.Dropout):
                module.p = 0
            elif isinstance(module, nn.MultiheadAttention):
                module.dropout = 0
        self.backbone.eval()
        return self

    @classmethod
    def load(cls, root: Path, device: str = "cuda:0") -> Self:
        from transformers import AutoConfig, AutoModel, AutoTokenizer
        verify_bundle(root)
        if not torch.cuda.is_available() or torch.device(device).type != "cuda":
            raise ValueError("Real smoke-model requires CUDA; no silent CPU/mock model fallback")
        torch.cuda.set_device(device)
        if not torch.cuda.is_bf16_supported():
            raise ValueError("Public NanoJev BF16 requires BF16 support")
        torch.backends.cuda.matmul.allow_tf32 = False
        config = AutoConfig.from_pretrained(root / "backbone_config", local_files_only=True, trust_remote_code=False)
        config.use_cache = False
        factory: Any = AutoModel
        model = cls(factory.from_config(config, attn_implementation="sdpa", trust_remote_code=False).float())
        weights = load_file(str(root / "best.safetensors"))
        model.backbone.load_state_dict({k.removeprefix("backbone."): v for k, v in weights.items() if k.startswith("backbone.")}, strict=True)
        model.choice.load_state_dict({k: v for k, v in weights.items() if not k.startswith("backbone.")}, strict=True)
        model.tokenizer = AutoTokenizer.from_pretrained(root / "tokenizer", local_files_only=True, trust_remote_code=False)
        if model.tokenizer.pad_token_id is None:
            model.tokenizer.pad_token = model.tokenizer.eos_token
        model.bf16 = True
        model.to(device=device, dtype=torch.float32)
        return model

    def encode_tokens(self, paths: list[list[int]], pad_token: int) -> Tensor:
        if not paths or any(not path or len(path) > self.max_length for path in paths):
            raise ValueError("Empty or overlength candidate tokens")
        device = next(self.backbone.parameters()).device
        chunk_size = max(1, 32768 // max(map(len, paths)))
        leaves = []
        self.backbone.eval()
        with torch.no_grad(), torch.autocast(device.type, dtype=torch.bfloat16, enabled=self.bf16):
            for offset in range(0, len(paths), chunk_size):
                chunk = paths[offset:offset + chunk_size]
                lengths = torch.tensor([len(path) for path in chunk], device=device)
                width = int(lengths.max())
                tokens = torch.full((len(chunk), width), pad_token, dtype=torch.long, device=device)
                for index, path in enumerate(chunk):
                    tokens[index, :len(path)] = torch.tensor(path, device=device)
                attention = torch.arange(width, device=device)[None, :] < lengths[:, None]
                hidden = self.backbone(input_ids=tokens, attention_mask=attention, use_cache=False).last_hidden_state
                leaves.append(hidden[torch.arange(len(chunk), device=device), lengths - 1])
        return torch.cat(leaves).detach()

    def encode_candidates(self, encoded: ChoiceInput) -> Tensor:
        return self.encode_tokens(tokenize(encoded, self.tokenizer, self.max_length), self.tokenizer.pad_token_id)

    def score_features(self, features: Tensor, mask: Tensor, context: Tensor) -> tuple[Tensor, dict[str, Tensor]]:
        if (features.ndim != 2 or mask.shape != features.shape[:1] or mask.dtype != torch.bool
                or context.shape != (4,) or not mask.any() or not torch.isfinite(features).all() or not torch.isfinite(context).all()):
            raise ValueError("Invalid features, candidate mask or objective/budget context")
        with torch.autocast(features.device.type, dtype=torch.bfloat16, enabled=self.bf16):
            logits = self.choice(features, mask)
            pooled = torch.cat([features[mask].mean(0), context.to(features.dtype)])
            values = {kind: head(pooled).squeeze(-1).float() for kind, head in self.critics.items()}
        if not torch.isfinite(logits[mask]).all() or not all(torch.isfinite(v) for v in values.values()):
            raise ValueError("Nonfinite NanoJev logits/value")
        return logits, values

    def evaluate_actions(self, features: Tensor, mask: Tensor, context: Tensor, objective: str,
                         index: int) -> tuple[Tensor, Tensor, Tensor, bool]:
        if objective not in {"local", "full"} or not 0 <= index < len(mask) or not mask[index]:
            raise ValueError("Invalid saved action/objective")
        logits, values = self.score_features(features, mask, context)
        logprobs = logits.log_softmax(-1)
        eligible = int(mask.sum()) > 1
        entropy = -(logprobs[mask].exp() * logprobs[mask]).sum()
        return logprobs[index], entropy, values[objective], eligible

    def heads(self) -> dict[str, Tensor]:
        return {k: v for k, v in self.state_dict().items() if not k.startswith("backbone.")}

    def save_heads(self, path: Path) -> None:
        temporary = path.with_suffix(".tmp")
        save_file({k: v.detach().cpu().contiguous() for k, v in self.heads().items()}, str(temporary),
                  metadata={"revision": REVISION, "initial_weights_sha256": WEIGHTS_SHA256})
        temporary.replace(path)

    def load_heads(self, path: Path) -> None:
        with safe_open(path, framework="pt") as handle:
            if handle.metadata() != {"revision": REVISION, "initial_weights_sha256": WEIGHTS_SHA256}:
                raise ValueError("Head checkpoint provenance mismatch")
        heads = load_file(str(path), device=str(next(self.parameters()).device))
        current = self.heads()
        if heads.keys() != current.keys():
            raise ValueError("Head checkpoint keys mismatch")
        if any(value.shape != current[key].shape or value.dtype != current[key].dtype or not torch.isfinite(value).all()
               for key, value in heads.items()):
            raise ValueError("Head checkpoint shape, dtype or finite-value mismatch")
        self.choice.load_state_dict({k.removeprefix("choice."): v for k, v in heads.items() if k.startswith("choice.")}, strict=True)
        self.critics.load_state_dict({k.removeprefix("critics."): v for k, v in heads.items() if k.startswith("critics.")}, strict=True)


class NanoJevSelector:
    def __init__(self, model: NanoJevAdapter, mode: Literal["sampling", "argmax"], seed: int) -> None:
        self.model, self.mode = model, mode
        self.generator = torch.Generator(device=next(model.parameters()).device).manual_seed(seed)

    def __call__(self, observation: Observation, goal: Goal, saved: CandidateSet, _failures: Sequence[str]) -> SelectionResult:
        encoded = choice_input(observation, goal, saved)
        features = self.model.encode_candidates(encoded)
        mask = torch.tensor(encoded.mask, device=features.device)
        context = torch.tensor(encoded.context, device=features.device)
        with torch.no_grad():
            logits, values = self.model.score_features(features, mask, context)
            probabilities = logits.softmax(-1)
            index = int(torch.multinomial(probabilities, 1, generator=self.generator)) if self.mode == "sampling" else int(logits.argmax())
        return result(saved.candidates[index], self.mode, provider="local", model=f"C-Tianyu/NanoJev@{REVISION}",
                      probabilities=dict(zip(encoded.candidate_ids, probabilities.cpu().tolist())),
                      logprob=float(logits.log_softmax(-1)[index]), values={k: float(v) for k, v in values.items()},
                      actor_eligible=sum(encoded.mask) > 1)
