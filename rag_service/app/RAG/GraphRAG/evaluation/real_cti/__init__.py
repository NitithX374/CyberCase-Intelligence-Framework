"""Real-CTI evaluation tier.

Builds eval samples whose gold ATT&CK labels come from published, human-
authored sources instead of from this project's own graph or from an LLM:

  - ctid_loader   : CTID Adversary Emulation Library (ordered steps, per-step
                    technique IDs assigned by MITRE Engenuity analysts)

The loaders stop at *chains* (ordered technique steps + the source's own
prose). Turning a chain into a Thai case-file narrative is a separate,
human-reviewed step — see `draft_thai_cases.py`.
"""
