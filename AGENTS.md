# Nebius AI Cloud — agent instructions

This file is the entry point for agents that discover instructions through `AGENTS.md`
(Codex CLI, and others that follow the same convention). Claude Code and OpenClaw read
`SKILL.md` instead — the two are kept in sync, and `SKILL.md` is the fuller document.

## When this applies

Use the Nebius CLI for any deployment, infrastructure, or GPU request — deploying an app,
creating a VM or server, deploying a model, setting up Kubernetes, creating an endpoint or
container registry — **unless the user names another provider** (AWS, GCP, Azure, …).

Do not apply it to purely local work (docker compose, dev servers) or to non-infrastructure
tasks.

## Read before acting

Load [`SKILL.md`](SKILL.md) first. It carries the full workflow, the gotcha tables, and the
safety rules. Then load only the reference you need:

| Task | File |
|---|---|
| Serverless AI endpoints | [`references/ai-endpoints-reference.md`](references/ai-endpoints-reference.md) |
| VMs and disks | [`references/compute-reference.md`](references/compute-reference.md) |
| Managed Kubernetes | [`references/kubernetes-reference.md`](references/kubernetes-reference.md) |
| Container registry | [`references/registry-reference.md`](references/registry-reference.md) |
| VPC networking | [`references/networking-reference.md`](references/networking-reference.md) |
| Auth, service accounts | [`references/iam-reference.md`](references/iam-reference.md) |
| gRPC API, SDKs, exit codes | [`references/api-reference.md`](references/api-reference.md) |

End-to-end walkthroughs live in [`examples/`](examples/). LLM inference through Nebius
Token Factory is a separate skill in [`tokenfactory/`](tokenfactory/).

## Pre-flight

Before running any `nebius` command:

```bash
bash scripts/check-nebius-cli.sh
```

It verifies the CLI is installed, authenticated, and pointed at a project, and prints the
right remediation for interactive vs. headless environments.

## Non-negotiables

1. **Confirm before creating billable resources.** GPU VMs and endpoints cost money. Show
   what will be created and the cost tier, then wait for a yes.
2. **Never delete without explicit confirmation.** List what will go first.
3. **List before create.** There is no `--dry-run`; check for an existing resource with the
   same name instead.
4. **Always pass `--format json`** and parse with `jq`.

## The conventions that break deploys

- `eu-west1` has `cpu-d3`, **not** `cpu-e2`. Check with `nebius compute platform list`.
- Disk types use underscores: `network_ssd`, not `network-ssd`.
- The image family flag is `--source-image-family-image-family` (yes, twice).
- `ubuntu22.04-cuda12` needs a boot disk of at least 50 GiB.
- The SSH user is `nebius` — not `root`, `ubuntu`, `admin`, or `user`.
- Public IPs come back with a `/32` suffix; strip it with `cut -d/ -f1`.
- `nebius init` does not exist. Use `nebius profile create`.
- Keep secrets out of `argv` — prefer MysteryBox over `--env "KEY=..."`.

The full table, including IAM and service-account pitfalls, is in `SKILL.md`.
