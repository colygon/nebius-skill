---
title: Common Gotchas
description: Subtle issues that bite when working with the Nebius CLI
---

Every item below is a real failure mode with a verified fix. If a command here
disagrees with something you read elsewhere, trust this page and
[`SKILL.md`](https://github.com/opencolin/nebius-skill/blob/main/SKILL.md) — they are
kept in sync.

## CLI & Configuration

### The install URL changed

The old `storage.ai.nebius.cloud` host no longer resolves.

```bash
# ✅ Current install URL
curl -sSL https://storage.eu-north1.nebius.cloud/cli/install.sh | bash
exec -l $SHELL
```

### `nebius init` does not exist

```bash
# ❌ Not a command
nebius init

# ✅ Create a profile instead
nebius profile create
```

### `nebius profile create` needs a terminal

It prompts interactively and cannot be scripted. In CI, containers, or any headless
environment, write `~/.nebius/config.yaml` directly — see [Authentication](/intro/authentication/).

### A macOS binary will not run on Linux

Copying `~/.nebius/bin/` from a Mac to a Linux box gives `Exec format error`. Copy the
config files only, and reinstall the CLI natively on the target host.

### Profile scoping hides projects

`nebius iam project list` is scoped to the active profile's parent. To see projects in
other regions, pass the tenant explicitly:

```bash
nebius iam project list --parent-id <TENANT_ID> --format json
```

### `nebius iam whoami` nests the user name

```bash
# ✅ The name lives here
nebius iam whoami --format json | jq -r '.user_profile.attributes.name'

# ❌ This field does not exist
nebius iam whoami --format json | jq -r '.identity.display_name'
```

## Regions & Platforms

### `cpu-e2` does not exist in `eu-west1`

This is the single most common deploy failure. `eu-west1` (Paris) only offers `cpu-d3`.

```bash
# ❌ Fails in eu-west1
nebius ai endpoint create --platform cpu-e2 ...

# ✅ Check what the region actually has
nebius compute platform list --format json
```

See [Regions & Platforms](/core-concepts/regions/) for the full mapping.

### Token Factory has a separate US endpoint

Using the EU URL from `us-central1` fails as a silent 401 or "model not found" rather
than an obvious error.

| Region | Token Factory base URL |
|---|---|
| `eu-north1`, `eu-west1` | `https://api.tokenfactory.nebius.com/v1` |
| `us-central1` | `https://api.tokenfactory.us-central1.nebius.com/v1` |

## Compute & Disks

### Disk types use underscores

```bash
# ❌ Rejected
--type network-ssd

# ✅ Correct
--type network_ssd    # also: network_hdd, network_ssd_io_m3
```

### The image family flag says "image-family" twice

```bash
# ❌ Not a flag
--source-image-family ubuntu22.04-cuda12

# ✅ Correct
--source-image-family-image-family ubuntu22.04-cuda12
```

### CUDA images need at least 50 GiB

`ubuntu22.04-cuda12` fails validation at 30 GiB. Give the boot disk 50 GiB or more.

### Public IPs come back with a `/32` suffix

```bash
# ✅ Strip the CIDR suffix
nebius compute instance get --id <ID> --format json \
  | jq -r '.status.network_interfaces[0].public_ip_address.address' \
  | cut -d/ -f1
```

### The SSH user is `nebius`

Not `root`, `ubuntu`, `admin`, or `user`. This is the default on both VMs and endpoints
unless your own cloud-init creates a different account.

### SSH keys can only be set at creation

`--ssh-key` must be passed to `nebius ai endpoint create`. There is no way to add a key
afterwards — you have to recreate the endpoint. To recover a public key from a private
one:

```bash
ssh-keygen -y -f key > key.pub
```

## Endpoints

### Expose every port you need

`--container-port` is repeatable. A health check on 8080 and a dashboard on 18789 need
both flags:

```bash
nebius ai endpoint create --container-port 8080 --container-port 18789 ...
```

### Public IP quota is 3 per tenant

`RESOURCE_EXHAUSTED` on a `--public` endpoint usually means you are at the limit, not
that the region is full. Free one up:

```bash
nebius ai endpoint list --format json | jq '.items[] | {name: .metadata.name, state: .status.state}'
nebius ai endpoint delete <ID>
```

## IAM & Service Accounts

### Federation auth opens a browser

On a headless VM, `nebius iam get-access-token` tries to launch a browser and hangs. Use
a service account for anything unattended.

### Service account keys must be 4096-bit RSA

2048-bit keys are rejected:

```bash
openssl genrsa 4096
```

### Registry pushes need `editors` membership

A service account that can authenticate can still get `denied` from `docker push` until
it is in the `editors` group:

```bash
nebius iam group list --parent-id <TENANT_ID> --format json
nebius iam group-membership create --parent-id <EDITORS_GROUP_ID> --member-id <SA_ID>
```

### Strip Mac paths when copying a config to Linux

`private-key-file-path` in a config copied from a Mac will point at a path that does not
exist on the VM.

## Cost

- CPU (`cpu-e2` / `cpu-d3`) is far cheaper than GPU — use it for agent and orchestration
  workloads that call a remote inference API.
- `nebius ai endpoint stop` and `nebius compute instance stop` pause billing. Stopping is
  not deleting; disks still cost.
- Size disks to the image. A 250 GiB disk for a 400 MB container is pure waste.
- Prefer H100 over H200 when the model fits in 80 GB, and L40S for small-model inference.
- `--preemptible-priority` suits batch and training jobs that tolerate interruption.
