## Reusable Conventions

**Test-script resolver pattern:** When a session surfaces a test that broke because a hardcoded skill-internal script path moved (e.g. after consolidating skills into a single-source repo), propose the `_resolve_script(name)` helper. It tries the runtime location first (where the installed/symlinked skill lives), then a sibling-checkout fallback. Expose both `SCRIPT` (the file) and `SCRIPTS_DIR` (its parent, needed for `sys.path.insert` before `import <module>`):

```python
def _resolve_script(name):
    for p in (
        Path.home() / ".claude" / "skills" / "<skill-name>" / "scripts" / name,
        Path(__file__).parents[N] / "<skills-repo>" / "<skill-name>" / "scripts" / name,
    ):
        if p.exists():
            return p
    raise RuntimeError(f"{name} not found; install <skills-repo> via <skill-repo>/install.sh")


SCRIPT = _resolve_script("my_script.py")
SCRIPTS_DIR = SCRIPT.parent
```

See MEMORY `resolve_script_helper_pattern.md`.


## Example Session Context

From a real session that built a bulk action bar:

```
SESSION CONTEXT:
- User corrections: "The bulk options menu does not have rounded edges —
  make sure it does" (user provided screenshot showing expected pill shape)
- Bugs investigated: User reported "bulk select was removed from workflows
  page" — systematic investigation showed feature NEVER existed in any
  git version. CSS classes existed but were used by a different JS file.
- Patterns established: "Update the UI skills to make this the default
  style" — bulk action bar with rounded edges is now standard.
- Gotchas hit: Security hook blocked innerHTML=''. Fixed with
  while(el.firstChild) el.removeChild(el.firstChild).
- New components built: Floating bulk action bar (.wf-bulk-bar),
  card selection with progressive disclosure (.card-select-checkbox)
```

This produced 3 skill updates (defensive-ui-flows patterns #23-25) and 1 project skill update (courierflow-ui-standards bulk action bar section).
