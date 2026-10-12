# Paper story — Ubi-Media 2027 short paper

## Title
"Traceable by Construction: Evidence-Grounded LLM Analysis of Thai Cybercrime Cases" (system left unnamed; "backend" kept only in Implementation).

## Thesis
LLM case-analysis tools for cybercrime complaints should not be trusted to write their own
evidence pointers. CyberCase moves traceability out of the prompt and into the backend: the
model may only *select* backend-issued Source-unit IDs, the backend reproduces the quoted text
from exact offsets, and a frozen, cheap Claim/Source NLI check labels each Claim before
synthesis.

## Gap
- Attributed-generation work (ALCE, Attribute-First) and domain workflows (default-judgment
  review, chat forensics, exhibit design) either let the model emit citations/quotes, or rely on
  manual audit of explicit evidence IDs (Yang et al. 2026: manual unit tables, n=2 experts).
- Thai-language cybercrime complaints are multi-document, OCR-heavy and low-resource; no work
  we found evaluates a Claim/Source check under English-to-Thai transfer for this setting.

## Contributions (bounded)
1. Architecture: claims-only Reader over backend-issued Source-unit IDs; deterministic binding to
   original spans; Judgement that sees Claims only and ends every summary sentence with Claim IDs;
   deterministic report snapshots.
2. A frozen three-stage Claim/Source check (MPNet selection -> mDeBERTa NLI -> TRAIN-fitted LR),
   evaluated on WiCE TEST, AttributionBench ID/OOD, and Google MT-TH translations of the latter.
3. A paired downstream replay showing the admission/utilisation trade-off when the check is used
   as a hard gate, which motivates deploying it as a warning label instead.

## Claims to make
- Structural: no generated quotation reaches a report; unknown/stale/duplicate IDs are rejected
  (design property + tests).
- Verifier: B1-LR improves Macro-F1 over raw NLI thresholding on WiCE TEST (+0.033, CI excludes 0).
- Transfer: MT-TH raises false acceptance (+17.4 pp ID, +4.4 pp OOD).
- Replay: as a gate, unsupported-ID utilisation 100% -> 22.2% (15 pairs, p = 0.016) at the cost of
  ~30% supported coverage.

## Claims to avoid
- Native Thai case accuracy; factual or legal correctness; hallucination reduction in prose;
  user benefit or time saved; population-level propagation gains; that mDeBERTa is the best
  backbone; that "bound" means "true".
