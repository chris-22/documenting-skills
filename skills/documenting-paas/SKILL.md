---
name: documenting-paas
description: >
  Generates exhaustive, high-quality technical documentation for enterprise software projects.
  Use when the user asks to: document a project, generate technical documentation, document
  integrations, document APIs, create architecture docs, generate microservice docs,
  document a BPMN process, publish documentation to GitHub Wiki, generate standalone HTML
  from documentation, export docs to HTML, or any variant of "document this project/service/API"
  — even without explicitly mentioning "technical documentation" or "Mermaid."
  Supports Java projects (Quarkus, Spring Boot), BPMN processes (Kogito/jBPM/BAMOE), REST
  microservices, external system integrations, Kubernetes/AWS/Azure deployments, and CI/CD pipelines.
  NOT for Appian XML exports (use documenting-appian instead).
  NOT for standalone wiki/HTML publishing of existing Markdown files (use wiki-html-publisher instead).
compatibility: >
  Python 3.x with 'markdown' pip package required for HTML export script (Phase 7).
  Optional: Playwright browser tools for HTML validation.
---

# Technical Documentation Generator

7-phase workflow to generate comprehensive technical documentation for enterprise projects.
Phases 1–5 analyze and generate content. Phases 6–7 publish to **GitHub Wiki** and **standalone HTML**.

---

## PHASE 1: DISCOVERY — Exhaustive project analysis

> Refer to `references/analysis-checklist.md` for the complete checklist of items to verify.

Execute the following steps using file reading tools and codebase search:

1. **Build & Dependencies** — Read `pom.xml` / `build.gradle`:
   - Extract groupId, artifactId, version, parent, plugins, profiles.
   - Classify each dependency by role: framework, persistence, messaging, testing, security, code generation.

2. **Existing documentation** — Read `README.md` and all files in `docs/` to capture prior context.

3. **Containerization** — Read `Dockerfile`: base image, JDK version, layer structure, entrypoint.

4. **Application configuration** — Read ALL configuration files (`application.properties`, `application.yml`, `application-{profile}.yml`, `bootstrap.yml`). Extract:
   - Application name (`quarkus.application.name` / `spring.application.name`)
   - REST clients: configKey, URLs per environment (dev/cert/pre/pro)
   - Datasources: DB type, host, schemas, pool configuration
   - Messaging: brokers, topics, serializers, SSL security
   - Cache: engine, cache names, TTLs
   - Security: OIDC, TLS, tokens
   - Logging: categories, levels

5. **BPMN/DMN processes** (if present) — Read ALL `.bpmn` / `.dmn` files. For each process:
   - Process name and process ID
   - Process variables with full Java type (from `itemDefinition[@structureRef]`)
   - Service Tasks: Java interface + method (from `bpmn2:interface` + `bpmn2:operation`)
   - Inputs/Outputs of each Service Task (from `dataInputAssociation` / `dataOutputAssociation`)
   - Gateways: type (exclusive, inclusive, parallel), conditions on sequence flows
   - Error definitions: errorCode of each `bpmn2:error`
   - Boundary error events: which Service Task they catch and where they redirect
   - Subprocesses: hierarchical structure
   - Script Tasks: inline Java/JavaScript code (from `bpmn2:script`)

6. **Java code** — Read ALL files in `src/main/java`:
   - Models/DTOs: fields, types, annotations (`@JsonProperty`, `@Valid`, `@NotNull`, `@VariableInfo`)
   - Resources/Controllers: REST endpoints (`@Path`, `@POST`, `@GET`), request/response types
   - Service Tasks: CDI classes (`@ApplicationScoped`), public methods, parameters, return types
   - Configuration: classes extending frameworks
   - Mappers: MapStruct interfaces

7. **Tests** — Read files in `src/test/java` to understand validated scenarios.

8. **Infrastructure & CI/CD** — Read `deployment.yaml`, `.chart/values*.yaml`, `.github/workflows/*.yml`, `.gluon/ci/properties.env`:
   - Environments (cert/pre/pro), K8s namespaces, clusters, cloud regions
   - Docker image registries
   - Referenced secrets
   - Deployment strategy (Helm, blue-green, etc.)

