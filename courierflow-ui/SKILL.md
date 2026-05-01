---
name: courierflow-ui
description: CourierFlow frontend guidance for Jinja templates, Bootstrap 5, Vue workflow builder pages, dashboards, calendar/sidebar screens, static CSS/JS, and design-system changes. Use when editing app/templates, app/static, page headers, workflow UI, tenant/property forms, or any user-facing landlord confirmation flow.
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# CourierFlow UI

## Purpose

Keep CourierFlow's landlord-facing UI consistent, scoped, and useful for the
calendar-event-to-workflow product loop. Use this skill for templates, CSS,
static JavaScript, Vue workflow-builder behavior, and visual verification.

## Load Strategy

1. Read `references/ui-patterns.md` before editing templates, CSS, or JS.
2. Pair with `defensive-ui-flows` for interactive flows, async saves, and
   modal state.
3. If the change touches backend routes or schemas, also load
   `courierflow-api` or `courierflow-data`.

## Non-Negotiables

- Build the actual landlord workflow, not a marketing page.
- Use central patterns from `base.html`, `macros/ui_macros.html`, and design
  system CSS before adding page-specific styles.
- Use `page_title`, `extra_css`, `extra_scripts`, and `content` blocks exactly.
- Use `.page-content-wrapper` with page containers.
- Use `.page-header-standard`, `.page-title`, `.page-subtitle`,
  `.page-actions`, and `.page-status-badge` for page headers.
- Use design-system CSS variables without fallback values.
- Do not hardcode colors.
- Make confirmation, dry-run, conflict warning, and destructive-preview states
  visible in the same dashboard/sidebar visit.

## Verification

- Run `scripts/check_template_blocks.py` when template blocks change.
- Grep for legacy header classes after template work.
- Run focused template/static tests when available.
- For substantial UI work, run the app and inspect the changed screen.
