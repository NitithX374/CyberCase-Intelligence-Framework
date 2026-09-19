# The MITRE applicability gate as an encoder

Before a case is analysed, something has to decide whether ATT&CK has anything
to say about it. Most of what a Thai police file contains — a seized laptop, a
printed email, CCTV, a transfer — is not cyber behaviour, and retrieving
techniques for it produces confident mappings of nothing.

Today that decision is a prompt: one model call reads the whole case and writes
back the spans it chose to copy out. This directory measures an alternative
that is shown **one sentence at a time** and answers about that sentence.

Two things follow from the sentence being the unit:

- **The trigger text cannot be invented.** The LLM gate is asked to quote the
  material and the quote is checked afterwards; the encoder's answer *is* a
  sentence of the material, so it is an exact span by construction.
- **The retrieval query gets better.** `trigger_text` is what goes to the RAG
  service. Per sentence, the technical sentences go and the case's name,
  address and warrant number stay behind.

## Splitting the input

`backend/app/services/case_analysis/sentences.py`, PyThaiNLP `crfcut`. Thai is
written without spaces between words, so a sentence has to be found rather than
split off. Two things the real material forced:

- **Lines are separated first.** A report is headings, form fields and table
  rows, which a splitter trained on prose runs together into one long sentence.
- **Short fragments join a neighbour.** crfcut breaks at the dot in
  `PowerShell.exe`, and leaves scraps like `upload` at the end of a line. Alone,
  `upload` became a trigger and the SQL-injection clause it was cut from did
  not — a useless retrieval query in place of a good one.

Every sentence returned is an exact substring of its source. That is what lets
the gate's answer pass the same grounding check the LLM gate's output has to.

## The answer, first

The LLM gate that runs today is **100% on this set** — perfect precision and
recall, in both languages, including the 36 sentences that are not near-copies
of the worked examples in its own prompt. The encoder gate loses every single
disagreement, ten out of ten.

| on the 36 sentences neither gate was shown | accuracy | precision | recall |
|---|---|---|---|
| LLM gate (`openai/gpt-5.6-luna`) | **100.0%** | **100.0%** | **100.0%** |
| encoder gate (LADDER checkpoint) | 72.2% | 88.9% | 47.1% |

Read the 100% carefully: it means this set never found the LLM gate's limits,
not that it has none. 36 items is small, and the set was designed to trap a
classifier — a strong model walks through it. Finding where the prompt gate
actually fails needs harder material: real OCR'd Thai, and sentences where the
technical and the incidental are in the same clause.

The recommendation is to stay on `MITRE_GATE_MODE=llm`. Reproduce with
`python compare_gates.py`.

### On measuring a gate with its own examples

Ten of the 46 eval sentences turned out to be near-copies of the worked
examples inside `MITRE_APPLICABILITY_SYSTEM_PROMPT` — both were written from
the same list of traps. `compare_gates.py` finds them by trigram containment
(the same measure the analysis uses to tell a clumsy quotation from an invented
one) and reports the clean subset separately. Here it changed nothing, because
the LLM gate scored 100% either way, but a gate scored on its own examples is
not scored at all.

## What the existing model scores

