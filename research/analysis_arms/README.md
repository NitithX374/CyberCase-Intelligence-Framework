# Analysis arms

`analysis_arms.py` holds the ablation arms that were built from the steps
`advance_case` runs:

| Arm | What it runs |
|---|---|
| `direct` | the technical context and the writer, without binding |
| `verify` | the same, then binding |
| `revise` | the one-call writer, then up to `max_revisions` calls that hand back the quotations the binder could not find |
| `single` | the one-call writer production used before the reading and judgement split, then binding |

Until 17 October 2026 the module lived in `backend/experiments/`. It was moved
here with its tests when the backend dropped what only these arms used: the
one-call contract (`CaseProviderAnalysis`, `CaseProviderClaim`,
`CaseProviderCitation`), binding a quotation that names no evidence unit, and the
grounding counters that `revise` reads. The arms therefore run only against the
backend as it was at commit `712aeeed`, the last one that has all three.

The held-out comparison and RQ2 imported the copy of this module inside their own
pinned backends (`1e29bd3` and `4aa8b18`), so moving this copy changes neither.

## Running the tests

From the repository root, check out the pinned backend once and point the tests
at it. Without `CYBERCASE_ARMS_BACKEND` the tests are not collected.

```bash
git worktree add --detach ../cybercase-arms-712aeeed 712aeeed
CYBERCASE_ARMS_BACKEND=../cybercase-arms-712aeeed/backend python -m pytest research/analysis_arms
```
