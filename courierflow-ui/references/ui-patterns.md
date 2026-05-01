# CourierFlow UI Patterns

## Product Lens

CourierFlow is for small landlords confirming calendar-detected events and
arming communication workflows. UI changes should make this path clearer:

1. landlord selects or reviews a Google Calendar event
2. CourierFlow shows event type, property, tenant, sequence, and confidence
3. landlord confirms or corrects the match
4. workflow dry-run timeline appears before arming
5. failures show up where the landlord already checks status

Do not add generic CRM, assistant, or real-estate platform surfaces.

## Template Rules

- Templates extending `base.html` use only these blocks:
  `page_title`, `extra_css`, `content`, `extra_scripts`.
- Browser tab text is the page name only; `base.html` adds the app prefix.
- Page wrappers use `.page-content-wrapper`.
- Page headers use the standard pattern or `page_header` macro.
- Avoid custom `wf-*` header/title/action classes.
- Keep CSS in shared design-system locations unless the style is genuinely
  one-off and cannot be centralized.

## Design-System Rules

- Use `var(--ds-*)` variables with no fallback values.
- Body, labels, buttons, and inputs use `var(--ds-font-family)`.
- Non-heading elements that need heading typography use
  `var(--ds-font-family-heading)`.
- Do not hardcode hex colors.
- Do not create nested cards or decorative page-section cards.
- Cards are for repeated items, modals, and framed tools.

## Landlord-Control States

Any UI that arms, pauses, deletes, archives, or overrides a workflow must show:

- affected event/property/tenant
- affected workflow instance or step count
- confirmation state and confidence source
- opt-out or conflict warning when relevant
- next scheduled action timestamps in the user's timezone

## Static Asset Checks

- If changing CSS or JS loaded with cache-busting query strings, update the
  corresponding `?v=` references.
- If adding icons, prefer the app's existing icon library.
- If changing Vue workflow-builder state, verify the DOM updates after array
  or nested-object mutations.

## Search Checks

Run these before finishing template work:

```bash
grep -r "wf-page-header\\|wf-page-title" app/templates/
grep -r "block title\\|block extra_js\\|block scripts" app/templates/
grep -r "var(--ds-[^)]*," app/templates app/static/css
```
