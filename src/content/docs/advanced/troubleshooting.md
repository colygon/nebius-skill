---
title: Troubleshooting
description: Errors you will actually hit, and what fixes them
---

## Exit codes

The CLI returns gRPC status codes. The number tells you which class of problem you have:

| Code | Status | Usual cause | Fix |
|---|---|---|---|
| 7 | `UNAUTHENTICATED` | Token expired (they last ~12 h) | `nebius iam login`, or check the service account key |
| 13 | `NOT_FOUND` | Wrong resource ID, or wrong project/profile | Verify the ID and the active profile's `parent-id` |
| 15 | `PERMISSION_DENIED` | Identity is not in the `editors` group | Add the user or service account to `editors` |
| 24 | `RESOURCE_EXHAUSTED` | Quota — often the 3-public-IP tenant limit | Delete unused resources, or request an increase in the console |
| 25 | `NOT_ENOUGH_RESOURCES` | The region has no capacity for that preset | Try another region or a smaller preset |

## Installation & authentication

### `nebius: command not found`

```bash
curl -sSL https://storage.eu-north1.nebius.cloud/cli/install.sh | bash
exec -l $SHELL
nebius version
```

### `nebius init` is not a command

Use `nebius profile create`. See [Authentication](/intro/authentication/).

### `nebius profile create` hangs

It requires an interactive terminal. In CI or a container, write `~/.nebius/config.yaml`
directly, then run `nebius iam login` once — or skip browser auth entirely with a service
account. Both paths are in [IAM](/services/iam/).

### `UNAUTHENTICATED` on a headless VM

Federation tokens expire, and `nebius iam get-access-token` then tries to open a browser.
Switch that host to service account auth: create the account, generate a **4096-bit RSA**
key, add it to `editors`, and set `auth-type: service account` in `~/.nebius/config.yaml`.

### Everything returns `NOT_FOUND`

Usually the profile is pointing at the wrong parent:

```bash
nebius config get parent-id
nebius iam project list --format json | jq -r '.items[] | {id: .metadata.id, name: .metadata.name}'
```

## Deploying

### The platform is not available in this region

`eu-west1` has `cpu-d3`, not `cpu-e2`. Confirm before deploying:

```bash
nebius compute platform list --format json
```

### Disk validation fails on a CUDA image

`ubuntu22.04-cuda12` needs a boot disk of at least 50 GiB.

### `docker push` is denied

The service account authenticates but lacks write access to the registry:

```bash
nebius iam group list --parent-id <TENANT_ID> --format json
nebius iam group-membership create --parent-id <EDITORS_GROUP_ID> --member-id <SA_ID>
```

### The endpoint will not become `RUNNING`

Read the container's own logs before touching the endpoint config:

```bash
nebius ai endpoint logs <ENDPOINT_ID> --follow --since 5m --timestamps
```

### Public IP quota exceeded

The default tenant limit is 3. List what holds them and release one:

```bash
nebius ai endpoint list --format json | jq '.items[] | {name: .metadata.name, state: .status.state}'
nebius ai endpoint delete <ID>
```

## Connectivity

### The health port answers but the dashboard does not

`--container-port` only exposes the ports you name. Pass it once per port:

```bash
nebius ai endpoint create --container-port 8080 --container-port 18789 ...
```

### Cannot reach the endpoint at all

Check the state and the address, remembering the `/32` suffix:

```bash
nebius ai endpoint get <ENDPOINT_ID> --format json | jq '{state: .status.state, ip: .status.instances[0].public_ip}'
```

If the state is `RUNNING` and the port is exposed, the remaining suspect is the security
group — see [Networking](/services/networking/).

## OpenClaw endpoints

These apply to the OpenClaw/NemoClaw images in [Deploy OpenClaw](/examples/openclaw/).

| Symptom | Fix |
|---|---|
| "device identity" / secure-context error | Browsers refuse device identity without HTTPS or localhost. Tunnel first: `ssh -f -N -L 28789:<IP>:18789 nebius@<IP>`, then use `http://localhost:28789/...` |
| "pairing required" | The approve command needs the gateway token in its environment, or it returns "unauthorized". See [Deploy OpenClaw](/examples/openclaw/) for the exact command. |
| Gateway token mismatch after a restart | The token must be in `gateway.auth.token` in `~/.openclaw/openclaw.json`, not only in the environment — the env var is lost on a manual restart. |
| `Config invalid - plugins` | `plugins` is not a valid top-level key and crashes the gateway. Recognised keys: `agents`, `models`, `gateway`, `channels`. NemoClaw auto-loads from its global npm install. |
| 404 from inference | Wrong model ID format, or the wrong regional Token Factory URL. Use `zai-org/GLM-5`, not the HuggingFace-style `THUDM/GLM-4-9B-0414`. |
| `openclaw config get` returns `__OPENCLAW_REDACTED__` | Secrets are redacted on read. Inspect the raw file: `cat ~/.openclaw/openclaw.json` |

## Getting help

- [Nebius CLI documentation](https://docs.nebius.com/cli/)
- [CLI configuration reference](https://docs.nebius.com/cli/configure)
- [Nebius API protos](https://github.com/nebius/api)
