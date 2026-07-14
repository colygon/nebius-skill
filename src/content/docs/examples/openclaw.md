---
title: Deploy OpenClaw on Nebius Serverless
description: Documentation page
---

# Deploy OpenClaw on Nebius Serverless

Deploy an OpenClaw AI agent to Nebius in under 5 minutes using a pre-built public image.

## Quick Deploy (No Docker Build Required)

```bash
# 1. Choose your model
MODEL="zai-org/GLM-5"
# Other options: deepseek-ai/DeepSeek-R1-0528, MiniMaxAI/MiniMax-M2.5, zai-org/GLM-4.5

# 2. Get your Token Factory API key
# Option A: From MysteryBox (if stored):
TF_KEY=$(nebius mysterybox payload get --secret-id <SECRET_ID> --format json \
  | jq -r '.data[0].string_value')
# Option B: Set manually from https://tokenfactory.nebius.com:
TF_KEY="v1.xxx..."

# 3. Set region and Token Factory URL
REGION="eu-north1"    # or eu-west1, us-central1
PLATFORM="cpu-e2"     # eu-west1 uses cpu-d3
if [[ "$REGION" == "us-central1" ]]; then
  TOKEN_FACTORY_URL="https://api.tokenfactory.us-central1.nebius.com/v1"
else
  TOKEN_FACTORY_URL="https://api.tokenfactory.nebius.com/v1"
fi

# 4. Generate a gateway password
PASSWORD=$(openssl rand -hex 16)
echo "Save this password: $PASSWORD"

# 5. Deploy
nebius ai endpoint create \
  --name openclaw-agent \
  --image ghcr.io/opencolin/openclaw-serverless:latest \
  --platform $PLATFORM \
  --preset 2vcpu-8gb \
  --container-port 8080 \
  --container-port 18789 \
  --disk-size 250Gi \
  --env "TOKEN_FACTORY_API_KEY=${TF_KEY}" \
  --env "TOKEN_FACTORY_URL=${TOKEN_FACTORY_URL}" \
  --env "INFERENCE_MODEL=${MODEL}" \
  --env "OPENCLAW_WEB_PASSWORD=${PASSWORD}" \
  --public \
  --ssh-key "$(cat ~/.ssh/id_ed25519.pub 2>/dev/null || echo '')" \
  --format json

# 6. Wait for RUNNING
ENDPOINT_ID=$(nebius ai endpoint get-by-name openclaw-agent --format json | jq -r '.metadata.id')
while true; do
  STATE=$(nebius ai endpoint get $ENDPOINT_ID --format json | jq -r '.status.state')
  echo "Status: $STATE"
  [ "$STATE" = "RUNNING" ] && break
  sleep 10
done

# 7. Get the public IP
IP=$(nebius ai endpoint get $ENDPOINT_ID --format json \
  | jq -r '.status.instances[0].public_ip' | cut -d/ -f1)
echo "Endpoint IP: $IP"

# 8. Verify
curl http://$IP:8080
# Expected: {"status":"healthy","service":"openclaw-serverless","model":"zai-org/GLM-5",...}
```

## Connect to Your Agent

### Step 1: SSH tunnel (required — browsers block device identity without HTTPS or localhost)
```bash
ssh -f -N -o StrictHostKeyChecking=no -L 28789:$IP:18789 nebius@$IP
```

### Step 2: Approve device pairing (first time only)
The gateway token **must** be passed as an env var or this fails with "unauthorized":
```bash
ssh -o StrictHostKeyChecking=no nebius@$IP \
  "sudo docker exec \$(sudo docker ps -q | head -1) \
   env OPENCLAW_GATEWAY_TOKEN=$PASSWORD openclaw devices approve --latest"
```

### Step 3: Open dashboard or TUI

**Via Browser** (always use localhost, never direct IP):
```
http://localhost:28789/#token=<PASSWORD>&gatewayUrl=ws://localhost:28789
```

**Via TUI:**
```bash
openclaw tui --url ws://localhost:28789 --token $PASSWORD
```

## Configure Nebius Provider Plugin

After deployment, install the Nebius provider plugin to access 44+ open-source models via Token Factory:

