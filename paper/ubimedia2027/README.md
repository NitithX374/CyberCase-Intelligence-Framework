# CyberCase: Ubi-Media 2027 paper

Start with `HANDOFF.md` for the current state and open items.

Build (Springer LNCS class v2.26 and `splncs04.bst` are vendored in this folder):

```bash
tectonic main.tex        # or: latexmk -pdf main.tex
```

The figures are prebuilt and committed as PDFs. To rebuild them:

```bash
tectonic figures/units.tex            # XeLaTeX; needs the Thai font Loma (TLWG)
tectonic figures/provenance.tex
python figures/make_results.py        # from the repository root; reads the recorded result files
```

`make_results.py` follows the style of the scientific-figure-making skill in
https://github.com/ChenLiu-1996/figures4papers (palette, spines, bar encoding).

- `main.tex`, `references.bib` — the paper.
- `paper_story.md` — thesis, contributions, claims to make and to avoid.
- `claim_evidence_map.md` — where every number comes from.
- `citation_verification.md`, `literature/raw/` — fetched citation metadata.
- `plan/progress.md`, `paper_state.json` — status and blockers.

`main.pdf` is git-ignored by the repository's `*.pdf` rule; rebuild locally or upload the folder
to Overleaf.
