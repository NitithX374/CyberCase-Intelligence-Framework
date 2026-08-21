# Published-Baseline Results

Scored with the TechniqueRAG protocol (see `metrics.py`). Gold labels reconciled to ATT&CK v19 (see `attack_version_map.py`). All arms are zero-shot: compare against the published zero-shot / off-the-shelf-retriever rows, not the fine-tuned ones.

## tram

### mode = technique

| Run | Precision | Recall | F1 | MRR | F1-micro |
|-----|-----------|--------|----|-----|----------|
| retrieval__k20-techonly (n=713) | 0.0698 | 0.8054 | 0.1285 | 0.5139 | 0.1198 |
| retrieval__k20 (n=713) | 0.1450 | 0.6668 | 0.2382 | 0.5029 | 0.2082 |

P@k / R@k:

| Run | P@1 | R@1 | P@3 | R@3 |
|-----|-----|-----|-----|-----|
| retrieval__k20-techonly | 0.3731 | 0.3530 | 0.2508 | 0.5511 |
| retrieval__k20 | 0.3843 | 0.3645 | 0.2632 | 0.5481 |

### mode = subtechnique

| Run | Precision | Recall | F1 | MRR | F1-micro |
|-----|-----------|--------|----|-----|----------|
| retrieval__k20-techonly (n=713) | 0.0384 | 0.6952 | 0.0727 | 0.3811 | 0.0725 |
| retrieval__k20 (n=713) | 0.0864 | 0.5415 | 0.1490 | 0.3614 | 0.1291 |

P@k / R@k:

| Run | P@1 | R@1 | P@3 | R@3 |
|-----|-----|-----|-----|-----|
| retrieval__k20-techonly | 0.2637 | 0.2489 | 0.1519 | 0.4229 |
| retrieval__k20 | 0.2609 | 0.2478 | 0.1547 | 0.4082 |

