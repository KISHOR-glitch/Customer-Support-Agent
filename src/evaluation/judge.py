import os
import json
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def judge_case(case):

    prompt = f"""
You are an evaluator for an AI customer-support agent.

Your job is to independently evaluate:
1. The quality of the generated reply.
2. Whether the case should be AUTO-HANDLE or ESCALATE.

Do NOT simply approve a case because historical evidence exists.

==================================================
CUSTOMER MESSAGE
==================================================

{case["customer_message"]}


==================================================
PREDICTED INTENT
==================================================

{case["predicted_intent"]}


==================================================
GENERATED REPLY
==================================================

{case["reply"]}


==================================================
HISTORICAL EVIDENCE
==================================================

{json.dumps(case["retrieved_cases"], indent=2)}


==================================================
REPLY QUALITY RUBRIC
==================================================

GOOD:
- Directly addresses the customer's problem.
- Relevant to the predicted intent.
- Grounded in the historical support evidence.
- Does not invent unsupported facts or procedures.
- Professional and useful.
- Gives an appropriate next step when possible.

ACCEPTABLE:
- Generally relevant and safe.
- Partially addresses the problem.
- May be incomplete or somewhat generic.
- Does not contain a major unsupported or misleading claim.

BAD:
- Irrelevant to the customer's problem.
- Contradicts the historical evidence.
- Invents unsupported troubleshooting steps.
- Gives unsafe or misleading advice.
- Fails to address the actual request.

==================================================
ESCALATION RUBRIC
==================================================

Choose ESCALATE when ANY of the following applies:

1. SAFETY / HARDWARE RISK
Examples:
- fire
- smoke
- burning
- overheating
- electric shock
- swollen device
- serious charging failure
- hardware that may be unsafe

2. DATA LOSS
Examples:
- lost photos
- missing photos
- disappearing texts/messages
- lost data
- missing songs/data
- failed restore or backup involving potentially lost data

3. ACCOUNT / AUTHENTICATION ACCESS
Examples:
- cannot access an account
- locked out
- sign-in problems
- Apple ID access
- password/access problems
- two-factor authentication problems
- factory-reset account recovery

4. REPEATED OR PERSISTENT FAILURE
Examples:
- keeps crashing
- constantly crashes
- keeps restarting
- repeatedly freezes
- happens again
- happens constantly
- recurring problem
- problem returns after reboot

5. FEATURE REQUEST
Examples:
- asking Apple to add a feature
- requesting new functionality
- asking whether a feature can be added

6. SOFTWARE UPDATE REGRESSION
Examples:
- problem started after an iOS update
- update caused the problem
- new update introduced a bug
- device behavior changed after updating

7. MULTIPLE SIGNIFICANT SYMPTOMS
If the customer reports several distinct technical symptoms in one message,
prefer ESCALATE because the case may require investigation.

8. CASE-SPECIFIC / UNCERTAIN REQUEST
Choose ESCALATE when the customer asks about a product behavior that
cannot be confidently resolved from the supplied historical evidence.

==================================================
AUTO-HANDLE RULE
==================================================

Choose AUTO-HANDLE ONLY when:

- The intent is clearly understood.
- Historical evidence directly supports the response.
- The issue is routine and low-risk.
- There is no safety concern.
- There is no potential data loss.
- There is no account-access problem.
- There is no repeated/persistent failure.
- There is no feature request.
- There is no clear update regression.
- The reply can safely provide useful guidance without human investigation.

IMPORTANT:

Historical retrieval alone is NOT sufficient for AUTO-HANDLE.

If there is meaningful uncertainty between AUTO-HANDLE and ESCALATE,
choose ESCALATE.

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Use exactly these values:

{{
    "reply_quality": "GOOD | ACCEPTABLE | BAD",
    "escalation": "AUTO-HANDLE | ESCALATE",
    "reason": "short explanation based on the rubric"
}}

Do not include markdown.
Do not include additional fields.
"""

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    text = response.choices[0].message.content.strip()

    # Remove markdown fences if the model adds them
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)