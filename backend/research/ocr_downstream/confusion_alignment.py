from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable

import Levenshtein


def count_operations(reference: str, prediction: str) -> dict[str, Any]:
    operations = Levenshtein.editops(reference, prediction)
    substitutions: Counter[tuple[str, str]] = Counter()
    insertions: Counter[str] = Counter()
    deletions: Counter[str] = Counter()
    for operation, reference_index, prediction_index in operations:
        if operation == "replace":
            substitutions[(reference[reference_index], prediction[prediction_index])] += 1
        elif operation == "insert":
            insertions[prediction[prediction_index]] += 1
        elif operation == "delete":
            deletions[reference[reference_index]] += 1
    return {
        "reference_characters": len(reference),
        "prediction_characters": len(prediction),
        "substitutions": substitutions,
        "insertions": insertions,
        "deletions": deletions,
        "edit_distance": len(operations),
    }


def compute_reference_character_statistics(
    reference_occurrences: Counter[str],
    substitutions: Counter[tuple[str, str]],
    deletions: Counter[str],
) -> list[dict[str, Any]]:
    substitutions_per_ref: Counter[str] = Counter()
    for (ref_char, _), count in substitutions.items():
        substitutions_per_ref[ref_char] += count

    stats: list[dict[str, Any]] = []
    all_chars = sorted(
        set(reference_occurrences.keys()) | set(substitutions_per_ref.keys()) | set(deletions.keys()),
        key=lambda c: (-reference_occurrences[c], c),
    )

    for char in all_chars:
        occurrences = reference_occurrences[char]
        sub_count = substitutions_per_ref[char]
        del_count = deletions[char]
        error_count = sub_count + del_count

        sub_rate = sub_count / occurrences if occurrences > 0 else 0.0
        del_rate = del_count / occurrences if occurrences > 0 else 0.0
        cer = error_count / occurrences if occurrences > 0 else 0.0

        stats.append(
            {
                "character": char,
                "reference_occurrences": occurrences,
                "substitution_count": sub_count,
                "deletion_count": del_count,
                "error_count": error_count,
                "substitution_rate": sub_rate,
                "deletion_rate": del_rate,
                "character_error_rate": cer,
            }
        )
    return stats


def compute_substitution_bank(
    substitutions: Counter[tuple[str, str]],
    reference_occurrences: Counter[str],
    examples: dict[tuple[str, str], list[dict[str, str]]],
) -> list[dict[str, Any]]:
    all_subs_for_ref: Counter[str] = Counter()
    for (ref_char, _), count in substitutions.items():
        all_subs_for_ref[ref_char] += count

    bank: list[dict[str, Any]] = []
    for (ref_char, pred_char), count in substitutions.most_common():
        ref_count = reference_occurrences[ref_char]
        total_subs = all_subs_for_ref[ref_char]
        prob_given_sub = count / total_subs if total_subs > 0 else 0.0
        rate_given_ref = count / ref_count if ref_count > 0 else 0.0

        bank.append(
            {
                "reference": ref_char,
                "predicted": pred_char,
                "count": count,
                "reference_occurrences": ref_count,
                "all_substitutions_for_reference": total_subs,
                "probability_given_substitution": prob_given_sub,
                "empirical_rate_given_reference": rate_given_ref,
                "examples": examples.get((ref_char, pred_char), []),
            }
        )
    return bank


