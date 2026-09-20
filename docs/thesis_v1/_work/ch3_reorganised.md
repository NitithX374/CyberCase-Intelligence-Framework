# Chapter 3 — Methodology (reorganised)

Source: `D:\Doc\TSR Mitre Doc\Cybercase Intelligent framework Doc\ร่างบทที่ 3.docx`
Revised 2026-09-10 following `.claude/skills/ai-research-writing` (`references/section-writing.md`).

Paste the prose into Word. Everything marked **[TODO]** is an unresolved gap that must be
closed before the chapter is final — they are listed together at the end of this file.

---

## Section map — old → new

| Old | New | Action |
|---|---|---|
| 3.1 Co-op journey | 3.1 | Kept, register rewritten |
| — | 3.2 System overview | **New** — the chapter had no orientation section |
| 3.2 Database preparation | 3.3 | Merged with 3.3.1–3.3.3 |
| 3.2.1 Vector & Graph database | 3.3.3 / 3.3.4 | Split; schema tables moved next to the loaders that write them |
| 3.3 RAG pipeline (intro) | 3.4 | Rewritten |
| 3.3.1 Data parsing | 3.3.2 | Moved under knowledge-base construction |
| 3.3.2 Data ingestion | 3.3.1 | Became the framing paragraph of the construction section |
| 3.3.3 Graph store construction | 3.3.3 | Kept |
| 3.3.4 Query input | 3.4.1 | Absorbed into pipeline overview |
| 3.3.5 Query decomposition | 3.4.2 | Kept, renumbered |
| 3.3.6 Retrieval | 3.4.3 | Kept, renumbered |
| 3.3.7 Self-reflection | 3.4.4 | **3.3.7.2–.4 were empty — now written** |
| 3.4 Evaluation | 3.5 | Renumbered |
| 3.4 Query decomposition (2nd) | — | **Deleted** — superseded duplicate of 3.4.2 |

Structural defects repaired: two sections numbered 3.4; three empty headings; the
database schema separated from the code that builds it; parsing described before the
ingestion it belongs to; every cross-reference stale.

---

# 3.1 Co-operative education timeline

*Register note: the original is a first-person diary. A methodology chapter cannot carry
"we was flabbergasted". Below keeps every fact and the personal frame the co-op report
format expects, in reportable prose.*

The co-operative education placement began in April 2026 with departure preparations,
including the Ministry of Education documentation and the visa application; the visa was
issued for ninety days and extended subsequently. The team arrived at Taoyuan in May and
divided between two institutions, with the author and one colleague placed at National
Central University and the remaining two at National Yang Ming Chiao Tung University.
The author was assigned to the Wireless Ad-Hoc and Sensor Networks Laboratory (WASN Lab),
a research-oriented group, and the first month was spent establishing the working
environment and reviewing the literature for the assigned module of the CIFra system:
vector databases, embedding models, retrieval-augmented generation, and cyber threat
intelligence RAG.

Implementation began in June. The initial configuration used ChromaDB as the vector store
and Neo4j as the graph store, with `multilingual-e5-large` as the embedding model. Parsing
the MITRE ATT&CK STIX bundles through that model on the available hardware, an RTX 2050,
was impractical: embedding the corpus took approximately four hours. Moving the embedding
workload to rented GPU infrastructure reduced this to approximately ten minutes and made
iteration on the ingestion pipeline feasible. The research topic proposal was presented to
a panel of four faculty members on 19 June, and their recommendations informed the
subsequent design.

The third month, July, was spent implementing the retrieval pipeline with LangChain and
comparing configurations empirically. The controlling question was which configuration
preserved answer quality at the lowest cost. BGE-M3 outperformed `multilingual-e5-large`
on this corpus and was adopted for all subsequent work. Latency remained an open problem
at that point and is addressed in Section 3.4.3. **[TODO-1]** *Record the comparison that
selected BGE-M3 as a table, or state that it was a qualitative selection — the sentence
"BGE-M3 conquer over multilingual-e5-large" asserts a measured result that the chapter
does not yet show.*

---

# 3.2 System overview

CIFra takes a Thai-language cybercrime case file and produces a structured case summary in
Thai, grounded in the MITRE ATT&CK knowledge base. The chapter describes the module the
author is responsible for: the knowledge base and the retrieval-augmented generation
pipeline that consumes it.

Three properties of the task determine the design and recur throughout the chapter.
The input is *cross-lingual*: queries and answers are Thai while the knowledge base is
English, which constrains every component that touches text to be multilingual. The input
is *multi-step*: a case file narrates a sequence of attacker actions, so the retrieval
target is a set of techniques covering all of them rather than the single best match. And
the output is *evidentiary*: the summary is intended for prosecutorial use, so an
unsupported technique identifier is a more serious failure than an omitted one.

The pipeline is a state machine with four stages. A case file is decomposed into atomic
sub-queries (Section 3.4.2); each is retrieved through a hybrid of vector search and graph
expansion (Section 3.4.3); the assembled context is judged for sufficiency and, if
inadequate, retrieval is repeated with a rewritten query (Section 3.4.4); the surviving
context is passed to the generation model. **[TODO-2]** *Insert Figure 3.1, the pipeline
diagram. The chapter currently has no figure showing control flow, and the reader must
assemble it from prose across nine sub-sections.*

---

# 3.3 Knowledge base construction

## 3.3.1 MITRE ATT&CK as the knowledge source

The pipeline retrieves over the MITRE ATT&CK knowledge base, which serves two purposes.
It supplies the domain knowledge the generation model lacks, reducing hallucination by
grounding each assertion in a retrieved document; and it supplies traceability, since every
retrieved item carries a stable identifier through which an analyst can return to the
authoritative source for detail the summary omits.

