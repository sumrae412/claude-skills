---
name: shadcn
description: Project-aware shadcn/ui workflow for searching, adding, composing, and fixing shadcn/ui components with correct patterns. Use when working with shadcn/ui, React, Tailwind, component registries, presets, components.json, or any task involving shadcn init, adding components, or switching presets.
user-invocable: true
allowed-tools: Bash(npx shadcn@latest *), Bash(pnpm dlx shadcn@latest *), Bash(bunx --bun shadcn@latest *)
---

# shadcn/ui

A framework for building UI, components, and design systems. Components are added as source code to the user's project via the CLI.

> **IMPORTANT:** Run all CLI commands using the project's package runner: `npx shadcn@latest`, `pnpm dlx shadcn@latest`, or `bunx --bun shadcn@latest` — based on the project's `packageManager`. Examples below use `npx shadcn@latest` but substitute the correct runner for the project.

## Current Project Context

```json
!`npx shadcn@latest info --json`
```

The JSON above contains the project config and installed components. Use `npx shadcn@latest docs <component>` to get documentation and example URLs for any component.

## Principles

1. **Use existing components first.** Use `npx shadcn@latest search` to check registries before writing custom UI.
2. **Compose, don't reinvent.** Settings page = Tabs + Card + form controls. Dashboard = Sidebar + Card + Chart + Table.
3. **Use built-in variants before custom styles.** `variant="outline"`, `size="sm"`, etc.
4. **Use semantic colors.** `bg-primary`, `text-muted-foreground` — never raw values like `bg-blue-500`.

## Critical Rules

These rules are **always enforced**. Each links to a references file with Incorrect/Correct code pairs.

### Styling & Tailwind → [references/styling.md](./references/styling.md)

- **`className` for layout, not styling.** Never override component colors or typography.
- **No `space-x-*` or `space-y-*`.** Use `flex` with `gap-*`. For vertical stacks, `flex flex-col gap-*`.
- **Use `size-*` when width and height are equal.** `size-10` not `w-10 h-10`.
- **Use `truncate` shorthand.** Not `overflow-hidden text-ellipsis whitespace-nowrap`.
- **No manual `dark:` color overrides.** Use semantic tokens (`bg-background`, `text-muted-foreground`).
- **Use `cn()` for conditional classes.** Don't write manual template literal ternaries.
- **No manual `z-index` on overlay components.** Dialog, Sheet, Popover, etc. handle their own stacking.

### Forms & Inputs → [references/forms.md](./references/forms.md)

- **Forms use `FieldGroup` + `Field`.** Never use raw `div` with `space-y-*` or `grid gap-*` for form layout.
- **`InputGroup` uses `InputGroupInput`/`InputGroupTextarea`.** Never raw `Input`/`Textarea` inside `InputGroup`.
- **Buttons inside inputs use `InputGroup` + `InputGroupAddon`.**
- **Option sets (2-7 choices) use `ToggleGroup`.** Don't loop `Button` with manual active state.
- **`FieldSet` + `FieldLegend` for grouping related checkboxes/radios.**
- **Field validation uses `data-invalid` + `aria-invalid`.**

### Component Structure → [references/composition.md](./references/composition.md)

- **Items always inside their Group.** `SelectItem` → `SelectGroup`. `DropdownMenuItem` → `DropdownMenuGroup`.
- **Use `asChild` (radix) or `render` (base) for custom triggers.** → [references/base-vs-radix.md](./references/base-vs-radix.md)
- **Dialog, Sheet, and Drawer always need a Title.** Use `className="sr-only"` if visually hidden.
- **Use full Card composition.** `CardHeader`/`CardTitle`/`CardDescription`/`CardContent`/`CardFooter`.
- **`TabsTrigger` must be inside `TabsList`.**
- **`Avatar` always needs `AvatarFallback`.**

### Icons → [references/icons.md](./references/icons.md)

- **Icons in `Button` use `data-icon`.** `data-icon="inline-start"` or `data-icon="inline-end"`.
- **No sizing classes on icons inside components.** Components handle icon sizing via CSS.
- **Pass icons as objects, not string keys.** `icon={CheckIcon}`, not a string lookup.

### CLI → [references/cli.md](./references/cli.md)

