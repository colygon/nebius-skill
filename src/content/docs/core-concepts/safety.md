---
title: Safety & Best Practices
description: Safety guidelines and best practices for Nebius
---

## Security Best Practices

### API Key Management

✅ **Do:**
- Store API keys in environment variables
- Rotate keys every 90 days
- Use different keys for different environments
- Enable key expiration policies

❌ **Don't:**
- Commit API keys to version control
- Share keys via email or chat
- Use the same key across environments
- Store keys in plaintext files

### Network Security

✅ **Do:**
- Use VPC security groups
- Enable firewall rules
- Restrict inbound traffic to needed ports
- Use VPN for sensitive workloads

❌ **Don't:**
- Open all ports (0.0.0.0/0)
- Disable authentication on endpoints
- Transmit sensitive data in plaintext
- Use default credentials

## Operational Safety

### Before Deploying

1. **Test in staging** before production
2. **Review resource limits** to avoid runaway costs
3. **Set up monitoring** and alerting
4. **Document your setup**
5. **Have a rollback plan**

### During Deployment

```bash
# Check whether the resource already exists before creating a duplicate
nebius ai endpoint list --format json \
  | jq -r '.items[] | select(.metadata.name=="my-endpoint") | .metadata.id'

# Create, then watch it come up
nebius ai endpoint create --name my-endpoint ... --format json
nebius ai endpoint logs <ENDPOINT_ID> --follow --since 5m --timestamps
```

There is no `--dry-run`. The safe pattern is **list before create**: confirm the resource
does not already exist, and show the user what will be billed before running the create.

### Cost Control

- Set resource quotas per project
- Monitor usage regularly
- Use spot instances for non-critical workloads
- Implement auto-scaling limits
- Review billing weekly

## Disaster Recovery

### Backup Strategy

- Export models/code regularly
- Keep configuration versioned in git
- Document recovery procedures
- Test recovery process quarterly

### High Availability

- Run multiple replicas
- Distribute across regions/zones
- Implement health checks
- Use load balancing

### Incident Response

1. **Monitor** for errors and anomalies
2. **Alert** on SLO violations
3. **Respond** within defined SLA
4. **Review** root cause after incident
5. **Improve** based on learnings

## Compliance

### Data Protection

- Encrypt data at rest (default: enabled)
- Encrypt data in transit (TLS)
- Implement access controls (IAM)
- Audit data access logs

### Audit Logging

Audit events are exposed through the gRPC API at `audit.api.nebius.cloud:443`
(`AuditEvent`, `AuditEventExport`) rather than a dedicated CLI verb. See
[API & SDKs](/advanced/api-sdks/) for how to call it.

### Regional Requirements

Ensure your region complies with local regulations:

- **EU**: GDPR compliance required
- **US**: Data residency in US region
- **Custom**: Contact Nebius for specific needs

## Monitoring & Alerting

### Key Metrics to Monitor

- API latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Resource utilization (CPU, memory, GPU)
- Cost per model invocation
- Availability/uptime

### Setting Up Alerts

Alerting is configured in the Nebius console rather than through the CLI. For scripted
checks, poll the resource state and its logs:

```bash
nebius ai endpoint get <ENDPOINT_ID> --format json | jq -r '.status.state'
nebius ai endpoint logs <ENDPOINT_ID> --since 5m
```