ATT&CK is distributed as STIX 2.1 bundles, one per domain. Both the Enterprise and Mobile
bundles are ingested; the ICS domain is outside the scope of this work and is not ingested.
Construction proceeds in three stages, described in the sections that follow: the bundles
are parsed into typed entities and relationships, the result is written to a graph store
that preserves their structure, and the same result is embedded into a vector store that
makes it searchable by meaning. Both stores are populated from a single parse, so they
always hold the same snapshot, and the STIX identifier is the join key that lets a vector
hit be expanded in the graph.

## 3.3.2 Data parsing

A bundle is a flat `objects` array in which nodes and edges are interleaved, carrying no
explicit schema for the graph the framework requires; a parser is therefore needed to
project it onto the typed schema of Sections 3.3.3 and 3.3.4.

Objects flagged `revoked` or `x_mitre_deprecated` are collected into a tombstone set and
excluded, so that superseded content — which the bundles retain — cannot be retrieved as
current. The remaining objects are mapped to entity types by their STIX `type`, with two
exceptions. `tool` and `malware` are unified into a single Software entity distinguished by
a `software_type` attribute, since both participate identically in the graph. And
`attack-pattern` is split by `x_mitre_is_subtechnique` into Technique or Subtechnique
nodes, so the hierarchy is expressed structurally rather than inferred from the identifier
string. The ATT&CK identifier and canonical URL, which are not top-level STIX fields, are
recovered from `external_references`.

Edges are then built from `relationship` objects, mapping `relationship_type` onto the
schema labels (USES, MITIGATES, SUBTECHNIQUE_OF, ATTRIBUTED_TO, DETECTS); `revoked-by`
relationships and any edge with a missing endpoint are discarded. Two further edge types
have no STIX representation and are derived: IN_TACTIC from each technique's
`kill_chain_phases`, and HAS_COMPONENT from `x_mitre_data_source_ref`, both assigned
synthetic identifiers so that repeated ingestion remains idempotent. A final pass
deduplicates by STIX identifier, applies the tombstone set, and re-checks endpoint
existence against the surviving entities, yielding the consistent snapshot summarised in
Table 3.1. **[TODO-3]** *Table 3.1 is a placeholder in the source draft. Populate it with
per-label node and edge counts from an ingestion run, and state the ATT&CK version.*

## 3.3.3 Graph store construction

The graph store is Neo4j, which holds the ATT&CK entities as nodes and their relationships
as edges, so that the retriever can traverse a link and recover what an entity is connected
to rather than only what it is. Nine node labels and seven edge labels are used.

**Table 3.2 — Node labels**

| Node Label | STIX 2.1 Type | Properties | Description |
|---|---|---|---|
| Technique | attack-pattern | stix_id, attack_id (e.g. T1566), name, description, platforms, url | Technique that adversaries use (e.g. Phishing, Brute Force) |
| Subtechnique | attack-pattern | stix_id, attack_id (e.g. T1566.001), name, description, platforms, url | More specific sub-techniques (e.g. Spearphishing Attachment, a sub-technique of Phishing) |
| Group | intrusion-set | stix_id, attack_id (e.g. G0016), name, description, aliases | Threat actor (e.g. APT29, Lazarus Group) |
| Software | tool / malware | stix_id, attack_id (e.g. S0154), name, description, aliases, type | Tools or malware that adversaries use (e.g. Cobalt Strike, Mimikatz) |
| Campaign | campaign | stix_id, attack_id (e.g. C0015), name, description | Specific attack campaign |
| Mitigation | course-of-action | stix_id, attack_id (e.g. M1036), name, description | Measure reducing the risk of a technique (e.g. enable MFA) |
| Tactic | x-mitre-tactic | stix_id, attack_id (e.g. TA0001), name, shortname, description | Strategic objective at each stage (e.g. Initial Access, Persistence, Exfiltration) |
| DataSource | x-mitre-data-source | stix_id, attack_id, name, description, platforms | Data source for attack detection (e.g. Windows Event Log, Network Traffic) |
| DataComponent | x-mitre-data-component | stix_id, name, description | Subpart of a data source with specific context (e.g. Process Creation within Windows Event Log) |

**Table 3.3 — Edge labels**

| Edge Label | Source Node | Destination Node | Properties |
|---|---|---|---|
| USES | Group, Software, Campaign | Technique, Subtechnique, Software | stix_id, description |
| SUBTECHNIQUE_OF | Subtechnique | Technique | stix_id |
| MITIGATES | Mitigation | Technique, Subtechnique | stix_id, description |
| ATTRIBUTED_TO | Campaign | Group | stix_id, description |
| IN_TACTIC | Technique, Subtechnique | Tactic | derived from kill_chain_phases |
| DETECTS | DataComponent | Technique, Subtechnique | stix_id, description |
| HAS_COMPONENT | DataSource | DataComponent | stix_id |

The parsed records are written in a single transactional pass. The database is first
cleared, after which uniqueness constraints on `stix_id` are declared for every node label
together with a shared `:Entity` label, and secondary indexes are created on the access
paths used at query time: `attack_id` for techniques and sub-techniques, `name` for groups
and software, and `shortname` for tactics. Nodes are then grouped by label and written with
`UNWIND … MERGE` in batches of 5,000; the `:Entity` label is applied to every node so that
the subsequent edge pass can resolve both endpoints through one indexed lookup rather than
a label scan. Edges are grouped by label and created in batches of the same size, with the
relationship description stored as an edge property so that graph expansion can surface the
textual evidence for a link rather than the link alone. Because duplicates are removed
during parsing and the database is cleared beforehand, edges are written with `CREATE`
rather than `MERGE`, avoiding a match on every write. Node and edge counts are read back
from the database after loading and reported in Table 3.1.

