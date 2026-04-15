# Prototype Patterns

Patterns for generating functional UI prototypes from a PRD. Two formats: React + Tailwind (artifact-ready) and standalone HTML/CSS (browser-ready).

## General Principles

1. **Prototype MUST-HAVE features only** — the PRD's MoSCoW priorities determine scope
2. **Realistic sample data** — use plausible names, numbers, dates. Never lorem ipsum.
3. **Visual hierarchy = feature priority** — Must-Have features get primary placement, Should-Have features appear smaller or grayed out as "coming soon"
4. **PRD-driven visual cues** — if the PRD emphasizes privacy, show a "Local Processing" badge. If it emphasizes speed, show a latency metric. The prototype should visually prove the value proposition.
5. **Interactive where meaningful** — toggle states, sample data, hover effects. Not animation for animation's sake.

## React + Tailwind Pattern

Self-contained component that works in Claude artifacts or can be pasted into CodeSandbox/v0.dev.

### Structure
```jsx
import React, { useState } from 'react';

// Self-contained — no external dependencies beyond React + Tailwind
export default function ProductDashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  // Sample data — realistic, not placeholder
  const sampleData = {
    // ... derived from PRD
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with product name + key value prop badge */}
      <header className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">[Product Name]</h1>
          {/* PRD-driven badge */}
          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
            [Value Prop Badge — e.g., "100% Local Processing"]
          </span>
        </div>
      </header>

      {/* Main dashboard — Must-Have features get cards */}
      <main className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* One card per Must-Have feature */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-medium text-gray-900">[Feature Name]</h3>
          <p className="text-3xl font-bold mt-2">[Key Metric]</p>
          <p className="text-sm text-gray-500 mt-1">[Context]</p>
        </div>

        {/* Should-Have features — shown but subdued */}
        <div className="bg-white rounded-lg shadow p-6 opacity-60">
          <h3 className="font-medium text-gray-400">[Coming Soon Feature]</h3>
          <span className="text-xs bg-gray-100 px-2 py-1 rounded">Coming Soon</span>
        </div>
      </main>
    </div>
  );
}
```

### Key Tailwind patterns
- `bg-gray-50` for page background, `bg-white` for cards
- `shadow` for elevation, `rounded-lg` for card corners
- `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3` for responsive grid
- Status badges: `bg-green-100 text-green-700` (positive), `bg-red-100 text-red-700` (alert), `bg-blue-100 text-blue-700` (info)

## HTML/CSS Standalone Pattern

Single file that opens directly in any browser.

### Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Product Name] — Prototype</title>
  <style>
    /* CSS custom properties for easy theming */
    :root {
      --bg-primary: #f9fafb;
      --bg-card: #ffffff;
      --text-primary: #111827;
      --text-secondary: #6b7280;
      --accent: #059669;
      --accent-light: #d1fae5;
      --border: #e5e7eb;
      --shadow: 0 1px 3px rgba(0,0,0,0.1);
      --radius: 8px;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: var(--bg-primary); color: var(--text-primary); }

    .dashboard { max-width: 1200px; margin: 0 auto; padding: 24px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
    .card { background: var(--bg-card); border-radius: var(--radius); box-shadow: var(--shadow); padding: 24px; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 0.875rem; }
    .badge-accent { background: var(--accent-light); color: var(--accent); }
    .coming-soon { opacity: 0.5; }
  </style>
</head>
<body>
  <header style="background: var(--bg-card); border-bottom: 1px solid var(--border); padding: 16px 24px;">
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
      <h1 style="font-size: 1.25rem;">[Product Name]</h1>
      <span class="badge badge-accent">[Value Prop Badge]</span>
    </div>
  </header>

  <main class="dashboard">
    <div class="grid">
      <!-- Must-Have feature cards -->
      <div class="card">
        <h3>[Feature Name]</h3>
        <p style="font-size: 2rem; font-weight: bold; margin-top: 8px;">[Key Metric]</p>
        <p style="color: var(--text-secondary); font-size: 0.875rem;">[Context]</p>
      </div>

      <!-- Should-Have — coming soon -->
      <div class="card coming-soon">
        <h3 style="color: var(--text-secondary);">[Coming Soon Feature]</h3>
        <span class="badge" style="background: #f3f4f6; color: var(--text-secondary);">Coming Soon</span>
      </div>
    </div>
  </main>

  <script>
    // Minimal interactivity — toggle states, sample data updates
  </script>
</body>
</html>
```

## Dashboard Widget Patterns

Common widgets to include based on PRD feature types:

| Feature Type | Widget | Example |
|-------------|--------|---------|
| Monitoring/status | Status card with indicator | Door Status: Open/Closed with green/red dot |
| Metrics/analytics | Number + trend arrow | "Power: 145W ↓ 12% this week" |
| Control/settings | Toggle or slider | "Smart Mode: ON/OFF" |
| Alerts/notifications | Badge count + list | "3 items expiring soon" |
| Chat/AI interface | Input field + message bubbles | "Ask about recipes..." |
| Timeline/history | Compact event list | "2:30 PM — Door opened" |

## Checklist Before Delivery

- [ ] Every Must-Have feature from PRD has a visible UI element
- [ ] Sample data is realistic and consistent (dates make sense, names are plausible)
- [ ] Value proposition is visually reinforced (badge, metric, or visual cue)
- [ ] Responsive — works on mobile and desktop
- [ ] No lorem ipsum anywhere
- [ ] No Should-Have features promoted to primary position
