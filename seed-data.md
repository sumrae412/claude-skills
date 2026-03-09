---
name: seed-data
description: Guide database seeding for dev/test environments. Lists available seed scripts and runs them.
disable-model-invocation: true
---

# Seed Data

Populate the database with test/development data using the project's seed scripts.

## Available Seeders

| Script | What It Seeds | Use When |
|--------|--------------|----------|
| `scripts/seed_test_users.py` | Test user accounts | Setting up a fresh dev environment |
| `scripts/seed_e2e_test_user.py` | E2E test user with known credentials | Before running Playwright tests |
| `scripts/seed_email_templates.py` | Email templates for workflows | Fresh DB or after template schema changes |
| `scripts/seed_landlord_templates.py` | Pre-built workflow templates for landlords | Fresh DB or demoing the product |
| `scripts/seed_quick_actions.py` | Dashboard quick action buttons | After clearing quick actions or fresh DB |
| `scripts/seed_help_articles.py` | Help/knowledge base articles | Fresh DB or after help content updates |
| `scripts/seed_administrative_workflows.py` | Administrative workflow templates | Fresh DB setup |
| `scripts/seed_relationship_workflows.py` | Relationship-based workflow templates | Fresh DB setup |
| `scripts/seed_benchmarks.py` | Performance benchmark data | Before running load tests |

## Usage

Ask the user which scenario they need, then run the appropriate scripts:

### Fresh Development Environment (run all core seeders)
```bash
python3 scripts/seed_test_users.py
python3 scripts/seed_email_templates.py
python3 scripts/seed_landlord_templates.py
python3 scripts/seed_quick_actions.py
python3 scripts/seed_help_articles.py
python3 scripts/seed_administrative_workflows.py
```

### Before E2E Tests
```bash
python3 scripts/seed_e2e_test_user.py
```

### Before Load/Performance Tests
```bash
python3 scripts/seed_benchmarks.py
```

## Notes

- All scripts are idempotent — safe to run multiple times
- Scripts require DATABASE_URL environment variable
- Run from project root directory
- For Railway: `railway run python3 scripts/<script>.py`
