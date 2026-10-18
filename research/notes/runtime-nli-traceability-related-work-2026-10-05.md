# Traceability with NLI or model checks at run time: verified related work (2026-10-05)

Three search agents covered three angles: RAG citation, grounded summarization, and applied high-stakes domains. They
verified every entry on arXiv, the ACL Anthology or the publisher. I spot-checked four key entries myself (CAMS
abstract and method, Actions with Receipts abstract and method, Verifiable by Construction abstract). Many entries are
2026 arXiv preprints and not peer reviewed, as marked.

## The three closest, and what each changes for our paper

**1. CAMS: closest in structure.** Guan, S. "Attributable by Construction: Claim-Anchored Provenance for
Multi-Document Summarization." arXiv 2606.23989. Versions 1-2 were titled "Faithful by Construction: Claim-Anchored
Attribution …"; v5 is dated 11 Sep 2026.
- **Same as ours:** claims carry verbatim quotes that code resolves to spans; summary sentences end in IDs that code
  parses back to spans; provenance is kept apart from support.
- **Matching:** exact substring first, then fuzzy windowed indel similarity accepted above ρ (0.85 in v2). Claims
  whose quote does not match are dropped (§3.3).
- **NLI at run time, in four places, with authority:**
  - DeBERTa-v3-MNLI merges clusters and detects conflicts (§3.4);
  - a TRUE/SummaC-style self-support score drives selection (§3.5);
  - a verifier checks each summary sentence for support and "no-overflow" (§3.7). A failing sentence gets at most two
    repairs and is then dropped.
- No person is involved during generation.
- **Paper impact.** Our draft describes CAMS only as fuzzy 0.85 with dropping. It must add that CAMS also uses NLI at
  run time to select, repair and drop. The contrast is authority:
  - CAMS: fuzzy matching accepts, NLI deletes, failures disappear.
  - Ours: fuzzy matching only points, NLI only warns, failures stay visible.

  Reference [7] should cite the version read and its current title.

**2. Actions with Receipts: closest in principle.** Hu, M., Hu, S., Guo, X., Wang, X., Wang, B., Sa, Y., Zha, D.,
Xiao, J. "Actions with Receipts: Jointly Binding Claims, Evidence, and Execution for Replayable Tool-Agent Auditing."
arXiv 2610.00327, 29 Sep 2026 (cs.CR).
- **Integrity plane.** Exact spans, offsets, hashes and quotes, recorded by the runtime from tool output. A mismatch
  rejects the receipt.
- **Support plane.** Separate and advisory only; integrity does not imply support. Its options are lexical overlap, a
  deterministic guard on numbers, entities and dates, a frozen NLI verifier, and an LLM judge.
- **Results.** On unseen failure families the guard scored F1 0.868 with 0.094 false acceptance, against lexical
  overlap at 0.778 and 0.349 (Table 7).
- **Paper impact.** Code-anchored spans plus an advisory number guard and NLI is not ours alone. We must not write
  "unlike prior work" about this combination. What differs:
  - their spans are recorded by the runtime, so nothing needs locating;
  - in our system the LLM writes the quotation, so code must locate it under tolerance tiers that keep values exact,
    and the tiers are measured against exact and fuzzy matching;
  - unlocated claims stay visible with a pointer;
  - the domain is Thai and English case analysis with a summary written from checked claims.

**3. Verifiable by Construction: closest locator.** Zhang, J., Chen, Y., Commodore-Mensah, Y., Oberst, M.
"Verifiable by Construction: Claim-Level Evaluation of Verbatim Citation in Clinical Question Answering." arXiv
2609.15964 (v2, 17 Sep 2026).
- **Locator.** Code locates quotes in three tiers: exact; normalized (Unicode, case, dashes, quote marks, whitespace,
  markup); and elided, with pieces around an ellipsis. No fuzzy matching. This mirrors our locator.
- **Support.** An LLM judge sees only the claim and its quotes; it is evaluation only.
- **Headline.** Claude Opus 5 quoted verbatim for 98.0% of claims but fully substantiated only 37.1%.
- **Paper impact.** This is independent evidence that provenance is not support, which motivates the screening layer.
  It is also a convergent locator design: cite it, and claim no novelty for the tiers.

## Other verified work, by the authority given to the model check

