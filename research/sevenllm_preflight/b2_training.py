from __future__ import annotations

import hashlib
import inspect
import json
import math
import os
import random
from pathlib import Path
from typing import Any

os.environ.pop("SSLKEYLOGFILE", None)

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    set_seed,
)

from .b2_config import (
    B2_LEARNING_RATE,
    B2_LR_SCHEDULER,
    B2_MAX_INPUT_TOKENS,
    B2_MAX_TARGET_TOKENS,
    B2_MODEL_NAME,
    B2_MODEL_REVISION,
    B2_OPTIMIZER,
    B2_SAVE_TOTAL_LIMIT,
    B2_WEIGHT_DECAY,
    B2_WARMUP_RATIO,
    B2_EVAL_BATCH_SIZE,
    B2_LOGGING_STEPS,
    B2_NUM_EPOCHS,
    SELECTED_CATEGORIES,
)

def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def load_preflight_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    if manifest.get("preflight", {}).get("status") != "PASS":
        raise RuntimeError("Training requires a PASS B2 preflight manifest")
    decisions = manifest.get("fixed_decisions", {})
    if decisions.get("base_model") != B2_MODEL_NAME:
        raise RuntimeError("Preflight model does not match the fixed google/mt5-base decision")
    if decisions.get("language") != "English only" or decisions.get("selected_categories") != list(SELECTED_CATEGORIES):
        raise RuntimeError("Preflight language or category contract does not match B2")
    if decisions.get("target_field") != "output" or decisions.get("excluded_fields") != ["thought"]:
        raise RuntimeError("Preflight target contract is not output-only without thought")
    if not isinstance(decisions.get("seed"), int):
        raise RuntimeError("Preflight manifest must contain an integer deterministic seed")
    if not manifest.get("leakage_check", {}).get("passed"):
        raise RuntimeError("Training requires a passing benchmark leakage check")
    if manifest.get("runtime", {}).get("benchmark_scores_used") is not False:
        raise RuntimeError("Benchmark scores cannot be used by the trainer")
    for name in ("train_jsonl", "validation_jsonl"):
        path_value = manifest.get("artifacts", {}).get(name)
        expected_hash = manifest.get("artifacts", {}).get(f"{name}_sha256")
        if not path_value or not expected_hash:
            raise RuntimeError(f"Preflight manifest is missing the {name} artifact hash")
        artifact = Path(path_value)
        if not artifact.exists() or file_sha256(artifact) != expected_hash:
            raise RuntimeError(f"Preflight artifact changed or is missing: {artifact}")
    return manifest

def select_precision() -> dict[str, Any]:
    if not torch.cuda.is_available():
        return {"mode": "none", "bf16": False, "fp16": False, "device_capability": None}
    capability = torch.cuda.get_device_capability()
    bf16_supported = (
        capability >= (8, 0)
        and hasattr(torch.cuda, "is_bf16_supported")
        and torch.cuda.is_bf16_supported()
    )
    if bf16_supported:
        return {"mode": "bf16", "bf16": True, "fp16": False, "device_capability": capability}
    return {"mode": "fp16", "bf16": False, "fp16": True, "device_capability": capability}


def seed_runtime(seed: int) -> None:
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    set_seed(seed, deterministic=True)


def tokenized_dataset(path: Path, tokenizer: Any, split_name: str) -> Any:
    dataset = load_dataset("json", data_files={split_name: str(path)}, split=split_name)

    def encode(batch: dict[str, list[str]]) -> dict[str, Any]:
        model_inputs = tokenizer(
            batch["input_text"],
            max_length=B2_MAX_INPUT_TOKENS,
            truncation=True,
        )
        labels = tokenizer(
            text_target=batch["target_text"],
            max_length=B2_MAX_TARGET_TOKENS,
            truncation=True,
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    return dataset.map(encode, batched=True, remove_columns=dataset.column_names, desc=f"Tokenize {split_name}")


def latest_checkpoint(output_dir: Path) -> Path:
    checkpoints = [
        path for path in output_dir.glob("checkpoint-*") if path.is_dir() and path.name.split("-")[-1].isdigit()
    ]
    if not checkpoints:
        raise RuntimeError(f"No checkpoint exists under {output_dir} for --resume-latest")
    return max(checkpoints, key=lambda path: int(path.name.rsplit("-", 1)[1]))


def warmup_steps_for(dataset_size: int, args: Any) -> int:
    world_size = max(1, int(os.environ.get("WORLD_SIZE", "1")))
    batches = math.ceil(dataset_size / (args.per_device_train_batch_size * world_size))
    update_steps = math.ceil(batches / args.gradient_accumulation_steps)
    return max(1, math.ceil(update_steps * B2_WARMUP_RATIO))


def build_training_arguments(
    output_dir: Path,
    precision: dict[str, Any],
    args: Any,
    dataset_size: int,
    seed: int,
) -> Seq2SeqTrainingArguments:
    fields = inspect.signature(Seq2SeqTrainingArguments.__init__).parameters
    warmup_config = (
        {"warmup_ratio": B2_WARMUP_RATIO}
        if "warmup_ratio" in fields
        else {"warmup_steps": warmup_steps_for(dataset_size, args)}
    )
    return Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=B2_NUM_EPOCHS,
        learning_rate=B2_LEARNING_RATE,
        optim=B2_OPTIMIZER,
        lr_scheduler_type=B2_LR_SCHEDULER,
        weight_decay=B2_WEIGHT_DECAY,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=B2_EVAL_BATCH_SIZE,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        bf16=precision["bf16"],
        fp16=precision["fp16"],
        seed=seed,
        data_seed=seed,
        full_determinism=True,
        eval_strategy="epoch",
        save_strategy="steps",
        save_steps=args.save_steps,
        save_total_limit=B2_SAVE_TOTAL_LIMIT,
        logging_strategy="steps",
        logging_steps=B2_LOGGING_STEPS,
        report_to=[],
        do_train=True,
        do_eval=True,
        remove_unused_columns=True,
        dataloader_num_workers=0,
        dataloader_pin_memory=torch.cuda.is_available(),
        load_best_model_at_end=False,
        predict_with_generate=False,
        **warmup_config,
    )


