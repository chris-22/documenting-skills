# TC5: HTML-only Export from Existing Documentation

## Prompt

```
Convierte docs/INTEGRATIONS.md a un HTML standalone con diagramas Mermaid renderizados.
```

## Context

- A master document already exists at `docs/INTEGRATIONS.md`
- The document contains Mermaid diagram blocks
- No new documentation generation is needed, only HTML export (Phase 7)

## Expected Output

1. **HTML file** saved in `docs/` as `.html`
2. No wiki files generated or modified
3. No new Markdown documentation generated

## Assertions

- [ ] HTML file is generated at `docs/{artifact-id}-documentation.html` or similar path
- [ ] HTML file contains `<pre class="mermaid">` blocks converted from ` ```mermaid ` source
- [ ] HTML file references Mermaid JS CDN (`https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js`)
- [ ] HTML file includes GitHub-like CSS styling
- [ ] HTML file has a table of contents with internal anchor links
- [ ] HTML file includes header metadata (project name, date)
- [ ] No files created or modified in `{repo}.wiki/`
- [ ] No new `.md` files created in `docs/` (only `.html`)
- [ ] Script `scripts/md-to-html.py` was used OR equivalent direct HTML generation was performed
- [ ] User was informed of the output file location
