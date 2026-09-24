# CyberCase Overleaf starter package

This package contains the current English Chapter 3 and Chapter 4 deliverables converted into a modular XeLaTeX project:

- `main.tex` — Overleaf entrypoint;
- `preamble.tex` — fonts, page layout, tables, figures, and hyperlinks;
- `chapters/chapter3.tex` and `chapters/chapter4.tex` — converted chapter text;
- `figures/chapter3/` and `figures/chapter4/` — extracted PNG figures;
- `tools/convert_docx_to_latex.py` — reproducible converter used for this package;
- `conversion_notes.md` — conversion boundaries and remaining thesis work.

## Overleaf

1. Zip the contents of this directory, or upload the directory as a new Overleaf project.
2. Set the project compiler to **XeLaTeX**.
3. Set `main.tex` as the main document if Overleaf does not detect it automatically.
4. Replace `Author Name` and the title-page text in `main.tex`.
5. Add the university class/template and bibliography after the institution provides the required format.

The preamble uses `Angsana New` when that font is available and otherwise falls back to `TeX Gyre Termes`. For an exact Angsana New match, upload a permitted font file to Overleaf and keep the font name in `preamble.tex`.

## Regenerating the chapters

Run the converter from the repository root, not from an uploaded Overleaf project:

```powershell
$py = "C:\Users\kkham\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py deliverables/overleaf-cybercase-2026-09-22/tools/convert_docx_to_latex.py
```

The converter reads the current English DOCX deliverables under `deliverables/thesis-chapter3-2026-09-21/` and `deliverables/thesis-chapter4-2026-09-21/`.

## Local build status

The package was smoke-tested with the bundled Tectonic 0.17.0 engine. The build completed with exit code 0 and produced a 31-page PDF in `build-local/main.pdf`. Representative pages were rendered and checked for clipping, missing figures, and broken table boundaries. Dense tables still produce normal overfull-box warnings, so the final university template and Overleaf rendering should receive a visual review.

Overleaf remains the target environment: set the compiler to XeLaTeX because the preamble uses `fontspec` and can use Angsana New when that font is available.
