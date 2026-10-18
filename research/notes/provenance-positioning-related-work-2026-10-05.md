# Provenance positioning: four related-work claims checked (2026-10-05)

Four claims from a ChatGPT message, checked one by one against the ACL Anthology (paper pages and BibTeX), arXiv
(abstract pages and HTML full text), ACM/Crossref and the dated W3C documents. All four sources exist. Claims 1 to 3
are correct in substance, with the precisions below. Claim 4 has one wrong word in the definition. Each source is
quoted at most once, in under 15 words.

## At a glance

| | (a) Code locates the quotation | (b) An attribution that fails | (c) Automatic support check |
|---|---|---|---|
| GenProve | No. The model writes source sentence IDs, and they are scored against gold offline | Nothing checks it at run time; it is output as written | Training reward and evaluation only |
| SciTrue | No. An LLM picks the sentence, and people checked it afterwards | Nothing checks it at run time; nothing is marked | The verdict is the model's own output; an LLM judge was tried in evaluation only |
| PaperTrail | Only inside the answer, for highlighting. On the source side, embeddings and an LLM pick the sentences | Kept and flagged; omitted claims are shown too | Advisory cosine flag; nothing is gated |
| Ours | Yes, in tiers, at run time | Kept, marked "not confirmed", with a pointer to the nearest passage | NLI flags for human review only |

## 1. GenProve

**Citation.** Wei, J., Wang, X., Liao, Y., Dong, J., Liu, Y., Jia, C., Yu, B., Zhu, J. "GenProve: Learning to Generate
Text with Fine-Grained Provenance." In *Proceedings of the 64th Annual Meeting of the ACL (Volume 1: Long Papers)*,
ACL 2026, San Diego, pp. 5027-5048. Anthology ID 2026.acl-long.228, DOI 10.18653/v1/2026.acl-long.228,
https://aclanthology.org/2026.acl-long.228/. Preprint arXiv:2601.04932 (v2, 12 Apr 2026).

**What it does.** It defines a task it calls *Generation-time Fine-grained Provenance*. After every factual sentence
of an answer, the model writes a tag of triples (document ID, sentence ID, relation). The triples point into source
sentences that are numbered in the prompt. The relation is Quotation, Compression or Inference. That taxonomy comes
from TROVE (Zhu et al., ACL 2025, 2025.acl-long.577), minus TROVE's Other class. The paper releases ReFInE, annotated
by GPT-4o and then validated by experts. It trains Qwen3-8B with SFT, then GRPO. The reward adds two parts: an
embedding-gated ROUGE-L similarity to the reference answer, and F1 against the reference triples. Scoring is exact
match of the triples to gold, plus LLM and human judges. Models handle Quotation well and Inference poorly.

**The claim, part by part.**
- ACL 2026: correct (main conference, long paper).
- "Generation-time fine-grained provenance": correct. It is the paper's own name for the task.
- Sentence-level provenance, with each link labelled Quotation, Compression or Inference: correct, with two
  precisions. First, the link points to a numbered source sentence; it is not a quoted string. Second, Quotation is
  the model's own label (the prompt lets a Quotation include small rewrites). Nothing checks that label against the
  text at run time.
- Framed as accountability or provenance, not factual truth: correct. The abstract motivates the task by
  accountability. The limitations say the system should not be used as "a standalone authority on factual
  correctness".

**(a)** No. **(b)** Nothing checks a link at run time, so a wrong link is neither flagged nor dropped. Training only
lowers its reward. ReFInE's construction discarded samples whose tags were missing or could not be parsed. **(c)**
None at run time. Similarity and F1 are training rewards, and the LLM judge is used only in evaluation.

## 2. SciTrue

**Citation.** Tan, N., Li, M., Gahegan, M. "SciTrue: Evidence-Grounded Claim Verification in Science." In
*Proceedings of the 19th Conference of the European Chapter of the ACL (Volume 3: System Demonstrations)*, EACL 2026,
Rabat, pp. 397-406. Anthology ID 2026.eacl-demo.27, DOI 10.18653/v1/2026.eacl-demo.27,
https://aclanthology.org/2026.eacl-demo.27/. I found no arXiv version. arXiv:2609.00654 is a different paper by the
same team (their NTCIR-19 SciClaimEval system); do not cite it for this.

**What it does.** A user submits a scientific claim, and GPT-4o agents do the rest:
- refine the claim and retrieve up to 15 papers through the Semantic Scholar API;
- pick the most relevant sentence from each paper and label it as supporting or refuting, with its assumptions;
- write a summary, linking each statement to one article, and give a verdict: fully, mostly, partially or not
  supported;
- break the result into subclaims. Each is shown with its source sentence, the paragraph around it, and labels.

Two annotators rated 60 claims × 5 articles, about 300 attributions per system, on yes/no criteria. The baselines
were GPT-4o-search-preview and Perplexity Sonar Pro. SciTrue scored 98.5% on summary traceability, 96.7% on factual
accuracy of attribution and 95.3% on context and assumptions. The annotators agreed 90% of the time.

**The claim, part by part.**
- EACL 2026 Demo: correct.
- Links claim components to explicit scientific sources, so users can inspect or challenge inferences: correct
  (abstract).
- A human evaluation of 300 attributions on traceability, attribution accuracy and context alignment: correct as the
  abstract puts it. The body says about 300 per system (900 sources over three systems). The table names the
  measures Summary Traceability, Factual Accuracy of Attribution and Context & Assumptions.
