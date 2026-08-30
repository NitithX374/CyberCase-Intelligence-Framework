from __future__ import annotations


SCORING_PROTOCOL = {
    "generation": {
        "primary": "ROUGE-L",
        "official_code": [
            "code/score/f1_rougel/gen_score_rougeL-en-path.py",
            "code/score/f1_rougel/gen_score_rougeL-path.py",
        ],
        "secondary": "multilingual SBERT cosine similarity",
        "secondary_official_code": [
            "code/score/sbert/gen_score_sbert-en-path.py",
            "code/score/sbert/gen_score_sbert-path.py",
        ],
    },
    "choice": {
        "primary": "exact match after strict A/B/C/D normalization",
        "official_code": "code/score/f1_rougel/choice_sorce-path.py",
        "aggregate": "correct_count / selected_count, grouped by model, category, language, and format",
    },
    "extraction": {
        "primary": "official flattened-leaf precision, recall, and F1",
        "official_code": [
            "code/score/f1_rougel/ex-score-en-path.py",
            "code/score/f1_rougel/ex-score-path.py",
        ],
        "sample_count": 1,
        "schema_policy": "preserve the requested schema; do not add a new groundedness metric",
    },
    "gpt_score": {
        "official_prompt": "code/score/get_score_gpt4_prompt.py",
        "status": "secondary only if model, revision, prompt, temperature, seed, and provider are pinned and available",
    },
    "reporting": {
        "dimensions": ["model", "category", "language", "format"],
        "preserve_raw_predictions": True,
        "no_new_groundedness_metric": True,
    },
}
