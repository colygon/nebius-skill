---
title: Authentication
description: Authenticating the Nebius CLI, SDKs, and Token Factory
---

## Two different credentials

These are not interchangeable, and mixing them up is a common first-hour mistake:

| Credential | What it is for | How it is supplied |
|---|---|---|
| **IAM token** | The CLI, gRPC API, and SDKs — creating VMs, endpoints, clusters | Browser federation or a service account, via `~/.nebius/config.yaml` |
| **Token Factory API key** | Inference only — calling models over the OpenAI-compatible API | `NEBIUS_API_KEY` / `TOKEN_FACTORY_API_KEY` environment variable |

There is no "Nebius API key" that authenticates the CLI. If you have a key that starts
with `v1.`, that is a Token Factory key and the CLI will not accept it.

## Interactive setup

With a browser available:

```bash
# Create a profile — prompts for name, endpoint, and auth
nebius profile create

# Re-authenticate later, when the token expires
nebius iam login

# Verify
nebius iam whoami --format json
```

`nebius init` does not exist. Use `nebius profile create`.

The user name is nested deeper than you would expect:

```bash
nebius iam whoami --format json | jq -r '.user_profile.attributes.name'
```

Access tokens last roughly 12 hours. When one expires you get `UNAUTHENTICATED`
(exit code 7) — run `nebius iam login` again.

## Non-interactive setup

`nebius profile create` needs a terminal and cannot be scripted. In CI, a container, or
any headless environment, write the config directly:

```bash
mkdir -p ~/.nebius
cat > ~/.nebius/config.yaml << 'EOF'
current-profile: default
profiles:
  default:
    endpoint: api.nebius.cloud
    auth-type: federation
    federation-endpoint: auth.nebius.com
    parent-id: <PROJECT_ID>
    tenant-id: <TENANT_ID>
EOF

nebius iam login   # one browser login, then the token is cached
```

## Service accounts (fully automated)

The only option with no browser at any point — required for headless VMs, where
`nebius iam get-access-token` would otherwise try to open one.

```bash
SA_ID=$(nebius iam service-account create \
  --name my-ci-sa \
  --parent-id <PROJECT_ID> \
  --format json | jq -r '.metadata.id')

# Add it to the editors group, or every write returns PERMISSION_DENIED
nebius iam group list --parent-id <TENANT_ID> --format json
nebius iam group-membership create --parent-id <EDITORS_GROUP_ID> --member-id $SA_ID

# Generate the key pair
nebius iam auth-public-key generate --parent-id $SA_ID --format json > sa-key.json
chmod 600 sa-key.json
```

Then set `auth-type: service account`, `service-account-id`, `public-key-id`, and
`private-key-file-path` in `~/.nebius/config.yaml`.

Two things that bite here: keys must be **4096-bit RSA** (2048 is rejected), and if you
copied the config from a Mac, the `private-key-file-path` will point at a path that does
not exist on the target host.

Full detail: [IAM](/services/iam/).

## Setting the project

Most commands are scoped to the profile's `parent-id`:

```bash
nebius iam project list --format json | jq -r '.items[].metadata.id'
nebius config set parent-id <PROJECT_ID>
```

`nebius iam project list` only shows projects under the active profile's parent. To see
projects in other regions, pass `--parent-id <TENANT_ID>`.

## SDKs

The SDKs read the same credentials and handle token refresh themselves.

```python
from nebius.sdk import SDK

sdk = SDK()   # reads NEBIUS_IAM_TOKEN, or the service account config
```

```go
import "github.com/nebius/gosdk"

sdk, err := gosdk.New(ctx, gosdk.WithCredentials(gosdk.IAMToken(token)))
```

For a raw gRPC call, mint a token with the CLI:

```bash
ACCESS_TOKEN=$(nebius iam get-access-token)
grpcurl -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  cpl.iam.api.nebius.cloud:443 \
  nebius.iam.v1.ProfileService/Get
```

See [API & SDKs](/advanced/api-sdks/) for the JWT exchange used by service accounts.

## Token Factory

Inference uses a separate key from the [Token Factory console](https://tokenfactory.nebius.com/),
and a regional base URL:

```bash
export NEBIUS_API_KEY="v1.your-key-here"
export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"   # us-central1: https://api.tokenfactory.us-central1.nebius.com/v1

curl -s "$NEBIUS_BASE_URL/models" -H "Authorization: Bearer $NEBIUS_API_KEY" | head
```

## Keeping credentials safe

- Never commit keys. Store them in environment variables or in MysteryBox
  (`nebius mysterybox secret create`).
- Prefer MysteryBox over `--env "API_KEY=..."` on a create command — anything in `argv` is
  visible to `ps` and lands in shell history.
- Rotate keys regularly and use separate keys per environment.
- Service account private keys should be `chmod 600` and never checked in.

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `UNAUTHENTICATED` (7) | Token expired | `nebius iam login` |
| `PERMISSION_DENIED` (15) | Not in `editors` | Add the identity to the group |
| `NOT_FOUND` (13) | Wrong project or profile | Check `nebius config get parent-id` |
| `nebius profile create` hangs | No interactive terminal | Write `~/.nebius/config.yaml` directly |
| Browser opens on a headless VM | Federation auth | Switch to a service account |
