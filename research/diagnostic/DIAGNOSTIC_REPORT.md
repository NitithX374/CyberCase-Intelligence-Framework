# Main Case Analysis Diagnostic Report

> This is a no-RAG pilot requested after the production RAG service could not be started. It is not evidence about the original RAG-grounded experiment.

## Execution boundary

- Retrieval status: `skipped_by_user`.
- Analysis context for every case: empty `retrieved_context`, empty `mitre_table`, null retrieval ID and null previous analysis.
- The production Main Case Analysis prompt and service were called unchanged.
- `diagnostic_notes` were excluded from generation and claim audits; they were used only for coverage evaluation.

## Aggregate results

- Cases: **12**
- Atomic claims: **570**
- Successful Main Case Analysis calls: **12**
- Research direction diagnostic: **E_NO_CLEAR_INTERVENTION_YET**
- Second judge: **completed**
- Judge diversity: **no; same-model independent repeat**

| Support status | Count | Percentage |
|---|---:|---:|
| SUPPORTED | 535 | 93.9% |
| UNSUPPORTED | 15 | 2.6% |
| CONTRADICTED | 1 | 0.2% |
| UNCLEAR | 19 | 3.3% |

Judge B (independent same-model repeat): SUPPORTED=540; UNSUPPORTED=12; CONTRADICTED=1; UNCLEAR=17

### Issue tags

- `CERTAINTY_STRENGTHENING`: 3
- `CAUSAL_OVERCLAIM`: 0
- `ATTRIBUTION_OVERCLAIM`: 2
- `POLARITY_NEGATION_ERROR`: 1
- `ROLE_RELATION_DISTORTION`: 0
- `SOURCE_ROLE_CONTAMINATION`: 0
- `UNSUPPORTED_TECHNICAL_INTERPRETATION`: 7
- `OTHER`: 0

### Coverage

- Addressed supported: 48
- Addressed incorrectly: 0
- Omitted: 1
- Coverage evaluation errors: 0

### Judge agreement

- Comparable claims: 570
- Support-status agreement: 551 (96.7%)
- Support-status disagreement: 19
- Issue-tag-set agreement: 556 (97.5%)
- Issue-tag-set disagreement: 14

## Case-by-case error examples

### case-002 / C21

- Claim: An external mailbox forwarding rule may be relevant to email-account compromise or collection concepts in a broader investigation.
- Support status: `UNSUPPORTED`
- Issue tags: UNSUPPORTED_TECHNICAL_INTERPRETATION
- Case State evidence IDs: evidence-002-01
- Relevant Case State evidence: The mailbox audit shows external-forwarding-rule-02 active on lchen@northbridge.example at 09:05 UTC.
- External context evidence: none (RAG was skipped).
- Reason: The case establishes an external forwarding rule, but supplies no basis for linking it to email-account compromise or collection concepts.

### case-002 / C40

- Claim: The distinction between a rule being active and messages actually being forwarded is an analytical qualification.
- Support status: `UNSUPPORTED`
- Issue tags: none
- Case State evidence IDs: none
- Relevant Case State evidence: none
- External context evidence: none (RAG was skipped).
- Reason: The case state shows an active rule and a forwarding relationship, but does not establish that this distinction was an analytical qualification.

### case-002 / C41

- Claim: The warning against inferring causality from timing is an analytical qualification.
- Support status: `UNSUPPORTED`
- Issue tags: none
- Case State evidence IDs: none
- Relevant Case State evidence: none
- External context evidence: none (RAG was skipped).
- Reason: The case state provides timing but does not state that a warning against inferring causality from timing was an analytical qualification.

### case-002 / C42

- Claim: The analytical qualifications do not add facts to the case.
- Support status: `UNSUPPORTED`
- Issue tags: none
- Case State evidence IDs: none
- Relevant Case State evidence: none
- External context evidence: none (RAG was skipped).
- Reason: Neither the case state nor the analysis context establishes that the stated analytical qualifications add no facts or resolve no questions.

### case-002 / C43

- Claim: The analytical qualifications do not resolve the case’s unanswered questions.
- Support status: `UNCLEAR`
- Issue tags: none
- Case State evidence IDs: none
- Relevant Case State evidence: none
- External context evidence: none (RAG was skipped).
- Reason: The case state does not identify the analytical qualifications or specify which questions remain unanswered, so their ability to resolve them cannot be assessed.

### case-004 / C19

- Claim: No ATT&CK technique can be assigned from the available information.
- Support status: `UNCLEAR`
- Issue tags: CERTAINTY_STRENGTHENING, UNSUPPORTED_TECHNICAL_INTERPRETATION
- Case State evidence IDs: evidence-004-01, evidence-004-02
- Relevant Case State evidence: EDR-ALERT-004 names update-check.ps1 and FIN-WS-04 but does not contain a process-start event. | The preliminary telemetry review found no confirmed powershell.exe process start for update-check.ps1 in the available window.
- External context evidence: none (RAG was skipped).
- Reason: The case shows no confirmed script or PowerShell execution, but does not establish that no ATT&CK technique can be assigned.

