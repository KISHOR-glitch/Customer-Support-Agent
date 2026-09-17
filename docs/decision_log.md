# SupportLens Decision Log

1. **Selected AppleSupport as the target brand**
   - **Decision**: Focused the analysis and system building entirely on the AppleSupport subset of the Kaggle dataset.
   - **Reason**: AppleSupport has a high volume of tweets and a diverse range of technical support issues (hardware, software, services).
   - **Evidence/trade-off**: Provided a sufficiently large subset (106,860 tweets) from the Kaggle dataset to build a robust intent classifier and retrieval system, though it narrows the domain strictly to Apple products.

2. **Reconstructed conversations using response relationships**
   - **Decision**: Grouped individual customer and agent tweets into complete support threads.
   - **Reason**: Individual tweets lack context. Reconstructing threads allows the system to see the full customer problem and the final support resolution.
   - **Evidence/trade-off**: Initially reconstructed 102,121 threads, creating a robust historical dataset for retrieval.

3. **Cleaned low-information support cases**
   - **Decision**: Filtered out threads that did not contain actionable support problems or meaningful resolutions.
   - **Reason**: Many tweets contain only greetings, generic complaints, or follow-ups without the actual problem description.
   - **Evidence/trade-off**: Reduced the dataset to 94,362 high-quality cases, improving the quality of retrieved resolutions at the cost of some data loss.

4. **Defined an 11-intent taxonomy from observed customer messages**
   - **Decision**: Built a custom taxonomy of 11 core intents based on actual data rather than theoretical categories.
   - **Reason**: A data-driven taxonomy ensures the system handles the actual problems customers are reporting.
   - **Evidence/trade-off**: Covered the vast majority of cases while including an `other_insufficient_information` category to catch long-tail or ambiguous queries safely.

5. **Created a 200-example golden set**
   - **Decision**: Manually labelled 200 customer support cases with their true intent.
   - **Reason**: Required a high-quality, manually verified dataset for objective evaluation.
   - **Evidence/trade-off**: 200 cases is small enough to manually annotate accurately but large enough to provide a meaningful evaluation signal.

6. **Used a majority-class model as the trivial baseline**
   - **Decision**: Evaluated a model that always predicts the most frequent intent class.
   - **Reason**: Establishes the absolute minimum performance threshold.
   - **Evidence/trade-off**: Yielded 37.50% accuracy (0.0496 Macro F1), proving that the problem is not trivially solved by guessing the most frequent class.

7. **Implemented an interpretable keyword baseline**
   - **Decision**: Built a simple rule-based model relying entirely on explicitly defined keywords.
   - **Reason**: Provides a fast, deterministic baseline to understand the lexical predictability of the intents.
   - **Evidence/trade-off**: Achieved 60.00% accuracy (0.5103 Macro F1), showing that many intents have strong keyword indicators.

8. **Tested TF-IDF + Logistic Regression as a simple semantic baseline**
   - **Decision**: Evaluated a statistical machine learning approach using TF-IDF features.
   - **Reason**: Evaluates whether basic statistical machine learning can capture the nuance missed by simple keywords.
   - **Evidence/trade-off**: Achieved 40.00% accuracy (0.2167 Macro F1), indicating that sparse features without deep semantic understanding or extensive tuning struggle on this dataset.

9. **Selected BM25 for historical support-case retrieval**
   - **Decision**: Used the BM25 algorithm to fetch relevant past support threads given a new query.
   - **Reason**: BM25 provides strong, proven lexical matching which is highly effective for technical support where specific error codes and product names matter.
   - **Evidence/trade-off**: Achieved Recall@5 of 82.00% for intent-agreement, offering a solid foundation for grounding, though it may miss purely semantic matches.

10. **Used retrieved historical resolutions as grounding evidence for reply generation**
    - **Decision**: Passed the retrieved BM25 cases as context to the reply generator.
    - **Reason**: Reduces hallucinations and ensures the generated reply is based on actual, historically verified support protocols.
    - **Evidence/trade-off**: 92% of generated replies were rated Acceptable-or-better in human evaluation.

11. **Added deterministic escalation rules for safety, data loss, account issues and persistent failures**
    - **Decision**: Created an explicit policy that forces human handoff (`ESCALATE`) when specific risk factors are detected.
    - **Reason**: Certain categories carry high risk or require human authorization, making them unsuitable for automated resolution.
    - **Evidence/trade-off**: Achieved 1.0000 precision and 0.8298 recall on the ESCALATE class, prioritizing safety over maximum automation.

12. **Created a 50-case human evaluation set**
    - **Decision**: Isolated 50 cases for deep, manual, end-to-end evaluation.
    - **Reason**: Detailed manual evaluation of the full pipeline (including generation and escalation) is time-consuming.
    - **Evidence/trade-off**: Provided high-fidelity insights but, because it was also used for development, results represent a development-set evaluation rather than an unbiased production estimate.

13. **Evaluated reply quality using Good / Acceptable / Bad**
    - **Decision**: Used qualitative categories instead of automated metrics like BLEU or ROUGE to evaluate the final reply.
    - **Reason**: Standard automated generation metrics correlate poorly with perceived support quality.
    - **Evidence/trade-off**: Allowed for nuanced assessment of reply helpfulness and tone.

14. **Added LLM-as-judge evaluation but excluded stale results after rubric refinement and quota exhaustion**
    - **Decision**: Attempted automated LLM evaluation, but ultimately removed the numbers from the final report.
    - **Reason**: Aimed to scale evaluation automatically, but rubric changes necessitated a re-run which was blocked by external API quotas.
    - **Evidence/trade-off**: Chose to transparently exclude the stale results rather than report misleading numbers.

15. **Added leakage-safe retrieval evaluation by removing the query's own conversation**
    - **Decision**: Ensured the query thread itself was explicitly removed from the retrieval corpus during testing.
    - **Reason**: Evaluating retrieval on the same thread would artificially inflate metrics since the exact text might be retrieved.
    - **Evidence/trade-off**: Provides a more realistic measure of how the system will perform on novel, unseen customer queries.
