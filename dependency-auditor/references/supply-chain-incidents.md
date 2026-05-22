# Supply-Chain Incident Runbooks

Concrete incident patterns and the safe cleanup orders that prevent self-inflicted damage during remediation. Add new cases when novel attack patterns emerge — the goal is to keep a small library of "don't do the obvious thing first" warnings.

---

## Case 1 — npm "Mini Shai-Hulud" (2026-05-11, `@tanstack/*`)

**Source:** Prosper, "npm Supply Chain Attack: The Only Safe Cleanup Order" (Substack, 2026-05).

84 malicious versions of `@tanstack/*` published with **valid provenance certificates** via a poisoned GitHub Actions cache. Hit Mistral AI, Guardrails AI, and OpenAI internal environments. Attributed to "TeamPCP".

### The trap

The malware installs a background persistence daemon (`gh-token-monitor`) that watches your GitHub token. **If you revoke the token before killing the daemon, the daemon executes `rm -rf ~/`** as its final act. Most generic "rotate-credentials-first" cleanup guidance walks straight into this.

### Safe cleanup sequence

1. **Do NOT rotate any tokens yet.**
2. Look for the daemon process:
   - macOS: scan `~/Library/LaunchAgents/` and `/Library/LaunchAgents/` for `gh-token-monitor` plists.
   - Linux: `systemctl --user list-units | grep -i token` and check `~/.config/systemd/user/`.
3. **Stop the daemon first, then delete the launch file.** Both steps in that order.
4. Sweep for dropped payloads:
   - `~/.claude/` and `~/.vscode/` for `router_runtime.js` or `setup.mjs`.
5. Audit lockfiles for `@tanstack/*` entries with `2026-05-11` timestamps (`grep -n "tanstack" package-lock.json pnpm-lock.yaml yarn.lock`).
6. **NOW** rotate credentials: GitHub PATs and OAuth tokens, npm tokens, cloud provider keys touched in the affected window.
7. Block the attacker infrastructure at network egress (`git-tanstack[.]com` was the documented C2 host for this campaign).
8. Upgrade to clean `@tanstack/*` versions (anything published after 2026-05-12).

### Generalizable rules from this incident

- **"Rotate tokens immediately" is the wrong first step when a watcher daemon is plausible.** Kill background watchers first. The rule is: rotate AFTER you've killed every process that could observe the rotation event.
- **Valid provenance ≠ safe.** Sigstore / npm provenance certs only attest "this build came from this Actions workflow" — if the workflow itself was poisoned (cache, dependency, or pre-existing infrastructure compromise), the cert is still valid. Treat provenance as a useful but non-load-bearing signal.
- **Lockfile timestamp sweeps catch what version-pin policies miss.** `grep` by date window in `package-lock.json` / `pnpm-lock.yaml` is fast and finds packages installed in a known-bad window even if they're now pinned to a clean version.
- **AI-ecosystem packages are a primary target.** Tools that auto-pull deep dependency trees (Cursor, Claude Code plugins, MCP servers, agentic SDKs) shorten the attacker's path from publish to victim. Audit `~/.claude/`, `~/.vscode/`, `~/.cursor/` after any major npm incident, not just project lockfiles.

---

## Recommended scanning tools (one-liners)

- **slopcheck** — flags hallucinated/squatted package names before install. Use in pre-install hook for any AI-generated `package.json` / `requirements.txt`. See https://github.com/slop-research/slopcheck.
- **Socket** — deep package inspection (typosquats, install scripts, network calls, obfuscation). Use as a CI gate on new dependencies. See https://socket.dev.
- **Gitleaks** — pre-commit secret scanner. Add as Husky / pre-commit hook.
- **TruffleHog** — CI-time secret scanner with credential verification (confirms a leaked key is live before alerting).

Both `slopcheck` and `Socket` exist specifically to catch the slopsquatting / hallucinated-package class of supply-chain attack that vibe-coded AI output is most prone to. Gitleaks + TruffleHog handle the hardcoded-secret class.
