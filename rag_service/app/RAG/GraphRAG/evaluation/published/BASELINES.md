# Published numbers to compare against

Reference figures taken from the papers named in `NOTICE.md`, kept here so a
run can be read against them without re-opening the PDFs. Only the rows that
matter for this comparison are reproduced. **These are their numbers, not
ours** — nothing in this file is produced by this repository.

## TRAM — the split common to all three papers

Source: TechniqueRAG (arXiv 2505.11988), Tables 2 and 3. Single-label split.

### Technique level (sub-techniques rolled up to parent)

| Method | Prec. | Rec. | F1 |
|---|---|---|---|
| *Retrieval / ranking* | | | |
| NCE | 90.30 | 78.90 | 84.22 |
| BM25 | 67.86 | 64.74 | 66.26 |
| RankGPT | 61.93 | 58.56 | 60.20 |
| TechniqueRAG re-ranker | 64.69 | 61.43 | 63.02 |
| Text2TTP | 51.59 | 21.36 | 30.22 |
| *Generative, zero-shot* | | | |
| GPT-4o | 38.28 | 49.98 | 43.35 |
| DeepSeek v3 | 43.74 | 65.69 | 52.51 |
| Ministral 8B | 7.68 | 31.71 | 12.36 |
| *RAG* | | | |
| GPT-4 (RAG) | 55.50 | 70.64 | 62.16 |
| DeepSeek v3 (RAG) | 54.59 | 77.36 | 64.01 |
| IntelEx | 60.67 | 70.71 | 65.31 |
| **TechniqueRAG (fine-tuned)** | **76.00** | **72.14** | **74.02** |

### Sub-technique level

| Method | Prec. | Rec. | F1 |
|---|---|---|---|
| NCE | 77.00 | 65.80 | 70.96 |
| BM25 | 48.41 | 46.56 | 47.47 |
| RankGPT | 43.03 | 40.97 | 41.97 |
| TechniqueRAG re-ranker | 50.76 | 48.45 | 49.58 |
| GPT-4o | 27.62 | 36.34 | 31.38 |
| DeepSeek v3 | 30.97 | 47.07 | 37.36 |
| GPT-4o (RAG) | 39.29 | 52.84 | 45.07 |
| DeepSeek v3 (RAG) | 39.31 | 58.54 | 47.04 |
| IntelEx | 53.09 | 63.33 | 57.76 |
| **TechniqueRAG (fine-tuned)** | **72.69** | **68.74** | **70.66** |

## Expert — multi-label, and the only split with published @k figures

Source: TechniqueRAG Table 4 (ranking methods).

| Method | @1 P | @1 R | @1 F1 | @3 P | @3 R | @3 F1 |
|---|---|---|---|---|---|---|
| *technique level* | | | | | | |
| BM25 | 51.6 | 21.4 | 30.2 | 35.5 | 40.4 | 37.8 |
| Text2TTP | 53.5 | 26.1 | 35.1 | 37.4 | 49.1 | 42.4 |
| RankGPT | 56.7 | 25.3 | 34.9 | 37.4 | 46.6 | 41.5 |
| NCE | 74.5 | 23.6 | 35.9 | — | — | 48.3 |
| **TechniqueRAG re-ranker** | **71.3** | **35.3** | **47.2** | **44.6** | **59.9** | **51.1** |
| *sub-technique level* | | | | | | |
| BM25 | 45.9 | 15.6 | 23.3 | 31.0 | 29.9 | 30.5 |
| RankGPT | 49.7 | 19.8 | 28.4 | 34.8 | 37.8 | 36.3 |
| **TechniqueRAG re-ranker** | **66.9** | **29.0** | **40.5** | **47.1** | **54.2** | **50.4** |

## H-TechniqueRAG

Source: arXiv 2604.14166. Note it reports on **CTI-RCM and MITRE CTI**, using
TRAM only for cross-domain generalisation, so its headline numbers are not
directly comparable to the TRAM tables above.

| | CTI-RCM | MITRE CTI |
|---|---|---|
| micro-F1 | 72.1 | 69.8 |
| Precision | 75.3 | 72.9 |
| Recall | 69.2 | 66.9 |
| MAP@10 | 69.8 | 69.8 |
| Inference | 820 ms (vs 2180 ms) | — |
| LLM calls | 2 (vs 5) | — |

Claimed improvement over TechniqueRAG: +3.8% F1, −62.4% latency, −60% API calls.

## How to read our runs against these

- **Retrieval arm** → the retrieval/ranking block. Note their P ≈ R on the
  single-label TRAM split, which means they are scoring roughly one prediction
  per sample: the comparable figure from our runs is **P@1**, not the
  full-ranked-list precision.
- **rag-en arm** → the RAG block (GPT-4 RAG, DeepSeek v3 RAG, IntelEx).
- **llm-only arm** → the zero-shot generative block.
- **The TechniqueRAG row itself is fine-tuned on the matching train split.**
  Our arms are all zero-shot. Beating the zero-shot and off-the-shelf-retriever
  rows is the achievable claim; matching the fine-tuned row is not the target
  unless we fine-tune too.
- Their corpus is technique summaries only. Ours is a mixed ATT&CK entity graph
  (techniques, groups, software, campaigns, mitigations). On procedure text
  lifted from Group/Software pages that is a materially harder haystack — which
  is what `--technique-only` exists to isolate.
