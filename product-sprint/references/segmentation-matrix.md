# Customer Segmentation Matrix

A framework for mapping potential users on two behavioral axes to identify distinct customer segments, estimate their distribution, and design tailored offerings for each.

## Why This Works

Single-persona thinking ("our user is...") misses the diversity within a market. A 2-axis matrix forces you to see 4-9 distinct segments, estimate which are biggest, and design for each — preventing the common trap of building for one archetype while ignoring profitable adjacent segments.

## The Framework

### Step 1: Choose Two Behavioral Axes

Pick two dimensions that meaningfully divide your users. The axes should be:
- **Observable** — you can tell which segment someone belongs to from their behavior
- **Actionable** — different positions on the axis imply different product needs
- **Independent** — the axes shouldn't be proxies for the same thing

**Common axis pairs by domain:**

| Domain | Axis 1 | Axis 2 |
|--------|--------|--------|
| Consumer app | Casual ↔ Power user | Solo ↔ Social |
| B2B tool | Self-serve ↔ High-touch | Single user ↔ Team |
| Marketplace | Browser ↔ Buyer | Price-driven ↔ Quality-driven |
| Content platform | Consumer ↔ Creator | Niche ↔ Broad interest |
| Community/venue | Dedicated ↔ Explorer | Introvert ↔ Extrovert |
| Education | Beginner ↔ Advanced | Structured ↔ Self-directed |

### Step 2: Build the Grid

Create a 3x3 grid (or 2x2 for simpler markets). For each cell:

```
## [Segment Name] — [Axis1 position] x [Axis2 position]

**Who they are**: [1-sentence description]
**What they need**: [Primary need from the product]
**How they discover you**: [Acquisition channel]
**Estimated %**: [Percentage of total addressable users]
**Retention driver**: [What keeps them coming back]
```

### Step 3: Estimate Distribution

Assign percentages to each segment. These should:
- Sum to 100%
- Be informed by Stage 1 research (forum demographics, survey data, competitor user bases)
- Identify which 2-3 segments represent the bulk of your market
- Flag any segment that's <5% — consider whether it's worth designing for

### Step 4: Design Per-Segment Offerings

For each major segment (>10%), define:
- **Core offering**: The must-have that serves this segment
- **Discovery path**: How they find and try the product
- **Upgrade trigger**: What converts them from free/trial to paying/committed
- **Churn risk**: What makes them leave

This output feeds directly into the PRD's feature prioritization — features serving the largest segments get Must-Have status.

## Example: Board Game Cafe (from real case study)

**Axes**: Dedicated (one game) ↔ Explorer (many games) x Introvert ↔ Extrovert

| | Introvert | Ambivert | Extrovert |
|---|---|---|---|
| **Dedicated** | Silent Strategist (solo practice, tournament prep) | League Regular (weekly game night, same group) | Competitive Socializer (tournaments as social events) |
| **Balanced** | Quiet Sampler (tries new games with close friends) | Flexible Regular (mix of favorites and new finds) | Group Organizer (brings friends, tries everything) |
| **Explorer** | Solo Discoverer (browses, plays solo/2p) | Social Explorer (open to any table, any game) | Event Hopper (every theme night, every event) |

Each segment got: estimated %, a tailored event type, and a retention hook.

## Common Patterns

**The "Flexible Regular" is usually your biggest segment.** Most markets have a moderate middle — don't over-design for extremes.

**Edge segments are your evangelists.** The "Competitive Socializer" or "Solo Discoverer" may be small but they create content, bring friends, and define your brand.

**Two segments often share infrastructure.** Look for segments that can be served by the same feature with minor customization — this reduces build scope.
