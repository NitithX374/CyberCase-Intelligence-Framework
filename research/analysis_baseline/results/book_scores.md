# Book scores

Every number chapters 5 and 6 print, recounted by `book_scores.py` from saved files. No model was called.
Intervals: paired, 2,000 resamples, numpy default_rng(2026), 95% percentile, cases in id order.

## Table 5-1

| Item | Book | book_scores | Match |
|---|---|---|---|
| CASIE articles | 1,000 | 1,000 | yes |

## Table 5-2

| Item | Book | book_scores | Match |
|---|---|---|---|
| cases 51-150: cases | 100 | 100 | yes |
| cases 51-150: main-event facts | 776 | 776 | yes |
| cases 51-150: facts per case, median (range) | 6 (3 to 32) | 6 (3 to 32) | yes |
| cases 151-250: cases | 100 | 100 | yes |
| cases 151-250: main-event facts | 832 | 832 | yes |
| cases 151-250: facts per case, median (range) | 7 (3 to 32) | 7 (3 to 32) | yes |

## Table 5-3

| Item | Book | book_scores | Match |
|---|---|---|---|
| ladder train: sentences | 2,214 | 2,214 | yes |
| ladder train: positive share | 0.500 | 0.500 | yes |
| ladder dev: sentences | 568 | 568 | yes |
| ladder dev: positive share | 0.500 | 0.500 | yes |
| ladder test: sentences | 662 | 662 | yes |
| ladder test: positive share | 0.500 | 0.500 | yes |
| mtdb train: sentences | 4,437 | 4,437 | yes |
| mtdb train: positive share | 0.258 | 0.258 | yes |
| mtdb dev: sentences | 698 | 698 | yes |
| mtdb dev: positive share | 0.362 | 0.362 | yes |
| mtdb test: sentences | 1,831 | 1,831 | yes |
| mtdb test: positive share | 0.288 | 0.288 | yes |
| mtdb test: positive sentences | 527 | 527 | yes |
| mtdb reports train/dev/test | 23/8/8 | 23/8/8 | yes |

## Table 5-5

| Item | Book | book_scores | Match |
|---|---|---|---|
| XLM-R base: LADDER test AUROC | 0.915 ± 0.005 | 0.915 ± 0.005 | yes |
| XLM-R large: LADDER test AUROC | 0.943 ± 0.006 | 0.943 ± 0.006 | yes |
| BGE-M3: LADDER test AUROC | 0.943 ± 0.004 | 0.943 ± 0.004 | yes |
| the checkpoint the system runs: LADDER test AUROC | 0.917 | 0.917 | yes |
| TF-IDF and logistic regression: LADDER test AUROC | 0.881 | 0.881 | yes |
| TF-IDF and linear SVM: LADDER test AUROC | 0.881 | 0.881 | yes |
| larger encoders minus XLM-R base, 'about' | 0.03 | 0.03 | yes |

## Section 5.3.1

| Item | Book | book_scores | Match |
|---|---|---|---|
| ladder_test: F1 of flagging every sentence | 0.667 | 0.667 | yes |
| mtdb_test: F1 of flagging every sentence | 0.447 | 0.447 | yes |

## Table 5-8

| Item | Book | book_scores | Match |
|---|---|---|---|
| E1: AUROC, precision, recall, F1 (mean over seeds) | 0.881 0.795 0.834 0.814 | 0.881 0.795 0.834 0.814 | yes |
| E2: AUROC, precision, recall, F1 (mean over seeds) | 0.735 0.714 0.535 0.611 | 0.735 0.714 0.535 0.611 | yes |
| E3: AUROC, precision, recall, F1 (mean over seeds) | 0.920 0.833 0.849 0.839 | 0.920 0.833 0.849 0.839 | yes |
| E4: AUROC, precision, recall, F1 (mean over seeds) | 0.762 0.737 0.558 0.635 | 0.762 0.737 0.558 0.635 | yes |
| E5: AUROC, precision, recall, F1 (mean over seeds) | 0.923 0.848 0.854 0.851 | 0.923 0.848 0.854 0.851 | yes |

## Table 5-9

