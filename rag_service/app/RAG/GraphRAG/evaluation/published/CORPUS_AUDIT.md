# Corpus audit — what the STIX parser was leaving out

Written after the oracle experiment pointed at retrieval as the bottleneck.
Before swapping the embedding model, the question was whether the right document
was being embedded *badly*, or whether it was never in the corpus at all.

It was often the second.

## How this was checked

Counted directly against `Mitre_ATT&CK Doc/enterprise-attack/enterprise-attack.json`
(ATT&CK v19.0, `x_mitre_attack_spec_version` 3.3.0), then re-run through the
parser to see what survived.

```bash
python -m RAG.GraphRAG.ingestion.stix_parser   # via parse_folder in a REPL
```

## Finding 1 — every DETECTS edge was being dropped

`RELATIONSHIP_TYPE_MAP` maps `detects` → `DETECTS`, and the bundle holds 697 of
them. The parser emitted **zero**.

ATT&CK v17 moved the source endpoint of a `detects` relationship:

```
detects: source types = Counter({'x-mitre-detection-strategy': 697})
detects: target types = Counter({'attack-pattern': 697})
```

`x-mitre-detection-strategy` was not in `STIX_TYPE_TO_LABEL`, so it never became
an entity, so `finalize_parsing()` discarded every edge on the grounds that an
endpoint did not resolve. That filter does not log, which is why the loss was
invisible for as long as it was.

## Finding 2 — 1,758 detection analytics were never indexed

| STIX type | count | before | after |
|---|---:|---|---|
| `x-mitre-analytic` | 1,758 | not parsed | indexed |
| `x-mitre-detection-strategy` | 699 | not parsed | parsed as a join node, not indexed |

Detection strategies carry **no description at all** (0 of 699 in v19), so they
are deliberately not embedded. Their value is structural: they name the technique
each analytic detects.

The analytics are the interesting part. Median 211 characters, and written at
observable level:

> Monitor `/var/log/audit/audit.log` and DNS resolver logs for repeated failed
> lookups or connections to high-entropy domain names. Correlate suspicious DNS
> queries with process lineage (e.g., Python, bash, or unusual system daemons).

Compare the register of `Technique.description`, median 1,298 characters of
defender-encyclopedia prose thick with `(Citation: …)` markers. The earlier
token-overlap measurement — 0.43 between TRAM inputs and its exemplar corpus,
0.25 between the same inputs and ours — is a measurement of exactly this gap.

Each analytic is stamped with the ATT&CK ID of the technique its strategy
detects, so a vector hit on one resolves to a T-number with no special-casing
downstream. 1,745 of 1,758 resolve; the remaining 13 have a strategy with no
`detects` edge.

## Finding 3 — relationship payloads carried no ATT&CK ID

`context_builder.build_context()` prints an ID only when the payload has one:

```python
attack_id = vr.metadata.get("attack_id", "")
...
if attack_id:
    header += f" ({attack_id})"
```

Entities had one. Relationships did not. So a hit on any of the ~18k procedure
examples reached the LLM like this:

```
[3] Relationship: USES — Explosive | relevance: 0.812
    Explosive USES System Network Configuration Discovery: [Explosive](...) has
    collected the MAC address from the victim's machine.
```

The technique is *named* but its number is absent, so the model had to supply
`T1016` from memory. Both endpoint IDs now travel on the payload.

**This does not invalidate any earlier measurement.** Those runs measured the
system as it actually behaved; nothing was scored incorrectly. It is a gap that
was found, not a result that has to be withdrawn.

### It does not, however, explain the low precision

The obvious hypothesis was that the model names techniques correctly and then
cites the wrong number, which would score as a false positive while the analysis
underneath was right. Counted over the existing run files — a gold technique the
run missed, where the technique's canonical name nevertheless appears in the
answer text — that turns out to be a small effect:

| run (sub-techniques rolled to parent) | missed | named anyway | share |
|---|---:|---:|---:|
| `tram__rag-en__k20-techonly` | 312 | 2 | 0.6% |
| `tram__agent__qwen3-5-9b-nothink` | 381 | 25 | 6.6% |
| `thai-cti__agent__luna` | 68 | 1 | 1.5% |
| `thai-cti__agent__qwen3-5-9b-nothink` | 148 | 4 | 2.7% |

The agent scores higher than the extraction arm because it writes prose, which
names things without always citing them. But at 0.6–6.6% of misses, this is not
what precision 0.495 is made of. The overwhelming majority of misses never name
the technique at all — they are genuine misses, which is consistent with the
oracle result pointing at retrieval rather than at generation.

Counted without the parent rollup, the same measurement reads 6.4–14.3%, but
that number is wrong: it books a gold `T1566` answered as `T1566.001` as a miss,
when the scoring mode used throughout rolls exactly that up to a hit. Both
counts are recorded here so the discrepancy is not rediscovered later.

## Finding 4 — DataSource / HAS_COMPONENT is dead against v17+

```
x-mitre-data-source : 38, of which deprecated 38
x-mitre-data-component with x_mitre_data_source_ref : 0 / 109
```

All 38 data sources are deprecated, and the ref field they were linked by is
gone — replaced by `x_mitre_log_sources` on the component. The parser correctly
drops the deprecated objects, so `_parse_data_source()` and
`_build_data_source_edges()` are unreachable in practice. Left in place for
older bundles, with the docstring corrected. The log-source channel names are
now read, but only where they hang off an analytic.

## Finding 5 — fields that were parsed and then discarded

`build_entity_document()` embedded `"{label}: {name}. {description}"` and nothing
else, although the parser had already extracted:

- **aliases** — how write-ups actually name a group (APT29 / Cozy Bear /
  Midnight Blizzard) or a tool
- **tactics** — the kill-chain phase
- **platforms**

All three are now appended to the embedded text.

## Net effect on the corpus

```
entities        1,913 -> 4,368        DETECTS       0 -> 697
Analytic            0 -> 1,758        ANALYTIC_OF   0 -> 1,745
```

Across enterprise + mobile, the indexed corpus is 4,164 entity documents and
21,347 relationship documents, and **every relationship document now carries an
ATT&CK ID**.

## What this does not tell us

Nothing here is a result. A larger, better-labelled corpus is a hypothesis about
retrieval quality, not evidence of it — more documents can just as easily mean
more competition for the same top-K slots. `compare_corpus.py` measures it, and
it deliberately separates the corpus change from the embedding-model change so
neither can take credit for the other.