```bash
# Install
openclaw plugins install clawhub:@colygon/openclaw-nebius

# Set API key (both needed)
launchctl setenv NEBIUS_API_KEY "v1.YOUR_KEY_HERE"
# Also add to ~/.openclaw/agents/main/agent/auth-profiles.json (see SKILL.md)

# Enable and restart
openclaw config set plugins.allow '["nebius"]'
openclaw gateway restart

# Verify
openclaw models list --provider nebius

# Optional: set default model
openclaw config set agents.defaults.model.primary "nebius/deepseek-ai/DeepSeek-V3.2"
```

Always use the `nebius/` prefix for model names (e.g., `nebius/zai-org/GLM-5`). See the [plugin repo](https://github.com/opencolin/openclaw-nebius-plugin) for the full model catalog and pricing.

## Deploy NemoClaw (NVIDIA Plugin)

NemoClaw wraps OpenClaw with NVIDIA's enhanced agent capabilities. Ideal for GPU endpoints with local models.

```bash
# Same command, different image:
nebius ai endpoint create \
  --name nemoclaw-agent \
  --image ghcr.io/opencolin/nemoclaw-serverless:latest \
  --platform cpu-e2 \
  --preset 2vcpu-8gb \
  --container-port 8080 \
  --container-port 18789 \
  --disk-size 250Gi \
  --env "TOKEN_FACTORY_API_KEY=${TF_KEY}" \
  --env "TOKEN_FACTORY_URL=${TOKEN_FACTORY_URL}" \
  --env "INFERENCE_MODEL=${MODEL}" \
  --env "OPENCLAW_WEB_PASSWORD=${PASSWORD}" \
  --public \
  --ssh-key "$(cat ~/.ssh/id_ed25519.pub 2>/dev/null || echo '')" \
  --format json
```

## Region → Platform Mapping

| Region | Platform | Notes |
|--------|----------|-------|
| `eu-north1` (Finland) | `cpu-e2` | Default region |
| `eu-west1` (Paris) | `cpu-d3` | Different CPU — must match! |
| `us-central1` (US) | `cpu-e2` | US-based workloads. Token Factory URL: `api.tokenfactory.us-central1.nebius.com` |

## Token Factory Models

```bash
# List all available models:
curl -s $TOKEN_FACTORY_URL/models \
  -H "Authorization: Bearer $TF_KEY" | jq '.data[].id'
```

Common models:
- `zai-org/GLM-5` — Latest GLM, strong reasoning
- `deepseek-ai/DeepSeek-R1-0528` — DeepSeek reasoning model
- `MiniMaxAI/MiniMax-M2.5` — Fast, powerful
- `zai-org/GLM-4.5` — Lighter, faster responses

**Important:** Use Token Factory model IDs (e.g., `zai-org/GLM-5`), NOT HuggingFace IDs (e.g., `THUDM/GLM-4-9B-0414`). Wrong format causes silent 404 errors.

## Store API Key in MysteryBox

```bash
PROJECT_ID=$(nebius config get parent-id)

nebius mysterybox secret create \
  --name token-factory-key \
  --parent-id $PROJECT_ID \
  --secret-version-payload \
    '[{"key":"TOKEN_FACTORY_API_KEY","string_value":"v1.xxx..."}]' \
  --format json
```

## Managing Your Endpoint

```bash
nebius ai endpoint list --format json | jq '.items[] | {name: .metadata.name, state: .status.state}'
nebius ai endpoint stop <ID>      # Pause billing
nebius ai endpoint start <ID>     # Resume
nebius ai endpoint delete <ID>    # Remove
nebius ai endpoint logs <ID> --follow --since 5m
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Health check works but gateway unreachable | Add `--container-port 18789` (both ports needed) |
| "device identity" / secure context error | Browser requires HTTPS or localhost. Set up SSH tunnel: `ssh -f -N -L 28789:<IP>:18789 nebius@<IP>` then use `http://localhost:28789/...` |
| "pairing required" | Must pass gateway token: `ssh nebius@<IP> "sudo docker exec $(docker ps -q) env OPENCLAW_GATEWAY_TOKEN=<password> openclaw devices approve --latest"` |
| "gateway token mismatch" | Token lost after restart. SSH in and set in config: `openclaw config set gateway.auth.token <password>` |
| 404 on inference | Wrong model ID format. Use `zai-org/GLM-5` not `THUDM/...` |
| "Config invalid - plugins" | Remove `plugins` key from `openclaw.json`. NemoClaw auto-loads via npm. |
| Endpoint won't start | Check platform matches region: `cpu-e2` for eu-north1/us-central1, `cpu-d3` for eu-west1 |
