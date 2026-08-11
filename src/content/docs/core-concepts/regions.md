---
title: Regions & Platforms
description: Nebius regions, and which compute platforms exist in each
---

## Regions

| Region | Location | CPU platform | Notes |
|---|---|---|---|
| `eu-north1` | Finland | `cpu-e2` | Primary region |
| `eu-west1` | Paris | `cpu-d3` | **`cpu-e2` does not exist here** |
| `us-central1` | US | `cpu-e2` | Requires a separate project |

The `eu-west1` CPU difference is the most common source of failed deploys. When in doubt,
ask the API rather than guessing:

```bash
nebius compute platform list --format json
```

## GPU platforms

| Platform | GPU | VRAM | Best for |
|---|---|---|---|
| `gpu-h100-sxm` | H100 | 80 GB | General inference, training |
| `gpu-h200-sxm` | H200 | 141 GB | Large model inference |
| `gpu-b200-sxm` | B200 | 180 GB | Next-gen workloads |
| `gpu-b300-sxm` | B300 | 288 GB | Largest models |
| `gpu-l40s-pcie` | L40S | 48 GB | Cost-effective inference |

## CPU platforms

| Platform | Available in |
|---|---|
| `cpu-e2` | `eu-north1`, `us-central1` |
| `cpu-d3` | `eu-west1` |

## Presets

A preset selects the vCPU/RAM/GPU shape on a platform.

| Preset | vCPU | RAM | GPU |
|---|---|---|---|
| `1gpu-16vcpu-200gb` | 16 | 200 GB | 1 |
| `2gpu-32vcpu-400gb` | 32 | 400 GB | 2 |
| `4gpu-64vcpu-800gb` | 64 | 800 GB | 4 |
| `8gpu-128vcpu-1600gb` | 128 | 1600 GB | 8 |

CPU-only endpoints use presets such as `2vcpu-8gb`.

## Token Factory endpoints

Token Factory — the managed inference API — has its own regional base URLs, and they do
not follow the control-plane naming. Using the wrong one fails as a silent 401 or a
"model not found", not as an obvious connection error.

| Region | Base URL |
|---|---|
| `eu-north1`, `eu-west1` | `https://api.tokenfactory.nebius.com/v1` |
| `us-central1` | `https://api.tokenfactory.us-central1.nebius.com/v1` |

## Choosing a region

- **Latency** — pick the region closest to your users or your data.
- **Data residency** — EU workloads with GDPR obligations belong in `eu-north1` or `eu-west1`.
- **Availability** — GPU capacity varies; `NOT_ENOUGH_RESOURCES` (exit code 25) means try
  another region or a smaller preset.
- **Projects are per-region** — `us-central1` needs its own project, and
  `nebius iam project list` only shows the active profile's parent. Pass
  `--parent-id <TENANT_ID>` to see everything.