| Item | Book | book_scores | Match |
|---|---|---|---|
| E1: AUROC, precision, recall, F1 (mean over seeds) | 0.781 0.608 0.541 0.572 | 0.781 0.608 0.541 0.572 | yes |
| E2: AUROC, precision, recall, F1 (mean over seeds) | 0.832 0.640 0.617 0.628 | 0.832 0.640 0.617 0.628 | yes |
| E3: AUROC, precision, recall, F1 (mean over seeds) | 0.844 0.753 0.481 0.579 | 0.844 0.753 0.481 0.579 | yes |
| E4: AUROC, precision, recall, F1 (mean over seeds) | 0.893 0.705 0.701 0.702 | 0.893 0.705 0.701 0.702 | yes |
| E5: AUROC, precision, recall, F1 (mean over seeds) | 0.847 0.734 0.518 0.605 | 0.847 0.734 0.518 0.605 | yes |
| E3 seed 42 recall on MalwareTextDB | 0.583 | 0.583 | yes |

## Table 5-10

| Item | Book | book_scores | Match |
|---|---|---|---|
| shipped checkpoint AUROC | 0.917 | 0.917 | yes |
| TP / FN / FP / TN at 0.50 | 278 / 53 / 44 / 287 | 278 / 53 / 44 / 287 | yes |
| precision | 278/322 = 0.863 | 278/322 = 0.863 | yes |
| recall | 278/331 = 0.840 | 278/331 = 0.840 | yes |

## Table 5-11

| Item | Book | book_scores | Match |
|---|---|---|---|
| one call: M1 | 1,340/1,383 = 0.969 | 1,340/1,383 = 0.969 | yes |
| one call: M2 | 1,399/1,424 = 0.982 | 1,399/1,424 = 0.982 | yes |
| one call: M3 | 77/100 | 77/100 | yes |
| two calls: M1 | 1,670/1,693 = 0.986 | 1,670/1,693 = 0.986 | yes |
| two calls: M2 | 1,779/1,803 = 0.987 | 1,779/1,803 = 0.987 | yes |
| two calls: M3 | 86/95 | 86/95 | yes |
| shipped: M1 | 1,577/1,614 = 0.977 | 1,577/1,614 = 0.977 | yes |
| shipped: M2 | 1,649/1,668 = 0.989 | 1,649/1,668 = 0.989 | yes |
| shipped: M3 | 85/96 | 85/96 | yes |
| final: M1 | 1,601/1,625 = 0.985 | 1,601/1,625 = 0.985 | yes |
| final: M2 | 1,677/1,704 = 0.984 | 1,677/1,704 = 0.984 | yes |
| final: M3 | 85/99 | 85/99 | yes |
| M1 range in the text | 97% to 99% | 97% to 99% | yes |
| M2 range in the text | 98.2% and 98.9% | 98.2% and 98.9% | yes |

## Table 5-12

| Item | Book | book_scores | Match |
|---|---|---|---|
| prose: M5 | 0.699 | 0.699 | yes |
| prose: M5-std | 0.767 | 0.767 | yes |
| prose: chance floor (cases) | 0.141 (100) | 0.141 (100) | yes |
| one call: M4 | 0.805 | 0.805 | yes |
| one call: M4b | 0.624 | 0.624 | yes |
| one call: M5 | 0.771 | 0.771 | yes |
| one call: M5-std | 0.808 | 0.808 | yes |
| one call: chance floor (cases) | 0.151 (100) | 0.151 (100) | yes |
| two calls: M4 | 0.872 | 0.872 | yes |
| two calls: M4b | 0.729 | 0.729 | yes |
| two calls: M5 | 0.793 | 0.793 | yes |
| two calls: M5-std | 0.833 | 0.833 | yes |
| two calls: chance floor (cases) | 0.159 (95) | 0.159 (95) | yes |
| shipped: M4 | 0.888 | 0.888 | yes |
| shipped: M4b | 0.743 | 0.743 | yes |
| shipped: M5 | 0.825 | 0.825 | yes |
| shipped: M5-std | 0.842 | 0.842 | yes |
| shipped: chance floor (cases) | 0.111 (96) | 0.111 (96) | yes |
| final: M4 | 0.928 | 0.928 | yes |
| final: M4b | 0.775 | 0.775 | yes |
| final: M5 | 0.847 | 0.847 | yes |
| final: M5-std | 0.870 | 0.870 | yes |
| final: chance floor (cases) | 0.102 (99) | 0.102 (99) | yes |
| one call: M4 over completed cases | 0.805 | 0.805 | yes |
| two calls: M4 over completed cases | 0.917 | 0.917 | yes |
| shipped: M4 over completed cases | 0.925 | 0.925 | yes |
| final: M4 over completed cases | 0.938 | 0.938 | yes |
| M4 range in the text | 80.5% to 92.8% | 80.5% to 92.8% | yes |
| M4 minus M4b in the text | 0.14 to 0.18 | 0.14 to 0.18 | yes |
| M4b range in the text | 0.624 to 0.775 | 0.624 to 0.775 | yes |
| chance floor range in the text | 0.102 to 0.159 | 0.102 to 0.159 | yes |

