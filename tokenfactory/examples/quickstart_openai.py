"""Minimal Token Factory call via the OpenAI SDK.

Setup:
    pip install openai
    export NEBIUS_API_KEY="your-key"
    export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"  # confirm in dashboard
Run:
    python quickstart_openai.py
"""
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1"),
    api_key=os.environ["NEBIUS_API_KEY"],
)

MODEL = "nvidia/nemotron-3-super-120b-a12b"

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a concise data analyst."},
        {"role": "user", "content": "In one sentence, what is a yield excursion?"},
    ],
    temperature=0.2,
)
print(resp.choices[0].message.content)
