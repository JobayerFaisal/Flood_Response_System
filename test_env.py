# test_env.py

import os
from dotenv import load_dotenv

load_dotenv()

# print("USER:", os.getenv("POSTGRES_USER"))
# print("PORT:", os.getenv("POSTGRES_PORT"))

# from backend.core.settings import settings
# print("DB URL:", settings.DATABASE_URL)

import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_API_KEY"],
)

completion = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    messages=[{"role": "user", "content": "Say hello"}],
)

print(completion.choices[0].message.content)