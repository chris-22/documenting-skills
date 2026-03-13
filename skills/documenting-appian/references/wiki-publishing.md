# Phase H — Wiki Publishing + HTML Export (Detailed Instructions)

> **DELEGATED**: This phase is handled by the **`wiki-html-publisher`** skill.
> After completing all documentation phases (A–G) and validation, invoke `wiki-html-publisher` to publish and export.

## Contents
- [How it works](#how-it-works)
- [Wiki page mapping](#wiki-page-mapping)

---

## How it works

1. **Ask the user** if they want to:
   - Publish to **GitHub Wiki** — generates Home.md, _Sidebar.md, content pages, and pushes to `{repo}.wiki`
   - Generate **standalone HTML** — creates a self-contained `.html` with rendered Mermaid diagrams (CDN or offline)
   - Both, or neither

2. **Input file**: Since this skill generates multiple docs, create a consolidated entry point before invoking the publisher:
   - Use `docs/README.md` as the **Wiki Home.md** (it already serves as index)
   - For the Wiki content pages, copy each `docs/appian-*.md` file as individual Wiki pages
   - For HTML export, concatenate or use `docs/README.md` as the primary input (the publisher will generate `docs/{artifact-id}-documentation.html`)

## Wiki page mapping

   | Source file | Wiki page name |
   |---|---|
   | `docs/README.md` | `Home.md` |
   | `docs/01-appian-overview.md` | `01-Overview.md` |
   | `docs/02-appian-glossary.md` | `02-Glossary.md` |
   | `docs/03-appian-inventory.md` | `03-Inventory.md` |
   | `docs/04-appian-architecture.md` | `04-Architecture.md` |
   | `docs/05-appian-navigation.md` | `05-Navigation.md` |
   | `docs/06-appian-data.md` | `06-Data-Model.md` |
   | `docs/07-appian-integrations.md` | `07-Integrations.md` |
   | `docs/08-appian-security.md` | `08-Security.md` |
   | `docs/09-appian-deployment.md` | `09-Deployment.md` |
   | `docs/10-appian-i18n.md` | `10-Internationalization.md` |
   | `docs/11-appian-interfaces.md` | `11-Interfaces.md` |
   | `docs/12-appian-health.md` | `12-Health-Analysis.md` |
   | `docs/process-models/*.md` | `PM-{name}.md` (one per process model) |

4. **Generate `_Sidebar.md`** with links to all pages and their main sections.

5. **Language**: Use the same language as the documentation (match the application's primary language per Authoring conventions).

6. **Update Progress Checklist** with:
   ```
   - [ ] Phase H: Wiki published + HTML exported (via wiki-html-publisher)
   ```
