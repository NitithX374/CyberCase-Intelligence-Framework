# Citation verification (2026-10-12)

All metadata fetched live; raw responses in `literature/raw/`. Sentence-level use checked by
reading the abstract/known content; the uploaded PDF of Yang et al. was read in full.

| Key | Source of metadata | Used for | Status |
|---|---|---|---|
| li2024attributionbench | ACL Anthology 2024.findings-acl.886 | dataset; "automatic attribution evaluation remains hard" | verified |
| kamoi2023wice | ACL Anthology 2023.emnlp-main.470 | dataset; real-world claim/evidence entailment | verified |
| gao2023alce | ACL Anthology 2023.emnlp-main.398 | LLMs generating text with citations | verified |
| slobodkin2024afg | ACL Anthology 2024.acl-long.182 | select spans before generation | verified |
| reimers2020multilingual | ACL Anthology 2020.emnlp-main.365 | multilingual MPNet selector lineage | verified |
| min2023factscore | ACL Anthology 2023.emnlp-main.741 | atomic fact checking | verified |
| rashkin2023ais | ACL Anthology 2023.cl-4.2 | definition of attribution | verified |
| ji2023hallucination | Crossref 10.1145/3571730 | hallucination in NLG | verified |
| dehing2026forensics | Crossref 10.1145/3785318.3785330 | chat forensics structured reports | verified (method per repo survey) |
| yang2026traceable | Crossref 10.1145/3829918.3829930 + full PDF | evidence IDs, G/C labels, 2 experts | verified |
| worledge2026default | arXiv API 2607.01256 (author list corrected: 7 authors) | default-judgment review assistant | verified (numbers per repo survey) |
| lewis2020rag | arXiv API 2005.11401 | (not cited in the 15-page draft; kept in .bib) | verified |
| he2021debertav3 | arXiv API 2111.09543 | DeBERTaV3 backbone | verified |
| laurer2022mdeberta | Hugging Face API (sha b5113eb…, created 2022-08-22) | deployed NLI checkpoint | verified |
| conneau2018xnli | ACL Anthology D18-1269 | XNLI human-translated test set (planned Thai NLI check) | verified |
| tang2024minicheck | ACL Anthology 2024.emnlp-main.499 | efficient grounding fact-checker; checkpoint comparison | verified |
| yue2023attrscore | ACL Anthology 2023.findings-emnlp.307 | AttrScore attribution evaluator; checkpoint comparison | verified |
| laban2022summac | ACL Anthology 2022.tacl-1.10 | NLI-based inconsistency detection at sentence granularity | verified |
| phatthiyaphaibun2023pythainlp | ACL Anthology 2023.nlposs-1.4 | Thai sentence segmentation (crfcut) | verified |
| chen2024bgem3 | ACL Anthology 2024.findings-acl.137 | BGE-M3 embeddings (translation similarity diagnostic; RAG retrieval) | verified |
| gotel1994traceability | Crossref 10.1109/ICRE.1994.292398 (author initials per the paper: O.C.Z. Gotel, A.C.W. Finkelstein) | definition of traceability; problems from missing origin/production information | verified |
| buneman2001provenance | Crossref 10.1007/3-540-44503-X_20 (Crossref swapped Tan's name order; corrected) | why- vs where-provenance | verified |
| lebo2013provo | w3.org/TR/prov-o (title and editors read from page) | PROV ontology | verified |
| liu2023verifiability | ACL Anthology 2023.findings-emnlp.467; abstract read: 51.5% / 74.5% | motivation numbers | verified |
| bohnet2022attributedqa | arXiv API 2212.08037 | attribution as a task | verified |
| gao2023rarr | ACL Anthology 2023.acl-long.910; abstract read | post-hoc research and revision | verified |
| huang2024front | ACL Anthology 2024.findings-acl.838 | quote extraction before grounded citation (per repo survey matrix) | verified |
| wan2025generationprograms | arXiv API 2506.14580 | executable programs over source sentences (per repo survey) | verified |
| worledge2024spectrum | arXiv API 2411.17375 | extractive–abstractive verifiability trade-off (per repo survey) | verified |
| shen2025citelab | ACL Anthology 2025.acl-demo.47 | citation workflow tooling incl. AfG baseline (per repo survey) | verified |
| cattan2026localizing | Crossref 10.1162/tacl.a.598 | QA-proposition localisation of inconsistencies (per repo survey) | verified |
| wu2025medgraphrag | ACL Anthology 2025.acl-long.1381 | uses AfG as baseline (per repo survey) | verified |
| zhao2025finragbenchv | ACL Anthology 2025.emnlp-main.211 | page-image / bounding-box evidence units (per repo survey) | verified |
| schimanski2024specialists | ACL Anthology 2024.acl-long.105 | training data filtered for source quality/attributability (per repo survey) | verified |

AfG verification-time / AIS trade-off sentence follows the repo survey's reading of Slobodkin et al. Tables 3–4
(MDS 47→22 s, AIS 89.3→79.9; LFQA 59→35 s, AIS 87.6→94.4).
| frohmann2024sat | ACL Anthology 2024.emnlp-main.665 | SaT sentence segmenter used for Source units (code: trace/sentences.py, model sat-3l-sm) | verified |
| wu2025sourcecheckup | Crossref 10.1038/s41467-025-58551-6 | 50–90% of medical LLM responses not fully supported by cited sources (abstract) | verified |
| wallat2025faithfulness | Crossref 10.1145/3731120.3744592 | up to 57% of citations lack faithfulness (post-rationalised) | verified |
| zhang2025longcite | ACL Anthology 2025.findings-acl.264 | sentence-level citations in long-context QA | verified |

2026-10-13: per the authors' request, citations are kept within roughly the last three years except
core ones. Removed: bohnet2022attributedqa, laban2022summac, lebo2013provo (entries kept in .bib,
uncited). Kept as core despite age: gotel1994traceability, buneman2001provenance (concepts used in the
method), reimers2020multilingual, he2021debertav3, laurer2022mdeberta (models in the system),
conneau2018xnli (dataset in the planned study).
| gupta2025autosumm | ACL Anthology 2025.acl-industry.35 + full PDF read | post-hoc entity/embedding/entailment hallucination layers, sentence-level flags shown to reviewers, no evidence pointers | verified |
| chumpolsathien2020thaisum | ThaiSum dataset card (pythainlp/thaisum @ 6c2928cb, "Citation Information", MIT licence) | source of the Thai corpus in Sect. 5 only; metadata as given by the dataset authors | verified |