## Section 5.4.2 design

| Item | Book | book_scores | Match |
|---|---|---|---|
| M1, two calls − one call | +0.019 [−0.012, +0.056] | +0.019 [−0.009, +0.055] | point equal, interval moved 0.003 |
| M2, two calls − one call | +0.005 [−0.015, +0.018] | +0.005 [−0.014, +0.018] | point equal, interval moved 0.001 |
| M4, two calls − one call, failures 0 | +0.066 [−0.009, +0.142] | +0.066 [−0.008, +0.136] | point equal, interval moved 0.006 |
| M4, two calls − one call, completed in both | +0.120 [+0.059, +0.180] | +0.120 [+0.061, +0.181] | point equal, interval moved 0.002 |
| M4b, two calls − one call, failures 0 | +0.105 [+0.035, +0.172] | +0.105 [+0.035, +0.172] | yes |
| M4b, two calls − one call, completed in both | +0.151 [+0.090, +0.212] | +0.151 [+0.090, +0.212] | yes |

## Section 5.4.2 prose

| Item | Book | book_scores | Match |
|---|---|---|---|
| M5-std, two calls − prose | +0.067 [+0.016, +0.117] | +0.067 [+0.016, +0.117] | yes |
| V3, two calls − prose | +0.064 [+0.010, +0.114] | +0.064 [+0.012, +0.116] | point equal, interval moved 0.002 |
| M5-std, one call − prose | +0.041 [−0.004, +0.090] | +0.041 [−0.004, +0.090] | yes |
| M5-std, two calls − one call | +0.025 [−0.037, +0.081] | +0.025 [−0.037, +0.081] | yes |
| V3, two calls − one call | +0.016 [−0.044, +0.079] | +0.016 [−0.045, +0.075] | point equal, interval moved 0.004 |

## Section 5.4.2 binder

| Item | Book | book_scores | Match |
|---|---|---|---|
| two calls: M4 without stitched quotes | 0.855 | 0.855 | yes |
| shipped: M4 without stitched quotes | 0.888 | 0.888 | yes |
| final: M4 without stitched quotes | 0.926 | 0.926 | yes |
| two calls: M4 lowered by removing them | 0.017 | 0.017 | yes |
| shipped and final: M4 lowered by removing them | 0.002 or less | 0.000 and 0.002 | yes |
| quotes the binder dropped, cases 51-150 | 22 | 22 | yes |
| of them, every word kept in order | 19 | 19 | yes |
| of those, in case 1271 | 14 | 14 | yes |
| 1271: claims demoted (every quote wrapped in quotation marks) | 14 (14) | 14 (14) | yes |
| 10086 A-05: characters written, characters kept | 207 -> 719 | 207 -> 719 | yes |

## Table 5-13 decoding

| Item | Book | book_scores | Match |
|---|---|---|---|
| M1, final − shipped | +0.008 [−0.013, +0.042] | +0.008 [−0.013, +0.040] | point equal, interval moved 0.002 |
| M2, final − shipped | −0.004 [−0.015, +0.005] | −0.004 [−0.014, +0.005] | point equal, interval moved 0.001 |
| M4, final − shipped, failures 0 | +0.041 [−0.010, +0.099] | +0.041 [−0.010, +0.095] | point equal, interval moved 0.004 |
| M4b, final − shipped, failures 0 | +0.032 [−0.019, +0.088] | +0.032 [−0.019, +0.088] | yes |
| M5-std, final − shipped | +0.028 [−0.012, +0.068] | +0.028 [−0.012, +0.068] | yes |
| shipped: M1, M2, M4, M4b, M5-std | 0.977 0.989 0.888 0.743 0.842 | 0.977 0.989 0.888 0.743 0.842 | yes |
| final: M1, M2, M4, M4b, M5-std | 0.985 0.984 0.928 0.775 0.870 | 0.985 0.984 0.928 0.775 0.870 | yes |
| failed cases, shipped and final | 4/100 and 1/100 | 4/100 and 1/100 | yes |

## Table 5-14

