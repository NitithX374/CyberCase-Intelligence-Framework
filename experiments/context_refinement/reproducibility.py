from __future__ import annotations

import os
import random
from typing import Any

import numpy as np
import torch


def set_deterministic_seed(seed: int) -> dict[str, Any]:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    report: dict[str, Any] = {
        "seed": seed,
        "python_hash_seed": str(seed),
        "numpy_seeded": True,
        "torch_seeded": True,
        "cuda_available": bool(torch.cuda.is_available()),
    }
    return report


def runtime_device_report() -> dict[str, Any]:
    cuda_available = bool(torch.cuda.is_available())
    return {
        "torch_version": torch.__version__,
        "cuda_available": cuda_available,
        "cuda_version": torch.version.cuda,
        "device": "cuda" if cuda_available else "cpu",
        "device_name": torch.cuda.get_device_name(0) if cuda_available else "cpu",
    }
