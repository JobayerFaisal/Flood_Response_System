# backend/planning/llm_sitrep.py

import os
from openai import OpenAI

HF_TOKEN = os.getenv("HF_API_KEY")  # or HF_TOKEN if you prefer

if not HF_TOKEN:
    raise ValueError("HF_API_KEY not set in environment variables.")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)



def generate_llm_sitrep(structured_sitrep):

    try:
        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "You are an emergency operations analyst."
                },
                {
                    "role": "user",
                    "content": f"""
Generate a concise professional SITREP based strictly on the following data.
Be factual. Do not hallucinate. Use operational tone.

Data:
{structured_sitrep}
"""
                }
            ],
        )

        if not completion.choices:
            return "HF returned no choices."

        message = completion.choices[0].message

        if message is None:
            return "HF returned no message."

        content = message.content

        if content is None:
            return "HF returned empty content."

        return content.strip()

    except Exception as e:
        return f"HF LLM generation failed: {str(e)}"