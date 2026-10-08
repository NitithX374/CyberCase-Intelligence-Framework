from __future__ import annotations

import platform
from importlib.metadata import version
from pathlib import Path

from app.config import settings
from app.trace.b1_verifier import B1Verifier, load_verifier
from app.trace.nli_model import MdebertaNli


class DeviceTokenizer:
    def __init__(self, tokenizer, device):
        self.tokenizer = tokenizer
        self.device = device

    def __call__(self, *args, **kwargs):
        return self.tokenizer(*args, **kwargs).to(self.device)


def load_runtime(device: str):
    import torch

    if device not in ("cpu", "cuda"):
        raise ValueError("Choose an explicit CPU or CUDA research device")
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("Requested CUDA research runtime is unavailable")
    root = Path(__file__).resolve().parents[2]
    settings.claim_nli_path = str(root / "backend/nli_mdeberta")
    settings.claim_selector_path = str(root / "backend/source_selector_mpnet")
    original = load_verifier()
    original.selector.model.to(device)
    nli_model = original.nli.model.to(device).eval()
    nli = MdebertaNli(
        torch,
        DeviceTokenizer(original.nli.tokenizer, device),
        nli_model,
        original.nli.order,
    )
    receipt = {
        "device": device,
        "nli_dtype": str(next(nli_model.parameters()).dtype),
        "selector_dtype": str(next(original.selector.model.parameters()).dtype),
        "python": platform.python_version(),
        "libraries": {
            name: version(name)
            for name in ("torch", "transformers", "sentence-transformers")
        },
        "cuda_device": torch.cuda.get_device_name() if device == "cuda" else None,
        "policy": "Both EN and TH recomputed with identical frozen assets/device; archived EN scores retained separately",
    }
    return B1Verifier(original.selector, nli), receipt


def peak_vram_bytes(device: str) -> int | None:
    if device == "cpu":
        return None
    import torch

    return torch.cuda.max_memory_allocated()
