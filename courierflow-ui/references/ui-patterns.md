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

## CopilotKit and GenUI cards

- The SPA shell (`app/templates/spa_shell.html`) must `<link>` all three CSS layers in order before `spa.css`: `design-system/index.css` (tokens) → `components/_copilot-gen-cards.css` (card rules using `--ds-*`) → CopilotKit's bundled CSS via `{% for href in vite_asset_css('src/spa.tsx') %}<link rel="stylesheet" href="{{ href }}">{% endfor %}`.
- CopilotKit class-name contract (stable, safe to target/portal-into): `.copilotKitChat`, `.copilotKitChatBody`, `.copilotKitMessages` (scroll container), `.copilotKitInput`, `.copilotKitInputContainer`. `.copilotKitMessages` ships with `justify-content: space-between` — override to `flex-start !important` when portaling content into it.
- Cache-bust `spa.css` (`?v=YYYYMMDD-N`) when the cascade ordering changes; CopilotKit-rendered chat history is also browser-cached, so verify CSS deploys via Playwright in a fresh session before assuming "still broken" reports are real.
- Unit-prefix double-up: when backend serializers emit fields like `unit_label = "Unit B"`, components must strip a case-insensitive leading "Unit " before re-prefixing in JSX (see `TenantSearchCard.tsx`).
- **CopilotKit v2 hook surface is NOT uniform across the three hooks.** A migration plan must enumerate each hook's contract separately:
  - `useRenderTool` (backend-paired, render-only): render-prop is `({status, parameters, result})` — note `parameters`, NOT `args`. `status` is the string-literal union `'inProgress' | 'executing' | 'complete'`.
  - `useFrontendTool` (LLM-exposed, frontend-handled): render-prop is `({status, args, result})`. `status` is the `ToolCallStatus` enum.
  - `useHumanInTheLoop` (LLM-exposed, awaits user via `respond`): render-prop is `({status, args, respond})`. `status` is the `ToolCallStatus` enum.
  `ToolCallStatus.Complete === "complete"` so `status !== ToolCallStatus.Complete` works against both the string-literal and enum shapes — preferred over bare string literals for grep-ability. Source of truth: `node_modules/@copilotkit/react-core/dist/copilotkit-DFaI4j2r.d.mts` (`RenderToolInProgressProps` / `ReactToolCallRenderer` / `ReactHumanInTheLoop`).
- **`args` / `parameters` is `Partial<T>` during `InProgress` status, even with Zod schemas.** Required-string fields become `string | undefined` in the render union — keep defensive `?? "fallback"` coercion or early-return on non-Complete status. The "Zod schema fully types render args" claim is wrong for the streaming window.
- **`CopilotChatLabels` v2 dropped `title` and `initial`.** Only `chatInputPlaceholder` (renamed from v1's `placeholder`) is a valid key for the placeholder slot. Importing `CopilotChat` from `@copilotkit/react-core/v2` (NOT `@copilotkit/react-ui`) and pairing with `'@copilotkit/react-core/v2/styles.css'` is the v2 swap pattern.

## Search Checks

Run these before finishing template work:

```bash
grep -r "wf-page-header\\|wf-page-title" app/templates/
grep -r "block title\\|block extra_js\\|block scripts" app/templates/
grep -r "var(--ds-[^)]*," app/templates app/static/css
```
