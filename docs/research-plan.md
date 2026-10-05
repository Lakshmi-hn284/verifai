# VERIFAI — Research Evaluation & Experimental Methodology Plan

## 1. Research Objectives & Questions

VERIFAI is designed as a research-grade prototype to systematically evaluate key hypotheses in privacy-preserving document intelligence, evidence-based reasoning, and selective disclosure.

### Research Questions (RQs)
- **RQ1**: Does multimodal document understanding improve structured credential extraction precision and recall compared with traditional OCR-only processing?
- **RQ2**: Does evidence-graph reasoning improve the explainability and user auditability of eligibility decisions?
- **RQ3**: Can minimum-disclosure policy engines reliably reduce unnecessary personal attribute exposure without impacting application validity?
- **RQ4**: Does hybrid (deterministic rules + vector semantic search + evidence graph) reasoning reduce eligibility false-positive and false-negative rates compared with LLM-only freeform reasoning?
- **RQ5**: Can permission-controlled subagent architectures safely automate multi-step credential application workflows without prompt-injection vulnerabilities?

---

## 2. Experimental Framework & Evaluation Metrics

### 2.1 Document Extraction Benchmark
- **Dataset**: Synthetic & benchmark academic transcripts, course certificates, identity docs, marksheets (50+ test documents).
- **Metrics**:
  - Field Extraction Precision: $P = \frac{TP}{TP + FP}$
  - Field Extraction Recall: $R = \frac{TP}{TP + FN}$
  - Field-Level Accuracy & Micro/Macro $F_1$ Score.
  - Bounding region IoU (Intersection over Union) for visual evidence grounding.

### 2.2 Requirement Extraction Benchmark
- **Dataset**: 30 diverse real-world / synthetic job descriptions, scholarship guidelines, and university entry criteria.
- **Metrics**: Precision, Recall, $F_1$ score on extracted conditions (e.g. minimum CGPA, specific degree, skill tags, experience years).

### 2.3 Eligibility Engine Accuracy & Robustness
- **Comparative Baseline**: LLM-only prompt vs Deterministic Rules vs VERIFAI Hybrid Engine.
- **Metrics**:
  - Eligibility Classification Accuracy.
  - False Positive Rate (FPR) & False Negative Rate (FNR).
  - Explanation Quality Score (rated on Groundedness, Traceability, Clarity).

### 2.4 Privacy & Data Minimization Impact
- **Metric**: Disclosure Reduction Percentage ($DRP$)
  $$DRP = \left( 1 - \frac{\text{Attributes Disclosed}}{\text{Total Attributes in Vault}} \right) \times 100\%$$
- Measuring unnecessary field exposure across 50 test application scenarios.

---

## 3. Evaluation Module Pipeline Architecture

```
[Synthetic Document Suite / Test Datasets]
                  |
                  v
       +--------------------+
       |  VERIFAI Evaluator |
       +---------+----------+
                 |
  +--------------+--------------+
  |                             |
  v                             v
[Extraction Benchmarking]    [Eligibility Engine Benchmarking]
  - Precision / Recall         - Hybrid vs LLM-only Accuracy
  - Field accuracy             - False Positive / Negative Rate
  - Layout grounding IoU       - Privacy Reduction % (DRP)
```
