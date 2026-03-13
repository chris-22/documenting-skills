# HTML Export Guide

Detailed guide for generating standalone HTML with rendered Mermaid diagrams.

## Table of Contents

- [1. Objective](#1-objective)
- [2. Markdown → HTML Conversion Strategies](#2-markdown--html-conversion-strategies)
- [3. Mermaid Rendering](#3-mermaid-rendering)
- [4. Required CSS (GitHub Style)](#4-required-css-github-style)
- [5. Generated HTML Structure](#5-generated-html-structure)
- [6. Output File Location](#6-output-file-location)
- [7. Validation](#7-validation)
- [8. Offline Mode](#8-offline-mode)

---

## 1. Objective

Generate a **self-contained** HTML file that:
- Anyone can open in a browser without needing GitHub
- All Mermaid diagrams render automatically as SVG
- Has GitHub-like styling for professional readability
- Is shareable via email, Confluence, SharePoint, or any medium

---

## 2. Markdown → HTML Conversion Strategies

### Option A: Python Script (preferred)

Use the `scripts/md-to-html.py` script included in the skill:

```bash
pip install markdown
python scripts/md-to-html.py input.md output.html --title "Project Name - Technical Documentation"
```

**Advantages**: Reproducible, automatable, consistent.

### Option B: Direct generation

If Python is not available, generate the HTML directly from the model, manually converting each Markdown element:

| Markdown | HTML |
|---|---|
| `# Heading 1` | `<h1 id="heading-1">Heading 1</h1>` |
| `## Heading 2` | `<h2 id="heading-2">Heading 2</h2>` |
| `**bold**` | `<strong>bold</strong>` |
| `\`code\`` | `<code>code</code>` |
| `\`\`\`json ... \`\`\`` | `<pre><code class="language-json">...</code></pre>` |
| `\`\`\`mermaid ... \`\`\`` | `<pre class="mermaid">...</pre>` |
| `\| table \|` | `<table><tr><td>...</td></tr></table>` |
| `> blockquote` | `<blockquote>...</blockquote>` |
| `---` | `<hr>` |
| `- item` | `<ul><li>item</li></ul>` |
| `[text](url)` | `<a href="url">text</a>` |

### Option C: Pandoc

If `pandoc` is installed:

```bash
pandoc -f markdown -t html --standalone --metadata title="Project Name" -o output.html input.md
```

Then manually inject Mermaid JS and CSS into the generated HTML.

---

## 3. Mermaid Rendering

### Block conversion

Markdown ` ```mermaid ` blocks are converted to:

```html
<pre class="mermaid">
flowchart TD
    A --> B
    B --> C
</pre>
```

> **IMPORTANT**: Do not use `<code>` inside `<pre class="mermaid">`. Mermaid JS looks directly for `<pre class="mermaid">` and renders its content as SVG.

### Loading and initializing Mermaid JS

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose'
  });
</script>
```

- `startOnLoad: true` — Automatically renders all `<pre class="mermaid">` on page load
- `theme: 'default'` — Standard theme, compatible with white background
- `securityLevel: 'loose'` — Allows HTML in node labels (required for `<br/>` in labels)

### Rendering flow

1. Browser loads the HTML
2. Mermaid JS is downloaded from CDN
3. `mermaid.initialize()` executes
4. Mermaid finds all `<pre class="mermaid">`
5. Each block is converted to an inline SVG
6. The original `<pre>` is replaced by the generated `<svg>`

---

## 4. Required CSS (GitHub Style)

The complete CSS is defined in `assets/html-template.html`. Key style rules:

- **Body**: `-apple-system` font stack, `max-width: 980px`, centered
- **Headings**: `h1`/`h2` with bottom border, scaled sizes
- **Tables**: collapsed borders, alternating row backgrounds (`#f6f8fa`)
- **Code**: monospace font, light gray background, `85%` font size
- **Mermaid**: `pre.mermaid` with transparent background (Mermaid renders its own SVG)
- **Blockquotes**: left border accent, muted color
- **Print**: full width, constrained SVGs
- **Responsive**: reduced padding on screens < 768px

> **Source of truth**: `assets/html-template.html` — read it for the full CSS. The `scripts/md-to-html.py` default template contains a minified version as fallback.

---

## 5. Generated HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{PROJECT_NAME} - Technical Documentation</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
  <script>mermaid.initialize({startOnLoad: true, theme: 'default', securityLevel: 'loose'});</script>
  <style>
    /* CSS from section 4 above */
  </style>
</head>
<body>
  <div class="markdown-body">
    <div class="header-meta">
      Generated: {DATE} | Version: {VERSION}
    </div>
    <!-- Converted Markdown content as HTML -->
  </div>
</body>
</html>
```

---

## 6. Output File Location

Save to: `docs/{artifact-id}-documentation.html`

Examples:
- `docs/fundonbdgbpmn-documentation.html`
- `docs/myservice-documentation.html`

---

## 7. Validation

### HTML validation checklist

- [ ] File opens correctly in Chrome/Firefox/Edge
- [ ] All Mermaid diagrams render as SVG (no plain text visible)
- [ ] Tables have borders and are readable
- [ ] JSON/Java code blocks are monospaced
- [ ] Table of contents has functional internal links (scrolls on click)
- [ ] Document is readable on screens from 1024px to 1920px
- [ ] CSS styles are applied correctly (font, colors, spacing)

### Playwright validation (if available)

If browser tools are available:

1. Open the generated HTML in the browser
2. Wait for Mermaid JS to load and render
3. Verify that `<pre class="mermaid">` elements have been converted to `<svg>`
4. Take a screenshot for visual confirmation

---

## 8. Offline Mode

For corporate environments without CDN access:

1. Download Mermaid JS: `https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js` (~2MB)
2. Embed the full JS content inside an inline `<script>` tag
3. The resulting HTML will be heavier (~2MB+) but completely self-contained

**Offer to the user**: "If you need an offline version without CDN dependency, I can embed Mermaid JS directly in the HTML so it works without an internet connection."
