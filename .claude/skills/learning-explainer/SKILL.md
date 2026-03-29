---
name: learning-explainer
description: Research a topic and build a self-contained interactive HTML explainer for the learning repo at ~/repos/learning. Follows the existing SPA pattern (sidebar, MathJax, Plotly, seeded PRNG, lazy-init sections). Use when the user wants to add a new topic explainer page to the learning site.
origin: local
---

# Learning Explainer

Build a new interactive HTML explainer page in `~/repos/learning`, following the exact template used by existing pages.

## When to Activate

- User says "add a topic to the learning site / repo"
- User says "create an explainer for X"
- User says "new learning page for X"
- User invokes `/learning-explainer`

## Before Starting — Confirm Two Things

**Always confirm before doing any work:**

1. **Subject type (field directory):** Infer from the topic (e.g. "Fourier analysis" → `math`, "sorting algorithms" → `cs`, "transformer architecture" → `ml`). State your inference and ask the user to confirm or correct. Common fields in this repo: `math`, `cs`, `ml`, `physics`.

2. **Date:** Use today's date (`YYYYMMDD` format from the system) unless the user explicitly provides a different date.

Then immediately proceed — do not wait for a second confirmation.

## Folder Naming Convention

```
{field}/{YYYYMMDD}_{slug_with_underscores}/index.html
```

Examples:
- `math/20260330_locality_sensitive_hashing/index.html`
- `math/20260327_random_fourier_features/index.html`

The slug is derived from the topic title in snake_case.

## Workflow

### Phase 1 — Parallel Research (3 agents)

Launch three background research agents in parallel. Do NOT wait for them one by one.

```
Agent 1 — History & Theory:
  Research the historical origins, key papers, inventors, and mathematical
  foundations of the topic. Include formal definitions, key theorems, and
  the core theoretical results. Return detailed findings with sources.

Agent 2 — Applications & ML Relevance:
  Research how this topic is used in machine learning and industry practice.
  Include comparisons with alternative approaches, tradeoffs, and modern
  usage (2024-2025). Return detailed findings with sources.

Agent 3 — Visualizations & Intuition:
  Research what visualizations exist or are recommended for building intuition
  on this topic. What interactive demos exist? What geometric/visual intuitions
  matter most? Identify 3-4 concrete visualization ideas suitable for
  implementation as Plotly charts or pure DOM/CSS interactions.
  Return detailed findings with sources.
```

Synthesize all three agents' results into a unified research summary before proceeding.

### Phase 2 — Read Existing Template

Glob for all inner `index.html` files (excluding the root), pick any one or two, and read them to extract the exact template:

```
Glob: **/index.html  (then exclude the root ./index.html)
Read: first ~200 lines of any inner index.html for CSS + HTML structure
Read: last ~100 lines of the same file (or another) for the JS section
```

Extract and reuse:
- CSS custom properties pattern (`--accent`, `--sw`, `--sbg`, etc.)
- Sidebar HTML skeleton (`.sb-logo`, `.nav-btn`, `.home-btn`)
- `nav()`, `tab()`, `toggleSidebar()` JavaScript functions (copy verbatim)
- `initialized` Set + `initSection()` lazy-init pattern
- `mkRng()` Mulberry32 PRNG (copy verbatim)
- `PLT` Plotly config object pattern
- `window.addEventListener('load', ...)` boot pattern
- All CSS utility classes (`.cols`, `.c11`, `.c12`, `.info`, `.warn`, `.success`, `.card`, `.ctrl`, `.btn`, `.tab-bar`, `.tab-pane`, `.metric`, `.caption`, `.pill-*`, etc.)

**Do not invent new patterns.** Copy the skeleton exactly and only change content.

### Phase 3 — Choose Accent Color

Scan the existing inner `index.html` files for CSS variables named `--<topic>` at the top of `:root` to find colors already in use as primary accents. Then pick something visually distinct from all of them. Update `--accent` (or topic-named variable) and all derived rgba values, `.info` box background tint, `.nav-btn.active` background, and `a` link color.

### Phase 4 — Design Sections

Plan 5–7 sidebar sections based on the research. Always include:
- **Section 0 (Overview):** Executive summary, history timeline table, key definition box, complexity/comparison table
- **Middle sections:** Topic-specific math, theory, variants — use tabs where 3+ parallel subtopics exist
- **Visualizations section:** 3–4 interactive Plotly charts or DOM animations (see below)
- **Applications section:** ML/industry uses, tradeoffs table, when-to-use guidance
- **Sources section:** Papers table + learning resource links + cross-links to related pages on this site

### Phase 5 — Build Visualizations

