# NLI grounding experiment

The experiment that chose the claim verifier, B1-LR. Its verdict is in
`FINAL_VERDICT.md` and its cross-family re-evaluation in
`CROSS_FAMILY_REEVALUATION.md`.

Until 2026-10-18 this folder was `nli_grounding_experiment/` at the repository root.
Files written before then name it by that path. One of them is
`backend/app/trace/b1_lr.json`, whose `source_artifact` is now
`research/nli_grounding/outputs/canonical/final_lr_coefficients.json`; the file
keeps the old path because the verifier's `artifact_sha256` is the hash of its
bytes. The coefficients file still matches its recorded `source_artifact_sha256`.

`config.py` resolves `data/`, `cache/` and `outputs/` from its own location, so the
move did not change where the scripts read and write.
