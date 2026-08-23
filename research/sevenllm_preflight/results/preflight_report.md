# SEvenLLM Six-Task Pilot Preflight

Status: **READY FOR PILOT**

This is a preflight only. No B0 or mT5 weights were loaded and no model inference was run for the 593 selected samples.

## 1. Dataset and approved selection

Source: [SEvenLLM](https://github.com/CSJianYang/SEevenLLM), benchmark file `code/score/f1_rougel/test_all.jsonl`, audited commit `a84b86aabf2b5be35a2cbbac546511883cc5ff85`.

| Category | Samples |
| --- | ---: |
| Threat Analysis | 316 |
| Protection Strategy Research | 89 |
| Summary Generation | 61 |
| Incident Response Planning | 52 |
| Risk Assessment | 47 |
| Impact Scope | 28 |
| **Total** | **593** |

The selection contains 300 English and 293 Chinese rows, with 549 generation, 43 choice, and 1 structured-extraction row. IDs are unique, and all selected records passed the format-structure checks. The complete selected-ID list is in [`preflight_manifest.json`](./preflight_manifest.json).

## 2. Exact mT5 tokenizer and configuration

| Field | Resolved value |
| --- | --- |
| Model | [`google/mt5-base`](https://huggingface.co/google/mt5-base/tree/2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f) |
| Hugging Face revision | `2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f` |
| Runtime | `transformers==5.8.0`, `sentencepiece==0.2.2` |
| Loaded tokenizer | `transformers.models.t5.tokenization_t5.T5Tokenizer` |
| Fast-tokenizer flag | `True` |
| Tokenizer vocabulary | 250,100 SentencePiece entries; model config vocab size 250,112 |
| Special IDs | pad=0, eos=1, unk=2 |
| Reported tokenizer max | `1000000000000000019884624838656` (`VERY_LARGE_INTEGER` sentinel) |
| Serialized `model_max_length` | absent from `tokenizer_config.json` |
| Serialized tokenizer `name_or_path` | `google/mt5-small`; this is shared tokenizer metadata and does not change the requested base model |

The exact tokenizer files were loaded locally without model weights. The base Python environment was missing SentencePiece; the successful measurement used the temporary pinned package above. That dependency must be installed or equivalently pinned before the pilot run.

Relevant mT5 config values are `MT5ForConditionalGeneration`, `d_model=768`, `d_ff=2048`, `d_kv=64`, 12 encoder layers, 12 decoder layers, 12 heads, `relative_attention_num_buckets=32`, and effective `relative_attention_max_distance=128` from the `MT5Config` default because the serialized field is absent. The config has no `max_position_embeddings`, `n_positions`, or `max_length`. Therefore, no absolute practical input limit is claimed from metadata; the measured maximum below is the usable pilot bound for this selected data.

## 3. mT5 input token lengths

Inputs were formed exactly as requested, with EOS included by the loaded tokenizer and no truncation:

```text
task: <category>
instruction: <instruction>
context: <input>
```

Choice rows append `answer:` after the context. No thought, gold output, filename, or hidden metadata entered the prompt.

| Subset | n | Mean | P50 | P75 | P90 | P95 | P99 | Max | >512 | >768 | >1024 | >confirmed practical limit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **All** | **593** | **248.651** | **223** | **268** | **356** | **459** | **781.8** | **1019** | **26 (4.384%)** | **7 (1.18%)** | **0 (0%)** | **N/A: unconfirmed** |
| Impact Scope | 28 | 199.607 | 201.5 | 240.5 | 267.7 | 288.15 | 346.02 | 366 | 0 (0%) | 0 (0%) | 0 (0%) | N/A |
| Incident Response Planning | 52 | 216.538 | 206.5 | 235.5 | 265 | 291.6 | 447.47 | 449 | 0 (0%) | 0 (0%) | 0 (0%) | N/A |
| Protection Strategy Research | 89 | 248.91 | 208 | 274 | 354 | 452.4 | 890.04 | 949 | 4 (4.494%) | 2 (2.247%) | 0 (0%) | N/A |
| Risk Assessment | 47 | 222.064 | 212 | 255.5 | 276.2 | 332.8 | 453.66 | 513 | 1 (2.128%) | 0 (0%) | 0 (0%) | N/A |
| Summary Generation | 61 | 308.967 | 268 | 300 | 470 | 674 | 876.2 | 1019 | 6 (9.836%) | 2 (3.279%) | 0 (0%) | N/A |
| Threat Analysis | 316 | 250.519 | 222.5 | 268 | 360.5 | 464.25 | 741.3 | 859 | 15 (4.747%) | 3 (0.949%) | 0 (0%) | N/A |
| English | 300 | 247.777 | 227.5 | 265.25 | 324.4 | 449.15 | 755.05 | 1019 | 11 (3.667%) | 3 (1%) | 0 (0%) | N/A |
| Chinese | 293 | 249.546 | 214 | 277 | 384.2 | 488.4 | 781.8 | 882 | 15 (5.119%) | 4 (1.365%) | 0 (0%) | N/A |
| Choice | 43 | 223.767 | 178 | 250.5 | 342 | 456.2 | 700.28 | 791 | 2 (4.651%) | 1 (2.326%) | 0 (0%) | N/A |
| Extraction | 1 | 252 | 252 | 252 | 252 | 252 | 252 | 252 | 0 (0%) | 0 (0%) | 0 (0%) | N/A |
| Generation | 549 | 250.594 | 224 | 269 | 356.2 | 459.2 | 768.04 | 1019 | 24 (4.372%) | 6 (1.093%) | 0 (0%) | N/A |

The 20 longest selected inputs are:

| ID | Category | Language | Format | Input tokens | Gold output tokens |
| ---: | --- | --- | --- | ---: | ---: |
| 1156 | Summary Generation | EN | generation | 1019 | 136 |
| 903 | Protection Strategy Research | EN | generation | 949 | 310 |
| 433 | Protection Strategy Research | ZH | generation | 882 | 192 |
| 915 | Threat Analysis | EN | generation | 859 | 271 |
| 388 | Threat Analysis | ZH | generation | 836 | 133 |
| 1288 | Threat Analysis | ZH | choice | 791 | 2 |
| 340 | Summary Generation | ZH | generation | 781 | 154 |
| 1060 | Summary Generation | EN | generation | 754 | 193 |
| 586 | Threat Analysis | ZH | generation | 750 | 219 |
| 424 | Threat Analysis | ZH | generation | 692 | 167 |
| 1125 | Summary Generation | EN | generation | 674 | 116 |
| 923 | Protection Strategy Research | EN | generation | 672 | 268 |
| 589 | Threat Analysis | ZH | generation | 659 | 163 |
| 500 | Threat Analysis | ZH | generation | 644 | 146 |
| 521 | Threat Analysis | ZH | generation | 638 | 137 |
| 1026 | Threat Analysis | EN | generation | 631 | 249 |
| 335 | Summary Generation | ZH | generation | 619 | 112 |
| 928 | Protection Strategy Research | EN | generation | 613 | 275 |
| 1119 | Threat Analysis | EN | generation | 613 | 309 |
| 904 | Threat Analysis | EN | generation | 606 | 188 |

## 4. Truncation risk and decision

Using 512 only as a conservative diagnostic threshold, 26/593 rows (4.384%) overflow. Right truncation would preserve the task/instruction prefix but lose 4,708 context tokens in aggregate, including context suffixes. Left truncation would lose 1,218 prefix tokens in aggregate and can remove task or instruction text. No summary, repair call, or LLM preprocessing is authorized.

Decision: **Option A, no truncation** for the pilot. The selected maximum is 1,019 tokens, below B0’s 32,768-token model context and within the mT5 architecture’s relative-attention path. A hardware smoke on the longest rows remains an operational check, not a reason to silently truncate.

## 5. Gold output lengths and B1 generation cap

Gold outputs were serialized deterministically for structured output using compact UTF-8 JSON, then tokenized with the same loaded tokenizer. EOS is included.

| Subset | n | Mean | P50 | P75 | P90 | P95 | P99 | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **All** | **593** | **150.452** | **151** | **187** | **219** | **236** | **285.16** | **416** |
| Impact Scope | 28 | 143.071 | 153 | 170 | 202.9 | 205.65 | 206.73 | 207 |
| Incident Response Planning | 52 | 196.115 | 202.5 | 226.75 | 255.9 | 273.4 | 283.47 | 285 |
| Protection Strategy Research | 89 | 173.022 | 186 | 209 | 248 | 272 | 297.68 | 310 |
| Risk Assessment | 47 | 161.191 | 165 | 191.5 | 225.2 | 249.8 | 349.3 | 416 |
| Summary Generation | 61 | 122.492 | 122 | 140 | 154 | 169 | 194.2 | 196 |
| Threat Analysis | 316 | 141.035 | 143 | 173 | 198.5 | 218.25 | 256.65 | 309 |
| English | 300 | 169.07 | 179 | 205 | 235 | 258.05 | 296.13 | 416 |
| Chinese | 293 | 131.389 | 138 | 155 | 177.8 | 191.4 | 221.96 | 272 |
| Choice | 43 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Extraction | 1 | 130 | 130 | 130 | 130 | 130 | 130 | 130 |
| Generation | 549 | 162.117 | 155 | 190 | 220.2 | 238.2 | 286.04 | 416 |

Fixed cap: `max_new_tokens=512` for both models. It covers the observed maximum with a 96-token margin and is applied identically across categories, languages, and formats.

## 6. Format compatibility

Generation uses exactly:

```text
task: <category>
instruction: <instruction>
context: <input>
```

MCQ uses exactly:

```text
task: <category>
instruction: <question and options exactly as provided>
context: <input>
answer:
```

The expected choice output is normalized to exactly one uppercase `A`, `B`, `C`, or `D` before exact match; the raw generation is retained. The single extraction row keeps the supplied instruction, preserves its requested JSON schema, and is not converted to freeform text. No correct option is exposed in the prompt.

## 7. B0 candidate comparison and selection

The comparison used public, pinned Hugging Face metadata from the candidate repositories: [Qwen 1.5B](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct), [Qwen 3B](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), [Qwen 7B](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct), and [BigScience mT0-base](https://huggingface.co/bigscience/mt0-base).

| Candidate | Params | Context | Multilingual fit | Availability/reproducibility | Cost/fairness decision |
| --- | ---: | ---: | --- | --- | --- |
| **Qwen2.5-1.5B-Instruct** | **1.54B** | **32,768** | >29 languages, including EN/ZH | Apache-2.0; public pinned safetensors; revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | **Selected**: smallest modern general instruction baseline; manageable and clearly licensed |
| Qwen2.5-3B-Instruct | 3.09B | 32,768 | >29 languages, including EN/ZH | Public pinned checkpoint; current repository carries Qwen research/other license metadata | Not selected: stronger but less size-matched and less cleanly licensed |
| Qwen2.5-7B-Instruct | 7.62B | 131,072 | >29 languages, including EN/ZH | Apache-2.0; public pinned multi-shard checkpoint | Not selected: capability ceiling, but materially higher memory/cost and unfairer size comparison |
| BigScience mT0-base | 0.58B | mT5-style relative attention | 101 languages, including EN/ZH | Apache-2.0; public pinned checkpoint; same family as B1 | Not selected as B0: useful architecture/size control, not a vanilla general-purpose causal baseline |

Selected B0 contract:

- Model and tokenizer: `Qwen/Qwen2.5-1.5B-Instruct`, both pinned to `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.
- Tokenizer class: `Qwen2Tokenizer`; tokenizer metadata reports 131,072, while the model config’s `max_position_embeddings` is 32,768; use 32,768 as the model context.
- Precision: unquantized `float32` for both B0 and B1 to avoid quantization as a confound. The Qwen checkpoint’s native serialized dtype is bfloat16; the selected runtime contract explicitly loads float32.

## 8. Fixed prompt protocol and semantic equivalence

B0 receives the same task label, instruction, context, and row-specific format requirement as mT5. The only B0-specific rendering is the pinned Qwen chat template with an empty system message, one user message, and `add_generation_prompt=True`. There are no hints, few-shot examples, RAG/MITRE context, chain-of-thought requests, or task-specific prompt optimization.

## 9. Deterministic generation

Both models use `do_sample=false`, `num_beams=1`, and `max_new_tokens=512`. B0 sampling parameters are unset rather than silently inherited from Qwen’s repository generation defaults. B1 uses the same deterministic contract. Raw decoded predictions, normalized choice predictions, and parse failures must all be saved.

## 10. Official evaluation mapping

- Generation: primary ROUGE-L using the official [`gen_score_rougeL-en-path.py`](https://github.com/CSJianYang/SEevenLLM/blob/a84b86aabf2b5be35a2cbbac546511883cc5ff85/code/score/f1_rougel/gen_score_rougeL-en-path.py) and Chinese/general counterpart; multilingual SBERT is secondary using the official `code/score/sbert/gen_score_sbert-*.py` scripts.
- Choice: official [`choice_sorce-path.py`](https://github.com/CSJianYang/SEevenLLM/blob/a84b86aabf2b5be35a2cbbac546511883cc5ff85/code/score/f1_rougel/choice_sorce-path.py) exact match after the strict A-D normalization above. Report denominator-aware accuracy by model, category, language, and format rather than only the script’s fixed ID ranges.
- Extraction: official [`ex-score-en-path.py`](https://github.com/CSJianYang/SEevenLLM/blob/a84b86aabf2b5be35a2cbbac546511883cc5ff85/code/score/f1_rougel/ex-score-en-path.py) flattened-leaf precision/recall/F1 for the one selected row; preserve the requested schema and do not add a new groundedness metric.
- GPT score: the official `get_score_gpt4_prompt.py` is secondary only if provider, model revision, prompt, temperature, seed, and outputs are pinned well enough to reproduce. It is not a primary pilot metric.

Every result is grouped by model, category, language, and format, while raw predictions are retained.

## 11. Machine-readable manifest and verdict

- Manifest: [`preflight_manifest.json`](./preflight_manifest.json)
- Per-sample token/prompt records: [`preflight_records.jsonl`](./preflight_records.jsonl)
- Preflight implementation: [`research/sevenllm_preflight`](../)

The manifest records the full dataset commit and selected IDs, exact B0/B1 revisions, tokenizer/runtime versions, prompt rules, generation parameters, all token statistics, truncation analysis, format checks, scoring mapping, excluded samples, and the fact that no weights or full inference were run.

**Verdict: READY FOR PILOT.** There is no hard technical blocker invalidating `google/mt5-base`. Before execution, install/pin the verified `transformers==5.8.0` and `sentencepiece==0.2.2` pair (or an equivalently verified pair), run a single hardware smoke on the longest rows, then proceed with no input truncation and the fixed generation contract above.
