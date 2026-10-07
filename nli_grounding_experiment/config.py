import os
import random
from pathlib import Path
import numpy as np
import torch

SEED = 42

def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(SEED)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"
OUTPUTS_DIR = BASE_DIR / "outputs"

SEMANTIC_CACHE_DIR = CACHE_DIR / "semantic_scores"
FORWARD_NLI_CACHE_DIR = CACHE_DIR / "forward_nli"
REVERSE_NLI_CACHE_DIR = CACHE_DIR / "reverse_nli"

for d in [DATA_DIR, CACHE_DIR, OUTPUTS_DIR, SEMANTIC_CACHE_DIR, FORWARD_NLI_CACHE_DIR, REVERSE_NLI_CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

NLI_MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

HF_CACHE_DIRS = ["D:/AI/huggingface", "F:/Caches/huggingface/hub"]
os.environ["HF_HOME"] = "D:/AI/huggingface"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Binary label mapping:
# 1 = SUPPORTED
# 0 = NOT FULLY SUPPORTED (partially_supported or not_supported)
LABEL_MAPPING_BINARY = {
    "supported": 1,
    "partially_supported": 0,
    "not_supported": 0,
}

# Max token length for NLI
NLI_MAX_LENGTH = 512