- **Never decode preset codes or build preset URLs manually.** Use `npx shadcn@latest preset decode <code>`.
- **Apply preset codes directly with the CLI.** Use `npx shadcn@latest apply <code>`.

## Key Patterns

```tsx
// Form layout: FieldGroup + Field, not div + Label.
<FieldGroup>
  <Field>
    <FieldLabel htmlFor="email">Email</FieldLabel>
    <Input id="email" />
  </Field>
</FieldGroup>

// Validation: data-invalid on Field, aria-invalid on the control.
<Field data-invalid>
  <FieldLabel>Email</FieldLabel>
  <Input aria-invalid />
  <FieldDescription>Invalid email.</FieldDescription>
</Field>

// Icons in buttons: data-icon, no sizing classes.
<Button>
  <SearchIcon data-icon="inline-start" />
  Search
</Button>

// Spacing: gap-*, not space-y-*.
<div className="flex flex-col gap-4">  // correct
<div className="space-y-4">           // wrong

// Equal dimensions: size-*, not w-* h-*.
<Avatar className="size-10">   // correct
<Avatar className="w-10 h-10"> // wrong
```

## Workflow

1. **Get project context** — already injected above. Run `npx shadcn@latest info` again if you need to refresh.
2. **Check installed components first** — before running `add`, always check the `components` list from project context.
3. **Find components** — `npx shadcn@latest search`.
4. **Get docs and examples** — run `npx shadcn@latest docs <component>` to get URLs, then fetch them.
5. **Install or update** — `npx shadcn@latest add`. Use `--dry-run` and `--diff` to preview changes first.
6. **Fix imports in third-party components** — After adding from community registries, check for hardcoded import paths.
7. **Review added components** — Always read added files and verify they are correct.
8. **Registry must be explicit** — If no registry is specified, ask which registry to use.

## Updating Components

When the user asks to update a component from upstream while keeping their local changes, use `--dry-run` and `--diff` to intelligently merge. **NEVER fetch raw files from GitHub manually — always use the CLI.**

1. Run `npx shadcn@latest add <component> --dry-run` to see all files that would be affected.
2. For each file, run `npx shadcn@latest add <component> --diff <file>` to see what changed upstream vs local.
3. Decide per file based on the diff:
   - No local changes → safe to overwrite.
   - Has local changes → read the local file, analyze the diff, and apply upstream updates while preserving local modifications.
   - User says "just update everything" → use `--overwrite`, but confirm first.
4. **Never use `--overwrite` without the user's explicit approval.**

## Quick Reference

```bash
# Create a new project.
npx shadcn@latest init --name my-app --preset base-nova

# Initialize existing project.
npx shadcn@latest init --preset base-nova

# Apply a preset to an existing project.
npx shadcn@latest apply a2r6bw

# Add components.
npx shadcn@latest add button card dialog
npx shadcn@latest add @magicui/shimmer-button

# Preview changes before adding/updating.
npx shadcn@latest add button --dry-run
npx shadcn@latest add button --diff button.tsx

# Search registries.
npx shadcn@latest search @shadcn -q "sidebar"

# Get component docs and example URLs.
npx shadcn@latest docs button dialog select
```

## Detailed References

- [references/forms.md](./references/forms.md) — FieldGroup, Field, InputGroup, ToggleGroup, FieldSet, validation states
- [references/composition.md](./references/composition.md) — Groups, overlays, Card, Tabs, Avatar, Alert, Empty, Toast
- [references/icons.md](./references/icons.md) — data-icon, icon sizing, passing icons as objects
- [references/styling.md](./references/styling.md) — Semantic colors, variants, spacing, size, cn(), z-index
- [references/base-vs-radix.md](./references/base-vs-radix.md) — asChild vs render, Select, ToggleGroup, Slider
- [references/cli.md](./references/cli.md) — Commands, flags, presets, templates
- [references/registry.md](./references/registry.md) — Authoring source registries, item definitions
- [references/customization.md](./references/customization.md) — Theming, CSS variables, extending components

## See also

- `vercel-react-best-practices` — React + Next.js architectural patterns that compose with shadcn/ui component work
- `design-audit` — visual audit skill for reviewing UI against design intent, pairs well with shadcn component reviews