## 3.3.4 Vector store construction

The vector store is Qdrant, which holds both a dense and a sparse representation of every
entity and relationship, embedded by BGE-M3. Each record follows the schema in Table 3.4.

**Table 3.4 — Qdrant point schema**

| Field | Type | Description |
|---|---|---|
| id | UUID | Identifier derived deterministically from the STIX ID |
| vector | Dict[str, Vector] | Dense and sparse representations produced by BGE-M3 |
| payload | JSON/Dict | Used for filtering, carries the STIX ID for the Neo4j lookup, and is passed to the generation model |

Entities and relationships are held in two separate collections, because the text embedded
for each is structurally different: an entity document is rendered as
`"{label}: {name}. {description}"` and answers what a technique is, while a relationship
document is rendered as `"{source} {EDGE} {target}: {description}"` and answers who did
what to whom. Keeping them separate allows the retriever to control the proportion of each
that reaches the context (Section 3.4.3.2), which a single collection would leave to
whichever scored higher.

BGE-M3 produces both representations in a single forward pass. The sparse representation
performs lexical matching and captures cyber threat intelligence terms — technique
identifiers, malware names, group aliases — that appear verbatim in a Thai narrative. The
dense representation captures semantic similarity under cosine distance, so a Thai
paraphrase of an attack step can match an English technique description without a shared
token. Retrieval combines both, and the combination is what allows the system to serve
queries that state a technique by name and queries that merely describe the behaviour.

---

# 3.4 Retrieval-augmented generation pipeline

## 3.4.1 Overview and input characteristics

Retrieval-augmented generation allows a language model to answer questions outside its
parametric knowledge by retrieving relevant context at inference time, and has been shown
to reduce hallucination. This property is necessary in a specialised domain such as cyber
security, where factual precision over an evolving threat-intelligence corpus cannot be
guaranteed by pre-trained weights alone.

Two properties of this deployment shape the pipeline beyond a standard RAG configuration.
The first is cross-lingual retrieval: the query and the required answer are Thai while the
corpus is English, so the embedding model must be multilingual. BGE-M3 accepts inputs up to
8,192 tokens and produces 1,024-dimensional dense vectors, which suits the input in
question — a Thai cybercrime case file is a long chronological narrative carrying English
technical terms inline. No translation step is performed anywhere in the retrieval path;
the Thai text is embedded as written. **[TODO-4]** *Insert Figure 3.2, an example case file,
as promised by the source draft. Redact identifying details.*

The second is that the pipeline decides its own control flow. Rather than retrieving once
and generating, it judges whether the retrieved evidence suffices and, when it does not,
rewrites its own query and retrieves again. The retrieved context and the graph traversal
are then passed to the generation model, which answers in Thai.

*Note on a corrected figure: the source draft states BGE-M3 has "8194 dims". The model
produces 1,024-dimensional dense vectors and accepts a maximum input of 8,192 tokens; the
draft conflated the two and mis-stated the second. The corrected values are used above and
are consistent with Section 3.4.3.2.*

## 3.4.2 Query decomposition

### 3.4.2.1 Motivation

A real incident report rarely describes a single attacker action. A case file typically
narrates a sequence of phases — initial access, execution, persistence, privilege
escalation, credential access, discovery, lateral movement, collection, exfiltration and
impact — each corresponding to a distinct ATT&CK technique. Throughout this work such a
phase is referred to as an *attack step*, and the retrieval target for a case file is the
set of techniques covering all of its steps, not the single best-matching technique.

Issuing the narrative as one retrieval query is inadequate for this target. A dense encoder
compresses the entire narrative into a single vector, which is dominated by whichever phase
occupies the most text; peripheral but legally significant steps — data destruction or
exfiltration, typically one or two sentences at the end of a report — are averaged away and
never surface in the top-K. This is the known limitation of embedding a multi-faceted query
as one point in the representation space. Query decomposition addresses it by expanding one
compound query into several atomic queries, each retrieved on its own channel, so that
every attack step is given an independent opportunity to match.

### 3.4.2.2 Decomposition procedure

The decomposer is a language-model step that takes the incident text and emits one atomic
search query per distinct attacker action, one per line. The model is instructed to
traverse the kill chain explicitly and not to terminate early, because the phases that
matter most to a prosecutor — exfiltration and impact — are the ones stated last and were
empirically the ones dropped first. Each sub-query must name both the action and its object
as described in the incident; bare category words such as "Execution" or "Discovery" are
prohibited, since they retrieve generic detection metadata rather than the technique
performed.

Two design decisions distinguish this module from a conventional multi-query expander.
First, sub-queries are emitted in the language of the incident. Thai input yields Thai
sub-queries, with well-known MITRE names — SQL Injection, Phishing, Mimikatz, RDP —
preserved verbatim as they appear in the source text. Because BGE-M3 is multilingual, a
Thai sub-query matches the English corpus directly, and the English terms that survive
anchor the sparse channel of Section 3.3.4. Second, decomposition is performed by the
general instruction-following model at temperature 0 rather than by the domain-specialised
model, since the task is query planning rather than question answering.

**[TODO-5]** *Insert Table 3.5, the worked decomposition example (one Thai incident and its
six sub-queries). The prose asserts what the decomposer produces but never shows it.*

### 3.4.2.3 Output validation and fallback

