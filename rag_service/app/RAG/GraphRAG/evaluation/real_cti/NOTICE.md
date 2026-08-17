# Vendored third-party CTI data

## CTID Adversary Emulation Library

`data/ctid_plans/*.yaml` are the machine-readable emulation plans from:

- Repository: https://github.com/center-for-threat-informed-defense/adversary_emulation_library
- Publisher: Center for Threat-Informed Defense (MITRE Engenuity)
- Commit vendored: `4467a6eed6e67d25009704130e1d27d1a8007f57`
- Vendored on: 2026-08-07
- License: Apache License 2.0

Files are copied verbatim from `<plan>/Emulation_Plan/yaml/*.yaml`; only the
directory layout is flattened. No modifications were made to the contents.

Why vendored rather than fetched at runtime: the evaluation dataset must be
reproducible from the repo alone, and the gold ATT&CK labels in these files
are the ground truth for the `real_cti` eval tier. Pinning the commit means a
later upstream edit cannot silently change published eval numbers.

Only the plan YAML files are vendored. The upstream repository also contains
emulation payloads and binaries — none of those are copied here.

## CISA TTP Articles Data Set

`data/cisa_ttp_articles.jsonl` is **fetched, not vendored** — see
`fetch_cisa.py`, and note it is gitignored.

- Record: https://zenodo.org/records/14659512
- DOI: `10.5281/zenodo.14659512`
- Contents: 77 CISA cybersecurity advisories (Jul 2020 – Feb 2024) crawled
  from cisa.gov, kept because they carry an explicit MITRE ATT&CK section
- License: CC-BY-4.0
- Funding acknowledged upstream: European Defence Fund; Austrian FFG Kiras
  project ASOC

Fetched rather than copied because a Zenodo DOI resolves to an immutable
record, so pinning the DOI already gives reproducibility. The CTID plans
needed vendoring instead because their upstream branch moves.

cisa.gov answers 403 to scripted requests, so this dataset is also the
practical route to the advisory text — and the citable one.

The derived `data/cisa_chains.json` is committed; it is what the eval
actually consumes.
