---
description: "Generate comprehensive technical documentation for Appian applications from XML exports (equivalent to the documenting-appian skill)"
---

# Appian Application Technical Documentation

Generate comprehensive technical documentation for an Appian application from its XML export in `application_files/`.

## Instructions

### Source of truth

`application_files/` is **read-only**. All documentation is based exclusively on evidence from these XML files.

### Expected outputs

Generate the following files in `docs/`:

| File | Content |
|------|---------|
| `docs/README.md` | Index + maintenance guide |
| `docs/01-appian-overview.md` | Purpose, scope, conventions, metrics |
| `docs/02-appian-glossary.md` | Domain glossary |
| `docs/03-appian-inventory.md` | Inventory table + Mermaid `pie` chart |
| `docs/04-appian-architecture.md` | Architecture, entry points, flows |
| `docs/05-appian-navigation.md` | Pages → object mapping + `block-beta` |
| `docs/06-appian-data.md` | Record types, data stores, CDTs + `erDiagram` |
| `docs/07-appian-integrations.md` | Web APIs, connected systems + `sequenceDiagram` + `C4Context` |
| `docs/08-appian-security.md` | Group hierarchy + `flowchart` + role matrix |
| `docs/09-appian-deployment.md` | Packaging, ICF template, risks, checklist |
| `docs/10-appian-i18n.md` | Translation sets/strings |
| `docs/11-appian-interfaces.md` | Interfaces, expression rules, constants |
| `docs/12-appian-health.md` | Dead code, dependency graph + `stateDiagram-v2` |
| `docs/process-models/` | BPMN `flowchart` diagram per Process Model |

### Workflow

1. Parse XMLs in `application_files/` for each Appian object type
2. Generate complete inventory with counts by type
3. Analyze process models and generate BPMN diagrams as Mermaid flowcharts
4. Extract CDTs and generate ER diagrams
5. Document integrations with sequence diagrams
6. Map security (groups, roles, permissions)
7. Analyze dead code and orphan dependencies

### Rules

- Every assertion must be backed by XML evidence
- Use Mermaid diagrams whenever they add visual value
- Do not invent or assume — if something is not in the export, flag it as a gap