9. **Mocks** (if present) — Read WireMock mappings in `src/main/resources/wiremock/` to obtain real example JSONs.

10. **OpenAPI specs** (if present) — Read `.yaml`/`.json` in resources for exact schemas.

11. **Deep dependency analysis** (for backend JARs and Service Task dependencies not available as source code):

    > Refer to `references/dependency-resolution.md` for the complete step-by-step workflow (Steps A–F).

    Detect external dependency JARs referenced in BPMN/Java but absent from `src/main/java`. Ask the user whether to resolve them via Maven. Resolution priority: Maven remote (Nexus/JFrog) → local `~/.m2` cache → cloned repo on disk. Always use the **exact version from pom.xml**. Document any unresolvable JARs as gaps.

    > **CRITICAL — MANDATORY GATE**: Step 11 is **NOT optional**. You MUST execute dependency resolution (Steps A–F from `references/dependency-resolution.md`) **before** moving to Phase 2. If external dependencies exist and you skip this step, the generated DTO tables will be incomplete or inferred — which is a quality failure. The workflow is:
    > 1. After steps 1–10, list ALL external dependency JARs detected (groupId:artifactId:version).
    > 2. **Ask the user** if they want Maven resolution (Step B). Do NOT silently skip this.
    > 3. If Yes → resolve via Maven remote → `.m2` cache → cloned repo (Steps D.1–D.3), then analyze with `jar tf` + `javap -p` (Step E).
    > 4. If No → document gaps explicitly (Step F).
    > 5. Only after completing Steps A–F (or the user declining) may you proceed to Phase 2.

---

## PHASE 2: STRUCTURING — Document structure design

> Refer to `references/documentation-templates.md` for templates of each section type.
> Use the base template in `assets/doc-template.md` as the structural skeleton.

1. Select the applicable sections from `assets/doc-template.md` based on Phase 1 findings.

2. The document structure MUST follow the **exact section order** defined in `assets/doc-template.md` (omit only if truly not applicable). The order is: Architecture Overview → Process Entry Point → Security → System N (one per external system) → BPMN Process Flow → Event Code Catalog → Data Flow Map → Environment Configuration → Common Headers → Error Handling.

   > **LANGUAGE NOTE**: The template uses Spanish labels as examples. You MUST translate ALL section headings, descriptions, and labels to the language chosen by the user.

3. **CRITICAL**: Every system section MUST use the **exact same subsection structure** (Descripcion → REST Client Config → Endpoints → Additional Endpoints). No system may omit subsections that others include (except conditional ones marked with `> Solo incluir si...` in the template).

4. If the project has **NO BPMN**: omit BPMN-specific fields (Proceso BPMN, Nombre BPMN, Inputs/Output BPMN, process variables, BPMN flow diagram, evaluation script). Keep all other sections.

5. If the project has **NO external integrations**: focus on domain model, REST API, persistence, and replace system sections with internal component documentation.

6. Present the user with a summary of findings and the proposed structure. Ask whether they want full documentation or focused on a specific aspect.

---

## PHASE 3: ENRICHMENT — High-quality content generation

> Refer to `references/diagram-patterns.md` for proven and validated Mermaid patterns.

1. **DTO tables** — For each DTO/model, generate a table: Campo | Tipo | Descripcion. When a DTO has nested sub-objects, document each sub-DTO as a separate sub-table with its class name in bold (e.g., `**Organization**:`). Always include the full qualified class name as `**Clase**: \`fqn\`` above response DTO tables.

2. **Example JSONs** — For each endpoint, generate **TWO** code blocks:
   - **Request**: For GET endpoints, use an `http` code block showing the full request line + headers. For POST/PUT, use a `json` block with a comment like `// Request real anonimizado - POST /path`.
   - **Response**: Use a `json` block with a comment like `// Respuesta real anonimizada (basada en ejecucion {ENV} {DATE})`.
   - Priority for data: WireMock mocks > real execution data > inferred from DTO with domain-coherent values.
   - JSONs must be **realistic and deep** — include nested objects, arrays, and realistic field values (not `"string"`, `0`, `true`).

