---
name: coderabbit-review
description: Run CodeRabbit AI code review — one-shot review, autonomous fix-review cycles, or deep analysis. Replaces the coderabbit plugin (command + skill + agent consolidated).
argument-hint: [type] [--base <branch>]
allowed-tools: Bash(coderabbit:*), Bash(cr:*), Bash(git:*)
---

# CodeRabbit Code Review

AI-powered code review using CodeRabbit CLI. Use as `/coderabbit-review` or auto-triggered when reviewing code.

## When to Use

- Review code changes / PR feedback / code quality check
- Find bugs, security issues, or performance problems
- Autonomous implement-then-review cycles
- Pre-merge validation
- Run as a dispatched review agent (subagent)

## Context

- Branch: !`git branch --show-current 2>/dev/null || echo "detached HEAD"`
- Has changes: !`git status --porcelain 2>/dev/null | head -1 | grep -q . && echo "Yes" || echo "No"`

## Prerequisites

**Skip if already verified this session.**

```bash
coderabbit --version 2>/dev/null && coderabbit auth status 2>&1 | head -3
```

**If CLI not found:**
> Install CodeRabbit CLI: `curl -fsSL https://cli.coderabbit.ai/install.sh | sh`
> Then restart your shell and try again.

**If not authenticated:**
> Run in your terminal: `coderabbit auth login`

## Run Review

```bash
coderabbit review --plain -t <type>
```

Where `<type>` from `$ARGUMENTS` or context:

- `all` (default) — all changes
- `committed` — committed changes only
- `uncommitted` — uncommitted changes only

Add `--base <branch>` if specified or if reviewing a feature branch against main.

## Present Results

Group findings by severity and create a task list:

1. **Critical** — Security vulnerabilities, data exposure, auth flaws, injection risks, bugs
2. **High** — Missing error handling, resource leaks, race conditions, bug-prone patterns
3. **Medium** — Code duplication, complexity, missing tests, documentation gaps
4. **Low** — Style, minor optimizations, naming, organization
5. **Positive** — What's good about the code

Offer to apply fixes if `codegenInstructions` are present in the output.

## Autonomous Fix-Review Cycle

When the user wants implementation + review (or when dispatched as an agent):

1. Implement the requested feature/fix
2. Run `coderabbit review --plain`
3. Create task list from findings
4. Fix critical and high issues systematically
5. Re-run review until critical issues are resolved
6. Report final state

## Docs

<https://docs.coderabbit.ai/cli/claude-code-integration>