- Left out, and it matters for us: SciTrue is fact verification. It judges whether open-world scientific claims are
  true against the literature and returns a verdict. That is outside our scope.

**(a)** No. An LLM picks the sentence, and the paper describes no check that the sentence occurs in the article. An
attribution was counted correct if "the cited sentence, or a semantically equivalent statement, appears in the
referenced article". People made that judgement after the fact. **(b)** The paper describes no run-time check, so
nothing is marked unverified. **(c)** The support labels and the verdict are the system's answer, not a separate
check. A GPT-4.1 judge was tried on 10 claims, in evaluation only, and agreed weakly with the annotators. The authors
call SciTrue an assistive tool.

## 3. PaperTrail

**Citation.** Martin-Boyle, A., Leckey, C. A. C., Brown, M. C., Kaur, H. "PaperTrail: A Claim-Evidence Interface for
Grounding Provenance in LLM-based Scholarly Q&A." In *Proceedings of the 2026 CHI Conference on Human Factors in
Computing Systems* (CHI '26), Barcelona, April 2026, 25 pp. DOI 10.1145/3772318.3791101. Preprint arXiv:2602.21045
(cs.HC, 24 Feb 2026).

**What it does.**
- **Offline:** Gemini 2.5 Pro extracts claims from each source paper. Sentences above SPECTER cosine 0.75 become each
  claim's candidate support.
- **At question time:** an answerer LLM replies. An extraction LLM splits the reply into claims and supporting text,
  and code finds those strings in the reply to highlight them.
- **Matching:** a SPECTER filter narrows the paper claims, then an LLM matches the reply's claims to them. Supporting
  text in the reply below cosine 0.55 is flagged as possibly unsupported. Paper claims with no match are listed as
  omitted.
- **Offline evaluation:** claim extraction only (F1 0.65 on SciClaimHunt, 0.73 on BioClaimDetect).
- **User study:** within-subjects, 26 researchers, two editing tasks, against a citation-highlight baseline. With
  PaperTrail, trust was significantly lower (t(25) = 2.61, p = .015). Reliance (edit distance from the LLM draft) and
  confidence did not change significantly. Usability was rated lower.

**The claim, part by part.**
- On arXiv: correct but incomplete. It is a peer-reviewed CHI 2026 paper, so cite the ACM version.
- Splits an answer into claims mapped to evidence, showing supported assertions, unsupported claims and omitted
  information: correct. It splits the source papers too. "Omitted" means paper claims that the answer leaves out.
- A human study of the effect on trust and review behaviour: correct. Behaviour is measured as edit distance. The
  authors call the result a "trust-behavior gap": trust fell, but editing did not change significantly.

**(a)** Partly. Code locates strings only inside the answer. On the source side, embeddings and an LLM choose the
sentences, and no quotation is located. **(b)** Kept visible. Flagged support and omitted claims are both shown. The
answer itself is not changed; the user edits it. **(c)** Advisory. The 0.55 threshold was deliberately permissive,
tuned on five held-out examples to avoid alert fatigue. No accuracy figure is reported for the matching or for the
flag.

## 4. W3C PROV

**Documents.**
- PROV-Overview: "PROV-Overview: An Overview of the PROV Family of Documents". W3C Working Group Note, 30 April 2013,
  eds. P. Groth and L. Moreau. https://www.w3.org/TR/2013/NOTE-prov-overview-20130430/ (latest version:
  https://www.w3.org/TR/prov-overview/).
- PROV-DM: "PROV-DM: The PROV Data Model". W3C Recommendation, 30 April 2013, eds. L. Moreau and P. Missier.
  https://www.w3.org/TR/2013/REC-prov-dm-20130430/ (latest version: https://www.w3.org/TR/prov-dm/).

**The definition sentence.** It opens the PROV-Overview abstract and is repeated in its §1. The PROV-DM abstract uses
the same words. It says provenance is information about "entities, activities, and people involved in producing a
piece of data or thing". It adds that this information can be used to assess the thing's quality, reliability or
trustworthiness.

**The claim.** Partly correct. The quality, reliability and trustworthiness part is right, but the sentence says
people, not agents. "Agents" comes from PROV-DM §2.1, a non-normative section. It says that, at its core, provenance
describes entities being used and produced by activities, which agents may influence. PROV-DM §1 gives the
specification's own definition: a record of the people, institutions, entities and activities involved in producing,
influencing or delivering a piece of data or a thing.

**Recommendation.** Cite PROV-DM, the Recommendation, for the abstract sentence, and keep "people" if you quote it.
If the text says entities, activities and agents, cite PROV-DM §2.1.

## What it changes for the paper

- **GenProve is the clearest contrast.** There, the model asserts its own provenance, and that provenance is trained
  and scored against gold labels. GenProve's related work says it deliberately moves away from checking after
  generation. We keep the check after generation and give it to code: the model's claim that it quotes is checked at
  run time, not trusted. If we use the words Quotation, Compression and Inference, credit TROVE.
- **SciTrue is attribution inside fact verification.** It takes open-world claims, returns a verdict, uses sentences
  an LLM chose, and counted semantic equivalents as accurate attributions. Cite it as the scope we do not take.
- **PaperTrail is the closest on visible failures and advisory flags,** and it is the only one of the three with a
  user study. Its trust-behavior gap is a reason not to claim, without a study of our own, that "not confirmed" marks
  change what readers do.
