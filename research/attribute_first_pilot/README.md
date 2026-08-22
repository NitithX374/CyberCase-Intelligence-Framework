# CyberCase Research Pilot: Attribute-First Reasoning vs Direct Zero-Shot

## 1. Research Question
> **"Does explicit attribute-first reasoning improve zero-shot, context-grounded cybersecurity analytical QA compared with direct zero-shot generation?"**

This is an isolated feasibility pilot to determine whether an explicit intermediate context representation (answerability, question type, relevant evidence IDs, epistemic state, missing information) provides downstream benefits before investing in larger dataset construction or fine-tuning.

---

## 2. Experimental Conditions (Same Base LLM: `meta-llama/llama-3.1-8b-instruct`)

1. **B0 — Direct Zero-Shot Baseline**:
   $$\text{Context} + \text{Question} \longrightarrow \text{LLM} \longrightarrow \text{Answer}$$
   *(No exposure to intermediate attributes or schema)*

2. **A1 — Predicted Attribute-First Zero-Shot**:
   $$\text{Context} + \text{Question} \longrightarrow \text{LLM} \longrightarrow \text{Predicted Attributes} \longrightarrow \text{LLM} \longrightarrow \text{Answer}$$

3. **A2 — Oracle Attribute-First**:
   $$\text{Context} + \text{Question} + \text{Gold Attributes} \longrightarrow \text{LLM} \longrightarrow \text{Answer}$$

### Hypothesis Interpretation Framework
- **$B0 \approx A1 \approx A2$**: Attribute-first representation provides little benefit.
- **$A2 \gg B0$ but $A1 \approx B0$**: The attribute representation itself is valuable, but zero-shot attribute prediction is the bottleneck (suggests fine-tuning attribute prediction).
- **$A1 > B0$ and $A2 \ge A1$**: Strong evidence that explicit intermediate reasoning improves grounded cybersecurity QA.

---

## 3. Intermediate Attribute Schema

```json
{
  "answerability": "SUFFICIENT" | "INSUFFICIENT" | "CONFLICTING",
  "question_type": "MEANS" | "PROGRESSION" | "CORRELATION" | "IMPACT" | "OBJECTIVE" | "OTHER",
  "relevant_evidence_ids": ["S1", "S3"],
  "epistemic_state": "SUPPORTED" | "UNESTABLISHED" | "CONTRADICTED",
  "missing_information": [
    "description of missing information if insufficient"
  ]
}
```

### Definitions:
- **`SUFFICIENT`**: Context contains enough facts to answer the question at the required level.
- **`INSUFFICIENT`**: Conclusion cannot be established from the supplied context.
- **`CONFLICTING`**: Supplied facts provide contradictory information.
- **`SUPPORTED`**: The requested conclusion is established by the context.
- **`UNESTABLISHED`**: The context neither establishes nor disproves the claim (distinct from contradicted).
- **`CONTRADICTED`**: The claim is directly contradicted by the context.

---

## 4. Benchmark Composition

The pilot benchmark (`benchmark.json`) contains **33 instances** across **7 base cybersecurity scenarios**:

| Base Case | Domain / Scenario | Question Category | Perturbations |
| :--- | :--- | :--- | :--- |
| **Case 01** | PowerShell egress connection without volume log | `IMPACT` | C0 (Orig), C1 (Removed), C2 (Contradiction), C3 (Distractor), C4 (Reorder) |
| **Case 02** | SIEM 850 MB egress vs Firewall TCP RST 0-byte log | `IMPACT` | C0 (Conflict Orig), C1 (Removed), C2 (Contradiction Agree), C3 (Distractor) |
| **Case 03** | Malicious binary on WS-04 vs Server-02 utility | `CORRELATION` | C0 (Orig), C1 (Removed), C2 (Contradiction), C3 (Distractor), C4 (Reorder) |
| **Case 04** | Web CVE exploitation followed by web shell placement | `MEANS` | C0 (Orig), C1 (Removed), C2 (Contradiction), C3 (Distractor), C4 (Reorder) |
| **Case 05** | Database server compromise & subnet discovery scan | `PROGRESSION` | C0 (Orig), C1 (Removed), C2 (Contradiction), C3 (Distractor), C4 (Reorder) |
| **Case 06** | Screen capture & system discovery commands | `OBJECTIVE` | C0 (Orig), C1 (Removed), C2 (Contradiction), C3 (Distractor), C4 (Reorder) |
| **Case 07** | Scheduled task persistence registration | `MEANS` | C0 (Orig), C1 (Removed), C2 (Contradiction), C3 (Distractor) |

### Perturbation Types:
- **`C0 — ORIGINAL`**: All evidence present $\to$ supported conclusion.
- **`C1 — EVIDENCE REMOVED`**: Key fact omitted $\to$ `INSUFFICIENT` / `UNESTABLISHED`.
- **`C2 — CONTRADICTION`**: Explicitly contradicting evidence $\to$ `CONFLICTING` / `CONTRADICTED`.
- **`C3 — DISTRACTOR`**: Plausible unrelated host/network activity added $\to$ conclusion unchanged.
- **`C4 — REORDER`**: Sentence order permuted $\to$ conclusion unchanged.

---

## 5. Usage & CLI Commands

### 1. Dry Run (No API Calls, Validates Pipeline & Schemas)
```bash
python -m research.attribute_first_pilot.runner --dry-run
```

### 2. Smoke Test (2 Items Live API)
```bash
python -m research.attribute_first_pilot.runner --limit 2
```

### 3. Full Benchmark Execution (33 items $\times$ 4 calls = 132 model calls)
```bash
python -m research.attribute_first_pilot.runner --model meta-llama/llama-3.1-8b-instruct
```

### 4. Evaluation & Summary Report Generation
```bash
python -m research.attribute_first_pilot.evaluator --results research/attribute_first_pilot/results/<run_file>.json
```

### 5. Manual Scoring Flow
After running, answers are automatically exported to `manual_scoring.csv` for blind human scoring:
- `correctness` (0 = incorrect, 1 = partially correct, 2 = correct)
- `context_grounding` (0 = ungrounded / hallucinated, 1 = minor issues, 2 = fully grounded)
- `uncertainty_handling` (0 = overconfident / ignored conflict, 1 = partially preserved, 2 = correctly preserved)

Once scored, re-run `evaluator.py` with `--manual-csv research/attribute_first_pilot/manual_scoring.csv`.
