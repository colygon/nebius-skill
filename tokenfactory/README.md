# tokenfactory-skill

Everything an agent (or a hacker) needs to use **Nebius Token Factory** for LLM inference —
built for Nebius-sponsored hackathons and events.

Token Factory serves open models behind an **OpenAI-compatible API**. Point your agent at it by
setting a **base URL**, an **API key**, and a **model name** — then let your model reason and
**call your tools** (local functions or an MCP server's) to do the real work.

> **TL;DR**
> ```bash
> export NEBIUS_API_KEY="your-key-here"          # from https://dev.nebius.com/builders
> export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"   # confirm in dashboard
>
> # Persist across sessions:
> echo 'export NEBIUS_API_KEY="your-key-here"' >> ~/.zshrc    # macOS
> echo 'export NEBIUS_API_KEY="your-key-here"' >> ~/.bashrc   # Linux
>
> # model: nvidia/nemotron-3-super-120b-a12b
> ```
>
> New to Token Factory? `SKILL.md` §1 walks you from zero (get a key, store it securely,
> verify with one curl); signup trouble → `reference/signup-help.md`. Using Claude Code or
> Codex? `reference/proxy-setup.md`. OpenCode? Built-in provider — `reference/api.md`.

## What's here

```
tokenfactory-skill/
├── SKILL.md                        # start here — the skill entry point
├── .env.example                    # env vars template (Nebius + optional MCP server)
├── reference/
│   ├── signup-help.md              # signup gotchas: Gmail block, promo emails, hidden key button
│   ├── api.md                      # endpoints, auth, curl/Python/JS, LiteLLM, LangChain, OpenCode, CLI routing
│   ├── models.md                   # recommended models + IDs (Nemotron-3 Super 120B)
│   ├── function-calling.md         # tool-calling loop → your tools
│   ├── batch-and-embeddings.md     # batch evals + embeddings for RAG
│   ├── mcp-integration.md          # MCP-server tools + Token Factory, end to end
│   ├── proxy-setup.md              # install claude-codex-nebius-proxy (Claude Code / Codex)
│   ├── cookbooks.md                # discover examples: cookbooks + task-to-recipe map
│   └── troubleshooting.md          # common errors & fixes
└── examples/
    ├── quickstart_openai.py        # first call (OpenAI SDK)
    ├── litellm_nemotron.py         # via LiteLLM
    ├── function_calling.py         # model drives your tools (manual loop)
    └── langgraph_mcp_agent.py      # LangGraph + MCP adapter (framework loop)
```

## Using it as an agent skill

Drop this folder into your agent's skills directory (or point your loader at `SKILL.md`).
The frontmatter `description` tells the agent when to use it; the body links to the reference
files on demand.

## Important links

| What | Where |
|---|---|
| **Get credits** (Builders program) | https://dev.nebius.com/builders |
| **Token Factory console** — create/copy your API key | https://tokenfactory.nebius.com/ |
| **Official docs** | https://docs.tokenfactory.nebius.com/ |
| **API base URL** (OpenAI-compatible) | `https://api.tokenfactory.nebius.com/v1` |
| **Official cookbook** (~50 recipes) | https://github.com/nebius/token-factory-cookbook |
| **Browsable cookbook mirror** — notebooks rendered with outputs, filter/search | https://opencolin.github.io/nebius-ecosystem-cookbook/cookbook/ |
| **awesome-nebius** — curated resource list | https://github.com/opencolin/awesome-nebius |
| **Claude Code / Codex → Nebius proxy** | https://github.com/KiranChilledOut/claude-codex-nebius-proxy |
| **OpenCode provider docs** (Nebius is built in — no proxy) | https://opencode.ai/docs/providers/ |
| **Live support** | your event's community Slack `#help` |

## Related (Nebius ecosystem)

- **nebius-ecosystem-cookbook** (source for the browsable mirror): https://github.com/opencolin/nebius-ecosystem-cookbook
- **openclaw-nebius-plugin**: https://github.com/opencolin/openclaw-nebius-plugin

## Notes on accuracy

Model IDs, the exact base URL, and Batch availability can change — always trust the live
`GET /models` endpoint and your event's guide over any hardcoded value in these docs.
Values marked *"confirm in dashboard"* should be verified from your Token Factory account.

## License

MIT (docs and example code). Nebius, Token Factory, and product names belong to Nebius B.V.
