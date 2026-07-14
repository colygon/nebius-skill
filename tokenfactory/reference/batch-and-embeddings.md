# Batch API & Embeddings

Both are OpenAI-shaped on Token Factory.

## Embeddings (RAG over schema docs / glossary)

Useful for retrieving the right table/column or business-term definition before your agent
queries a wide enterprise schema — improves accuracy.

```python
from openai import OpenAI
import os

client = OpenAI(base_url=os.environ["NEBIUS_BASE_URL"], api_key=os.environ["NEBIUS_API_KEY"])

emb = client.embeddings.create(
    model="BAAI/bge-en-icl",      # confirm an available embedding model from /models
    input=["orders table: one row per purchase", "users table: customer profile"],
)
vectors = [d.embedding for d in emb.data]
```

Pattern: embed your schema descriptions / glossary once, store in any vector store
(FAISS, Chroma, in-memory), then retrieve the top-k relevant snippets to include in the
prompt before the model queries your data tools.

## Batch API (evaluations)

Run many prompts asynchronously at lower cost — handy for evaluating your agent across all the
benchmark questions, or scoring many candidate SQL outputs.

Typical flow (OpenAI-compatible Batch):

1. Build a JSONL file, one request per line:
   ```json
   {"custom_id": "q1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "nvidia/nemotron-3-super-120b-a12b", "messages": [{"role": "user", "content": "..."}]}}
   ```
2. Upload the file and create a batch:
   ```python
   f = client.files.create(file=open("requests.jsonl", "rb"), purpose="batch")
   batch = client.batches.create(
       input_file_id=f.id, endpoint="/v1/chat/completions", completion_window="24h")
   ```
3. Poll `client.batches.retrieve(batch.id)` until complete, then download the output file.

> Confirm Batch availability and limits in your dashboard; if unavailable, fall back to a bounded
> concurrency loop (e.g. `asyncio` + a semaphore) against `/chat/completions`.