3. **Mermaid diagrams**:
   - **Architecture**: `flowchart TD` with subgraphs: Entry → Process → Service Tasks → Backend JARs → API Gateway → External Systems
   - **Process flow**: `flowchart TD` with subgraphs per phase (`FASE1`, `FASE2`...), decision diamonds with conditions on arrows, inclusive/parallel gateway fork+join, error terminators `((""))`
   - **Data flow**: `flowchart TD` with labeled arrows `-- "data" -->` showing inter-system data dependencies
   - **Authentication sequence**: `sequenceDiagram` with `Note over` for cache info
   - **Error flows**: compact `flowchart LR` per error pattern (boundary event → script → event → end)

4. **System section consistency** — Each system section MUST follow the same subsection pattern (translate labels to the user's chosen language):
   - Description (with numbered purposes list)
   - REST Client Configuration (table with 7 fields: configKey, URL DEV, URL PROD, Java Interface, Base path, Service Task, Backend JAR)
   - Endpoints numbered `N.M` with tag `(READ)` / `(WRITE)` (or localized equivalent)
   - Each endpoint: summary table → params → request DTO → response DTO → output service task → decision logic → JSON examples
   - Output Service Task tables always include `eventInfo` | `EventInfo` field
   - Decision logic as bullet list: `condition` → event **CODE** → outcome

5. **BPMN process variables** — Table with columns: Variable | Java Type | Tags | Usage. Tags use: `input, required` for inputs, `internal` for computed variables, `output` or `internal, output` for results. Translate column headers to chosen language.

6. **Event code catalog** — Single consolidated table ordered numerically. Columns: Code | Phase | Meaning | isError | BPMN Log. Bold the code column. Codes must be cross-referenced with system sections. Translate column headers to chosen language.

7. **Contextual notes** — Include `> **NOTE**:` / `> **CRITICAL**:` (or localized equivalent) for limitations, inter-system dependencies, or caveats.

8. **Anonymization** — Internal URLs → `{env}` placeholders, real IDs → realistic fictitious ones, secrets → names without values, PII → anonymized.

---

## PHASE 4: ASSEMBLY — Generate all outputs

This phase produces **TWO sets of outputs simultaneously** from the enriched content:

### 4.1 Master document (monolithic)

Compose a single Markdown file with:
- **Header**: proyecto, version, stack, dependencia service tasks, fecha de generacion
- **Tabla de Contenidos**: numbered list with internal anchor links matching section titles
- **Heading levels**: `##` for main sections (numbered), `###` for subsections, `####` for endpoint sub-sections
- **Tables**: aligned Markdown tables with `Field | Value` for config and `Field | Type | Description` for DTOs (adapt column headers to chosen language)
- **Code blocks**: always with language hint (`json`, `http`, `java`, `properties`, `mermaid`)
- **JSON comments**: annotate with `//` comments indicating source. Adapt to the chosen language.
- **Section separators**: `---` between every main `##` section
- **Footer note**: `> **NOTE**:` explaining DTO source and JSON example limitations

Save as `docs/DOCUMENTACION-TECNICA.md`.

> **NAMING RULE**: Always use `DOCUMENTACION-TECNICA.md`. Do NOT use narrower names like `INTEGRATIONS.md` because the document covers more than integrations alone.

### 4.2 Wiki pages (multi-page)

Generate **individual Markdown files** in `docs/wiki/`, one per topic. Do NOT copy or extract from the master doc — generate each page directly with content adapted for wiki consumption:

- **No section numbers** in headings (e.g., `# Seguridad` not `## 3. Seguridad`)
- **No TOC** (the sidebar provides navigation)
- **Wiki links** instead of anchor links: `[[Display Text|Page-Name]]` (display text FIRST, page name SECOND)
- **Breadcrumb** at top of each page: `← [[Home]]`
- **Cross-page references** use wiki syntax: `[[LoanIQ|System-2-LoanIQ]]`, `[[catálogo de eventos|BPMN-Process-Flow]]`

The page mapping follows the structure defined in Phase 6.

### 4.3 Common rules

1. **Consistency** — Every system section follows **EXACTLY** the same subsection structure. Verify by comparing subsection headings.
2. **Self-contained** — A new developer must fully understand the project from these documents alone.
3. **Language** — Generate ALL outputs in the **language chosen by the user**. If not yet specified, **ask before generating**. Technical terms, Java class names, configKeys, and code remain in their original language.

---

## PHASE 5: VALIDATION — Quality verification

> Refer to `references/quality-criteria.md` for the complete checklist.

1. **Completeness**:
   - Does each endpoint have HTTP method, path, DTOs, and JSON example?
   - Is each BPMN Service Task documented with inputs, outputs, and decision logic?
   - Do all Mermaid diagrams have valid syntax?
   - Do DTO tables include all fields with correct types?
   - Is there at least one architecture diagram, one flow diagram, and one data diagram?
   - Are environments documented with URLs?
   - Are error patterns explained with flow diagrams?
   - Does the table of contents reflect all sections?

2. **Consistency**:
   - Java class names match the source code
   - REST client configKeys match application.properties
   - Event codes match between the catalog and each system's sections

3. **Transparency** — Inform the user of any detected gaps (e.g., "Could not access the backend JARs generated from OpenAPI; the DTOs shown are inferred").

4. **Feedback loop** — For each failed criterion, return to Phase 3 or 4 to fix, then re-execute Phase 5 validation. Repeat until all applicable criteria pass or gaps are documented as unfixable.

5. **Resuming after interruption** — If the session is interrupted mid-workflow:
   - Check `docs/` for existing `DOCUMENTACION-TECNICA.md` → if present, Phases 1–4.1 are done.
   - Check `docs/wiki/` for existing pages → if present, Phase 4.2 is done.
   - Check the Progress Checklist (if the user provides it) to identify the last completed phase.
   - Resume from the next incomplete phase. Do NOT re-generate already completed outputs unless the user explicitly asks.

---

## PHASE 6: WIKI PUBLISHING — Multi-page structure

The Wiki uses a **multi-page structure** (one `.md` per topic). The wiki pages are generated directly in Phase 4.2 — this phase defines the structure and rules they must follow, and handles publishing to the wiki repo.

### 6.1 Page mapping

Generate separate Wiki pages following this mapping:

| Wiki Page | Source Sections | Content |
|---|---|---|
| `Home.md` | (generated) | Project overview, tech stack table, systems summary table, `[[links]]` to all pages |
| `Architecture.md` | §1 | Architecture overview + Mermaid architecture diagram + backend JARs table |
| `Process-Entry-Point.md` | §2 | REST endpoint, DTOs, JSON examples, BPMN process variables table |
| `Security.md` | §3 | Auth flow, REST clients, sequence diagram, cache config, secrets |
| `System-N-{Slug}.md` | §4..§9 | **One page per integrated system**. Each follows identical structure: description, REST client config, endpoints (inputs/outputs/DTOs/decision logic/JSONs) |
| `BPMN-Process-Flow.md` | §10 + §11 + §12 | BPMN flow diagram, evaluation script, event codes catalog, data flow map |
| `Environment-Configuration.md` | §13 + §14 | URLs per env, K8s deployment, Docker, DB, Kafka, WireMock, headers |
| `Error-Handling.md` | §15 + EventInfo constants | BPMN error types, code convention, error flow diagrams, EventInfo constants |

**System page slugs**: derive from system name, e.g., `System-1-GBO-Entities.md`, `System-2-LoanIQ.md`, etc.

### 6.2 Page generation rules

1. **Each page** starts with a breadcrumb: `← [[Home]]`.
2. **Headings**: The page title uses `# Heading` (H1). Subsections use `##` and `###`. Do NOT prefix with section numbers (those belong to the master doc only).
3. **Wiki link syntax**: GitHub Wiki uses `[[Display Text|Page-Name]]` — **display text FIRST, page name SECOND** after the pipe. Examples:
   - `[[Visión General|Architecture]]` → displays "Visión General", links to `Architecture.md`
   - `[[LoanIQ|System-2-LoanIQ]]` → displays "LoanIQ", links to `System-2-LoanIQ.md`
   - `[[Home]]` → displays and links to "Home" (no pipe needed when text = page name)
   - `[[catálogo de eventos|BPMN-Process-Flow]]` → displays "catálogo de eventos", links to `BPMN-Process-Flow.md`
4. **Mermaid diagrams**: Keep ` ```mermaid ` blocks as-is — GitHub Wiki renders them natively.
5. **No duplicate content**: Each piece of information appears in exactly one page. Home.md only contains summaries and links, not full content.

### 6.3 `Home.md` and `_Sidebar.md` templates

> Refer to `references/wiki-publishing.md` for the complete `Home.md` and `_Sidebar.md` templates, anchor generation rules, and sidebar formatting guidelines.

**Key rules**:
- `Home.md`: project title, tech stack table, `[[Page-Name]]` wiki links to all content pages, integrated systems summary table
- `_Sidebar.md`: `[[Home]]` link, bold page headings with `[[Wiki Link]]`, section anchor links, `---` separators between pages, max 2 indent levels

### 6.4 Output location

All Wiki files are saved to `docs/wiki/`. Inform the user to clone the wiki repo and copy:
```bash
git clone https://github.com/{org}/{repo}.wiki.git
cp docs/wiki/* {repo}.wiki/
cd {repo}.wiki && git add . && git commit -m "Update documentation" && git push
```

---

## PHASE 7: HTML EXPORT — Standalone HTML generation

1. Generate a **single self-contained HTML file** from the master document (NOT from the wiki pages).
2. Use the template from `assets/html-template.html` as the base (or generate inline if template not available).
3. Convert Markdown to HTML: headings, tables, code blocks, blockquotes.
4. Convert ` ```mermaid ` blocks to `<pre class="mermaid">` for Mermaid JS rendering.
5. Include Mermaid JS from CDN: `https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js`.
6. GitHub-like CSS: font-family, table borders, code highlighting, responsive layout.
7. HTML table of contents with internal anchor links.
8. Save to `docs/{artifact-id}-documentation.html`.

---

## GENERATED OUTPUTS (3 channels)

| Channel | Location | Audience | Diagrams |
|---|---|---|---|
| **Master document** | `docs/DOCUMENTACION-TECNICA.md` in the repo | Developers with repo access | Mermaid in code blocks (renderable in GitHub/VS Code) |
| **GitHub Wiki** | `docs/wiki/` → `{repo}.wiki/` (Home.md + N pages + _Sidebar.md) | Anyone with repo access on GitHub | Mermaid rendered natively by GitHub Wiki |
| **Standalone HTML** | `docs/{artifact-id}-documentation.html` | Anyone (no GitHub access needed) | Mermaid rendered as SVG via Mermaid JS CDN |

---

## EXPECTED BEHAVIOR

When the user asks to document a project:

1. Execute **Phase 1** (Discovery) using file reading tools and codebase search.
2. **Ask the user in which language** they want ALL the documentation generated (master document, Wiki pages, HTML). Suggest Spanish as default. Technical terms, Java class names, and code always remain in their original language regardless of the chosen language. Store the chosen language and apply it consistently to every output.
3. Present a summary of findings and proposed structure (**Phase 2**).
4. Ask whether they want full documentation or focused on a specific aspect.
5. Generate ALL documentation (**Phases 3 + 4**): master document (`docs/DOCUMENTACION-TECNICA.md`) AND wiki pages (`docs/wiki/*.md`) simultaneously.
6. Execute validation (**Phase 5**) and report any gaps. Fix and re-validate until all criteria pass.
7. **Ask the user** if they want to:
   - **Publish to GitHub Wiki** (Phase 6): clone `.wiki.git` repo, copy `docs/wiki/*`, commit and push.
   - **Generate standalone HTML** (Phase 7): create a self-contained `.html` with rendered Mermaid diagrams.
   - Both, or neither.
8. Execute only the phases the user requested (6, 7, both, or skip).

### Progress Checklist

```
- [ ] Phase 1: Discovery — project fully analyzed
- [ ] Phase 2: Structuring — document structure approved by user
- [ ] Phase 3: Enrichment — all DTOs, JSONs, diagrams generated
- [ ] Phase 4: Assembly — master doc + wiki pages generated in docs/
- [ ] Phase 5: Validation — all quality criteria pass
- [ ] Phase 6: Wiki — published to {repo}.wiki.git
- [ ] Phase 7: HTML — standalone .html with rendered Mermaid diagrams
```
