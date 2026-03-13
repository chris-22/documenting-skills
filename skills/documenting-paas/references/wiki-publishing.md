# Wiki Publishing Guide

Detailed guide for publishing technical documentation to GitHub Wiki.

## Table of Contents

- [1. Wiki Repository Structure](#1-wiki-repository-structure)
- [2. Naming Conventions](#2-naming-conventions)
- [3. Home.md Template](#3-homemd-template)
- [4. _Sidebar.md Template](#4-_sidebarmd-template)
- [5. Mermaid in GitHub Wiki](#5-mermaid-in-github-wiki)
- [6. Language](#6-language)
- [7. Publishing Workflow](#7-publishing-workflow)

---

## 1. Wiki Repository Structure

The GitHub wiki is a separate Git repository linked to the main repository.

- **Clone URL**: `https://github.com/{org}/{repo}.wiki.git`
- **Recommended location**: clone alongside the main repo in the same parent directory
  ```
  parent-directory/
  ├── repo-name/           # Main repository
  └── repo-name.wiki/      # Wiki repository
  ```
- **Required files**:
  - `Home.md` — Wiki landing page
  - `_Sidebar.md` — Sidebar navigation
- **Content files**: one `.md` page per main section/topic

### Detecting if the wiki already exists

Look in the parent directory of the main repo for a directory with suffix `.wiki` or `-wiki`:
- `{repo-name}.wiki/`
- `{repo-name}-wiki/`

If it does not exist, instruct the user:
```bash
cd <parent-directory>
git clone https://github.com/{org}/{repo}.wiki.git
# or if the wiki already exists with a different name:
git clone https://github.com/{org}/{repo}.wiki.git {repo}-wiki
```

---

## 2. Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Page files | PascalCase or Title-Case `.md` | `Technical-Documentation.md`, `Architecture.md` |
| Inter-page links | `[[Page Name]]` (no extension) | `[[Integrations]]` |
| Section links | `[Display Text](PageName#anchor)` | `[Security](Integrations#3-security---stssos)` |
| Anchors | Auto-generated from headings in kebab-case | `## My Section` → `#my-section` |

### Anchor generation rules

GitHub generates anchors from headings following these rules:
1. Convert to lowercase
2. Replace spaces with hyphens `-`
3. Remove special characters except hyphens
4. Parentheses, periods, commas are removed
5. Multiple hyphens are preserved (e.g., `---` in the heading → `---` in the anchor)
6. Accents are removed (e.g., `Visión` → `vision`)

**Examples**:
- `## 1. Architecture Overview` → `#1-architecture-overview`
- `## 3. Security — STS/SOS` → `#3-security--stssos`
- `## 4. System 1 — GBO Entities` → `#4-system-1--gbo-entities`

---

## 3. Home.md Template

```markdown
# {Project Name}

**Project**: `{artifact-id}`
**Version**: {version}
**Stack**: {stack description}

{Brief description of what the project does, its purpose, and main capabilities.}

---

## Available Documentation

| Page | Description |
|---|---|
| **[[Architecture]]** | Architecture overview, backend JARs, Mermaid architecture diagram |
| **[[Process-Entry-Point]]** | REST endpoint, DTOs, JSON examples, BPMN process variables |
| **[[Security]]** | Auth flow, REST clients, sequence diagram, cache config |
| **[[System-N-{Slug}]]** | One page per integrated system (identical structure) |
| **[[BPMN-Process-Flow]]** | BPMN flow diagram, evaluation script, event codes catalog |
| **[[Environment-Configuration]]** | URLs per env, K8s deployment, Docker, DB, messaging |
| **[[Error-Handling]]** | BPMN error types, error flow diagrams, EventInfo constants |

## Technology Stack

| Component | Version |
|---|---|
| {Framework} | {version} |
| {Runtime} | {version} |
| {Database} | {version} |
| {Messaging} | {version} |
| {Container} | {version} |

## Integrated Systems

| System | Type | Description |
|---|---|---|
| {System A} | REST API | {Brief description} |
| {System B} | REST API | {Brief description} |
| {System C} | Message Queue | {Brief description} |
```

---

## 4. _Sidebar.md Template

```markdown
**[[Home]]**

---

**[[Page Name]]**

- [1. Section One](PageName#1-section-one)
- [2. Section Two](PageName#2-section-two)
- [3. Section Three](PageName#3-section-three)
  - [3.1 Subsection](PageName#31-subsection)
- [4. Section Four](PageName#4-section-four)

---

**[[Another Page]]**

- [1. Section](AnotherPage#1-section)
```

### Rules for _Sidebar.md

1. Each main page as a bold heading with `[[Wiki Link]]`
2. `---` separator between pages
3. Subsections as indented list with direct links to anchors
4. Maximum 2 indentation levels for readability
5. Only include main sections (`##`), not minor subsections (`####`)

---

## 5. Mermaid in GitHub Wiki

` ```mermaid ` blocks render natively in GitHub Wiki since 2022.

**Requirements**:
- Mermaid code must be in a fenced code block with `mermaid` language hint
- No additional plugins or configuration needed
- Diagrams render as inline SVG

**Known limitations**:
- Very large diagrams (>50 nodes) may not render
- Some Mermaid themes may not work (use `default`)
- `securityLevel: 'loose'` is not supported on GitHub (does not affect most diagrams)

**Verification**: After pushing, open the wiki in the browser and confirm all diagrams display correctly.

---

## 6. Language

Generate the Wiki in the **same language chosen by the user** for the master document (`docs/DOCUMENTACION-TECNICA.md`). All outputs (master doc, Wiki, HTML) must be consistent in language. Rules:

1. All headings, descriptions, notes, and comments must be in the user's chosen language
2. Keep technical names untranslated: Java classes, configKeys, field names, event codes
3. Example JSONs remain identical (they are language-agnostic)
4. DTO table field names stay in their original language (Java field names are not translated)
5. Do NOT translate the Wiki to a different language than the master document — consistency across all outputs is mandatory

---

## 7. Publishing Workflow

1. **Verify** that the wiki directory exists and has write access
2. **Generate/update** `Home.md` with the project information
3. **Generate/update** content pages from the master document (`docs/DOCUMENTACION-TECNICA.md`)
4. **Generate/update** `_Sidebar.md` with links to all sections
5. **Validate** that all anchor links are correct
6. **Inform the user** of the created/updated files so they can review and run:
   ```bash
   cd {repo}.wiki/
   git add .
   git commit -m "Update technical documentation"
   git push origin master
   ```

> **NOTE**: Never commit/push automatically. Always inform the user and let them review and push manually.
