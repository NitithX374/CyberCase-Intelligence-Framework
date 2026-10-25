# Appendix A rerun with the temperature rule (2026-10-26)

What changes from `current_2026-10-25`: only the code. Branch `feat/temperature-rule`, commit `79f0eddc`, worktree
`C:/Users/kkham/cc-worktrees/temperature-rule`. Every model stage without thinking sends temperature 0, a stage with
thinking sends 1.0. In this harness: reading 0, views 0, judgement 1.0 with a thinking budget of 2,048.
Same harness (`../current_2026-10-25/run_current.py`), same 100 articles, same edits, same scoring. Arms: clean and
targeted only (Table A-1 uses targeted; the book does not report realistic).

Rules: do not edit any code or harness file. Do not print or copy article text anywhere (the raw files and the jsonl
hold it and stay out of git). Spend at most USD 0.80. Stop and report on a harness error, more than 10 failed runs in
an arm, or an HTTP 402.

Run every command from `F:\Cybercase Framework` in Git Bash, with `export MSYS_NO_PATHCONV=1` first.

## 1. Setup (skip if `/tmp/tr_backend/app` and `/tmp/ocr_rerun/thaisum_ocr` already exist in the container)

```bash
C=cybercase-backend
docker exec $C rm -rf /tmp/ocr_rerun /tmp/tr_backend
docker exec $C mkdir -p /tmp/tr_backend /tmp/ocr_rerun/thaisum_ocr
docker cp C:/Users/kkham/cc-worktrees/temperature-rule/backend/app $C:/tmp/tr_backend/app
docker exec $C ln -s /app/models /tmp/tr_backend/models
R=backend/research/ocr_downstream/thaisum_ocr
docker cp $R/data $C:/tmp/ocr_rerun/thaisum_ocr/data
docker cp $R/facts.py $C:/tmp/ocr_rerun/thaisum_ocr/facts.py
docker cp $R/current_2026-10-25 $C:/tmp/ocr_rerun/thaisum_ocr/current_2026-10-25
docker exec $C rm -rf /tmp/ocr_rerun/thaisum_ocr/current_2026-10-25/results
```

Check that the new code is the one loaded; it must print `0.0 1.0`:

```bash
docker exec -w /tmp/tr_backend cybercase-backend python -c "import sys; sys.path.insert(0,'/tmp/tr_backend'); import app.llm.payload as p; from app.llm.settings import AnalysisPipelineConfig as A; from pydantic import BaseModel; M=type('M',(BaseModel,),{'__annotations__':{'a':int}}); print(p.stage_payload(A(thinking_tokens=0),'s',{},M)['temperature'], p.stage_payload(A(thinking_tokens=2048),'s',{},M)['temperature'])"
```

## 2. Main run (about 40 minutes)

```bash
IMG=$(docker inspect -f '{{.Image}}' cybercase-backend)
docker exec -w /tmp/tr_backend -e CYBERCASE_BACKEND=/tmp/tr_backend \
  -e CLAIM_NLI_PATH=/tmp/ocr_rerun/no_verifier/nli_mdeberta \
  -e CLAIM_SELECTOR_PATH=/tmp/ocr_rerun/no_verifier/source_selector_mpnet \
  cybercase-backend python /tmp/ocr_rerun/thaisum_ocr/current_2026-10-25/run_current.py \
  --arms clean,targeted --articles 100 --cap-usd 0.80 --concurrency 8 --expect-segmenter sat --confirm-spend \
  --results-dir /tmp/ocr_rerun/results_main --code-commit 79f0eddc --image-id $IMG
```

## 3. Copy out and score (scoring runs on the host, not in the container)

```bash
OUT=backend/research/ocr_downstream/thaisum_ocr/temperature_rule_2026-10-26/results
mkdir -p $OUT
docker cp cybercase-backend:/tmp/ocr_rerun/results_main/. $OUT/
cd backend
PYTHONPATH=. PYTHONIOENCODING=utf-8 python research/ocr_downstream/thaisum_ocr/current_2026-10-25/score_current.py --run run_<stamp> --results-dir research/ocr_downstream/thaisum_ocr/temperature_rule_2026-10-26/results
cd ..
docker exec cybercase-backend rm -rf /tmp/ocr_rerun /tmp/tr_backend
```

`<stamp>` is the one in the `run_<stamp>.jsonl` file name. The score file prints a `realistic` hypothesis line that
says "does not hold": there is no realistic arm in this run, so ignore that line.

## 4. Report back (counts only, no article text)

From `run_<stamp>_summary.json`: runs and completed per arm, errors, view failures per arm, calls by stage,
spent USD, and the temperature each stage sent (count `temperature` per `stage` over the `calls` of the jsonl).
From `score_<stamp>.md`: the clean filter (targets counted of 179), and for the targeted arm, primary (written
statuses), the substitution rows (number, place, other) and the deletion rows with n and counts per outcome, and the
share of targets left out because both forms appeared ("mixed").
