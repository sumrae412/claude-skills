---
name: courierflow-ui-standards
description: Use when adding UI features, creating templates, writing CSS, or modifying any visual element in CourierFlow. Apply before writing any HTML, CSS, or Jinja template code.
---

# CourierFlow Design System v1.0 — "Quiet Elegance"

## Core Philosophy

| Principle | Meaning |
|-----------|---------|
| **Monochrome Dominant** | Color is noise. Use Slate for 95% of UI. Reserve color for "Sparks" and critical status. |
| **Content is King** | UI containers recede. Use background tints, spacing, subtle borders—not heavy containers. |
| **Crisp Interaction** | Typography and layout do heavy lifting. Animations 150-300ms, functional not decorative. |

---

## Typography — Inter Only

**Font:** Inter (Google Fonts). No mixed fonts (no Poppins).

| Element | Style |
|---------|-------|
| Page Titles | `text-xl font-semibold text-slate-800` |
| Section Headers | `text-xs font-semibold text-slate-500 uppercase tracking-wider` |
| Card Titles | `text-sm font-medium text-slate-800` |
| Body Text | `text-sm text-slate-600` |
| Muted/Helper | `text-xs text-slate-400` |
| Signatures | `font-signature` (Caveat) — signatures only |

---

## Color Palette

### Base Colors

| Element | Class |
|---------|-------|
| Page Background | `bg-slate-50` |
| Card/Panel BG | `bg-white` |
| Border (subtle) | `border-slate-100` |
| Border (standard) | `border-slate-200` |

### Buttons

| Type | Style |
|------|-------|
| **Primary** | `bg-slate-900 hover:bg-slate-800 text-white shadow-sm` |
| **Secondary** | `bg-white border border-slate-200 hover:border-slate-400 text-slate-600` |
| **Destructive** | `text-red-600 hover:bg-red-50` |
| **Size** | `px-4 py-2 text-xs font-semibold` |

**Primary = Black (slate-900). NEVER use Indigo/Blue for primary buttons.**

### Status Badges — Monochrome

| Status | Style |
|--------|-------|
| Draft/Inactive | `bg-slate-100 text-slate-500` |
| Sent/Pending | `border border-slate-300 text-slate-600` |
| Signed/Active | `bg-slate-800 text-white` |

**NO colorful badges (red, green, yellow).**

### "The Spark" (Accent Color)

Use Indigo/Blue sparingly for micro-interactions only:
- Selected checkboxes, active timeline nodes, loading spinners, focus rings

**NEVER use for:** Navigation bars, card headers, primary buttons

---

## Layout Patterns

### A. Sidebar + Canvas
**Used for:** Document Setup, Workflow Builder

```
┌──────────────┬─────────────────────────────┐
│  Sidebar     │      Canvas (bg-slate-50)   │
│  (w-80)      │                             │
│  bg-white    │      Work Area              │
│  border-r    │                             │
└──────────────┴─────────────────────────────┘
```

### B. Split View (Details)
**Used for:** Document Details, Tenant Details

- Left Column (2/3): Primary content (Preview, Documents)
- Right Column (1/3): Context/Metadata (Signers, Activity)

### C. Slide-Over Panel
**Used for:** Detail views from lists (clicking a tenant in table)

- Fixed position, right-aligned, `max-w-lg`
- Overlay: `bg-slate-900/20 backdrop-blur-sm`
- Sliding animation

---

## Component Specifications

### Cards
```html
<div class="bg-white rounded-xl border border-slate-100 shadow-sm hover:border-slate-200">
```
- Radius: `rounded-xl` (12px) for cards
- Radius: `rounded-lg` (8px) for buttons/inputs

### Inputs
```html
<input class="bg-white border border-slate-200 rounded-lg px-3 py-2.5 text-sm
              focus:ring-1 focus:ring-slate-300 focus:border-slate-300 outline-none
              placeholder:text-slate-400">
```

### Timeline (Vertical)
- Line: `absolute left-6 w-px bg-slate-200`
- Nodes: `w-12 h-12 rounded-full`
  - Pending: White with border
  - Active: Dark solid
- Drop Zones: `opacity-0 group-hover:opacity-100`

### Document Field Overlays
| Field Type | Style |
|------------|-------|
| Signature | Wide box (`w-64`), script font "Sign Here", icon |
| Initials | Square (`w-12 h-12`), dashed border |
| Date | Underline (`border-b`), "MM/DD/YYYY" placeholder |
| Text | Standard rectangle |

---

## Navigation & Header

### Top Nav Bar
- Background: `bg-white border-b border-slate-100`
- Active State: `text-slate-800`, no background pill (bold weight or small underline)
- Right Side: Primary Action Button + User Avatar

### Breadcrumbs
- Use for deep navigation (Workflow Builder)
- Style: `text-slate-400 text-sm` with back arrow

---

## Empty States

