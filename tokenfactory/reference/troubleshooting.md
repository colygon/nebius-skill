# Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Signup rejects your email | gmail.com is blocked (anti-fraud) | Use a work/school/non-Gmail address. Gmail-only? Ask event staff or Slack `#help` for a direct promo code. See `signup-help.md`. |
| Signup form won't load | Form is intermittently flaky | Refresh, try incognito/another browser, retry in a few minutes; ask `#help` for the backup form. |
| No promo-code email | Delivery is unreliable (especially from the backup form) | Check spam; wait ~10 min; then ask in `#help` — at events, staff carry spare codes. |
| "Promo code exhausted" email | That's **AI Cloud** — a different product you don't need | Ignore it. The Token Factory "here's your code" email is the one that matters. See `signup-help.md`. |
| Can't find "Get API Key" in the dashboard | Button sits off-screen at narrow window widths | Maximize/widen the browser window. |
| `401 Unauthorized` | Missing/expired key, or key not yet approved | Re-copy the key from the dashboard; confirm credits approved at https://dev.nebius.com/builders; ensure `Authorization: Bearer $NEBIUS_API_KEY`. |
| `404` / "model not found" | Wrong model ID or casing | Call `GET /models` and copy the exact ID (e.g. `nvidia/nemotron-3-super-120b-a12b`). |
| Connection errors / wrong host | Wrong base URL | Use the OpenAI-compatible base URL from your dashboard (`https://api.tokenfactory.nebius.com/v1`; older docs may show `https://api.studio.nebius.com/v1`); include the `/v1` path, no trailing slash. |
| Helper expects `OPENAI_API_KEY` | Tool only reads OpenAI vars | Set `OPENAI_API_KEY=$NEBIUS_API_KEY` and `OPENAI_BASE_URL=$NEBIUS_BASE_URL`. |
| Key worked earlier, gone in a new terminal | `export` only lasts for that session | Persist it: `echo 'export NEBIUS_API_KEY="your-key-here"' >> ~/.zshrc` (macOS) or `>> ~/.bashrc` (Linux), then open a new terminal or `source` the file. |
| `429` / rate limit | Too many concurrent requests | Add retry with backoff; cap concurrency (semaphore); use the Batch API for bulk evals. |
| Context length exceeded | Oversized tool results in history | Summarize/paginate results; pass artifact references not raw rows; trim old tool messages. |
| Model returns invalid tool-call JSON | Occasional malformed args | `try/except` around `json.loads`; on failure return an error tool-result so the model retries. |
| Model answers from memory instead of calling tools | Weak system prompt | Instruct explicitly which tool to use for which job ("always use X; never guess"); consider `tool_choice` to force a specific tool. |
| Claude Code / Codex won't use Nebius | CLIs are Anthropic-shaped | Route through a proxy (`opencolin/claude-codex-nebius-proxy`, `claude-code-router`, or LiteLLM proxy) — install walkthrough in `proxy-setup.md`. (OpenCode needs no proxy — see `api.md` → "OpenCode".) |
| Streaming shows nothing | Consuming deltas wrong | Read `chunk.choices[0].delta.content` (may be `None` on some chunks). |

## Fast sanity check

```bash
curl -s "$NEBIUS_BASE_URL/models" -H "Authorization: Bearer $NEBIUS_API_KEY" | head
```

If that returns a model list, your key + base URL are correct and the problem is in the request
(model name, message shape, or tool schema).

## Where to get help during the event

- Live support: your event's community Slack `#help`
- Nebius recipes: https://github.com/nebius/token-factory-cookbook
