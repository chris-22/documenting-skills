---
description: "Generate comprehensive technical documentation for Java/Quarkus/Spring/BAMOE projects (equivalent to the documenting-paas skill)"
---

# Enterprise Project Technical Documentation

Generate comprehensive technical documentation for this project following a 7-phase workflow.

## Instructions

### Phase 1: Discovery — Exhaustive project analysis

Analyze the complete project:

1. **Build & Dependencies** — Read `pom.xml` / `build.gradle`: groupId, artifactId, version, parent, plugins, profiles. Classify each dependency by role (framework, persistence, messaging, testing, security).
2. **Existing documentation** — Read `README.md` and all files in `docs/`.
3. **Containerization** — Read `Dockerfile`: base image, JDK, layer structure, entrypoint.
4. **Configuration** — Read ALL config files (`application.properties`, `application.yml`, `application-{profile}.yml`). Extract: name, REST clients, datasources, messaging, cache, security, logging.
5. **BPMN/DMN processes** (if present) — Read ALL `.bpmn` / `.dmn`. For each process: name, ID, variables, Service Tasks (Java interface + method), gateways, errors, subprocesses.
6. **Java code** — Read ALL files in `src/main/java`: DTOs, Controllers/Resources, Service Tasks, configuration, mappers.
7. **Tests** — Read `src/test/java` to understand validated scenarios.
8. **Infra & CI/CD** — Read `deployment.yaml`, `values*.yaml`, `.github/workflows/*.yml`.

### Phase 2: Structuring — Document structure design

Propose the document structure in `docs/`:
- `ARCHITECTURE.md` — Overview, stack, C4/component diagrams
- `DATA-MODEL.md` — Entities, DTOs, ER diagrams
- `INTEGRATIONS.md` — REST APIs, clients, external systems, sequence diagrams
- `BPMN-PROCESS.md` — BPMN processes with Mermaid flowchart diagrams
- Others as discovered

### Phases 3-5: Content generation

For each document:
- Use **Mermaid diagrams** (flowchart, sequenceDiagram, erDiagram, C4Context, stateDiagram)
- Include **tables** for endpoints, DTOs, configurations
- Reference source files with relative paths
- Generate content based **only** on code evidence (do not invent)

### Phases 6-7: Publishing (optional)

If requested, publish to GitHub Wiki and generate standalone HTML.

## Expected output

`docs/` folder with complete, navigable Markdown documentation with Mermaid diagrams.
