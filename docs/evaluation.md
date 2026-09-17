# Evaluation

This document details the evaluation methodology and results for the SupportLens pipeline components.

## Evaluation Pipeline Diagram

```mermaid
flowchart LR
    A[AppleSupport Dataset] --> B[Clean Support Cases]
    B --> C[Golden Set]
    C --> D[Intent Evaluation]

    C --> E[Human Evaluation]
    E --> F[Reply Quality]
    E --> G[Escalation]

    B --> H[BM25 Retrieval]
    H --> I[Recall@K / MRR]
```

## Dataset and Baselines

- **Golden Set**: 200 manually labelled examples.
- **Human Evaluation Set**: 50 manually labelled cases.

**Note**: The baseline split differs from the current 50-case human evaluation set. The current classifier and escalation results are based on the 50-case set, which was also used during development.

### Intent Baselines
| System                             | Accuracy | Macro F1 |
|------------------------------------|----------|----------|
| Majority baseline                  | 37.50%   | 0.0496   |
| Keyword baseline                   | 60.00%   | 0.5103   |
| TF-IDF + Logistic Regression       | 40.00%   | 0.2167   |

## Current System Performance

### Intent Classification
| Metric | Result |
|--------|--------|
| Accuracy | 76.00% |
| Macro F1 | 0.7899 |

*Evaluated on the 50-case development/human-evaluation set.*

### Retrieval
| Metric | Result |
|--------|--------|
| Recall@1 | 50.00% |
| Recall@3 | 78.00% |
| Recall@5 | 82.00% |
| MRR | 0.6367 |

*Important: These are intent-agreement proxy metrics, not manually judged retrieval relevance metrics. The evaluation is leakage-safe (the query's own conversation is removed to prevent data leakage).*

### Reply Generation
Human evaluation over 50 cases:
| Rating | Count | Percentage |
|--------|-------|------------|
| Good | 15/50 | 30.00% |
| Acceptable | 31/50 | 62.00% |
| Bad | 4/50 | 8.00% |

**Acceptable-or-better: 92.00% (46/50)**

### Escalation
| Metric | Result |
|--------|--------|
| Accuracy | 84.00% |
| ESCALATE Precision | 1.0000 |
| ESCALATE Recall | 0.8298 |

*Evaluated on the 50-case development/human-evaluation set.*

## LLM-as-Judge Limitation
An LLM-as-judge evaluation was attempted using OpenRouter free models. The judge rubric was later improved to align with human evaluation criteria. However, re-running all 50 cases after the rubric change was blocked by the external provider's free-tier daily request quota. Stale pre-refinement judge outputs were therefore excluded from the reported headline metrics.
