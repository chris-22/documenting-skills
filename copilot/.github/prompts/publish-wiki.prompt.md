---
description: "Publish a Markdown document to GitHub Wiki and generate standalone HTML with Mermaid (equivalent to the wiki-html-publisher skill)"
---

# Wiki & HTML Publisher

Publishes Markdown documents to **GitHub Wiki** and generates **standalone HTML** with rendered Mermaid diagrams.

## Instructions

### Input

1. **A Markdown file** (`.md`) to publish
2. **A Git repository** as context (to determine the Wiki org/repo)

If the file is not provided, ask the user.

### Phase 1: Wiki publishing

1. **Detect wiki repo**: Look for `{repo-name}.wiki` in the parent directory. If not found, clone: `git clone https://github.com/{org}/{repo}.wiki.git`
2. **Analyze the Markdown**: Extract title (H1), metadata, sections (H2), content language
3. **Generate `Home.md`**: Wiki landing page with link to the main document
4. **Generate `_Sidebar.md`**: Sidebar navigation with links to all H2 sections
5. **Copy the document** to the wiki repo with appropriate name (kebab-case)
6. **Commit and push**: `git add . && git commit -m "docs: update wiki" && git push`

#### Wiki rules

- Generate everything in the **same language** as the input Markdown
- Anchors follow GitHub Wiki rules: lowercase, hyphens, no special characters
- Internal links with `[[Page-Name]]` syntax

### Phase 2: HTML generation

1. Generate a Python script that converts Markdown to standalone HTML
2. Include Mermaid diagram rendering via mermaid.js CDN
3. The HTML must be self-contained (inline CSS, Mermaid via CDN)
4. Save as `docs/{name}-standalone.html`

### Example prompt

```
Publish docs/ARCHITECTURE.md to the repo wiki
```
