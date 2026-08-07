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
