---
title: Conventions
description: Naming and resource conventions for Nebius
---

## Naming Conventions

### Projects

- Format: `[team]-[purpose]`
- Example: `ml-training`, `api-staging`
- Length: 3-32 characters
- Allowed: lowercase letters, numbers, hyphens (no underscores)

### Resources

- **Endpoints**: `[service]-[env]-[version]`
  - Example: `llama-prod-v2`
- **VMs**: `[service]-[role]-[number]`
  - Example: `gpu-worker-01`, `cpu-api-03`
- **Kubernetes Clusters**: `[service]-[region]-[env]`
  - Example: `app-eu-prod`, `batch-us-staging`

## Environment Naming

Use consistent environment names:

- `prod` / `production` - Production workloads
- `staging` / `pre-prod` - Pre-production testing
- `dev` / `development` - Development/testing
- `test` - Automated testing environment

## Tagging Strategy

Tag resources for organization and cost tracking:

```bash
--tags \
  environment=prod \
  team=ml \
  cost-center=research \
  version=1.0
```

## Port Conventions

Standard ports by service type:

- **HTTP/REST**: 8080
- **gRPC**: 50051
- **Metrics**: 9090
- **Debugging**: 40000

## Resource Sizing

Recommended configurations:

### Agent / orchestration workloads
- Platform: `cpu-e2` (`cpu-d3` in `eu-west1`)
- Preset: `2vcpu-8gb`
- Storage: size it to the image — a 400 MB container does not need 250 GiB

### Single-GPU inference
- Platform: `gpu-l40s-pcie` for small models, `gpu-h100-sxm` for general use
- Preset: `1gpu-16vcpu-200gb`
- Storage: 100 GiB, and at least 50 GiB for any `ubuntu22.04-cuda12` boot disk

### Large model inference / training
- Platform: `gpu-h200-sxm`, `gpu-b200-sxm`, or `gpu-b300-sxm`
- Preset: `4gpu-64vcpu-800gb` or `8gpu-128vcpu-1600gb`
- Storage: 500 GiB+, plus `--shm-size 16Gi` for PyTorch

See [Regions & Platforms](/core-concepts/regions/) for the full platform list.
