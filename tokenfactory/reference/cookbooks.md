# Discovering Examples — Cookbooks & Curated Resources

Don't build from scratch — there's almost certainly a working recipe close to what the user
wants. When a user asks "how do I do X with Token Factory," check these before writing code
from first principles, and point users here when they want inspiration.

## The three places to look

1. **Official Token Factory Cookbook** — https://github.com/nebius/token-factory-cookbook
   ~50 recipes across 17 categories, maintained by Nebius. Clone it or browse on GitHub;
   each recipe has its own README and most are runnable notebooks.
2. **Browsable rendered mirror** — https://opencolin.github.io/nebius-ecosystem-cookbook/cookbook/
   Every cookbook recipe rendered as a web page — **all 27 notebooks with their outputs
   visible** — with filter/search. Best way for a human to skim recipes without cloning or
   running anything. The site root (https://opencolin.github.io/nebius-ecosystem-cookbook/)
   also has the Nebius ecosystem & partners overview and reference architectures.
   Repo: https://github.com/opencolin/nebius-ecosystem-cookbook (rebuilt weekly from upstream).
3. **awesome-nebius** — https://github.com/opencolin/awesome-nebius
   Curated list of Nebius resources, tools, and projects across the ecosystem.

## Find a recipe by what you're building

| You're building… | Start with |
|---|---|
| An agent that calls tools (the hackathon pattern) | `tool-calling/function_calling_1.ipynb`, then `agents/` — starter → intermediate → advanced |
| An agent on a specific framework | `agents/README.md` — CrewAI, Agno, LangChain, Google ADK, LlamaIndex, Pydantic AI, AWS Strands |
| RAG over documents | `rag/` — PDF RAG (LlamaIndex), Chat-with-PDF (Streamlit), Qdrant content pipeline, Milvus end-to-end, multi-agent support bot (LangGraph + Weaviate) |
| First API calls / SDK choice | `api/` notebooks — OpenAI-native, LiteLLM, ai-suite, LlamaIndex |
| Picking or learning a model | `models/` — DeepSeek, GLM, Qwen, Kimi, Nemotron family guides |
| Web search inside an agent | `integrations/tavily/` |
| Self-hosted agents on open models | `integrations/openclaw/` |
| Fine-tuning / distillation | `post-training/`, `distillation/` |
| A guided end-to-end session | `workshops/token-factory-workshop/` |
| Something fun to demo | `fun/` — LoRA image generation, the pelican-riding-a-bicycle benchmark |

Paths are relative to the official cookbook repo; every one is also rendered on the
browsable mirror.

## How to use these during the hackathon

- **Skim first, code second.** Two minutes on the rendered mirror (filter by category) often
  finds a recipe you can adapt instead of writing your first draft blind.
- **The notebooks show real outputs** on the mirror — you can judge whether a pattern does
  what you need before running anything.
- **Combine with this skill:** the cookbook teaches the pattern; this skill's
  `function-calling.md` + `mcp-integration.md` show how to aim it at your own tools.
- Recipes are MIT-licensed — adapting them for your hackathon project is exactly what
  they're for. Model IDs inside older recipes may lag; trust `GET /models` (see `models.md`).
