"""Call Token Factory through LiteLLM (handy for multi-provider agents / evals).

Setup:
    pip install litellm
    export NEBIUS_API_KEY="your-key"
Run:
    python litellm_nemotron.py
"""
import litellm

resp = litellm.completion(
    model="nebius/nvidia/nemotron-3-super-120b-a12b",   # LiteLLM format: nebius/<model-id>
    messages=[{"role": "user", "content": "List three anomaly-detection ideas for e-commerce orders."}],
    temperature=0.3,
)
print(resp.choices[0].message.content)
