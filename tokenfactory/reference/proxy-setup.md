# Installing the Claude/Codex → Token Factory Proxy

Claude Code and the Codex CLI don't speak OpenAI's wire format, so they can't hit Token
Factory directly. **claude-codex-nebius-proxy** is a local bridge that translates both —
Claude's `/v1/messages` and Codex's `/v1/responses` — into OpenAI-compatible calls to Nebius.

Repo: https://github.com/KiranChilledOut/claude-codex-nebius-proxy
(mirror: https://github.com/opencolin/claude-codex-nebius-proxy)

Two ways to get it installed:

- **User at the keyboard** → the TUI installer below (it's interactive and handles everything).
- **Agent doing the setup for the user** → the "Agent-driven install" section: a fully
  non-interactive path you can run end to end with shell commands.

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
git clone https://github.com/KiranChilledOut/claude-codex-nebius-proxy.git
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
git clone https://github.com/KiranChilledOut/claude-codex-nebius-proxy.git
cd claude-codex-nebius-proxy
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env    # edit: set OPENAI_API_KEY (your Nebius key), BIG_MODEL, etc.
.venv/bin/python start_proxy.py
```

## Agent-driven install (set it up for the user, no TUI)

If you're an agent installing the proxy on the user's machine, don't launch `./install.sh`
(it's an interactive TUI). Run the manual steps yourself, one at a time, verifying each:

```bash
# 0. Preconditions — stop and fix these first if either fails:
python3 -c 'import sys; assert sys.version_info >= (3, 9), sys.version'   # Python 3.9+
test -n "$NEBIUS_API_KEY" || echo "NEBIUS_API_KEY not set — do SKILL.md §1 first"

# 1. Clone + install into a venv
git clone https://github.com/KiranChilledOut/claude-codex-nebius-proxy.git ~/claude-codex-nebius-proxy
cd ~/claude-codex-nebius-proxy
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. Configure .env — inject the key from the environment (never echo/print it)
cp .env.example .env
python3 - <<'EOF'
import os, re
s = open('.env').read()
s = re.sub(r'^OPENAI_API_KEY=.*$', f'OPENAI_API_KEY="{os.environ["NEBIUS_API_KEY"]}"', s, flags=re.M)
open('.env', 'w').write(s)
EOF

# 3. (Recommended) verify the .env model IDs still exist — Nebius rotates availability:
curl -s "https://api.tokenfactory.nebius.com/v1/models" -H "Authorization: Bearer $NEBIUS_API_KEY" \
  | grep -o "$(grep -E '^(BIG|MIDDLE|SMALL|VISION)_MODEL=' .env | cut -d= -f2 | tr -d '"' | sort -u | paste -sd'|' -)" \
  || echo "WARNING: a model in .env is not in /models — pick replacements from the list and edit .env"

# 4. Start it (background) and verify
nohup .venv/bin/python start_proxy.py > proxy.log 2>&1 &
sleep 3
curl -s -o /dev/null -w "proxy dashboard: HTTP %{http_code}\n" http://localhost:8083/dashboard
```

HTTP 200 from the dashboard = the proxy is up. Then wire the user's CLI (sections below).
If it isn't, read `proxy.log` — the usual culprits are a bad key (401s in the log) or a
stale model ID in `.env` (step 3).

Useful `.env` knobs (see the file's comments): `BIG/MIDDLE/SMALL/VISION_MODEL` control
routing, `PORT=8083`, `LOG_LEVEL`. There's also a `docker-compose.yml` if the user prefers
containers over a venv.

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