Because the decomposer's output is fed directly into the retrieval engine, any line that is
not a search query becomes a spurious query consuming retrieval budget. Three failure modes
are filtered. When the input contains no concrete attacker action — a meta-request, or a
reference to "this incident" with nothing attached — the model is instructed to emit the
sentinel NONE. Lines addressing the user rather than the engine (clarification requests,
refusals, preambles, any line ending in a question mark or colon, any line containing
markdown emphasis) are rejected by a pattern filter. Finally, if the number of rejected
lines exceeds the number accepted, the entire reply is treated as prose and discarded,
since the surviving lines are almost certainly fragments of a sentence rather than queries.
In every failure case, including a model or network error, the module falls back to a
single channel containing the unmodified query, so decomposition can degrade retrieval but
never disable it.

This fallback is a deterministic input-sanitisation step confined to the decomposition
module, and should not be confused with the agentic self-reflection mechanism of Section
3.4.4. The filter is rule-based, is applied before any retrieval is issued, and terminates
in a single fixed action — reverting to the undecomposed query. The self-reflection loop,
by contrast, is a model-adjudicated decision taken after retrieval, which may re-enter the
retrieval stage with a rewritten query. The two address different failure modes: the former
guards against a malformed query plan, the latter against insufficient retrieved evidence.

### 3.4.2.4 Retrieval channels and result merging

The sub-queries do not replace the original query; they supplement it. The channel set is
the original incident text first, followed by the sub-queries in kill-chain order, followed
by any rewrites produced by the self-reflection loop (Section 3.4.4), deduplicated while
preserving order. The original query is retained as a *holistic channel* because it
preserves inter-phase context that atomic queries discard by construction; the sub-queries
then pin down each individual technique.

Each channel is retrieved independently through the full procedure of Section 3.4.3,
returning the top *K*<sub>v</sub> = 10 candidates, of which the top *q* = 3 are retained as
that channel's quota.

The retained results are merged by round-robin interleaving rather than by global score.
Rank 1 of every channel is emitted before rank 2 of any channel, and so on. A naive
score-based merge would sort all retained results into one list and truncate; because
reranker scores vary systematically with how well a phase is described in the narrative,
that truncation reliably eliminates whichever technique was described most briefly —
precisely the failure decomposition was introduced to prevent. Interleaving guarantees
instead that the head of the merged list spans all channels, so every attack step is
represented regardless of its absolute score. Within a single round, channels are visited
in descending score order; this affects presentation order, not membership, and is used
because emission order carries no confidence information. Scores from different channels
are not strictly comparable, as each is a cross-encoder score against a different question,
so the within-round sort is an ordering heuristic rather than a principled global ranking.

Duplicate entities are removed by STIX identifier during interleaving, and subgraphs are
deduplicated by their centre node, so a technique retrieved by two adjacent sub-queries
occupies one slot rather than two. The merged result is capped at 15 vector results and 8
subgraphs to fit the generation model's context budget. This cap is a global bound distinct
from the per-channel quota: the quota distributes representation across attack steps, while
the cap bounds the prompt against an incident that decomposes into many steps. Table 3.6
summarises the parameters.

**Table 3.6 — Retrieval parameters**

| Parameter | Symbol | Value | Role |
|---|---|---|---|
| Maximum sub-queries | — | 10 | One per kill-chain phase |
| Retrieval channels | — | 1 + *n*<sub>sub</sub> (+ rewrites) | Original query retained as holistic channel |
| Candidates per channel | *K*<sub>v</sub> | 10 | Before reranking |
| Quota retained per channel | *q* | 3 | After reranking; also bounds graph seeds |
| Merged vector cap | — | 15 | Context budget |
| Merged subgraph cap | — | 8 | Context budget |
| Context length cap | — | 10,000 characters | Prompt budget |
| Decomposer temperature | — | 0 | Deterministic planning |

## 3.4.3 Retrieval

### 3.4.3.1 Overview

Every channel is executed by the same five-stage procedure: hybrid vector search over the
two Qdrant collections, cross-encoder reranking, entity-type reweighting, graph expansion
of the surviving seeds, and assembly of the two modalities into a single context string.
Stages one to three operate on textual similarity and answer *which ATT&CK entities
describe this attack step*; stage four operates on the graph and answers *what is
structurally connected to those entities*. The two are kept as separate result sets
throughout and are never score-fused.

### 3.4.3.2 Hybrid vector search

The channel query is encoded once by BGE-M3, yielding a 1,024-dimensional dense vector and
a sparse lexical-weight vector in a single forward pass. Both are issued against the same
collection as two prefetch branches — the dense branch under cosine similarity, the sparse
branch under lexical weighting — each returning max(5*K*<sub>v</sub>, 50) candidates. The
two candidate lists are combined by Reciprocal Rank Fusion, executed natively inside
Qdrant, which scores each document as

*RRF*(*d*) = Σ<sub>*i*</sub> 1 / (*k* + rank<sub>*i*</sub>(*d*))

where rank<sub>*i*</sub>(*d*) is the rank of document *d* in branch *i* and *k* is a
smoothing constant fixed by the engine's implementation. RRF is preferred to a weighted sum
of the raw scores because cosine similarity and sparse lexical weight are not on a common
scale and their relative calibration varies by query; rank-based fusion requires no tuning
of a mixing coefficient and is robust to one branch producing systematically larger
magnitudes than the other. The consequence for this work is that a query need not match on
both channels to be retrieved: a Thai paraphrase with no shared vocabulary is recovered by
the dense branch, an English technique or tool name embedded verbatim in the Thai narrative
is recovered by the sparse branch, and a document ranked highly by either enters the fused
list. Agreement between the two is treated as stronger evidence than a decisive win on
either alone, which suppresses the characteristic failure of lexical matching over a domain
whose entity names are themselves ordinary English words.

