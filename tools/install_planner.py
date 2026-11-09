"""Download the public fixed Qwen bundle; no credentials, remote code or training."""

import hashlib
import json
from pathlib import Path

from huggingface_hub import snapshot_download

if __name__ == "__main__":
    root = Path("checkpoints/qwen2.5-7b")
    expected = json.loads(Path("src/mc_diamond/qwen_files.json").read_text())
    snapshot_download(expected["model"], revision=expected["revision"], local_dir=root,
                      allow_patterns=list(expected["files_sha256"]), token=False, max_workers=2)
    hashes = {}
    for name, digest in expected["files_sha256"].items():
        with (root / name).open("rb") as handle:
            hashes[name] = hashlib.file_digest(handle, "sha256").hexdigest()
        assert hashes[name] == digest, f"Official Qwen file hash mismatch: {name}"
    manifest = {"model": expected["model"], "revision": expected["revision"], "files_sha256": hashes}
    Path("artifacts/issue-10").mkdir(parents=True, exist_ok=True)
    Path("artifacts/issue-10/qwen-files.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