`backend/xlmr_ladder_best/` is the LADDER attack-pattern sentence classifier
([RAID 2023](https://arxiv.org/abs/2211.01753)) — XLM-R base, fine-tuned to
answer "does this sentence describe an attack pattern" over **English CTI
prose**. That is the gate's question, in neither the gate's language nor its
register.

Measured on `eval_sentences.jsonl` (46 sentences written by hand, never trained
on) at the threshold that suits it best — chosen on that same set, so these are
an upper bound:

| | n | accuracy | precision | recall | F1 |
|---|---|---|---|---|---|
| overall | 46 | 73.9% | **91.7%** | **50.0%** | 64.7% |
| th | 26 | 76.9% | 87.5% | 58.3% | 70.0% |
| en | 20 | 70.0% | 100.0% | 40.0% | 57.1% |

**Precision is good and recall is half.** The gate's own prompt says to prefer
precision, so one false RETRIEVE in 46 is the right shape — but half of the
genuinely technical cases would never get ATT&CK context at all, and the LLM
gate gets every one of those right.

The misses are not marginal. These scored **0.001**, the same as a parked car:

| sentence | score |
|---|---|
| Mimikatz was executed on the domain controller and credentials were dumped from memory | 0.001 |
| ตรวจพบ PowerShell.exe เชื่อมต่อออกไปยังไอพี 198.51.100.23 | 0.001 |
| An unknown service was installed on the file server and started automatically | 0.001 |
| Event logs on the workstation were cleared shortly after the suspicious login | 0.001 |
| A macro in the attached document launched a hidden command interpreter | 0.001 |

And one confident error in the other direction: *"ผู้เสียหายพิมพ์ภาพถ่ายหน้าจอ
อีเมลออกมาเป็นเอกสารแนบท้ายคำร้อง"* (the victim printed email screenshots as an
exhibit) at **0.992**.

This is a register mismatch, not a language one — the model reads Thai slightly
*better* than English here (mean score on positives 0.429 vs 0.241). It was
trained on threat-intel prose and is being shown incident records.

Reproduce with `python evaluate_gate.py`.

## The checkpoint is not broken — it is out of its domain

Before concluding anything from a 47% recall, the obvious question: is the
model bad, or is it being used wrong? Measured on LADDER's **own** test set
(`experiments/LADDER/attack_pattern/data/sentence_classification/`, 662
sentences, balanced), at its own decision boundary of 0.50:

| LADDER split | n | accuracy | precision | recall | F1 |
|---|---|---|---|---|---|
| test | 662 | 85.3% | 86.3% | 84.0% | **85.1%** |
| dev | 568 | 84.9% | 81.7% | 89.8% | **85.6%** |
| train | 2214 | 98.1% | 97.1% | 99.3% | 98.2% |

Train at 98% against test at 85% is the ordinary gap between what a fine-tune
memorises and what it learns — worth noting, not worth worrying about, and it
confirms these are the splits the checkpoint was actually trained on.

The checkpoint is healthy and it is being read correctly — the positive output
index is confirmed independently on both splits (86% agreement against 16% for
the other one), and 0.50 is a sensible boundary there.

So the collapse on case material is **domain transfer, and nothing else**.
Two symptoms of the same thing:

- F1 falls from 85% on English CTI prose to 62% on Thai and English incident
  records.
- The useful threshold falls from 0.50 to 0.10. The score distribution
  collapses toward zero on input the model has not seen the like of, which is
  what puts Mimikatz credential dumping at 0.001.

This is the result that says XLM-R is worth fine-tuning rather than
abandoning: the architecture reaches 85% F1 on this task shape, the plumbing is
correct, and the only missing piece is training material in the right register
— which `dataset.jsonl` already holds.

Reproduce with
`python evaluate_gate.py --eval ../../experiments/LADDER/attack_pattern/data/sentence_classification/test.csv`.

## What was ruled out

Zero-training embedding similarity: embed each sentence with BGE-M3 (itself an
XLM-RoBERTa-large encoder, and already the retriever's embedding model) and
take its similarity to the nearest ATT&CK technique description.

It does not work. Best *oracle* threshold reaches 87%, and the errors are the
cases the gate exists for — "a desktop computer was seized" (0.594) outranks
ten true positives, and ransomware encryption (0.538) falls below three
negatives. Similarity measures what a sentence is *about*, and both classes are
about computers. Reproduce with `_probe_similarity.py`.

## If the recall matters

`build_dataset.py` and `train.py` are the remedy, unused so far. The dataset
builder uses the **same model that runs the LLM gate today** to write case-file
sentences in the register the gate is actually shown — one per ATT&CK
technique, Thai and English — plus deliberate near misses taken from the traps
the LLM gate's own prompt names, plus real Thai legal prose. `dataset.jsonl`
holds 1373 such sentences already.

Continuing the fine-tune from the LADDER checkpoint on that material is what
would close the register gap. `train.py` reports every number per language and
prints a language-confound check, because a model trained on English positives
and Thai negatives scores well by detecting the language.

## Turning it on

```bash
MITRE_GATE_MODE=encoder      # llm (default) | encoder | never
MITRE_GATE_MODEL_PATH=xlmr_ladder_best/xlmr_ladder_best
```

`never` is the ablation: no retrieval at all, to measure what the technical
context was worth.

`gate.json`, written beside the weights by `evaluate_gate.py`, carries the
threshold and which output index means "attack pattern" — nothing in the
checkpoint itself says.

`torch` is deliberately **not** in `backend/requirements.txt`; it would add
roughly 2 GB to an image that installs no ML stack today. Only `pythainlp` and
`python-crfsuite` went in, for the splitter.