Search is performed over the entity and relationship collections separately. Entities
receive the full quota of *K*<sub>v</sub> = 10 while relationships receive ⌈*K*<sub>v</sub>/2⌉,
a deliberate bias toward technique and tactic nodes, which are the objects the case-summary
task must produce; relationship documents contribute the narrative evidence of how a group
employed a technique rather than the technique itself. Because RRF scores are rank-derived
and therefore not comparable across two independently fused collections, the scores within
each collection are min–max normalised to [0, 1] before the two lists are merged and
truncated to *K*<sub>v</sub>.

A domain restriction is applied at this stage. The knowledge base contains both Enterprise
and Mobile content, and the two share several technique titles verbatim — *Phishing* exists
as T1566 in the former and T1660 in the latter. Since the incidents under analysis are
enterprise cases, a mobile technique entering the context is not merely irrelevant but
factually wrong for the report, and retrieval is restricted to the Enterprise domain. The
restriction is applied after retrieval rather than as a server-side predicate: efficient
predicate filtering in Qdrant requires a payload index on the filtered field, which the
deployed collection does not carry, and creating one would modify shared infrastructure.
The retriever instead over-fetches by a factor of three and discards non-matching results
client-side, so that the required *K*<sub>v</sub> results survive the filter with high
probability. This is distinct from the over-fetch inside the fusion step, where each branch
retrieves max(5*K*<sub>v</sub>, 50) candidates so that fusion has a sufficient pool to rank
over; the two mechanisms operate at different stages and for different reasons.

### 3.4.3.3 Cross-encoder reranking

The *K*<sub>v</sub> = 10 fused candidates are rescored by `bge-reranker-v2-m3`, a
multilingual cross-encoder that receives the query and the candidate document jointly and
emits a single relevance score in [0, 1]. The distinction from the retrieval stage is
architectural: the bi-encoder used for search embeds query and document independently,
which is what makes an index searchable but also what discards any term-level interaction
between them; the cross-encoder attends over the concatenated pair and can therefore judge
whether a specific attacker action is the one the document describes, at a cost acceptable
only over a short candidate list. Documents are truncated to 512 tokens for scoring. The
reranker is multilingual and scores a Thai query against an English document directly,
consistent with the no-translation policy of Section 3.4.1.

### 3.4.3.4 Entity-type reweighting

Reranker scores are then multiplied by a fixed per-type coefficient — 1.2 for Technique and
Subtechnique, 1.1 for Tactic, 0.8 for Software, 0.75 for Group and Campaign — and the list
re-sorted. The adjustment corrects an observed failure mode in which attribution entities
outranked the techniques themselves: a narrative naming a well-known adversary retrieved
the corresponding intrusion-set document above the technique documents describing what was
actually done, because the group description is lexically closer to the narrative than any
single technique description is. Attribution entities remain in the result set, since they
are legitimate context for the graph section, but are placed below the techniques. This is
a hand-set heuristic reflecting the priorities of the case-summary task rather than a
learned weighting, and it is applied after reranking, so it alters ordering — and therefore
graph seed selection — but not which documents were retrieved.

### 3.4.3.5 Graph expansion

Graph expansion is seeded from the results the quota retains. Within a channel the top
*q* = 3 reranked hits supply the seeds, a retrieved relationship contributing both of its
endpoints since the relationship document is evidence about a pair of entities rather than
about one. Binding the seed set to the quota is deliberate: seeding from a wider slice
would re-admit through the graph section a technique the quota had discarded, raising
recall at a precision cost the case-summary task does not justify, since a weakly matched
technique carries its entire neighbourhood — attributed groups, mitigations, detection
components — into the context.

Expansion retrieves each seed's immediate neighbourhood, one hop, in both directions. Both
directions are required because ATT&CK edges inherit the direction of the underlying STIX
relationship: for a technique node only the tactic membership is an outgoing edge, whereas
the adversary groups and software that employ the technique, its mitigations, its detecting
data components and its sub-techniques are all incoming. The structural evidence the task
depends upon lies almost entirely on the incoming side.

The expansion is issued as three batched Cypher statements per channel rather than three
per seed. The seed identifiers are passed as a single list parameter and unwound
server-side, so that one statement resolves all centre nodes, a second collects all
outgoing edges and a third all incoming edges, with each returned row tagged by its
originating seed for reassembly. Because the graph store is cloud-hosted, retrieval latency
is dominated by the number of network round-trips rather than the volume of data returned,
and batching reduces that number from 3*n* to 3 for *n* seeds — that is, from linear in the
seed count to constant. Edge descriptions are retrieved alongside the edges themselves, so
the expansion returns not the bare assertion that a group uses a technique but MITRE's own
account of how that group was observed using it: the delivery mechanism, the file types
involved, the targeted sector. This distinction matters here because establishing that a
narrative corresponds to a technique requires comparing described behaviour against
documented behaviour, which the edge alone cannot support.

### 3.4.3.6 Context assembly

The merged results are rendered into a single context string with two sections. The
semantic section lists the merged vector results, capped at 15, each with its entity type,
ATT&CK identifier, relevance score and document text truncated to 600 characters. The graph
section renders up to eight subgraphs, each as its centre node followed by its edges grouped
by relationship type and relabelled for readability — incoming USES becomes *Used by*,
IN_TACTIC becomes *Belongs to tactic* — with edge descriptions attached beneath, truncated
to 200 characters. The assembled context is capped at 10,000 characters; since the semantic
section is written first, this bound falls on the graph section when it binds at all.

