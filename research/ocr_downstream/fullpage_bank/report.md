# Full-page OCR: three engines over ThaiOCRBench

The task is all 197 `Task=Full-page OCR` samples of ThaiOCRBench (IJCNLP-AACL 2025).
The `n` column says how many each engine actually got through: Typhoon has the whole
task, the two CPU engines were stopped short. Use the shared-page table below for any
comparison between engines.

CER is computed on NFC-normalised text with markup removed; `cer_micro` pools all
characters, `cer_macro` averages the pages.

| Engine | n | CER micro | CER macro | Empty | Crashed | s/page | Spans quotable verbatim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| typhoon | 197 | 0.0751 | 0.0694 | 0 | 0 | None | 2814/4609 (0.6105) |
| paddle | 73 | 0.419 | 0.4525 | 7 | 2 | 51.35 | 332/2058 (0.1613) |
| tesseract | 197 | 0.2786 | 0.2927 | 2 | 0 | 22.91 | 539/4609 (0.1169) |

## Head to head, on the 73 pages every engine read

The table above gives each engine its own page set, and the engines did not all
finish. Categories differ in difficulty, so those columns are not comparable to
each other. These are.

| Engine | CER on the shared pages |
| --- | ---: |
| typhoon | 0.1341 |
| paddle | 0.419 |
| tesseract | 0.3203 |

## What each engine was asked to do

**typhoon** — Typhoon OCR, the vision-language model the product uses. Whole page in, text out; no layout stage of our own. Predictions are reused from the earlier cached run rather than re-billed.

**paddle** — PaddleOCR full pipeline: PP-DocLayoutV3 for layout and reading order, then PP-OCRv5_server_det for line detection, then th_PP-OCRv5_mobile_rec. CPU. Regions labelled table, formula, chart, figure, image or stamp are EXCLUDED before recognition, so their text is scored as deleted. Some pages kill the native process outright; those are recorded with status=crashed and an empty prediction rather than dropped from the denominator.

**tesseract** — Tesseract LSTM, lang=tha+eng, official tessdata. Whole page, no layout stage.

The three are not equivalent readers of a page. Typhoon and Tesseract are given
the whole image; PaddleOCR is given only what its layout model calls text. Read
the PaddleOCR column as the pipeline's score, not the recogniser's.

## typhoon by category

| Category | n | CER |
| --- | ---: | ---: |
| Government | 54 | 0.0335 |
| Education | 35 | 0.0607 |
| Lifestyle | 18 | 0.0201 |
| Medical | 16 | 0.1287 |
| Finance | 12 | 0.1235 |
| Religion | 10 | 0.03 |
| Transportation | 9 | 0.1134 |
| Legal | 9 | 0.0819 |
| Advertising & Media | 5 | 0.0299 |
| Entertainment | 4 | 0.0846 |
| Retail | 4 | 0.0682 |
| Agriculture | 4 | 0.18 |
| Food & Beverage | 3 | 0.4363 |
| Technology | 3 | 0.1596 |
| Architecture | 3 | 0.0159 |
| Hospitality | 2 | 0.0261 |
| Logistics | 2 | 0.028 |
| Real Estate | 1 | 0.572 |
| Construction | 1 | 0.0836 |
| Manufacturing | 1 | 0.1929 |
| Environment | 1 | 0.015 |

## paddle by category

| Category | n | CER |
| --- | ---: | ---: |
| Medical | 14 | 0.2567 |
| Government | 14 | 0.4151 |
| Education | 10 | 0.4971 |
| Finance | 8 | 0.3195 |
| Religion | 4 | 0.4696 |
| Agriculture | 4 | 0.3766 |
| Retail | 3 | 0.6783 |
| Legal | 3 | 0.6561 |
| Entertainment | 2 | 0.5819 |
| Food & Beverage | 2 | 0.9109 |
| Technology | 2 | 0.4489 |
| Transportation | 2 | 0.4937 |
| Lifestyle | 1 | 0.4907 |
| Hospitality | 1 | 1.0 |
| Real Estate | 1 | 0.7118 |
| Construction | 1 | 0.3315 |
| Manufacturing | 1 | 0.4725 |

## tesseract by category

| Category | n | CER |
| --- | ---: | ---: |
| Government | 54 | 0.1965 |
| Education | 35 | 0.3315 |
| Lifestyle | 18 | 0.1639 |
| Medical | 16 | 0.2866 |
| Finance | 12 | 0.3508 |
| Religion | 10 | 0.2766 |
| Transportation | 9 | 0.3032 |
| Legal | 9 | 0.3983 |
| Advertising & Media | 5 | 0.1114 |
| Entertainment | 4 | 0.3986 |
| Retail | 4 | 0.5401 |
| Agriculture | 4 | 0.3417 |
| Food & Beverage | 3 | 0.6753 |
| Technology | 3 | 0.5123 |
| Architecture | 3 | 0.0377 |
| Hospitality | 2 | 0.1008 |
| Logistics | 2 | 0.1053 |
| Real Estate | 1 | 0.5755 |
| Construction | 1 | 0.3859 |
| Manufacturing | 1 | 0.2389 |
| Environment | 1 | 0.2291 |
