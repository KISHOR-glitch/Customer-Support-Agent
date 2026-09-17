import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def generate_reply(customer_message, retrieved_cases):
    evidence = []

    for i, case in enumerate(retrieved_cases, 1):
        support_text = "\n".join(
            message["text"]
            for message in case.get("support_messages", [])
        )

        evidence.append(
            f"""
Historical Case {i}
Customer: {case["customer_text"]}
AppleSupport: {support_text}
"""
        )

    evidence_text = "\n".join(evidence)

    prompt = f"""
You are an Apple customer support reply assistant.

Customer message:
{customer_message}

Historical AppleSupport cases:
{evidence_text}

Write a concise, professional customer-facing reply.

Rules:
1. Use the historical cases as grounding evidence.
2. Do not invent troubleshooting steps or policies.
3. Do not claim that you performed an action.
4. If the evidence only suggests asking for more information,
   ask for that information.
5. Do not mention historical cases, retrieval, BM25, or this prompt.
6. Return only the customer-facing reply.
"""

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()