The separation of the two sections is retained in the prompt so that the generation model
can distinguish evidence of *what a technique is* from evidence of *how it is connected*,
which the case summary must express differently: the former supports the identification of
a step, the latter supports statements about attribution and about the relationship between
steps.

## 3.4.4 Self-reflection loop

### 3.4.4.1 Rationale

The retrieval procedure of Section 3.4.3 is executed without any guarantee that its output
is adequate. Two failure conditions are of practical concern. In the first, an attack step
present in the narrative fails to retrieve its corresponding technique: the step may be
described obliquely, in operational language rather than in the vocabulary the ATT&CK
descriptions use, so that neither the dense nor the sparse channel surfaces the correct
entity. In the second, the input is not an analysable incident at all — a request referring
to "this incident" with no description attached, or a statement of outcome with no account
of how it occurred. Both conditions produce a context that a generation model, prompted to
be helpful, will nevertheless use: it will infer plausible techniques from the general
shape of the narrative and present them with the same confidence as grounded ones. For a
document intended for prosecutorial use this is the most damaging failure available to the
system, and it is invisible to the reader.

The pipeline therefore evaluates its own retrieved context before generation, and where the
context is judged inadequate it retrieves again with a query it rewrites itself. This
reflective step is what makes the pipeline *agentic* in the sense of Self-RAG (Asai et al.,
2023): control flow is decided at inference time by the model's own judgement of
intermediate state rather than fixed in advance.

### 3.4.4.2 Sufficiency evaluation

The evaluator receives the original query, the assembled context truncated to 4,000
characters, and the current iteration index, and returns a structured verdict of SUFFICIENT
or INSUFFICIENT together with the phases it considers covered, the phases it considers
missing, a recovery strategy, and the payload that strategy requires.

Evaluation proceeds in two stages. An **answerability gate** is applied first, and
independently of the context: if the query describes no concrete attacker action, the
verdict is INSUFFICIENT regardless of how relevant the retrieved material appears. This
ordering is deliberate. A vague query still retrieves — the embedding of "the system was
hacked" is closest to some set of ATT&CK documents, and that set will look topically
appropriate — so a gate applied after the context would be satisfied by material that in
fact evidences nothing. Topical relevance cannot substitute for a missing incident
description, and the gate encodes that as a precondition rather than as a judgement.

If the gate passes, coverage is assessed against four phases — Initial Access, Credential
Access, Privilege Escalation, and Impact — under a stated threshold: two or more covered
phases yield SUFFICIENT, as does a single phase the context explains clearly, on the ground
that a single-technique incident legitimately covers only one or two phases and must not be
penalised for the absence of stages that never occurred. Coverage is judged semantically,
so a technique counts as covering a phase when its description matches the behaviour,
whether or not the narrative names it. Two constraints on the judgement are worth noting.
Retrieved entries matching no described action — unrelated threat groups, software or
mitigations — contribute no coverage even when they dominate the context by volume, which
prevents the reranking bias toward well-known adversaries from being read as evidence. And
the evaluator is prohibited from citing ATT&CK identifiers in its justification unless they
appear verbatim in the context, since an identifier invented at this stage propagates into
the analyst-visible reasoning trace.

Where the verdict is INSUFFICIENT the evaluator selects one of three strategies, under the
explicit constraint that no further user input will arrive.

**Table 3.7 — Recovery strategies**

| Strategy | Condition | Payload |
|---|---|---|
| BROADEN_SEARCH | The incident is described but a phase was missed | A rewritten query |
| PARTIAL_ANSWER | Two or more phases covered, one detail absent | A gap warning |
| ACKNOWLEDGE_LIMIT | The answerability gate failed, or attempts are spent | A message to the user |

Of these, PARTIAL_ANSWER is defined in the evaluator's contract but is not acted upon by
the current implementation: the strategy and its gap warning are carried in the pipeline
state, but no downstream stage reads them, so an answer produced under this verdict is
emitted without the caveat the evaluator requested. Wiring the warning into the generated
answer is identified as future work.

### 3.4.4.3 Query rewriting and the retrieval loop

Under BROADEN_SEARCH the evaluator writes a replacement query describing the missing
attacker behaviour in plain language, typically at the level of the parent technique and
its tactic rather than the specific action that failed to match. The rewrite must differ
meaningfully from the queries already attempted, since repeating a query retrieves the same
context and consumes an attempt without changing the state.

Because this query is written by a language model but consumed by an embedding model, it is
sanitised before use: markdown emphasis and bare ATT&CK identifier tokens are stripped.
Both were observed in practice, and both are actively harmful at this point in the
pipeline, since an identifier token pulls the embedding toward documents that mention
identifiers rather than toward descriptions of the behaviour — the opposite of the
rewrite's purpose.

The sanitised rewrite is appended to the channel set and the pipeline re-enters retrieval
as described in Section 3.4.2.4. The rewrite does not replace the existing channels: the
original query and the decomposed sub-queries are retrieved again alongside it, so the loop
is strictly additive in coverage and a broadening step cannot lose a technique the previous
iteration had found.

### 3.4.4.4 Termination

The loop is bounded at two broadening iterations. Three conditions return control to
generation: the verdict is SUFFICIENT; the iteration budget is exhausted, at which point
the evaluator short-circuits to SUFFICIENT without invoking the model at all, the guard
being placed before the call so that an exhausted budget costs nothing; or the verdict is
INSUFFICIENT but the evaluator supplied no usable rewrite, since re-entering retrieval with
the same queries cannot change the outcome. On the second iteration the evaluator is
instructed to apply looser criteria, on the reasoning that a context retrieved with an
already-broadened query is unlikely to improve further and that answering with partial
evidence is preferable to consuming the remaining budget.

