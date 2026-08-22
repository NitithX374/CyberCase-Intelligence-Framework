# Published-Baseline Results

Scored with the TechniqueRAG protocol (see `metrics.py`). Gold labels reconciled to ATT&CK v19 (see `attack_version_map.py`). All arms are zero-shot: compare against the published zero-shot / off-the-shelf-retriever rows, not the fine-tuned ones.

## tram

### mode = technique

| Run | Precision | Recall | F1 | MRR | F1-micro |
|-----|-----------|--------|----|-----|----------|
| llm-only (n=713) | 0.6526 | 0.7381 | 0.6927 | 0.7269 | 0.6037 |
| llm-only__qwen3-5-9b-nothink (n=713) | 0.2604 | 0.3593 | 0.3020 | 0.3152 | 0.0767 |
| rag-en__k20-techonly (n=713) | 0.5889 | 0.6651 | 0.6247 | 0.6556 | 0.5703 |
| rag-en__k20-techonly__qwen3-5-9b-nothink (n=713) | 0.4948 | 0.6752 | 0.5711 | 0.6314 | 0.3522 |
| retrieval__k20-clean (n=713) | 0.0686 | 0.8117 | 0.1265 | 0.5055 | 0.1188 |
| retrieval__k20-norerank (n=713) | 0.0698 | 0.8054 | 0.1285 | 0.5196 | 0.1197 |
| retrieval__k20-rankfuse (n=713) | 0.1104 | 0.7247 | 0.1917 | 0.5139 | 0.1652 |
| retrieval__k20-techonly (n=713) | 0.0698 | 0.8054 | 0.1285 | 0.5139 | 0.1198 |
| retrieval__k20 (n=713) | 0.1450 | 0.6668 | 0.2382 | 0.5029 | 0.2082 |

P@k / R@k:

| Run | P@1 | R@1 | P@3 | R@3 |
|-----|-----|-----|-----|-----|
| llm-only | 0.6872 | 0.6557 | 0.6533 | 0.7274 |
| llm-only__qwen3-5-9b-nothink | 0.2875 | 0.2697 | 0.2726 | 0.3161 |
| rag-en__k20-techonly | 0.6213 | 0.5928 | 0.5893 | 0.6634 |
| rag-en__k20-techonly__qwen3-5-9b-nothink | 0.5820 | 0.5538 | 0.5192 | 0.6393 |
| retrieval__k20-clean | 0.3633 | 0.3448 | 0.2506 | 0.5446 |
| retrieval__k20-norerank | 0.3955 | 0.3750 | 0.2550 | 0.5401 |
| retrieval__k20-rankfuse | 0.3885 | 0.3677 | 0.2585 | 0.5511 |
| retrieval__k20-techonly | 0.3731 | 0.3530 | 0.2508 | 0.5511 |
| retrieval__k20 | 0.3843 | 0.3645 | 0.2632 | 0.5481 |

### mode = subtechnique

| Run | Precision | Recall | F1 | MRR | F1-micro |
|-----|-----------|--------|----|-----|----------|
| llm-only (n=713) | 0.4838 | 0.5508 | 0.5151 | 0.5426 | 0.4380 |
| llm-only__qwen3-5-9b-nothink (n=713) | 0.1947 | 0.3021 | 0.2368 | 0.2442 | 0.0437 |
| rag-en__k20-techonly (n=713) | 0.4288 | 0.4953 | 0.4597 | 0.4828 | 0.4092 |
| rag-en__k20-techonly__qwen3-5-9b-nothink (n=713) | 0.3506 | 0.5372 | 0.4243 | 0.4749 | 0.2147 |
| retrieval__k20-clean (n=713) | 0.0377 | 0.6899 | 0.0715 | 0.3826 | 0.0714 |
| retrieval__k20-norerank (n=713) | 0.0384 | 0.6952 | 0.0727 | 0.3772 | 0.0725 |
| retrieval__k20-rankfuse (n=713) | 0.0646 | 0.6117 | 0.1169 | 0.3741 | 0.1003 |
| retrieval__k20-techonly (n=713) | 0.0384 | 0.6952 | 0.0727 | 0.3811 | 0.0725 |
| retrieval__k20 (n=713) | 0.0864 | 0.5415 | 0.1490 | 0.3614 | 0.1291 |

P@k / R@k:

| Run | P@1 | R@1 | P@3 | R@3 |
|-----|-----|-----|-----|-----|
| llm-only | 0.5119 | 0.4883 | 0.4853 | 0.5424 |
| llm-only__qwen3-5-9b-nothink | 0.2146 | 0.2003 | 0.2057 | 0.2504 |
| rag-en__k20-techonly | 0.4544 | 0.4348 | 0.4292 | 0.4936 |
| rag-en__k20-techonly__qwen3-5-9b-nothink | 0.4278 | 0.4105 | 0.3637 | 0.4933 |
| retrieval__k20-clean | 0.2637 | 0.2496 | 0.1515 | 0.4252 |
| retrieval__k20-norerank | 0.2707 | 0.2543 | 0.1473 | 0.4092 |
| retrieval__k20-rankfuse | 0.2665 | 0.2525 | 0.1564 | 0.4220 |
| retrieval__k20-techonly | 0.2637 | 0.2489 | 0.1519 | 0.4229 |
| retrieval__k20 | 0.2609 | 0.2478 | 0.1547 | 0.4082 |

