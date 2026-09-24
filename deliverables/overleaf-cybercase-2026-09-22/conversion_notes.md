# Conversion notes

## Scope

The package is intentionally limited to the current Chapter 3 methodology and Chapter 4 system-development deliverables. It does not import the older full-thesis DOCX because that document contains superseded architecture and terminology.

The converted chapters preserve the current workflow:

```text
Case sources → gap assessment → deterministic Ask/Proceed
→ structured main analysis → source binding → validated analysis → report
```

Follow-up answers remain chat history rather than native Case sources. MITRE/RAG is described as optional external technical context and is not required by the core workflow.

## Conversion choices

- Word paragraphs became LaTeX paragraphs and numbered sections.
- Word tables became `longtable` environments with escaped special characters.
- Embedded Word figures were extracted as PNG files and referenced using project-relative paths.
- The package uses XeLaTeX because the source deliverables use a system font and include Unicode text.
- The university-specific title page, chapter numbering rules, margins, citation style, and bibliography are not assumed without the official template.

## Remaining work before thesis submission

- Add the official university `.cls` or template package.
- Convert or write Chapters 1, 2, 5, and 6 after the research questions and evaluation are frozen.
- Add verified citations and a `.bib` file.
- Compile on Overleaf with XeLaTeX and inspect page breaks, long tables, figure scaling, and font fallback.
- Replace placeholder author and institution fields.