Where ACKNOWLEDGE_LIMIT was selected and the verdict remains INSUFFICIENT, generation is
bypassed entirely and the evaluator's message is returned in place of an answer, stating
what the description lacks — attack vector, attacker actions, affected systems — or that
the knowledge base holds no data on the pattern described. The system thus has a defined
path to declining to answer, which the answerability gate makes reachable on the first pass
without consuming any budget.

Every failure of the evaluator itself — an unparseable response, a malformed verdict, an
unconfigured model, a network error — resolves to SUFFICIENT. The evaluator is a quality
gate on retrieval, not a component the pipeline depends on for liveness, and its own
failure must not prevent an answer that the retrieved context may well support.

---

# 3.5 Evaluation

Establishing how well the pipeline performs requires answering two distinct questions:
whether retrieval supplies the evidence the task needs, and whether generation uses that
evidence correctly. The two are evaluated separately rather than end-to-end, because an
incorrect final answer is not self-diagnosing. A report that omits a technique may do so
because the retriever never surfaced it, in which case no prompt or model change can
recover it, or because the retriever surfaced it and the generation stage failed to use it,
which is a different defect with a different remedy. Retrieval quality also bounds
generation quality: evidence absent from the context cannot be reasoned over, so the
retrieval score is the ceiling within which any generation score must be read. Evaluating
the stages independently makes that ceiling explicit and allows a deficiency to be
attributed to the stage responsible for it.

Retrieval is assessed by whether the ATT&CK entities constituting the ground truth for an
incident appear among the retrieved results, and at what rank. Generation is assessed along
two axes: *faithfulness*, whether the claims in the answer are supported by the retrieved
context rather than by the model's parametric knowledge, and *relevancy*, whether the
answer addresses the incident it was given. The distinction matters for this application,
since a fluent report citing a technique never present in the context is more damaging than
an incomplete one — the failure is invisible to a reader who does not independently verify
each identifier.

## 3.5.1 Datasets and ground truth

The task takes a Thai incident narrative and must return the ATT&CK techniques evidencing
each of its steps. No labelled corpus of Thai case files with ATT&CK annotations exists,
and annotating narratives directly would make the labels an artefact of this work. Two
evaluation tiers are therefore used, differing in what they can establish: the first
measures performance on narratives derived from real incidents, the second places the
system against published results on shared benchmarks.

**Tier 1 — Real-CTI incident chains.** One hundred attack chains are drawn in equal share
from two published sources whose ATT&CK labels were assigned by their own authors: the CTID
Adversary Emulation Library (50 chains of ordered emulation-plan steps, vendored at a
pinned commit under Apache-2.0) and CISA cybersecurity advisories (50 chains of incident
advisories carrying an explicit ATT&CK section, obtained through Zenodo DOI
10.5281/zenodo.14659512 under CC-BY-4.0). Chains are selected round-robin across
adversaries and advisories under a fixed seed, so that a heavily documented adversary
cannot dominate the sample and the selection remains reproducible. The CTID plans are
vendored because their upstream branch moves; the CISA set is fetched because a DOI already
resolves to an immutable record.

Each chain is rewritten by hand into a Thai case-file narrative in the register of the
documents the system processes — chronological prose with English technical terms embedded
as they appear in Thai incident reporting. The rewriting changes surface form only; the
gold identifiers remain the source's own. The dataset contains 100 samples over 347 steps,
and each sample carries its English parallel, so that any performance difference
attributable to language can be measured on identical content.

Each step is annotated with a **cue type** recording how its technique is expressed. A
*named* cue states the technique in terms recognisable as ATT&CK vocabulary; a *described*
cue relates only observed behaviour, leaving the technique to be inferred. Of the 347
steps, 61 are named and 286 described — a distribution reflecting the operational reality
the system addresses, since an investigating officer records what was observed rather than
which technique it instantiates. Retrieval performance is therefore reported separately by
cue type; an aggregate figure would be dominated by the harder condition while still being
inflated by the easier one, and would report neither. The named condition additionally
serves as a control: it establishes that the retrieval components function, so that a low
described-cue score can be attributed to the difficulty of behavioural inference rather
than to a defect in search.

**Tier 2 — Published benchmarks.** Tier 1 establishes how the system performs but not how
that compares to prior work, since its ground truth was constructed here. The second tier
evaluates on the test splits released with published ATT&CK mapping systems, permitting
direct comparison with their reported figures: a TRAM-derived set of 725 items, a
procedure-example set of 1,767 items, and an expert-annotated set of 157 items.

Two caveats constrain the comparison. These are English sentence-level mapping tasks,
whereas the system targets multi-step Thai narratives, so agreement evidences the soundness
of the retrieval components rather than of the case-analysis task. And they were annotated
against an earlier ATT&CK version than the one ingested here, so a label may refer to a
technique since revoked, renamed or reorganised; the version mapping applied is given in
Section 5.x and results are reported both with and without it. For the comparison to be
meaningful the metrics are computed as those works define them rather than by substituting
the definitions of Section 3.5.2.

Neither tier carries a reference answer, a deliberate consequence of deriving all labels
externally: no published source supplies a Thai prosecutorial case summary to compare
against, and authoring one here would reintroduce exactly the dependence on
self-constructed ground truth these tiers exist to avoid. Generation is therefore assessed
with reference-free measures (Section 3.5.3), and is additionally isolated from retrieval
quality by an oracle condition in which the gold context is supplied directly, so that the
difference between the oracle and served conditions attributes error to the stage
responsible for it.

## 3.5.2 Retrieval metrics

