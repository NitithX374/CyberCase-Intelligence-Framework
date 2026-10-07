# Whitespace runaway under constrained JSON decoding: who else has it, and what helps

Written 2026-09-30.

**Scope.** The review was compiled from three searches: inference-engine issues, provider documentation and forums,
and papers. Every item listed was opened by the search. The key GitHub items and the COLM paper were checked again by
hand, marked ✓.

**Our data** comes from `research/analysis_baseline` (README, results and `raw_*/max_tokens_*.txt`).

## 1. The failure in our system

- **What happens.** The reading call writes valid JSON for a while, then only whitespace (lines of spaces and
  newlines) until `max_tokens` (40,800). The stage then fails and is asked once more.
- **How often.** The first reading attempt ran away in about 14-19% of calls. Two runaways in a row lose the case:
  about 4-5% of two-call analyses.
- **Cost of one runaway.**
  - Time: median 10 minutes, up to 25. A normal reading takes 2.2 minutes.
  - Money: about USD 0.012, against 0.003 for a normal reading.
  - The client's 120-second setting does not bound the call. It is httpx's per-read timeout, not a total deadline.
- **Where the output stops.** 142 runaway dumps were read, keyed by arm from the schema's key order:

  | Stall | Key the schema forces next | Seen |
  |---|---|---|
  | end of a citation's `exact_quote` string | `document_id` (locator keys) | shipped 45 |
  | end of a claim's citation lists | `reasoning_summary`, or `contradicting_citations` after the supporting list | 76: slim 23, single 28, shipped 16, nonull 7, reorder 2 |
  | a claim's `text` string, closed early by a bare `"` inside the prose | none; the model wants to go on writing text | 3 |
  | right after `reasoning_summary`, or inside a citation after `page_numbers` | end of claim, or next citation | 5 |
  | stall position not in the saved text (older dumps keep only the head and tail) | unknown | 9 |
  | other stages: judgement `summary` 2, prose baseline 1, unparseable 1 | not the reading | 4 |

  The six rows add up to all 142 dumps.
- **What the two main stall sites share.** Each is the first required key after a point where the object could close:
  after the quote, and after the citation lists. Naming the key in the prompt is not what separates them: the shipped
  prompt does name `document_id` ("leave document_id and filename null"), and that is the largest group. Keys the
  prompt never names, such as `claim_type` and `exact_quote`, are not stall sites. Position is the better fit. This
  was inferred after the data, so it is exploratory.

- **Hesitation and recovery.** 20 whitespace-only lines appear inside the valid part of those dumps, always at the same
  stall points. Each time the model wrote a blank line or two and then gave in: it wrote `,` and the forced key.
- **The prompt names few of the keys.** Under vLLM the model does not see the schema (row E7). Our reading prompt never
  names `claim_type`, `epistemic_status`, `supporting_citations`, `contradicting_citations`, `reasoning_summary` or
  `exact_quote`. The model meets each of them only when the grammar forces it.
- **Reorder, descriptive.** The cancelled 100-case reorder confirmation left 21 runaway dumps: 19 from the shipped
  reading and 2 from the reorder reading. The runs were interleaved case by case, so the two arms had about the same
  number of calls. Iteration 2 had given 1 in 30.

## 2. Engineering reports

| # | Source | Model / engine | What it shows |
|---|---|---|---|
| E1 ✓ | vllm-project/vllm#38696 (2026-04-01, open) and its comment of 2026-08-18 | Qwen3.5 in the issue; **google/gemma-4-26b-a4b-it BF16, xgrammar, strict json_schema** in the comment | 6 of 10 production prompts failed with `finish_reason=length`, deterministic within a launch. The server flag `disable_any_whitespace` fixed them. Client-side changes did not (penalties, temperature, strict or not, a single-line instruction). The compact grammar returned empty arrays instead |
| E2 ✓ | vllm-project/vllm#40080 (2026-04-17) | Gemma 4 31B and 26B-A4B | Loops under a JSON schema. The same prompts without `response_format` finished. llama.cpp was 10/10 valid |
| E3 ✓ | vllm-project/vllm#42110 (2026-05-08, open) | gemma4-31b | Prompts that describe JSON requirements *and* send `response_format.json_schema` time out |
| E4 ✓ | ollama/ollama#18567 (2026-09-21) | gemma4 on Ollama's MLX engine (xgrammar) | Stalls exactly where the grammar needs the next property name, about 5,490 whitespace characters. The same model on llama.cpp finishes |
| E5 ✓ | jundot/omlx#2990 (2026-08-21) and PR #3321 (merged 2026-09-30) | Qwen3.6-35B-A3B, xgrammar | 23% of calls hit the token ceiling. Trigger: a bare ASCII quote from the source closes the JSON string early. Penalties and temperature did nothing. The fix caps whitespace at 32 |
| E6 ✓ | theroyallab/tabbyAPI PR #481 (2026-09-17, open) | Gemma4-26B-A4B, llguidance | Before: 5/5 `length`. After a stall guard that masks whitespace after 8 whitespace tokens: 5/5 valid |
| E7 | vLLM Gemma 4 recipe (docs.vllm.ai) | Gemma 4 | Under `response_format`, Gemma 4 does not see the schema or its field descriptions. Put output instructions in the system message |
| E8 ✓ | vllm-project/vllm#48765 (2026-07-15, open) | vLLM V1 | The per-request `disable_any_whitespace` returns HTTP 200 and does nothing. Only the server flag works |
| E9 ✓ | vllm-project/vllm PR #44619 (2026-06-05, open) | vLLM + xgrammar | Root cause: `compile_json_schema()` is called without `max_whitespace_cnt`, so whitespace is unbounded. Proposes a default of 8. Unmerged |
| E10 ✓ | mlc-ai/xgrammar PR #414 (merged 2025-09-06) | xgrammar | Adds `max_whitespace_cnt`. The default stays unbounded (`any_whitespace=True` since PR #123) |
| E11 ✓ | sgl-project/sglang#8250 (2025-07-22) | SGLang + xgrammar | Asks for a way to disable any-whitespace. Flags exist, off by default |
| E12 | OpenAI structured-outputs docs, as quoted by Microsoft Learn (Azure OpenAI JSON mode) | OpenAI JSON mode | Without a JSON instruction the model may emit whitespace until the token limit. Keys follow schema order |
| E13 | OpenRouter streaming docs | our providers | Aborting a stream stops billing only for listed providers. CoreWeave, NextBit and Parasail are not listed |

