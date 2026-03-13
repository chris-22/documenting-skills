# TC3: Wiki Publishing from Existing Documentation

## Prompt

```
Publica la documentación existente en docs/ al GitHub Wiki del proyecto.
```

## Context

- A master document already exists in `docs/` (e.g., `docs/INTEGRATIONS.md`)
- The wiki repo directory exists at `{repo-name}-wiki/` or `{repo-name}.wiki/`
- No new documentation generation is needed, only publishing

## Expected Output

1. **Home.md** in the wiki repo — landing page with project info and links
2. **Content page(s)** — adapted from the master document
3. **_Sidebar.md** — navigation with anchor links

## Assertions

- [ ] `Home.md` contains project title, version, technology stack table
- [ ] `Home.md` contains `[[Page Name]]` wiki links to content pages
- [ ] `Home.md` contains a summary table of integrated systems
- [ ] Content page headings generate valid GitHub Wiki anchors (kebab-case)
- [ ] `_Sidebar.md` contains `[[Home]]` link
- [ ] `_Sidebar.md` contains section links in format `[Section Title](PageName#anchor)`
- [ ] ` ```mermaid ` blocks from the source document are preserved (not converted to HTML)
- [ ] User was informed of generated files and told to review before committing
- [ ] No automatic `git commit` or `git push` was executed
- [ ] Anchor links in `_Sidebar.md` match actual headings in the content pages
- [ ] If wiki repo was not found, user was instructed how to clone it