Always include 3–4 interactive visualizations. Prefer:

1. **A geometric/intuitive chart** (Plotly scatter/line showing the core concept visually)
2. **A parameter exploration chart** (Plotly with sliders showing how tuning affects behavior)
3. **A complexity/comparison chart** (Plotly showing scaling or tradeoffs)
4. **A step-through or animated demo** (pure DOM/CSS showing an algorithm pipeline)

Rules:
- Use `mkRng(seed)` for all randomness so charts are deterministic
- Use `Plotly.newPlot` on first render, `Plotly.react` on slider updates
- Use `PLT.layout({...extra})` and `PLT.config` for all charts
- All charts: `height` specified, `responsive: true, displayModeBar: false`
- Lazy-init all chart sections (only initialize when first navigated to)

### Phase 6 — Write the File

Write the complete self-contained `index.html` to `{field}/{YYYYMMDD}_{slug}/index.html`.

File structure requirements:
- `<title>{Topic Name} — Interactive Explainer</title>`
- MathJax config + CDN (`mathjax@3/es5/tex-chtml.js`)
- Plotly CDN (`plotly-2.27.0.min.js`)
- All CSS inline in `<style>` — no external stylesheets
- All JS inline in `<script>` at bottom of `<body>` — no external scripts
- `← Home` link in sidebar pointing to `../../index.html`
- First section (s0) starts `.active` in HTML
- `window.addEventListener('load', ...)` initializes s0 charts and calls `MathJax.typesetPromise()`

Target length: 1,200–2,000 lines. If approaching 2,000 lines, trim prose and simplify one visualization.

### Phase 7 — Commit

After writing the file, commit only the new explainer (never commit the generated top-level `index.html`):

```bash
git add {field}/{YYYYMMDD}_{slug}/index.html
git commit -m "feat: add {topic} interactive explainer

{1-2 sentence description of what the explainer covers}"
```

## HTML Template Skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{Topic} — Interactive Explainer</title>
<script>
MathJax = {
  tex: { inlineMath: [['$','$']], displayMath: [['$$','$$']] },
  options: { skipHtmlTags: ['script','noscript','style','textarea','pre'] }
};
</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
/* CSS — copy base from existing page, change --accent color */
</style>
</head>
<body>
<button id="menu-toggle" aria-label="Toggle menu" onclick="toggleSidebar()">☰</button>
<div id="sidebar-overlay" onclick="toggleSidebar()"></div>
<nav id="sidebar">
  <div class="sb-logo">
    <h2>{emoji} {Short Title}</h2>
    <p>{Full Topic Name}</p>
    <a class="home-btn" href="../../index.html">← Home</a>
  </div>
  <button class="nav-btn active" onclick="nav('s0')">Overview</button>
  <!-- more nav-btn elements -->
</nav>
<main id="main">
  <div id="s0" class="section active"><!-- content --></div>
  <!-- more section divs, all display:none initially -->
</main>
<script>
function mkRng(seed) { /* Mulberry32 — copy verbatim */ }
const PLT = { /* copy verbatim, update accent color */ };
const initialized = new Set();
function nav(id) { /* copy verbatim */ }
function toggleSidebar() { /* copy verbatim */ }
function tab(group, id) { /* copy verbatim */ }
function initSection(id) { /* map section IDs to init functions */ }
/* section-specific init/update functions */
window.addEventListener('load', () => {
  initialized.add('s0');
  initS0();  // initialize first section's charts
  if (window.MathJax) MathJax.typesetPromise();
});
</script>
</body>
</html>
```

## Quality Checklist

Before committing:
- [ ] All 6 sections have substantive content (no placeholder text)
- [ ] All Plotly charts render (IDs match between HTML and JS)
- [ ] `nav()` buttons match section IDs exactly
- [ ] `tab()` group prefixes match tab-pane IDs exactly
- [ ] `initSection()` maps all sections that have charts
- [ ] Home link is `../../index.html` (two levels up)
- [ ] MathJax `$...$` and `$$...$$` used for all math
- [ ] No external CSS/JS dependencies (only MathJax + Plotly CDN)
- [ ] Accent color updated in: CSS variable, `.nav-btn.active` rule, `.info` box tint, `a` link color, `PLT` object, slider `accent-color`
- [ ] `build.py` will discover the folder (confirm `YYYYMMDD_slug` naming)

## Example Invocations

```
/learning-explainer Gaussian Processes
/learning-explainer Principal Component Analysis
/learning-explainer Variational Autoencoders
/learning-explainer The Fast Fourier Transform
/learning-explainer Markov Chain Monte Carlo  date:20260401
```
