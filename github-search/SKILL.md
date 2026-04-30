---
name: github-search
description: Search GitHub code, repositories, issues, and PRs via the `gh` CLI — finds prior art, related discussions, and existing implementations across public and authenticated repos. Use when the user says "search GitHub for", "find a repo that does X", "has anyone built", "is there an issue about", "find prior PRs", or when researching how other projects solved a similar problem before reinventing it. Returns ranked results with repo, file path, line, and link. NOT for searching the local repo (use grep/Read) or general web search (use WebSearch).
allowed-tools:
  - Bash
  - Read
---

# GitHub Search Skill

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


## When to Use

- Search code across repositories
- Find issues or PRs
- Look up repository information

## Instructions

```
gh search <type> <query> [flags]
```

### Parameters

- `<type>`: Search type - `code`, `repos`, `issues`, `prs`
- `<query>`: Search query (supports GitHub search syntax)
- `--owner`: (optional) Filter by repo owner (all search types)
- `--repo`: (optional) Filter by repo name (code/issues/prs only)
- `--limit`: (optional) Max results to fetch
- `--`: (optional) Use before the query when it contains a `-` qualifier, e.g. `-- "bug -label:critical"`

### Examples

```bash
# Search code
gh search code "authentication language:python"

# Search issues
gh search issues "bug label:critical" --owner "anthropics"

# Search pull requests in a repo
gh search prs "is:open review:required" --repo "cli/cli"
```

## Out of Scope

This skill does NOT:
- Search the local repo or working tree—use Grep/Read directly.
- Search the open web for articles, docs, or blog posts—use `web-search-quality` with WebSearch.
- Fetch and verify external API/library documentation—use `fetch-api-docs`.
- Open, review, or merge pull requests—use `review-pr` or `shipping-workflow`.
- Discover available Claude skills across registries—use `skill-discovery`.

## Requirements

Requires GitHub CLI (`gh`) to be installed and authenticated (`gh auth status` or `gh auth login`).
