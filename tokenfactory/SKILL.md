---
name: tokenfactory
description: >-
  Use Nebius Token Factory for LLM inference at Nebius-sponsored hackathons and
  events. Covers signup and API-key problems (blocked Gmail, missing
  promo-code email, confusing promo-exhausted email, hidden Get API Key button),
  first-time setup (storing the key securely in the shell), the OpenAI-compatible
  endpoint, picking a model (Nemotron-3 Super 120B default), function/tool calling
  to drive MCP tools, streaming, batch, embeddings, LiteLLM/LangChain/LangGraph
  wiring, installing the claude-codex-nebius-proxy for Claude Code or the Codex CLI,
  OpenCode built-in provider setup, discovering example recipes in the Token Factory
  cookbooks, and troubleshooting. Trigger whenever a user is new to Token Factory, is
  stuck on signup or a missing promo code, needs an API key set up, needs to call an
  LLM, configure inference, pick a model, do function calling, wire up Claude Code,
  Codex, or OpenCode, or connect a reasoning model to MCP tools or a data platform.
---

# Nebius Token Factory — Skill

Token Factory is Nebius's managed inference platform. It serves open models behind an
**OpenAI-compatible API**, so any agent framework that speaks OpenAI (or has a Nebius/OpenAI
provider) can use it by changing three things: **base URL**, **API key**, and **model name**.

The core agent pattern:

> **Your model on Token Factory does the reasoning and tool-calling → your tools (often an MCP server) do the real work.**

Your agent calls a Token Factory model; the model emits **tool calls**; your code dispatches
those to your tools — local functions, APIs, or an MCP server's tools — and feeds results
back. See `reference/function-calling.md` and `reference/mcp-integration.md`.

**Helping a beginner ("vibe coder")?** Assume no terminal fluency. Give **one copy-paste
block at a time** and verify it worked before moving on (e.g. `echo $NEBIUS_API_KEY` after
the export, the §1 curl after that). Don't assume they know what an environment variable or
a base URL is — say what each step does in one plain sentence. Reassure them: only three
things ever change vs. plain OpenAI — **base URL, API key, model name**.

## 1. Get access (do this first)

New to Token Factory? It's three steps: **get a key → store it securely → make one test call.**
If the user doesn't have a key yet, walk them through this section before anything else.

> **Signup not going smoothly?** (form won't load, Gmail rejected, no promo-code email,
> a confusing "promo code exhausted" email, can't find the Get API Key button) —
> every known signup gotcha and its workaround is in `reference/signup-help.md`.

1. Claim credits at **https://dev.nebius.com/builders** (apply early — approval can lag).
2. Log in to the Token Factory console — **https://tokenfactory.nebius.com/** — and
   create/copy your **API key**.
3. Store it as an environment variable — **never hardcode it in source code, never commit it**:

   ```bash
   # Add an environment variable for your API key to store it locally.
   # Copy-paste this into your terminal and insert your API key:
   export NEBIUS_API_KEY="your-key-here"
   export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"

   # Persist across sessions:
   echo 'export NEBIUS_API_KEY="your-key-here"' >> ~/.zshrc    # macOS (default shell: zsh)
   echo 'export NEBIUS_API_KEY="your-key-here"' >> ~/.bashrc   # Linux (bash)
   # Then open a new terminal, or reload now: source ~/.zshrc  (or: source ~/.bashrc)
   ```

   Per-project alternative: `cp .env.example .env` and fill in the key — `.env` is gitignored here.

4. Verify it works (should print a JSON list of models):

   ```bash
   curl -s "$NEBIUS_BASE_URL/models" -H "Authorization: Bearer $NEBIUS_API_KEY" | head
   ```

   If it errors, see `reference/troubleshooting.md` (401 = key/credits issue, connection error = base URL).

**Key safety:** treat the key like a password. Don't paste it into chats, issues, or shared docs;
don't commit it (this repo's `.gitignore` already excludes `.env`); if it leaks, revoke it in the
dashboard and create a new one.

> If a helper wants `OPENAI_API_KEY` / `OPENAI_BASE_URL` (many do), set those to the Nebius values.

## 2. First call (OpenAI SDK)

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url=os.environ["NEBIUS_BASE_URL"],
    api_key=os.environ["NEBIUS_API_KEY"],
)

