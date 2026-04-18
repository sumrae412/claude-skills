## IaC Snippet Templates

All templates below are starting points. Each is marked as a template that must be reviewed and adapted before applying.

### MFA — AWS Cognito (Terraform)

> **TEMPLATE — review and adapt before applying**

Target: `terraform/modules/auth/mfa.tf`

```hcl
resource "aws_cognito_user_pool" "main" {
  name = var.user_pool_name

  mfa_configuration = "ON"

  software_token_mfa_configuration {
    enabled = true
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
}
```

### Encryption at Rest — AWS RDS (Terraform)

> **TEMPLATE — review and adapt before applying**

Target: `terraform/modules/database/encryption.tf`

```hcl
resource "aws_db_instance" "main" {
  storage_encrypted = true
  kms_key_id        = var.rds_kms_key_arn

  # ... other configuration
}

resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption at rest"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}
```

### Encryption at Rest — S3 (Terraform)

> **TEMPLATE — review and adapt before applying**

Target: `terraform/modules/storage/encryption.tf`

```hcl
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_kms_key" "s3" {
  description             = "KMS key for S3 encryption at rest"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}
```

### Automated Backups — RDS (Terraform)

> **TEMPLATE — review and adapt before applying**

Target: `terraform/modules/database/backups.tf`

```hcl
resource "aws_db_instance" "main" {
  backup_retention_period = 30
  backup_window           = "03:00-04:00"
  copy_tags_to_snapshot   = true
  deletion_protection     = true

  # ... other configuration
}
```

### Anomaly Detection — CloudWatch (Terraform)

> **TEMPLATE — review and adapt before applying**

Target: `terraform/modules/monitoring/alarms.tf`

```hcl
resource "aws_cloudwatch_metric_alarm" "failed_login_spike" {
  alarm_name          = "${var.app_name}-failed-login-spike"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "FailedLoginAttempts"
  namespace           = var.app_name
  period              = 300
  statistic           = "Sum"
  threshold           = var.failed_login_threshold
  alarm_description   = "Alert on unusual number of failed login attempts"
  alarm_actions       = [var.sns_topic_arn]
}

resource "aws_cloudwatch_metric_alarm" "traffic_anomaly" {
  alarm_name          = "${var.app_name}-traffic-anomaly"
  comparison_operator = "GreaterThanUpperThreshold"
  evaluation_periods  = 3
  threshold_metric_id = "ad1"
  alarm_description   = "Alert on anomalous traffic patterns"

  metric_query {
    id          = "m1"
    metric {
      metric_name = "RequestCount"
      namespace   = "AWS/ApplicationELB"
      period      = 300
      stat        = "Sum"
    }
  }

  metric_query {
    id          = "ad1"
    expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
    label       = "RequestCount (expected)"
    return_data = true
  }

  alarm_actions = [var.sns_topic_arn]
}
```

### Incident Response Plan Stub

> **TEMPLATE — review and adapt before applying**

Target: `docs/incident-response.md`

```markdown
# Incident Response Plan

## Severity Levels

| Level | Name | Description | Response Time | Examples |
|---|---|---|---|---|
| SEV-1 | Critical | Service fully down, data breach | 15 min | Production outage, credential leak |
| SEV-2 | Major | Significant degradation | 30 min | Major feature broken, partial outage |
| SEV-3 | Minor | Limited impact | 4 hours | Minor bug in production, single user affected |
| SEV-4 | Low | Minimal impact | 24 hours | Cosmetic issue, non-critical alert |

## Response Procedure

1. **Detect** — alert fires or report received
2. **Triage** — assess severity, assign incident commander
3. **Communicate** — notify stakeholders via #incidents channel
4. **Mitigate** — apply immediate fix or rollback
5. **Resolve** — confirm service restored, root cause identified
6. **Postmortem** — blameless review within 48 hours (SEV-1/2)

## Contacts

| Role | Name | Contact |
|---|---|---|
| Incident Commander | TBD | TBD |
| Engineering Lead | TBD | TBD |
| Communications | TBD | TBD |

## Runbooks

- [ ] Database failover: `docs/runbooks/db-failover.md`
- [ ] Rollback deployment: `docs/runbooks/rollback.md`
- [ ] Credential rotation: `docs/runbooks/credential-rotation.md`
```

### Security Audit Schedule Stub

> **TEMPLATE — review and adapt before applying**

Target: `docs/security-audit-schedule.md`

```markdown
# Security Audit Schedule

## Recurring Audits

| Audit | Frequency | Owner | Last Completed | Next Due |
|---|---|---|---|---|
| Dependency vulnerability scan | Weekly (automated) | CI/CD | TBD | TBD |
| OWASP Top 10 review | Quarterly | Security Lead | TBD | TBD |
| Infrastructure access review | Quarterly | Platform Team | TBD | TBD |
| Penetration test | Annually | External Vendor | TBD | TBD |
| SOC 2 / compliance audit | Annually | Compliance Team | TBD | TBD |

## Ad-Hoc Triggers

Run an unscheduled security review when any of these occur:

- Major infrastructure change (new cloud provider, region, service)
- Authentication or authorization system changes
- New third-party integration with data access
- Security incident or near-miss (post-incident action item)
- Significant codebase refactor affecting security boundaries
```

---