```html
<div class="flex flex-col items-center justify-center py-12 text-center">
  <div class="w-12 h-12 rounded-full bg-slate-50 border border-slate-100 flex items-center justify-center mb-4">
    <i class="fas fa-inbox text-slate-400"></i>
  </div>
  <p class="text-sm font-medium text-slate-600">No items yet</p>
  <button class="btn btn-secondary mt-4">Add Item</button>
</div>
```

---

## Activity & Logging

Vertical timeline format:

| State | Dot Style |
|-------|-----------|
| Completed | `bg-slate-900` |
| Pending | `bg-slate-300` |
| Future | `bg-white border border-slate-200` |

- Action text: `text-xs text-slate-500`
- Timestamp: `text-[10px] text-slate-400`

---

## Do's and Don'ts

| Do | Don't |
|:---|:------|
| `hover:border-slate-200` for interactivity | `hover:bg-indigo-50` or colored highlights |
| `rounded-xl` for cards | Sharp corners or heavy circular borders |
| `text-slate-500` for secondary info | `text-gray-500` (Slate is warmer) |
| `gap-4` or `gap-6` for section spacing | Cramp elements together |
| `shadow-sm` (subtle) | Heavy shadows (`shadow-md`+) |
| Hide Delete in menus | Show Delete prominently in lists |
| Slide-over panels for list details | Navigate to new page for simple details |
| Inter font only | Mix fonts (Poppins, etc.) |
| Black (`slate-900`) primary buttons | Indigo/Blue primary buttons |
| Monochrome status badges | Colorful red/green/yellow badges |

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| **defensive-ui-flows** | Use alongside this skill. This skill = WHAT (visual design). defensive-ui-flows = HOW (error handling, state management, guard clauses). |
| **code-creation-workflow** | Orchestrator that invokes both UI skills during implementation phase. |

**Location:** `~/.claude/skills/courierflow-ui-standards/` — available to all projects using code-creation-workflow.

---

## Avoiding Generic "AI Slop" Aesthetics

When generating new UI (not modifying existing components), actively avoid the common patterns that make AI-generated interfaces look generic and undistinctive. These guidelines are adapted from Anthropic's [Prompting for Frontend Aesthetics](https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics) cookbook.

**CourierFlow uses Inter intentionally** — it's a design system choice, not a default. But other AI-slop signals still apply:

| AI Slop Signal | CourierFlow Fix |
|----------------|-----------------|
| Evenly-distributed timid palettes | Slate-dominant with sharp Indigo sparks — commit to the monochrome |
| Predictable cookie-cutter layouts | Three distinct layout patterns (Sidebar+Canvas, Split View, Slide-Over) — pick the right one for the context |
| Heavy containers competing with content | Content is king — `bg-white` cards recede, spacing does the work |
| Scattered micro-interactions | Functional animations only, 150-300ms, consistent easing |
| Solid flat backgrounds with no depth | Layer slate tints: `bg-slate-50` page → `bg-white` cards → `border-slate-100` separation |
| Generic status indicators | Monochrome badges with weight/border variation, not traffic-light colors |

### Typography Weight & Size Contrast

AI defaults to timid weight differences (400 vs 600). CourierFlow uses decisive contrast:
- **Page Titles:** `text-xl font-semibold` (bold, large)
- **Section Headers:** `text-xs font-semibold uppercase tracking-wider` (tiny but commanding)
- **Body Text:** `text-sm text-slate-600` (recedes)
- **Helper Text:** `text-xs text-slate-400` (barely visible)

The jump between section headers and page titles is 3x+ in size. This hierarchy guides attention without decoration.

### Motion: Less is More

- **One well-orchestrated transition** beats scattered animations
- Slide-over panels: single smooth entrance (200ms ease-out)
- Hover states: border color transition only (`transition-colors duration-150`)
- Loading states: subtle pulse, not spinner → content swap
- **Never animate** layout shifts, color changes on static elements, or decorative particles

---

## Quick Checklist

Before committing UI code:

- [ ] Using Inter only (no Poppins)?
- [ ] Primary buttons are `bg-slate-900` (black)?
- [ ] Secondary buttons are outline style?
- [ ] Status badges are monochrome?
- [ ] Cards use `rounded-xl border-slate-100 shadow-sm`?
- [ ] Page background is `bg-slate-50`?
- [ ] Using Slate palette (not gray)?
- [ ] Spark color (Indigo) only for checkboxes/focus rings?
- [ ] Correct layout pattern (Sidebar+Canvas vs Split vs Slide-over)?
- [ ] Any `repeat(N, 1fr)` grid? Switch to `repeat(N, minmax(0, 1fr))` to prevent content-driven column inflation.
- [ ] Grid used for tabular/calendar layout? Ensure `grid-auto-rows` is set to prevent uneven row heights.
- [ ] Typography hierarchy uses 3x+ size jumps (not timid 1.5x increments)?
- [ ] Animations are functional (150-300ms), not decorative?
- [ ] New layouts avoid cookie-cutter patterns — is this the right layout type for the context?