**Warns or flags only.**
- **VerifAI**: Košprdić et al., arXiv 2604.08549 (2026), biomedical QA. DeBERTa trained on SciFact colours each claim
  against its cited abstract. It also marks a claim "supported" in green, so it confirms.
- **Show Your Work**: Windisch et al., Cureus 2026, doi:10.7759/cureus.108666. An exact-substring quote check plus an
  LLM judge; unsupported predictions go to manual review. (Our [28], Windisch et al., may be this paper or its medRxiv
  preprint; check.)
- **HallDetect**: Oukelmoun et al., arXiv 2608.05823 (2026). NLI per claim over source chunks; it flags and points to
  a chunk; nothing is anchored by code.
- **CARE**: Bedi et al., arXiv 2606.08969 (2026). Flags for clinicians from a GPT-5-mini judge with conformal
  thresholds.
- **EviSearch**: arXiv 2604.14165 (2026). A value it cannot reproduce is kept, marked uncorroborated and sent for
  review. This is the closest "visible failure" design, but its verifier is an LLM.
- **SelfCheckGPT-NLI**: Manakul et al., EMNLP 2023. Its premise is the model's own samples.

**Selects, reranks, steers or drops.**
- **Falke et al.**, ACL 2019. NLI reranks summary beams; out-of-the-box NLI did not help on test, a negative result.
- **Chen, Choi, Durrett**, Findings EMNLP 2021. NLI verifies QA predictions. The premise is the decontextualized
  sentence holding the answer, close to our sentence holding the number; NLI drives abstention.
- **VeriCite**: Qian et al., SIGIR-AP 2025. A TRUE T5-11B filter drops statements.
- **VTG**: Sun et al., EMNLP 2024. A TRUE verifier triggers re-citation, retrieval and regeneration.
- **Think&Cite**: Li and Ng, ACL 2025. An NLI reward steers a tree search.
- **PrefixNLI**: Harary et al., ACL 2026. NLI penalises tokens during decoding.
- **TTPrint**: Cheng et al., arXiv 2605.25836 (2026), cyber threat intelligence and ATT&CK. Evidence is located
  approximately and an LLM verifier drops candidates.

**Edits or proposes edits.**
- **DCR**: Wadhwa et al., Findings EMNLP 2024. MiniCheck flags sentences, and a refiner edits them.
- **GenAudit**: Krishna et al., NeurIPS 2024 workshop. It suggests evidence and edits; a person accepts or rejects them.
- **RARR**: Gao et al., ACL 2023. A PaLM agreement model drives the edits; NLI (AutoAIS) is used only to evaluate.
- **Abridge whitepaper**, 2025, not peer reviewed. A deployed clinical scribe; a trained detector edits notes before a
  clinician signs.

**Evaluation only.**
- **ALCE**, AutoAIS, SummaC and MiniCheck as metrics.
- **DocLens**: ACL 2024.
- **SmartBook**: arXiv 2303.14337, for intelligence analysts. NLI measures citation precision and recall.
- **TR Labs legal groundedness**: NLLP 2024.
- **VeriFact**: NEJM AI 2026. An LLM judge against the patient's own EHR; its "Not Addressed" label is close to our
  "not confirmed".
- **Magesh et al.**: JELS 2025. Its definition of "misgrounded" (a real source that does not support the claim) is
  exactly the gap between Level 1 and Level 2.

**Corrections to things said earlier today.**
- AGREE (NAACL 2024) uses NLI only to build training data, not at test time.
- CEG (ACL 2024) calls a GPT prompt its "NLI module".
- Self-RAG uses no NLI model.

## Positioning sentence that the evidence supports

> Closest in structure, CAMS resolves verbatim quotes to spans and has claims cite IDs, but lets fuzzy matching accept
> a quote and NLI select, repair and drop sentences. Closest in principle, Actions with Receipts keeps an advisory
> support plane, including a numeric guard and NLI, apart from exact spans recorded by the runtime. We apply that
> division of authority to quotations written by the model itself, which code must locate under tolerance tiers that
> keep values exact, and we keep every failure visible to the person who decides.

## Housekeeping

WebFetch cached a few PDFs it could not parse in the session's `tool-results` folder, outside the repository
(Falke 2019, AGREE, SOUPS 2025). Nothing was saved in the repository.