def build_run_config(
    manifest_path: Path,
    output_dir: Path,
    precision: dict[str, Any],
    args: Any,
    resume_from_checkpoint: Path | None,
    warmup_steps: int,
    model_revision: str,
    seed: int,
) -> dict[str, Any]:
    return {
        "experiment": "SEvenLLM B2 training",
        "model": {"name": B2_MODEL_NAME, "revision": model_revision},
        "dataset_manifest": str(manifest_path.resolve()),
        "output_dir": str(output_dir.resolve()),
        "epochs": B2_NUM_EPOCHS,
        "learning_rate": B2_LEARNING_RATE,
        "optimizer": B2_OPTIMIZER,
        "warmup_ratio": B2_WARMUP_RATIO,
        "warmup_steps": warmup_steps,
        "lr_scheduler_type": B2_LR_SCHEDULER,
        "weight_decay": B2_WEIGHT_DECAY,
        "gradient_checkpointing": True,
        "precision": precision,
        "max_source_length": B2_MAX_INPUT_TOKENS,
        "max_target_length": B2_MAX_TARGET_TOKENS,
        "seed": seed,
        "data_seed": seed,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "per_device_eval_batch_size": B2_EVAL_BATCH_SIZE,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "save_steps": args.save_steps,
        "resume_from_checkpoint": str(resume_from_checkpoint) if resume_from_checkpoint else None,
        "checkpoint_selection": "none",
        "benchmark_scores_used_for_selection": False,
        "benchmark_usage": "evaluation_only",
        "torch_version": torch.__version__,
    }


def run_training(args: Any) -> dict[str, Any]:
    manifest_path = args.preflight_manifest.resolve()
    manifest = load_preflight_manifest(manifest_path)
    model_revision = str(manifest["fixed_decisions"].get("model_revision") or B2_MODEL_REVISION)
    seed = int(manifest["fixed_decisions"]["seed"])
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    precision = select_precision()
    seed_runtime(seed)
    resume_from_checkpoint = None
    if args.resume_from_checkpoint and args.resume_latest:
        raise RuntimeError("Use only one of --resume-from-checkpoint and --resume-latest")
    if args.resume_from_checkpoint:
        resume_from_checkpoint = args.resume_from_checkpoint.resolve()
        if not resume_from_checkpoint.is_dir():
            raise RuntimeError(f"Checkpoint does not exist: {resume_from_checkpoint}")
    elif args.resume_latest:
        resume_from_checkpoint = latest_checkpoint(output_dir)
    cache_dir = str(args.cache_dir.resolve()) if args.cache_dir else None
    tokenizer = AutoTokenizer.from_pretrained(B2_MODEL_NAME, revision=model_revision, cache_dir=cache_dir)
    model = AutoModelForSeq2SeqLM.from_pretrained(B2_MODEL_NAME, revision=model_revision, cache_dir=cache_dir)
    model.config.use_cache = False
    train_dataset = tokenized_dataset(Path(manifest["artifacts"]["train_jsonl"]), tokenizer, "train")
    validation_dataset = tokenized_dataset(Path(manifest["artifacts"]["validation_jsonl"]), tokenizer, "validation")
    collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model, label_pad_token_id=-100)
    warmup_steps = warmup_steps_for(len(train_dataset), args)
    training_args = build_training_arguments(output_dir, precision, args, len(train_dataset), seed)
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        data_collator=collator,
        processing_class=tokenizer,
    )
    run_config = build_run_config(
        manifest_path,
        output_dir,
        precision,
        args,
        resume_from_checkpoint,
        warmup_steps,
        model_revision,
        seed,
    )
    run_config["trainer_args"] = json.loads(training_args.to_json_string())
    (output_dir / "b2_training_config.json").write_text(json.dumps(run_config, ensure_ascii=False, indent=2), encoding="utf-8")
    train_result = trainer.train(resume_from_checkpoint=str(resume_from_checkpoint) if resume_from_checkpoint else None)
    eval_metrics = trainer.evaluate()
    trainer.save_state()
    model.config.use_cache = True
    final_dir = output_dir / "final_model"
    trainer.save_model(str(final_dir))
    tokenizer.save_pretrained(final_dir)
    metrics = {
        "train": train_result.metrics,
        "evaluation": eval_metrics,
        "log_history": trainer.state.log_history,
        "global_step": trainer.state.global_step,
        "checkpoint_selection": "none",
        "benchmark_scores_used_for_selection": False,
    }
    (output_dir / "b2_training_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "b2_dataset_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "output_dir": str(output_dir),
        "final_model": str(final_dir),
        "global_step": trainer.state.global_step,
        "train_metrics": train_result.metrics,
        "evaluation_metrics": eval_metrics,
        "resumed_from": str(resume_from_checkpoint) if resume_from_checkpoint else None,
    }