resp = client.chat.completions.create(
    model="nvidia/nemotron-3-super-120b-a12b",   # recommended for agentic tool use
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
)
print(resp.choices[0].message.content)
```

That's the whole integration surface. Everything else — streaming, tools, batch,
embeddings — is standard OpenAI-shaped and documented in `reference/api.md`.

## 3. Which model?

**New to this? Don't agonize — use the default below and move on; you can switch any time**
(it's just the `model` string). To see everything available on your account:
`curl -s "$NEBIUS_BASE_URL/models" -H "Authorization: Bearer $NEBIUS_API_KEY"`.

- **Default for agents / tool use:** `nvidia/nemotron-3-super-120b-a12b`
  (Nemotron-3 Super 120B, ~12B active, 1M context, **native function calling**).
- Token Factory hosts many open models (Llama, Qwen, DeepSeek, Kimi, etc.). Pick the smallest
  model that reliably tool-calls for your loop; scale up only if reasoning quality needs it.
- Full guidance + model IDs: `reference/models.md`.

## 4. Function calling → your tools

The whole game is: model proposes a tool call → you run the tool → return the result.
Minimal loop: `reference/function-calling.md` and `examples/function_calling.py`.
Tools on an MCP server: `reference/mcp-integration.md` and `examples/langgraph_mcp_agent.py`.

## 5. Identify the user's stack, then wire it

Before giving setup instructions, figure out which of these the user is on — ask if it isn't
obvious from context ("Are you writing your own agent in Python/JS, or using Claude Code,
the Codex CLI, or OpenCode?"). The setup differs:

| Stack | Wiring |
|---|---|
| **Own agent — OpenAI SDK (Python/JS)** | No proxy needed. Set `base_url` + `api_key` from the env vars in §1 (snippet in §2). |
| **Own agent — LiteLLM** | `model="nebius/nvidia/nemotron-3-super-120b-a12b"`, reads `NEBIUS_API_KEY` from env. |
| **Own agent — LangChain / LangGraph** | `ChatOpenAI(base_url=..., api_key=..., model=...)`. |
| **Claude Code** | Claude Code speaks Anthropic's `/v1/messages`, not OpenAI — route through a local proxy. Install walkthrough: `reference/proxy-setup.md`; quick reference: `reference/api.md` → "CLI routing". |
| **Codex CLI** | Same proxy, plus `~/.codex/config.toml` with `wire_api = "responses"`. Install walkthrough: `reference/proxy-setup.md`. |
| **OpenCode** | **No proxy needed** — Nebius Token Factory is a built-in provider: run `/connect`, search "Nebius Token Factory", paste the key, then `/models` to pick one. Details: `reference/api.md` → "OpenCode". |

**Secure key handling on every path:** the key lives in the `NEBIUS_API_KEY` environment
variable (§1). CLI configs should reference it via `env_key` (Codex) or the proxy's environment —
never paste the raw key into a config file, script, or repo.

Copy-paste snippets for each: `reference/api.md`. Runnable examples: `examples/`.

## 6. Find working examples (don't build from scratch)

Before writing anything from first principles, check the cookbooks — ~50 MIT-licensed
recipes (agents on 7 frameworks, RAG, tool calling, integrations) that are usually two
minutes from "adapt this":

- **Browse without cloning:** https://opencolin.github.io/nebius-ecosystem-cookbook/cookbook/
  — every recipe rendered, notebooks with outputs visible, filter/search.
- **Clone and run:** https://github.com/nebius/token-factory-cookbook

Task-to-recipe map and more resources: `reference/cookbooks.md`.

## 7. When stuck — run the checklist

If a user is stuck and it's unclear where, walk this in order — each step verifies the one
before it. Stop at the first "no" and fix there:

1. **Signed up?** With a non-Gmail address, promo code in hand → `reference/signup-help.md`
2. **Right email?** The Token Factory "here's your code" email — not the AI Cloud
   "exhausted" one → `reference/signup-help.md`
3. **Key copied?** From the dashboard (widen the window if the button is missing) → §1
4. **Key stored?** `echo $NEBIUS_API_KEY` prints it, and it's persisted in the shell
   profile → §1
5. **Key works?** `curl -s "$NEBIUS_BASE_URL/models" -H "Authorization: Bearer
   $NEBIUS_API_KEY"` returns a model list → §1; errors → `reference/troubleshooting.md`
6. **Tool wired?** Own agent → §2; Claude Code / Codex → `reference/proxy-setup.md`;
   OpenCode → `reference/api.md` § OpenCode
7. **First call succeeded?** If yes, stop debugging setup — start from a cookbook recipe
   (`reference/cookbooks.md`) instead of a blank file.

For specific errors (401, model-not-found, rate limits, tool-call JSON, context length):
`reference/troubleshooting.md`.

## Reference map

| File | What's in it |
|------|--------------|
| `reference/signup-help.md` | Signup gotchas & workarounds: Gmail block, flaky form, promo emails, hidden key button |
| `reference/api.md` | Endpoints, auth, streaming, curl/Python/JS, LiteLLM, LangChain, OpenCode, CLI routing |
| `reference/models.md` | Recommended models, IDs, when to use which |
| `reference/function-calling.md` | Tool-calling loop, schema format, dispatching to your tools |
| `reference/batch-and-embeddings.md` | Batch API (evals) and embeddings (RAG over schema docs) |
| `reference/mcp-integration.md` | Driving MCP-server tools from a Token Factory model, end to end |
| `reference/proxy-setup.md` | Install claude-codex-nebius-proxy: TUI installer, agent-driven non-interactive install, Claude Code + Codex wiring |
| `reference/cookbooks.md` | Discover examples: cookbook task-to-recipe map, browsable mirror, awesome-nebius |
| `reference/troubleshooting.md` | Common errors and fixes |
| `examples/` | Runnable Python: quickstart, LiteLLM, function calling, LangGraph+MCP |

## Related resources

- **Token Factory Cookbook** — 50 recipes / 27 notebooks: https://github.com/nebius/token-factory-cookbook
- **Browsable cookbook mirror** (rendered notebooks + search): https://opencolin.github.io/nebius-ecosystem-cookbook/cookbook/
- **awesome-nebius** — curated Nebius resources: https://github.com/opencolin/awesome-nebius
- **Claude Code / Codex → Nebius proxy** — https://github.com/KiranChilledOut/claude-codex-nebius-proxy
- **openclaw-nebius-plugin** — https://github.com/opencolin/openclaw-nebius-plugin