**Definition of a retrieved item.** Every metric below operates on an ordered list of
ATT&CK identifiers produced by one retrieval call. That list is the concatenation of the
merged semantic results, in rank order, followed by the centre node and neighbours of each
returned subgraph. Graph neighbours are counted as retrieved because they enter the
generation context and are available to be cited; a technique reached only through
expansion is nonetheless present to the model. This definition has a direct and asymmetric
consequence: a single subgraph can contribute two hundred neighbours, so an incident
retrieving fifteen semantic results routinely yields a retrieved list of two hundred or
more identifiers. Rank-sensitive measures remain meaningful, because the semantic results
occupy the head of the list, but precision at large *K* is bounded structurally rather than
by retrieval quality and should be read as a property of the context size, not of retrieval
accuracy.

**Standard measures.** Hit@*K*, Precision@*K*, MRR, NDCG@*K* and MAP are computed with
binary relevance against the gold identifiers of the sample; higher is better throughout.
Recall@*K* is computed with a capped denominator, hits / min(|relevant|, *K*), rather than
the conventional hits / |relevant|. The conventional form is uninformative for samples
whose gold set exceeds the retrieval budget: an enumerative sample with 180 gold techniques
evaluated at *K* = 10 cannot exceed 0.056 even under a perfect retriever, so the score
measures the ratio of budget to gold-set size rather than retrieval quality. The capped
form asks the answerable question — of the *K* positions available, how many were filled
with relevant results — and is identical to the conventional form whenever |relevant| ≤ *K*.
This substitution is noted because it makes the reported Recall figures incomparable with
works using the uncapped definition; the comparison against published baselines therefore
uses those works' own definitions.

**Step coverage.** The measures above score an incident against the union of its gold
identifiers, which conflates two different outcomes: retrieving five techniques for one
attack step and none for the remaining four scores identically to retrieving one technique
for each of five steps, although only the second is useful for a case summary. The primary
metric is therefore StepCoverage@*K*, the fraction of a sample's attack steps for which at
least one gold identifier appears in the top *K*. This is subtopic recall (S-recall@*K*;
Zhai, Cohen and Lafferty, 2003) with attack steps as subtopics, and it is the quantity the
decomposition and per-channel quota of Section 3.4.2 are designed to raise.
StrictStepCoverage@*K*, requiring all of a step's gold identifiers rather than any, is
reported alongside it as an upper bound on evidential completeness per step.

**Diagnosing rank versus recall.** A step covered at *K* = 50 but not at *K* = 5 has been
retrieved and mis-ranked, not missed; the remedy is reranking rather than search. The
harness records the rank of the first retrieved identifier evidencing each step as a
diagnostic companion to the coverage curve, so that this distinction can be drawn per step
rather than inferred from aggregate curves.

**Scope of the measurement.** Four of the 347 annotated steps are excluded from scoring.
Their gold techniques are absent from the ingested graph — one is a technique not present
in the parsed bundles, and the remainder belong to the ICS domain, which is outside the
scope of this work and was never ingested. No retriever could return them, so scoring them
would measure ingestion coverage rather than retrieval, and they are reported separately as
an ingestion limitation. All figures are therefore over 343 scoreable steps.

Results are reported from a single run without confidence intervals. Embedding, fusion,
reranking and graph expansion are deterministic given a fixed index, but the decomposition
step is a language-model call, and although it is issued at temperature 0 the resulting
channel set is not guaranteed reproducible across invocations. Reported differences between
configurations should therefore be read as indicative where they are small; the absence of
repeated runs is a limitation of the evaluation rather than a property of the system.

## 3.5.3 Generation metrics

**[TODO-6]** *Not yet written. Must cover: RAGAS faithfulness and answer relevancy;
ATT&CK-identifier agreement against `gold_attack_ids`; the oracle condition as the
error-attribution mechanism; the evaluating model and its independence from the generating
model; and the absence of reference-based measures with the justification given in 3.5.1.*

---

# Unresolved items

| # | Item | Blocking? |
|---|---|---|
| TODO-1 | Embedding-model comparison (BGE-M3 vs multilingual-e5-large) asserted in 3.1 but not shown | Yes — an unsupported quantitative claim |
| TODO-2 | Figure 3.1, pipeline control flow | Yes — chapter has no figure |
| TODO-3 | Table 3.1, node/edge counts + ATT&CK version | Yes — placeholder in source |
| TODO-4 | Figure 3.2, example case file | No |
| TODO-5 | Table 3.5, worked decomposition example | No |
| TODO-6 | Section 3.5.3, generation metrics | Yes — section is empty |

## Numeric-evidence status

No number in this chapter is currently registered against a source file. The evaluation
figures that will populate Chapter 5 are **stale**: every result in
`rag_service/app/RAG/GraphRAG/evaluation/results/` predates the change binding graph seeds
to the per-channel quota (Section 3.4.3.5), which alters the retrieved-identifier list and
therefore every metric. Re-run before Chapter 5 cites them.

## Reviewer risks

1. **Counting graph neighbours as retrieved items** (3.5.2) will be challenged. The
   justification is stated, but be prepared to also report metrics over the semantic
   results alone.
2. **Type-reweighting coefficients** (3.4.3.4) are hand-set. The chapter says so; expect to
   be asked why these values and whether an ablation exists.
3. **Post-retrieval domain filtering** (3.4.3.2) is justified by an infrastructure
   constraint, not by a principle. Acceptable, but it invites the question of whether the
   relationship collection is filtered — it is not, and that is not yet disclosed in the
   chapter. **Consider adding one sentence.**
4. **Single run, no confidence intervals** (3.5.2) is disclosed. Expect it to be raised.
5. **Four excluded steps** (3.5.2) is disclosed and defensible.
