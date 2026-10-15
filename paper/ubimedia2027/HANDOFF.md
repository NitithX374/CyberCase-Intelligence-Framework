# Handoff: Ubi-Media 2027 paper (from the cloud session, 2026-10-15)

Read this first if you are picking the paper up in a new session.

## State

- Branch `claude/cybercase-work-7bf6lf`. The cloud session could not push (GitHub 403), so these commits
  reached this machine through a git bundle.
- Title: "From Lossless Units to Verbatim Spans: Traceable Evidence for LLM Document Analysis".
  Running head: "From Lossless Units to Verbatim Spans".
- Authors: Thattapon Surasak and Kritsakorn Khamwiset (KMUTNB).
- Paper shape:
  - 16 pages (CFP limit 6-16 including references);
  - abstract 250 words;
  - 36 references, no arXiv preprints (the advisor decided to drop all three);
  - LNCS class v2.26 vendored (`llncs.cls`, `splncs04.bst`), with the mandatory Disclosure of Interests
    in `credits`.
- Venue: Ubi-Media 2027, Springer CCIS, EasyChair `conf=ubimedia2027`. The deadline is 2026-10-15 and the
  CFP gives no time zone. The paper is not anonymous.
- The PDF the cloud session last built is the submission candidate.

## Build

```powershell
cd paper/ubimedia2027
tectonic main.tex            # or: latexmk -pdf main.tex   (pdflatex + bibtex; main.tex has no Thai characters)
```

The figures are committed as PDFs. You only need to rebuild them if you change them:

- `figures/units.tex` and `figures/overview.tex` need XeLaTeX, fontawesome5 and the Thai font Loma (TLWG).
- `figures/provenance.tex` needs FreeSerif.
- `figures/make_results.py` reads the recorded result files.

## Where things are recorded

- Status and decisions: `plan/progress.md` (newest entries at the end), `paper_state.json` (build hashes,
  blockers) and `paper_story.md` (title history, claims to make and to avoid).
- Every number in the paper: `claim_evidence_map.md`.
- Citations: `citation_verification.md` (one line per entry) and `citation_crosscheck.md` (Crossref, arXiv
  and Semantic Scholar check, produced by `tools/crosscheck_citations.py`).
- Measurements:
  - `research/traceability_properties/run.py` produces `results/properties.json` (Table 3, Sect. 5.1).
  - `segmenter_switch.py` produces `results/segmenter_switch.json` (the 91% / 55% in the Limitations
    paragraph).

## Open items

1. **Author or advisor decisions**
   - The advisor has to approve this final PDF. Since the advisor last saw it, the title changed, the
     preprints were removed, the Limitations paragraph was added and the audit fixes went in.
   - Funding or acknowledgements: there is a TODO comment in `credits` that does not print. Add
     `\subsubsection{\ackname}` if there is funding; otherwise delete the comment.
   - ORCID IDs are optional and Springer encourages them.
   - "A case can hold a victim's account, ..." (Introduction): the authors should confirm this from real
     cases.
2. **The ai-tell-audit loop ran three rounds (15 findings, then 3, then 3).** The three left are all low
   confidence and none was applied:
   - The Introduction calls Yang et al.'s registry IDs "free-form identifiers".
   - "a character range and page" (abstract, contribution 3, Conclusion): typed narratives have no page.
     Fixing this needs the abstract trimmed again, because it is at 250 words.
   - About 13 "X, not Y" / "rather than" constructions remain. All of them do scoping work.
3. **Offered to the authors, no answer yet**
   - Restyle Figs. 1-2 plainly, to match Fig. 3.
   - Sect. 5.1: say that most counted mid-word cuts are artefacts of the tokeniser.
4. **Code fix, after the deadline.** Unit identifiers hash `v` and the source text, not the segmenter
   (`backend/app/sources/evidence.py::evidence_revision`). `backend/app/trace/sentences.py` falls back to
   PyThaiNLP crfcut whenever SaT fails, at load time or on a single call. The fix is to put the
   segmenter, with its version, in the revision tag, and to stop the per-call fallback.
   - Changing the hash also changes Eq. 1, the hashes printed in Fig. 2 (`figures/units.tex`) and the
     Table 3 digest.
   - `wtpsplit` and the SaT model revision are also unpinned (`backend/requirements.txt`).

## House rules the authors asked for

- British spelling. No em dashes. Plain, concise sentences (paper-writing-style).
- Keep the paper at 16 pages or fewer and the abstract at 250 words or fewer. Rebuild and check the page
  count after every edit.
- Never change a number, citation or heading during a style pass.
- The authors talk in casual Thai.
