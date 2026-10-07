# LLM output checked by deterministic code: five 2026 papers, verified (2026-10-05)

The five citations came from another chatbot, unverified. One agent per paper found and read each one, and checked
the claims made about it. Titles, authors and venues were then re-checked against the ACL Anthology landing pages and
against Crossref for the Springer and IEEE DOIs. All five exist.

## Citations

| Key | Citation |
|---|---|
| Awatramani 2026 | V. Awatramani. "Vasudev Awatramani at #SMM4H-HeaRD 2026: A Two-Pass LLM Pipeline with Deterministic Rule Derivation for Interpretable Insomnia Detection in Clinical Notes." SMM4H-HeaRD 2026 Workshop, ACL, pp. 160-164. https://aclanthology.org/2026.smm4h-1.26/, doi:10.18653/v1/2026.smm4h-1.26 |
| Pusapati and Singh 2026 | S. S. R. Pusapati, A. Singh. "Gladiator at MEDIQA-SYNUR 2026: Contextual Clinical Extraction: Integrating Foundation Models with Domain-Specific Validation Rules." 8th Clinical NLP Workshop @ LREC 2026, pp. 183-191. https://aclanthology.org/2026.clinicalnlp-1.20/, doi:10.63317/2tkvpwgzzcn2 |
| Foss 2026 | D. T. Foss. "Deterministic Validation for Reliable LLM-Based Causal Knowledge Extraction." ICECET 2026 (6th), Rome, pp. 1-6. doi:10.1109/ICECET65726.2026.11632715. Preprint: "The 14-Step FOSS Gate: …", Zenodo doi:10.5281/zenodo.18385710 |
| Falcão and Canedo 2026 | F. D. S. Falcão, E. D. Canedo. "Evaluating foundation model integration strategies for detecting PII in java software engineering pipelines." Empirical Software Engineering 31, 184 (2026). doi:10.1007/s10664-026-10919-y (open access) |
| Padró et al. 2026 | L. Padró, D. Ferrés, R. Saurí, M. Artigot. "An LLM-Based Assistant for Debt Waiver Court Procedures." LREC 2026, pp. 505-514. https://aclanthology.org/2026.lrec-1.35/ |

## What each does, and where the original table was wrong

**Awatramani 2026** (insomnia detection in MIMIC-III notes).
- **Pipeline.** One Gemini 2.5 Flash call returns typed evidence lists of verbatim strings, with no labels and no
  offsets. Python then derives every label: a component is "yes" if at least one item of its type exists. Code finds
  each quote by exact, unnormalised substring search and computes the offsets.
- **On failure.** A quote that is not found is dropped silently. There is no count, flag, pointer or person.
- **Gaps.** No LLM-only baseline and no ablation; the author lists both as missing. It is unclear whether a component
  whose quotes all fail goes back to "no".
- **Table check.** "Character-level citations" holds only because code computes the offsets; the model returns
  strings. The rule engine is minimal.

**Pusapati and Singh 2026** (nurse dictation to flowsheet; shared-task system paper).
- **Pipeline.** One Claude call returns IDs and values with no quotes or spans. Code then runs six veto filters
  (ranges, context keywords, hedges), five corrections that rewrite or infer values, a separate 400+ regex extractor
  that fills only the IDs the LLM missed, and schema validation that accepts options by fuzzy substring matching.
- **Results.** Dev set only, with no ablation; the counts in Table 3 do not reproduce its percentages.
- **Table check.** The 400+ regexes add recall; they do not check the LLM. "A rule layer controls precision" is the
  authors' stated intent, not a measured result: 57% of errors are false positives.

**Foss 2026** (causal triple extraction).
- **Gate.** An accepted triple must pass 14 predicates, joined by AND, covering structure, semantics, evidence and
  quality.
  - The source checks, P7 (numbers verifiable in the source) and P10 (traces to an evidence span), are one-line rules
    with no stated matching method.
  - In the ablation (20 documents), only P4 ever rejected anything, so source grounding had no measured effect.
- **Determinism.** "Reliability" is mostly byte-level reproducibility, which comes from greedy decoding.
- **On failure.** Failures are dropped, and no person is involved.
- **Read.** The preprint was read; the IEEE version is closed access, and only its abstract and metadata were read.

**Falcão and Canedo 2026** (PII literals in synthetic Java snippets).
- **Design.** The paper compares three architectures: classifiers only (P1), classifiers plus an LLM judge (P2), and
  LLM-only structured extraction (P3). P3 has deterministic stages for schema, sanitising, normalising, label mapping
  and a "non-verbatim" filter.
- **Unspecified.** The filter's mechanism is not given, and its effect is not measured.
- **Headline.** The LLM judge (P2) cost recall. The agent found that the P2 numbers are internally inconsistent, so
  they should be cited as printed and nothing derived from them.
- **Table check.** The title in the table was a paraphrase.

**Padró et al. 2026** (Spanish debt-discharge court files; EU JuLIA proof of concept).
- **Pipeline.** A rule-based document classifier (test F1 92.1), then Llama-3.1-8B extraction self-hosted for
  privacy (average field F1 79.0 on 93 held-out applications), similarity-based merging, and a UI with editable
  drafted court orders.
- **Authority.** The judge decides, but that is a stated intent.
- **Provenance.** No value carries a quotation or offset; the user is expected to open the original.
- **Missing.** No user study.
- **Table check.** "Draft ruling" was overstated: suggesting the ruling was a goal the authors dropped.

## How to use them in the paper

- **They establish the design family.** An LLM proposes; deterministic code accepts, derives or rejects. The pattern is
  not ours to claim, and we do not.
- **None gives evidence that the deterministic layer improves accuracy.** No paper ablates its check against an
  alternative. Foss's ablation shows one predicate firing. Cite them as design precedents, not as evidence.
- **Among these five, none does the three things the CyberCase paper measures:**
  1. anchoring each output to a verbatim source span under named tolerance tiers with exact values: Awatramani is
     exact and unnormalised; the PII paper and Foss leave the method unspecified; Gladiator and Padró have no
     per-value provenance;
  2. keeping failures visible: all five drop failures or leave verification to the user;
  3. measuring the acceptance policy against alternatives: exact versus similarity thresholds.

  This is a statement about these five papers, not a "first" claim.
- **Closest in mechanism:** Awatramani, with verbatim strings from the LLM, offsets from code, and labels from code.
- **Closest in genre:** Padró et al., an applied prototype on real legal case files, with held-out measurements, no
  user study, and a person who decides.

## Housekeeping

WebFetch cached the PDFs it could not parse in the session's `tool-results` folder, outside the repository. Nothing
was saved in the repository, and nothing was downloaded from Zenodo.
