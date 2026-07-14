# Installing the Claude/Codex → Token Factory Proxy

Claude Code and the Codex CLI don't speak OpenAI's wire format, so they can't hit Token
Factory directly. **claude-codex-nebius-proxy** is a local bridge that translates both —
Claude's `/v1/messages` and Codex's `/v1/responses` — into OpenAI-compatible calls to Nebius.

Repo: https://github.com/opencolin/claude-codex-nebius-proxy

If you're helping a user set this up, walk them through Prerequisites → Install (TUI path
first) → the section for whichever CLI they use.

## Prerequisites

- **Python 3.9+** (`python3 --version`)
- **A Nebius API key** — if the user doesn't have one, do SKILL.md §1 first
- Claude Code and/or Codex CLI installed
- Optional: a Tavily API key (enables server-side web search through the proxy)

> The proxy reads the Nebius key from **`OPENAI_API_KEY`** (it forwards it to the backend).
> If you followed SKILL.md §1 you have `NEBIUS_API_KEY` — just mirror it:
> ```bash
> export OPENAI_API_KEY="$NEBIUS_API_KEY"
> ```

## Install — the easy way (TUI installer)

```bash
git clone https://github.com/opencolin/claude-codex-nebius-proxy.git
cd claude-codex-nebius-proxy
./install.sh
```

The installer is a step-by-step TUI that checks prerequisites, creates a venv, installs
dependencies, **tests your Nebius API key**, lets you pick models from live dropdowns,
writes the `.env` file, runs a smoke test, and can optionally add `claude` / `claudius`
shell shortcuts and a Claude Code statusline.

After it finishes, start the proxy:

```bash
claudius                          # if you added the shell shortcuts
# OR
.venv/bin/python start_proxy.py   # from the proxy directory
```

Sanity check: open **http://localhost:8083/dashboard** — the observability dashboard
(usage, latency, cost, model routing) means the proxy is up.

## Install — manual (no TUI)

```bash
git clone https://github.com/opencolin/claude-codex-nebius-proxy.git
cd claude-codex-nebius-proxy
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env    # edit: set OPENAI_API_KEY (your Nebius key), BIG_MODEL, etc.
.venv/bin/python start_proxy.py
```

**Key safety:** the key goes in `.env` (gitignored in the proxy repo) or the environment —
same rule as everywhere else: never commit it, never inline it in scripts.

## Use with Claude Code

With the proxy running:

```bash
ANTHROPIC_BASE_URL=http://localhost:8083 ANTHROPIC_AUTH_TOKEN=claude-local claude
```

(`claude-local` is a placeholder token the proxy accepts — your real Nebius key stays in the
proxy's environment, and Claude Code never sees it.) If the installer added shortcuts,
`claude --proxy` or `claudius` does this for you.

## Use with Codex CLI

Edit `~/.codex/config.toml` (macOS/Linux) or `%APPDATA%\codex\config.toml` (Windows):

```toml
model = "nebius/moonshotai/Kimi-K2.6"
model_provider = "nebius"

[model_providers.nebius]
name = "Nebius Proxy"
base_url = "http://127.0.0.1:8083/v1"
env_key = "OPENAI_API_KEY"
wire_api = "responses"
```

Then make sure the key env var is set (`export OPENAI_API_KEY="$NEBIUS_API_KEY"`) and run
`codex` from your project. Note `env_key` — the config references the variable *name*, never
the key itself.

**Codex Desktop App (macOS):** the GUI doesn't inherit shell exports. Set the key via
launchd before launching:

```bash
launchctl setenv OPENAI_API_KEY "$NEBIUS_API_KEY"
open -a "Codex"
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `./install.sh` fails on prerequisites | Check `python3 --version` ≥ 3.9; install Python via your package manager. |
| Key test fails in the installer | Same causes as any 401 — see `troubleshooting.md` (key not approved, typo, credits pending). |
| CLI can't connect to `localhost:8083` | Proxy not running — start it (`claudius` or `.venv/bin/python start_proxy.py`) and confirm the dashboard loads. |
| Codex ignores the proxy | Check `~/.codex/config.toml` matches the block above and `OPENAI_API_KEY` is set in the shell that launches `codex`. |
| Deeper issues | The proxy repo's `docs/` folder: `docs/MANUAL_SETUP.md`, `docs/README.md`. |

## Lighter alternatives

If you only use Claude Code and want less to run: **claude-code-router**
(https://github.com/musistudio/claude-code-router) or the **LiteLLM proxy**'s Anthropic
surface. This proxy is the batteries-included option: both CLIs, web search via Tavily,
tool-call JSON repair, context auto-truncation, and the cost dashboard.