| Item | Book | book_scores | Match |
|---|---|---|---|
| traces selected, traces scored | 50, 48 | 50, 48 | yes |
| arm_b: claims kept | 2,601/2,601 | 2,601/2,601 | yes |
| arm_b: quotes kept in the claim's own row, normalised | 2,709/2,709 | 2,709/2,709 | yes |
| arm_b: quotes found verbatim anywhere | 2,709/2,709 | 2,709/2,709 | yes |
| arm_b: quotes found after NFKC and whitespace | 2,709/2,709 | 2,709/2,709 | yes |
| arm_b: malformed reports | 0/144 | 0/144 | yes |
| arm_b: traces whose three reports are identical | 48/48 | 48/48 | yes |
| arm_a: claims kept | 2,561/2,601 | 2,561/2,601 | yes |
| arm_a: quotes kept in the claim's own row, normalised | 2,630/2,709 | 2,630/2,709 | yes |
| arm_a: quotes found verbatim anywhere | 2,586/2,709 = 0.955 | 2,586/2,709 = 0.955 | yes |
| arm_a: quotes found after NFKC and whitespace | 2,638/2,709 = 0.974 | 2,638/2,709 = 0.974 | yes |
| arm_a: malformed reports | 3/144 | 3/144 | yes |
| arm_a: traces whose three reports are identical | 0/48 | 0/48 | yes |
| arm_a: claims lost (of them in the malformed reports) | 40 (40) | 40 (40) | yes |
| arm_a: quotes changed only in spacing or Unicode / cut, extended or dropped | 52 / 71 | 52 / 71 | yes |
| 10078 A-01, Arm A run 1: trace quotes changed, characters before -> after | 22 -> 79 (extended) | 22 -> 79 (extended); 56 -> 79 (extended); 84 -> 137 (extended); 52 -> 137 (extended); 98 -> 141 (extended); 42 -> 141 (extended) | yes |
| 10081 A-05, Arm A run 1: trace quotes changed, characters before -> after | 340 -> 96 (cut to its end) | 340 -> 96 (cut to its end) | yes |

## Table 5-15

| Item | Book | book_scores | Match |
|---|---|---|---|
| one call: failed / calls to the cap / median model s / USD per case | 0 / 4 / 92 / 0.0032 | 0 / 4 / 92 / 0.0032 | yes |
| two calls: failed / calls to the cap / median model s / USD per case | 5 / 25 / 170 / 0.0074 | 5 / 25 / 170 / 0.0074 | yes |
| shipped: failed / calls to the cap / median model s / USD per case | 4 / 19 / 253 / 0.0067 | 4 / 19 / 253 / 0.0067 | yes |
| final: failed / calls to the cap / median model s / USD per case | 1 / 4 / 136 / 0.0044 | 1 / 4 / 136 / 0.0044 | yes |
| final USD over shipped USD | about two thirds | 0.66 | yes |

## Table 5-16

| Item | Book | book_scores | Match |
|---|---|---|---|
| the attackers | Attacker 741-754 yes yes yes A-06 | Attacker 741-754 yes yes yes A-06 | yes |
| meta data | Compromised-Data 786-795 no no no A-07 | Compromised-Data 786-795 no no no A-07 | yes |
| 21 february | Time 768-779 yes yes yes A-06 | Time 768-779 yes yes yes A-06 | yes |
| a file server | Victim 831-844 yes yes yes A-07 | Victim 831-844 yes yes yes A-07 | yes |
| athlete tues | Victim 799-811 no yes yes A-07 | Victim 799-811 no yes yes A-07 | yes |
| athletes therapeutic use exemption tue applications | Victim 243-297 no yes yes A-02 | Victim 243-297 no yes yes A-02 | yes |
| iaaf servers | Victim 308-320 no yes yes A-02 | Victim 308-320 no yes yes A-02 | yes |
| the iaaf network | Victim 721-737 no yes yes A-06 | Victim 721-737 no yes yes A-06 | yes |
| totals: prose, one call, two calls mention; two calls cite | 3/8 7/8 7/8 8/8 | 3/8 7/8 7/8 8/8 | yes |
| one call: claims, quotes, facts cited | 1, 1, 0 | 1, 1, 0 | yes |
| two calls: claims that cite, facts cited and stated by one claim (M4b) | 3, 6/8 | 3, 6/8 | yes |

## Section 6.1.2

| Item | Book | book_scores | Match |
|---|---|---|---|
| final M4 and M4b as percentages | 92.8% and 77.5% | 92.8% and 77.5% | yes |

## Reproduction check

- Numbers checked: 153. Printed exactly as in the book: 141. Agreeing by the book's wording: 3.
- Point estimates or counts that differ: 0.
- Intervals that moved by more than 0.005: 1: 5.4.2 design M4, two calls − one call, failures 0 (book +0.066 [−0.009, +0.142], here +0.066 [−0.008, +0.136])
- Verdicts that flipped: 0.