def compute_insertions(
    insertions: Counter[str],
    total_reference_characters: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for char, count in insertions.most_common():
        rate = count / total_reference_characters if total_reference_characters > 0 else 0.0
        rows.append(
            {
                "character": char,
                "count": count,
                "rate_per_reference_character": rate,
            }
        )
    return rows


def compute_deletions(
    deletions: Counter[str],
    reference_occurrences: Counter[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for char, count in deletions.most_common():
        ref_count = reference_occurrences[char]
        del_rate = count / ref_count if ref_count > 0 else 0.0
        rows.append(
            {
                "character": char,
                "count": count,
                "reference_occurrences": ref_count,
                "deletion_rate": del_rate,
            }
        )
    return rows


def analyze_record_group(records: list[dict[str, Any]]) -> dict[str, Any]:
    substitutions: Counter[tuple[str, str]] = Counter()
    insertions: Counter[str] = Counter()
    deletions: Counter[str] = Counter()
    reference_occurrences: Counter[str] = Counter()
    examples: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)

    total_ref_chars = 0
    total_pred_chars = 0
    total_edit_distance = 0
    sample_metrics: list[dict[str, Any]] = []

    for record in records:
        ref_norm = record["reference_normalized"]
        pred_norm = record["prediction_normalized"]
        sample_id = record["sample_id"]
        category = record.get("category") or "unknown"

        for char in ref_norm:
            reference_occurrences[char] += 1

        metrics = count_operations(ref_norm, pred_norm)
        substitutions.update(metrics["substitutions"])
        insertions.update(metrics["insertions"])
        deletions.update(metrics["deletions"])

        for pair in metrics["substitutions"]:
            pair_examples = examples[pair]
            if len(pair_examples) < 5 and not any(e["sample_id"] == sample_id for e in pair_examples):
                pair_examples.append({"sample_id": sample_id, "category": category})

        ref_len = metrics["reference_characters"]
        pred_len = metrics["prediction_characters"]
        ed = metrics["edit_distance"]
        sub_cnt = sum(metrics["substitutions"].values())
        ins_cnt = sum(metrics["insertions"].values())
        del_cnt = sum(metrics["deletions"].values())

        total_ref_chars += ref_len
        total_pred_chars += pred_len
        total_edit_distance += ed

        sample_cer = ed / ref_len if ref_len > 0 else 0.0
        length_ratio = pred_len / ref_len if ref_len > 0 else 0.0

        sample_metrics.append(
            {
                "sample_id": sample_id,
                "category": category,
                "reference_characters": ref_len,
                "prediction_characters": pred_len,
                "edit_distance": ed,
                "cer": sample_cer,
                "substitution_count": sub_cnt,
                "insertion_count": ins_cnt,
                "deletion_count": del_cnt,
                "length_ratio": length_ratio,
            }
        )

    total_sub_cnt = sum(substitutions.values())
    total_ins_cnt = sum(insertions.values())
    total_del_cnt = sum(deletions.values())
    overall_cer = total_edit_distance / total_ref_chars if total_ref_chars > 0 else 0.0
    overall_sub_rate = total_sub_cnt / total_ref_chars if total_ref_chars > 0 else 0.0
    overall_del_rate = total_del_cnt / total_ref_chars if total_ref_chars > 0 else 0.0
    overall_ins_rate = total_ins_cnt / total_ref_chars if total_ref_chars > 0 else 0.0

    ref_char_stats = compute_reference_character_statistics(reference_occurrences, substitutions, deletions)
    sub_bank = compute_substitution_bank(substitutions, reference_occurrences, examples)
    ins_bank = compute_insertions(insertions, total_ref_chars)
    del_bank = compute_deletions(deletions, reference_occurrences)

    return {
        "sample_count": len(records),
        "reference_characters": total_ref_chars,
        "prediction_characters": total_pred_chars,
        "edit_distance": total_edit_distance,
        "cer": overall_cer,
        "substitution_count": total_sub_cnt,
        "insertion_count": total_ins_cnt,
        "deletion_count": total_del_cnt,
        "substitution_rate": overall_sub_rate,
        "deletion_rate": overall_del_rate,
        "insertions_per_reference_character": overall_ins_rate,
        "reference_character_statistics": ref_char_stats,
        "substitution_bank": sub_bank,
        "insertions": ins_bank,
        "deletions": del_bank,
        "sample_metrics": sample_metrics,
    }


def build_category_summary(
    categories_data: dict[str, Any],
    all_categories_data: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cat_name, data in categories_data.items():
        rows.append(
            {
                "category": cat_name,
                "samples": data["sample_count"],
                "reference_chars": data["reference_characters"],
                "prediction_chars": data["prediction_characters"],
                "cer": data["cer"],
                "substitution_rate": data["substitution_rate"],
                "deletion_rate": data["deletion_rate"],
                "insertions_per_reference_character": data["insertions_per_reference_character"],
            }
        )
    rows.append(
        {
            "category": "all_categories",
            "samples": all_categories_data["sample_count"],
            "reference_chars": all_categories_data["reference_characters"],
            "prediction_chars": all_categories_data["prediction_characters"],
            "cer": all_categories_data["cer"],
            "substitution_rate": all_categories_data["substitution_rate"],
            "deletion_rate": all_categories_data["deletion_rate"],
            "insertions_per_reference_character": all_categories_data["insertions_per_reference_character"],
        }
    )
    return rows


def build_outliers(sample_metrics: list[dict[str, Any]], top_k: int = 20) -> dict[str, Any]:
    top_cer = sorted(sample_metrics, key=lambda s: (-s["cer"], -s["edit_distance"]))[:top_k]
    top_edit_distance = sorted(sample_metrics, key=lambda s: (-s["edit_distance"], -s["cer"]))[:top_k]
    top_abnormal_length = sorted(
        sample_metrics,
        key=lambda s: -abs(s["length_ratio"] - 1.0),
    )[:top_k]
    return {
        "top_by_cer": top_cer,
        "top_by_edit_distance": top_edit_distance,
        "top_by_abnormal_length_ratio": top_abnormal_length,
    }


def build_bank(records: Iterable[dict[str, Any]], settings: dict[str, Any]) -> dict[str, Any]:
    valid_records = [r for r in records if r.get("status") == "ok"]

    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in valid_records:
        cat = r.get("category")
        if not cat:
            source = r.get("source_label", "")
            for part in source.split(";"):
                if part.startswith("category="):
                    cat = part.split("=", 1)[1]
                    break
        cat = cat or "unknown"
        r["category"] = cat
        by_category[cat].append(r)

    categories_banks: dict[str, Any] = {}
    for cat_name in sorted(by_category.keys()):
        categories_banks[cat_name] = analyze_record_group(by_category[cat_name])

    all_categories_bank = analyze_record_group(valid_records)
    category_summary = build_category_summary(categories_banks, all_categories_bank)
    outliers = build_outliers(all_categories_bank["sample_metrics"])

    dataset_summary = {
        "dataset": settings.get("default_dataset", "thai-ocr-evaluation"),
        "total_samples": len(valid_records),
        "categories": {cat: len(recs) for cat, recs in sorted(by_category.items())},
    }

    return {
        "schema_version": "ocr-character-confusion-bank.v2",
        "settings": settings,
        "dataset_summary": dataset_summary,
        "category_summary": category_summary,
        "categories": categories_banks,
        "all_categories": all_categories_bank,
        "outliers": outliers,
    }

