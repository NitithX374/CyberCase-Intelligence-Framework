from __future__ import annotations

from pathlib import Path


B2_PACKAGE_DIR = Path(__file__).resolve().parent
B2_MODEL_NAME = "google/mt5-base"
B2_MODEL_REVISION = "2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f"
B2_DATASET_REPOSITORY = "Multilingual-Multimodal-NLP/SEVENLLM-Dataset"
B2_DATASET_FILE = "train.jsonl"
B2_BENCHMARK_COMMIT = "a84b86aabf2b5be35a2cbbac546511883cc5ff85"
B2_VALIDATION_RATIO = 0.1
B2_SEED = 42
B2_MAX_INPUT_TOKENS = 1024
B2_MAX_TARGET_TOKENS = 512
B2_NUM_EPOCHS = 1.0
B2_LEARNING_RATE = 2e-5
B2_OPTIMIZER = "adamw_torch"
B2_WARMUP_RATIO = 0.03
B2_LR_SCHEDULER = "cosine"
B2_WEIGHT_DECAY = 0.0
B2_TRAIN_BATCH_SIZE = 1
B2_EVAL_BATCH_SIZE = 4
B2_GRADIENT_ACCUMULATION_STEPS = 16
B2_SAVE_STEPS = 500
B2_SAVE_TOTAL_LIMIT = 2
B2_LOGGING_STEPS = 10
B2_EXCLUDED_FIELDS = ("thought",)

SELECTED_CATEGORIES = (
    "Threat Analysis",
    "Protection Strategy Research",
    "Summary Generation",
    "Incident Response Planning",
    "Risk Assessment",
    "Impact Scope",
)

FIXED_BENCHMARK_IDS = frozenset(
    {
        "791",
        "901",
        "902",
        "903",
        "904",
        "906",
        "907",
        "908",
        "909",
        "910",
        "911",
        "912",
        "913",
        "914",
        "915",
        "916",
        "917",
        "919",
        "920",
        "921",
        "922",
        "923",
        "924",
        "925",
        "927",
        "928",
        "929",
        "930",
        "931",
        "932",
        "933",
        "934",
        "935",
        "936",
        "937",
        "939",
        "940",
        "942",
        "943",
        "944",
        "945",
        "946",
        "947",
        "951",
        "953",
        "954",
        "956",
        "968",
        "983",
        "996",
    }
)


def default_fixed_selection_path() -> Path:
    return B2_PACKAGE_DIR / "results" / "pilot_1_en" / "pilot_1_en_50_selection.json"


def training_defaults() -> dict[str, object]:
    return {
        "model_name": B2_MODEL_NAME,
        "model_revision": B2_MODEL_REVISION,
        "num_train_epochs": B2_NUM_EPOCHS,
        "learning_rate": B2_LEARNING_RATE,
        "optim": B2_OPTIMIZER,
        "warmup_ratio": B2_WARMUP_RATIO,
        "lr_scheduler_type": B2_LR_SCHEDULER,
        "weight_decay": B2_WEIGHT_DECAY,
        "gradient_checkpointing": True,
        "max_source_length": B2_MAX_INPUT_TOKENS,
        "max_target_length": B2_MAX_TARGET_TOKENS,
        "seed": B2_SEED,
        "data_seed": B2_SEED,
        "per_device_train_batch_size": B2_TRAIN_BATCH_SIZE,
        "per_device_eval_batch_size": B2_EVAL_BATCH_SIZE,
        "gradient_accumulation_steps": B2_GRADIENT_ACCUMULATION_STEPS,
        "checkpoint_selection": "none",
        "benchmark_scores_used_for_selection": False,
    }
