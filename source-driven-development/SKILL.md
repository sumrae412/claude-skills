---
name: source-driven-development
description: Grounds framework-specific code in official documentation. Use when building with any framework or library where correctness matters. Complements fetch-api-docs with a verify-and-cite discipline.
---

# Source-Driven Development

## Overview

Every framework-specific code decision must be backed by official documentation. Don't implement from memory — verify, cite, and let the user see your sources. Training data goes stale, APIs get deprecated, best practices evolve. This skill ensures code traces back to an authoritative source the user can check.

**Relationship to `fetch-api-docs`:** That skill handles Context Hub tooling (`chub search/get`). This skill is the broader discipline — verify everything against official docs, whether via Context Hub, WebFetch, or WebSearch.

## When to Use

- Building with any framework where the recommended approach matters (forms, routing, data fetching, state management, auth)
- The user asks for documented, verified, or "correct" implementation
- Building boilerplate or patterns that will be copied across a project
- Reviewing code that uses framework-specific patterns
- Any time you're about to write framework-specific code from memory

**When NOT to use:**

- Pure logic (loops, conditionals, data structures) — version-independent
- Renaming variables, fixing typos, moving files — no API involved
- The user explicitly wants speed over verification

## The Process

```
DETECT ──→ FETCH ──→ IMPLEMENT ──→ CITE
  │          │           │            │
  ▼          ▼           ▼            ▼
 What       Get the    Follow the   Show your
 stack?     relevant   documented   sources
            docs       patterns
```

### Step 1: Detect Stack and Versions

Read the project's dependency file to identify exact versions:

```
package.json         → Node/React/Vue/Angular/Svelte
pyproject.toml       → Python/Django/Flask/FastAPI
requirements.txt     → Python (older projects)
go.mod               → Go
Cargo.toml           → Rust
Gemfile              → Ruby/Rails
composer.json        → PHP/Symfony/Laravel
```

State what you found:

```
STACK DETECTED:
- Flask 3.1.0 (from pyproject.toml)
- SQLAlchemy 2.0.36
- Alembic 1.14.1
→ Fetching official docs for the relevant patterns.
```

If versions are missing or ambiguous, **ask the user**. The version determines which patterns are correct.

### Step 2: Fetch Official Documentation

Fetch the specific documentation page for the feature you're implementing. Not the homepage — the relevant page.

**Source hierarchy (in order of authority):**

| Priority | Source | Example |
|----------|--------|---------|
| 1 | Official documentation | docs.sqlalchemy.org, flask.palletsprojects.com |
| 2 | Official blog / changelog | blog.sqlalchemy.org, whatsnew pages |
| 3 | Web standards references | MDN, web.dev, html.spec.whatwg.org |
| 4 | Browser/runtime compatibility | caniuse.com, node.green |

**Not authoritative — never cite as primary sources:**

- Stack Overflow answers
- Blog posts or tutorials (even popular ones)
- AI-generated documentation or summaries
- Your own training data (that's the whole point — verify it)

**Tools to use:**

1. **Context Hub first** (if available): `chub search <service>` → `chub get <doc-id>`
2. **WebFetch** for specific doc pages: `WebFetch(url="https://docs.sqlalchemy.org/en/20/orm/relationships.html")`
3. **WebSearch** when you need to find the right page: `WebSearch(query="SQLAlchemy 2.0 relationship back_populates")`

**Be precise:**

```
BAD:  Fetch the Flask homepage
GOOD: Fetch flask.palletsprojects.com/en/3.1.x/patterns/sqlalchemy/

BAD:  Search "python authentication best practices"
GOOD: Fetch docs.djangoproject.com/en/5.1/topics/auth/
```

After fetching, extract the key patterns and note any deprecation warnings.

When official sources conflict, surface the discrepancy to the user — don't silently pick one.

### Step 3: Implement Following Documented Patterns

Write code that matches what the documentation shows:

- Use the API signatures from the docs, not from memory
- If the docs show a new way to do something, use the new way
- If the docs deprecate a pattern, don't use the deprecated version
- If the docs don't cover something, flag it as unverified

**When docs conflict with existing project code:**

```
CONFLICT DETECTED:
The existing codebase uses `backref=` for relationships,
but SQLAlchemy 2.0 docs recommend `back_populates=` for explicit bidirectional relationships.
(Source: docs.sqlalchemy.org/en/20/orm/relationships.html#back-populates)

Options:
A) Use the modern pattern (back_populates) — consistent with current docs
B) Match existing code (backref) — consistent with codebase
→ Which approach do you prefer?
```

Surface the conflict. Don't silently pick one.

### Step 4: Cite Your Sources

Every framework-specific pattern gets a citation.

**In code comments (sparingly — only non-obvious decisions):**

```python
# SQLAlchemy 2.0 relationship pattern — explicit bidirectional
# Source: https://docs.sqlalchemy.org/en/20/orm/relationships.html#back-populates
appointments = relationship("Appointment", back_populates="client")
```

**In conversation (always):**

```
Using back_populates instead of backref for the Client→Appointment relationship.
SQLAlchemy 2.0 recommends explicit bidirectional relationships.
Source: https://docs.sqlalchemy.org/en/20/orm/relationships.html#back-populates
```

**Citation rules:**

- Full URLs, not shortened
- Prefer deep links with anchors where possible
- Quote the relevant passage when it supports a non-obvious decision
- If you cannot find documentation, say so explicitly:

```
UNVERIFIED: Could not find official documentation for this pattern.
Based on training data — may be outdated. Verify before using in production.
```

Honesty about what you couldn't verify is more valuable than false confidence.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'm confident about this API" | Confidence is not evidence. Training data contains outdated patterns. Verify. |
| "Fetching docs wastes tokens" | Hallucinating an API wastes more. One fetch prevents hours of debugging. |
| "The docs won't have what I need" | If the docs don't cover it, that's valuable — the pattern may not be recommended. |
| "I'll just mention it might be outdated" | A disclaimer doesn't help. Either verify and cite, or flag as unverified. |
| "This is a simple task, no need to check" | Simple tasks with wrong patterns become templates copied into ten files. |

## Verification

After implementing with source-driven development:

- [ ] Framework and library versions identified from dependency files
- [ ] Official documentation fetched for framework-specific patterns
- [ ] All sources are official documentation, not blog posts or training data
- [ ] Code follows patterns shown in the current version's documentation
- [ ] Non-trivial decisions include source citations with full URLs
- [ ] No deprecated APIs used (checked against migration guides)
- [ ] Conflicts between docs and existing code surfaced to the user
- [ ] Anything unverifiable is explicitly flagged as unverified
