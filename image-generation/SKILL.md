---
name: image-generation
description: Optimizes image generation prompts using Subject-Context-Style structure. Use when generating images, creating illustrations, photos, visual assets, editing images, or crafting prompts for any image generation model (Gemini, GPT Image, DALL-E, Flux, Stable Diffusion, Midjourney, etc.).
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# Image Generation Prompt Guide

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Enhance every image generation prompt around three core elements: **Subject**, **Context**, and **Style**. Return the enhanced prompt as a single flowing paragraph.

## Prompt Structure

### 1. SUBJECT (What)

- Physical characteristics: textures, materials, colors, scale
- Actions, poses, expressions if applicable
- Distinctive features that define the subject

### 2. CONTEXT (Where/When)

- Setting, background, spatial relationships (foreground, midground, background)
- Time of day, weather, atmospheric conditions
- Mood and emotional tone of the scene

### 3. STYLE (How)

- Artistic or photographic approach: reference specific artists, movements, or styles
- Camera/lens choices: specify focal length, aperture, and shooting angle when photographic

## Core Principles

- **Preserve intent** — Add visual details (lighting, texture, composition) only in areas the user left unspecified; keep all user-specified elements unchanged
- **Positive descriptions only** — Describe what should be present; rephrase any exclusion as an inclusion
- **Specific over vague** — "golden hour sunlight at 15 degree angle" beats "nice lighting"
- **Natural flow** — Weave elements into a single flowing description, not a bullet list

## Enhancement Patterns

### Hyper-Specific Details

Add concrete visual details for any Subject/Context/Style element not specified by the user:

- Lighting: direction, quality, color temperature, shadow behavior
- Textures: surface materials, weathering, reflectivity
- Atmosphere: particulates, humidity, depth haze
- Scale: relative sizes, distances, proportions

### Camera Control Terminology

When a photographic look is appropriate:

- Lens type: "shot with 85mm portrait lens", "wide-angle 24mm"
- Aperture: "shallow depth of field at f/1.8", "deep focus at f/11"
- Angle: "low angle emphasizing height", "bird's eye view"
- Motion: "motion blur on the paws", "frozen mid-action"

### Atmospheric Enhancement

Convey mood through environmental details:

- Emotional tone with visual indicators: "serene (soft diffused light, muted palette)", "ominous (low contrast, heavy shadows, desaturated)", "jubilant (high saturation, warm tones, dynamic motion)"
- Weather/air: "morning mist", "dust particles in a sunbeam"

### Text in Images

When the image should contain readable text (signs, labels, titles, typography):

- Specify exact text content in quotes: `"OPEN 24 HOURS" in bold sans-serif`
- Describe visual treatment: font style, weight, size relative to the scene
- Define placement and integration: "centered on the storefront awning", "hand-lettered on the chalkboard"

## Feature Patterns

### Character Consistency

When the same character must be recognizable across multiple images:

- Include at least 3 recognizable visual markers (distinctive scar, signature clothing, unique hairstyle, characteristic accessory)
- Use anchoring words: "distinctive", "signature", "always wears", "always has"
- Be specific: "round tortoiseshell glasses" not just "glasses"

### Compositional Integration

When combining multiple visual elements in one scene:

- Define spatial relationships with proportions: "foreground (40% of frame)", "midground", "background"
- Define how elements interact: overlap, reflection, shared lighting, color echo between foreground and background
- Specify relative scale and interaction between elements

### Real-World Accuracy

When depicting real places, cultures, or historical elements:

- Use specific terminology: "traditional Edo-period architecture", "authentic Moroccan zellige tilework"
- Include culturally accurate details
- Reference geographical or historical specifics

### Purpose-Driven Enhancement

Tailor the prompt to the intended use:

| Purpose | Emphasis |
|---------|----------|
| Product photo | Clean background, studio lighting, commercial appeal |
| UI mockup | Flat design elements, consistent spacing, screen-appropriate |
| Presentation slide | Bold composition, clear focal point, text-friendly layout |
| Social media | Eye-catching, vibrant, crop-friendly aspect ratio |
| Book/album cover | Typography space, dramatic mood, symbolic elements |

## Image Editing

When modifying an existing image:

- **Preserve** the original's core characteristics: color palette, lighting style, composition
- Use anchoring phrases: "maintain the existing...", "preserve the original...", "keep the same..."
- Be specific about what to change vs what to keep unchanged
- Describe modifications relative to the existing image, not from scratch

## Guardrails

- When user intent is unclear between photographic and illustrative style, ask before enhancing
- When enhancement would significantly change the user's concept, present the original interpretation alongside the enhanced version
- When cultural or historical accuracy cannot be verified, flag the uncertainty rather than guessing
- Never generate prompts for content depicting real individuals without explicit user confirmation
- Respect platform-specific content policies — note any restrictions the target model may have

## Tool Selection

When the user needs actual image generation (not just prompt optimization), recommend based on output type:

| Output type | Recommended tool | Notes |
|-------------|-----------------|-------|
| Photos, illustrations | Gemini (mcp-image MCP) | Built-in prompt optimization via Subject-Context-Style |
| Vector graphics, icons, flat design | Recraft (AgentPatch) | Best for SVG-style, icon sets, flat vector output |
| Any model (prompt only) | This skill | Enhance prompts for whatever tool is already available |

- **mcp-image** (`npx -y mcp-image`): Gemini-powered, auto-enhances prompts, 3 quality tiers, image editing, 4K output. Requires `GEMINI_API_KEY`.
- **AgentPatch** (`pip install agentpatch`): Recraft-powered, supports realistic photos + vector/icon styles. Free credits on signup. Requires `AGENTPATCH_API_KEY`.

If no generation tool is connected, this skill still improves prompts for any external image model.

## Out of Scope

This skill does NOT:
- Generate the image itself when no generation tool is connected—it only optimizes the prompt for an external model.
- Produce architecture or workflow diagrams—use `excalidraw` or `excalidraw-canvas`.
- Run UI/UX visual audits of an existing app—use `design-audit`.
- Set up Sentry, observability, or any non-image tooling—out of domain.
- Generate prompts depicting real, identifiable individuals without explicit user confirmation—ask the user first.

## Example

**Input:** "A happy dog in a park"

**Enhanced:** "Golden retriever mid-leap catching a red frisbee, ears flying, tongue out in joy, in a sunlit urban park. Soft morning light filtering through oak trees creates dappled shadows on emerald grass. Background shows families on picnic blankets, slightly out of focus. Shot from low angle emphasizing the dog's athletic movement, with motion blur on the paws suggesting speed."