**Engine defaults** (from the searches' reading of source code):

| Engine | Whitespace between JSON tokens |
|---|---|
| xgrammar, vLLM, SGLang, llguidance, TensorRT-LLM | unbounded by default |
| outlines / outlines-core (`[ ]?`, since 2024) | bounded |
| llama.cpp (at most 2 newlines plus 20 spaces) | bounded |
| oMLX (since 2026-09-30) | bounded |

**Closest precedents** (added from the reviewer-2 search):
- **Predibase, "LoRAX + Outlines" (blog, 2024-03-03).** A schema key order that forced low-probability field names
  made the model generate whitespace until the token limit.
- **DCPMA / OASIS-LLM documentation (GitHub, 2026-04-26).** gemma-4-31b-it via OpenRouter produced whitespace-only
  completions under a strict schema that required a `reasoning` field the prompt did not ask for. Their fix was to name
  the keys in the prompt, drop `response_format` and parse tolerantly. That is our stall type and our fix, anecdotal,
  on one small schema.
- **ExtractBench (Ferguson et al., arXiv 2602.12247).** On large nested extraction schemas, provider structured-output
  modes lowered validity against prompt-based extraction.

## 3. Papers

| # | Paper | Bearing on our failure |
|---|---|---|
| P1 ✓ | Li, Rahili, Zhao. *Correctness-Guaranteed Code Generation via Constrained Decoding*. COLM 2025 (arXiv 2508.15866) | Nontermination is a well-known issue of constrained decoding, part of distribution distortion (p. 9). Infinite repetition occurs in JSON-schema decoding too, more often with smaller models; JSON generation can output infinite whitespace in outlines (p. 33) |
| P2 | Park et al. *Grammar-Aligned Decoding*. NeurIPS 2024 | Masking distorts the model's distribution. This is the general mechanism behind a masked closing brace |
| P3 | Beurer-Kellner, Fischer, Vechev. *DOMINO*. ICML 2024 | At a JSON key position the legal tokens are whitespace, a quote or a brace. Token/grammar misalignment shifts whitespace behaviour |
| P4 | Dong et al. *XGrammar*. MLSys 2025 | The engine likely behind our providers. It masks invalid tokens and renormalises. The library default allows unbounded whitespace |
| P5 | Geng et al. *JSONSchemaBench*. arXiv 2501.10868 | Counts generation timeouts as failures. No whitespace diagnosis |
| P6 | Tam et al. *Let Me Speak Freely?* EMNLP 2024 Industry; counterpoint: the .txt "Say What You Mean" post (2024) | Format restriction and key order can change output quality. Contested |
| P7 | Kato, Tarashima. *TruncProof*. arXiv 2605.13076 (IJCNN 2026 per its comment) | Grammar-constrained JSON decoders cannot guarantee they finish within a token budget |

What the papers do and don't show:
- They establish the general mechanism: masking plus renormalisation, and nontermination under constrained decoding.
- The exact trap is documented only in engineering reports. The trap: the closing brace is masked while a required key
  remains, whitespace is legal and leaves the parser state unchanged, so the same choice repeats.
- No paper links required keys or key order to nontermination.
- No paper evaluates remedies or retries.

## 4. What an API caller can do (we cannot change the providers' engines)

| Option | Evidence | Cost or risk |
|---|---|---|
| Name every key, in schema order, in the reading prompt (a JSON template) | E7, E3; our finding that the prompt omits most keys | Untested here. A prompt change, so outputs may shift |
| Order the schema so each object ends where the model wants to stop (reorder) | Ours: 2 against 19 in the cancelled run, and 1/30 in iteration 2 | Schema change, so outputs may shift |
| Escape or replace bare `"` inside prose | E5 | Quotes must still match the source verbatim |
| Retry on the other provider rather than the same one | E1: deterministic within a launch | Engineering only |
| Stream and abort at a long whitespace run | E6 (server-side version) | Saves time, not money, on CoreWeave and NextBit (E13) |
| A `stop` sequence on a whitespace-only line | Untested | Our hesitation lines show it would also kill calls that recover |
| Lower `max_tokens` | Certain to make a runaway cheaper | May cut long Thai readings; size it on Thai cases first |
| Drop `response_format` and validate in code | E1, E2, E5 controls all finished | Loses the structural guarantee; needs its own retry path |
| Ask OpenRouter or the providers to cap whitespace | E1, E9, E10 | Outside our control |
| Change the model | Qwen also loops (E1 issue, E5), so this is not a guaranteed fix | Every result was measured on Gemma |

**What does not help** (measured by others, E1 and E5):
- repetition, frequency and presence penalties;
- temperature;
- strict against non-strict mode;
- a "single-line JSON" instruction;
- OpenRouter's Response Healing.

## 5. Unknown

- Which engine and version CoreWeave and NextBit run. vLLM with xgrammar is an inference from the symptom.
- How gpt-oss-20b or other candidates behave under our schema.
- Thai. Everything above is on English text.
