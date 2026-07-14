# Models on Token Factory

Token Factory serves many open-weight models behind the OpenAI-compatible API. Query the live
list any time:

```bash
curl "$NEBIUS_BASE_URL/models" -H "Authorization: Bearer $NEBIUS_API_KEY"
```

## Recommended for the hackathon

| Use case | Model ID | Why |
|---|---|---|
| **Agentic tool use (default)** | `nvidia/nemotron-3-super-120b-a12b` | Nemotron-3 Super 120B, ~12B active, **1M context**, **native function calling**. Best all-round for agent loops that call MCP tools. |
| Long-context reasoning | `nvidia/nemotron-3-super-120b-a12b` | 1M context handles big schemas + long tool transcripts. |
| Fast / cheap drafting | a smaller instruct model from `/models` (e.g. a Llama/Qwen 8–30B) | Use for cheap sub-steps; keep the 120B for the reasoning that matters. |
| Alternative strong model | `moonshotai/Kimi-K2.6` | Strong general model available on Token Factory (seen in the proxy defaults). |

> Model IDs and casing can change — always trust the `/models` endpoint and the hackathon guide
> over any hardcoded string.

## Choosing a model

1. **Start with `nvidia/nemotron-3-super-120b-a12b`.** It tool-calls reliably and has the context
   headroom for enterprise schemas.
2. **Only downshift** to a smaller model for high-frequency, low-stakes calls (classification,
   short summaries) to save latency/credits.
3. **Match capability to the task:** function calling and long context are the two things your
   agent depends on — verify any alternate model supports both before switching.

## Capabilities cheat-sheet (Nemotron-3 Super 120B)

- Parameters: 120B total, ~12B active (MoE-style efficiency).
- Context window: ~1M tokens.
- Native function/tool calling (OpenAI `tools` format).
- Served OpenAI-compatible: works with OpenAI SDK, LiteLLM, LangChain `ChatOpenAI`.

## Embeddings

Token Factory also serves embedding models via `/embeddings` (OpenAI-shaped) — useful for RAG
over schema docs and business glossaries. See `batch-and-embeddings.md`.
