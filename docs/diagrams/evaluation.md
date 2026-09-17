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
