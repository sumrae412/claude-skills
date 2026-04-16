# GitHub Actions Authoring — Claude Code Action

Lazy-loaded reference. Read only when authoring or editing a `.github/workflows/*.yml` file that invokes `anthropics/claude-code-action`.

## Before You Write

**Always fetch live docs first.** The `@v1` input shape differs from `@beta`, and model IDs drift.

- Primary: https://code.claude.com/docs/en/github-actions
- Action repo: https://github.com/anthropics/claude-code-action
- Usage examples: https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md

## @v1 Canonical Skeleton

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "..."
    claude_args: |
      --max-turns 10
      --model claude-sonnet-4-6
      --allowedTools Read,Edit,Write,Bash
```

## @beta → @v1 Migration Map

| Beta input | @v1 equivalent |
|---|---|
| `mode: "tag"` / `mode: "agent"` | *(removed — auto-detected)* |
| `direct_prompt` | `prompt` |
| `override_prompt` | `prompt` (with GitHub template vars) |
| `custom_instructions` | `claude_args: --append-system-prompt` |
| `max_turns` | `claude_args: --max-turns` |
| `model` | `claude_args: --model` |
| `allowed_tools` | `claude_args: --allowedTools` |
| `disallowed_tools` | `claude_args: --disallowedTools` |
| `claude_env` | `settings` JSON format |

## Model ID Drift Mitigations

Hardcoded model IDs in workflow files go stale silently. Pick one:

1. **Omit `--model`** — default applies, always current
2. **Pin + comment** — `--model claude-sonnet-4-6  # verify against docs on edit`
3. **Fetch docs before edit** — verify the ID is still recommended

Never paste a model ID from training data without verification.

## Self-Committing Workflows — Loop Prevention

Any workflow that commits back to its own trigger branch needs **three layers**:

```yaml
on:
  push:
    branches: [main]
    paths-ignore:        # Layer 1: skip files the workflow writes
      - 'CHANGELOG.md'
      - '.github/workflows/this-workflow.yml'

jobs:
  run:
    if: "!contains(github.event.head_commit.message, '[auto-commit]')"  # Layer 2
    steps:
      - # ... make changes ...
      - run: |
          git commit -m "chore: auto-update [auto-commit]"              # Layer 3: marker in message
```

Missing any one layer risks infinite runs.

## Setup — Prefer `/install-github-app`

When proposing workflow setup to the user, recommend the CLI command first:

```bash
/install-github-app   # from Claude Code terminal in the repo
```

This installs the GitHub App AND adds `ANTHROPIC_API_KEY` as a repo secret in one step. Manual fallback: install https://github.com/apps/claude, then `Settings → Secrets and variables → Actions → New repository secret`.

## Cost / Turn Controls

Always set `--max-turns` on automated workflows. Typical:
- PR review / doc update: `5–15`
- Feature implementation from issue: `20–40`

Without a turn cap, a misconfigured prompt can burn tokens indefinitely.

## Related
- MEMORY `claude_code_action_v1_shape.md` — full input migration notes
- MEMORY `github_action_over_local_hook_for_merge_events.md` — design pattern for merge-triggered automation
