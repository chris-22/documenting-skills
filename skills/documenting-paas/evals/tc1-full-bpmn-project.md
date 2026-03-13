# TC1: Full BPMN Project Documentation

## Prompt

```
Documenta este proyecto con todas sus integraciones. Quiero documentación técnica completa
incluyendo wiki y HTML.
```

## Context

- Project has `pom.xml` with Quarkus + Kogito dependencies
- At least one `.bpmn` file with Service Tasks, gateways, error boundary events
- Multiple REST client configurations in `application.properties`
- `Dockerfile`, `deployment.yaml`, `.chart/values*.yaml` present
- `.github/workflows/` with CI/CD pipelines

## Expected Output

1. **Master document** saved in `docs/` as `.md`
2. **Wiki files**: `Home.md`, `_Sidebar.md`, at least one content page in the wiki repo
3. **HTML file** saved in `docs/` as `.html`

## Assertions

- [ ] Master document contains `## 1. Architecture Overview` with a ` ```mermaid ` block
- [ ] Master document contains at least one DTO table with columns: Field | Type | Description
- [ ] Master document contains a process flow diagram with gateways (diamond shapes `{}`)
- [ ] Master document contains an Event/Code Catalog table
- [ ] Master document contains Environment Configuration table with CERT/PRE/PRO columns
- [ ] Master document contains at least 3 Mermaid diagrams (architecture, flow, data flow)
- [ ] Master document contains JSON examples for each documented endpoint
- [ ] Wiki `Home.md` contains `[[Display Text|Page-Name]]` wiki-style links (display text FIRST, page name SECOND)
- [ ] Wiki `_Sidebar.md` contains `[[Display Text|Page-Name]]` links to all content pages
- [ ] Wiki has >=10 separate `.md` files (Home + Sidebar + Architecture + Entry Point + Security + Systems + BPMN + Config + Errors)
- [ ] Each wiki content page starts with breadcrumb `← [[Home]]`
- [ ] Wiki page headings use `#` (H1) without section numbers
- [ ] HTML file contains `<pre class="mermaid">` blocks
- [ ] HTML file references Mermaid JS CDN with pinned version
- [ ] All Java class names in the document match actual source code
- [ ] Progress checklist was used to track phase completion