### case-004 / C20

- Claim: PowerShell is a commonly used administrative and scripting tool.
- Support status: `UNSUPPORTED`
- Issue tags: none
- Case State evidence IDs: none
- Relevant Case State evidence: none
- External context evidence: none (RAG was skipped).
- Reason: The Case State contains no general characterization of PowerShell as an administrative or scripting tool.

### case-004 / C41

- Claim: The stated confidence and status have been preserved.
- Support status: `UNCLEAR`
- Issue tags: none
- Case State evidence IDs: none
- Relevant Case State evidence: none
- External context evidence: none (RAG was skipped).
- Reason: The Case State contains confidence and status fields, but no supplied baseline establishes that they were preserved.

### case-005 / C46

- Claim: The principal limitations are unestablished identity and downstream activity.
- Support status: `UNCLEAR`
- Issue tags: none
- Case State evidence IDs: evidence-005-02, evidence-005-03
- Relevant Case State evidence: A file-system record shows renewal_terms.zip saved to FS-05 after the message arrived. | Omar Haddad is the listed vendor contact, but the preliminary record does not establish that he personally sent the message.
- External context evidence: none (RAG was skipped).
- Reason: Identity uncertainty is supported, but the case state does not establish that identity and downstream activity are the principal limitations.

### case-006 / C03

- Claim: The case materials report that Nina Alvarez used **Browser session 06**.
- Support status: `UNSUPPORTED`
- Issue tags: ATTRIBUTION_OVERCLAIM
- Case State evidence IDs: evidence-006-01
- Relevant Case State evidence: Browser history records a visit from Browser session 06 to portal-login-check.example.
- External context evidence: none (RAG was skipped).
- Reason: The case state reports that Browser session 06 visited the site, but does not establish that Nina personally used that session.

## Independent-judge disagreements

Judge B used the same Luna model independently. These disagreements are retained rather than forced into consensus:

- `case-001/C01`: A=`SUPPORTED` []; B=`CONTRADICTED` ['ROLE_RELATION_DISTORTION']. Claim: The case state reports three relevant events on workstation WS-17 on 11 May 2026.
- `case-004/C19`: A=`UNCLEAR` ['CERTAINTY_STRENGTHENING', 'UNSUPPORTED_TECHNICAL_INTERPRETATION']; B=`SUPPORTED` []. Claim: No ATT&CK technique can be assigned from the available information.
- `case-006/C03`: A=`UNSUPPORTED` ['ATTRIBUTION_OVERCLAIM']; B=`UNCLEAR` ['ATTRIBUTION_OVERCLAIM']. Claim: The case materials report that Nina Alvarez used **Browser session 06**.
- `case-006/C04`: A=`UNSUPPORTED` ['ATTRIBUTION_OVERCLAIM']; B=`UNCLEAR` ['ATTRIBUTION_OVERCLAIM']. Claim: The case materials report that Nina Alvarez used **Browser session 06** to visit **portal-login-check.example**.
- `case-006/C25`: A=`UNCLEAR` ['UNSUPPORTED_TECHNICAL_INTERPRETATION']; B=`SUPPORTED` []. Claim: The reported behavior may be consistent with a credential-collection or impersonation scenario in general cybersecurity practice.
- `case-006/C26`: A=`UNSUPPORTED` []; B=`UNCLEAR` []. Claim: The credential-collection or impersonation characterization is external analytical framing only.
- `case-006/C51`: A=`UNCLEAR` []; B=`UNSUPPORTED` []. Claim: General references to credential collection or impersonation are external analytical context.
- `case-006/C52`: A=`UNCLEAR` []; B=`UNSUPPORTED` []. Claim: General references to credential collection or impersonation are not facts about this case.
## Interpretation

This pilot can indicate how the current analysis behaves when no retrieved context is supplied, but it cannot assess source-role contamination, MITRE grounding, or the full production Case State plus RAG boundary. The raw issue-tag signal is weak and includes judge disagreement; several non-supported claims are self-referential analytical qualifications rather than case-fact hallucinations. No thesis contribution or novelty claim is justified from this run alone.

Floor-effect warning: the low observed violation rate is not a floor-effect result for the RAG-grounded production flow because live RAG was skipped.

The five fixtures most useful for manual inspection are `case-006` claims C03/C04 (person-to-session attribution), `case-012` claims C28/C29 (shared-account certainty wording), `case-007` claim C32 (negative/polarity wording), `case-002` claim C21 (technical interpretation of forwarding), and `case-003` observation O04 (coverage omission of shared-session and automation alternatives).
