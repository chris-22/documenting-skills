# Mermaid Diagram Legend — Color Palettes & Style Guide

Two color palettes exist depending on the diagram type.
For detailed syntax and examples of each type, see the corresponding `style-*.md` file.

## Contents
- [Decision tree — which diagram type to use](#decision-tree--which-diagram-type-to-use)
- [Diagram type reference files](#diagram-type-reference-files)
- [Quick summary](#quick-summary)
- [Palette A — Architecture](#palette-a----architecture--integrations--navigation--security)
- [Palette B — Process Models (BPMN)](#palette-b----process-models-bpmn-20)
- [classDef](#classdef-copy-to-the-end-of-each-mermaid-diagram)
- [Arrow styles](#arrow-styles-palette-b----process-models)
- [Click links](#click-links-navigation-between-diagrams)
- [Diagram types per document](#mermaid-diagram-types-per-document)

---

## Decision tree — which diagram type to use

```
Components & connections?
├── Few (<15), icons+layers?       → architecture-beta (manual)
├── C4 vision (persons, systems)?  → C4Context (auto: extract_integrations.py)
├── Many, colors, conditional?     → flowchart TD + Palette A
Message flow between actors?       → sequenceDiagram (auto: extract_integrations.py)
Entity lifecycle / states?         → stateDiagram-v2 (auto: analyze_health.py)
Data model (entities+relations)?   → erDiagram
Grid layout (positions)?           → block-beta (auto: generate_navigation.py)
BPMN process flow?                 → flowchart + Palette B (auto: pm2mermaid.py)
Proportional distribution?         → pie (auto: generate_inventory.py)
Permissions (group→role→type)?     → flowchart LR + Palette A (auto: extract_role_maps.py)
```

## Diagram type reference files

| Type | Use case | Auto-generated | Reference |
|------|----------|:--------------:|-----------|
| `architecture-beta` | High-level system architecture (~15 services max) | Manual | [style-architecture-beta.md](style-architecture-beta.md) |
| `sequenceDiagram` | Integration request/response flows per CS | `extract_integrations.py` | [style-sequence-diagram.md](style-sequence-diagram.md) |
| `stateDiagram-v2` | Entity lifecycle (auto-discovered states) | `analyze_health.py` | [style-state-diagram.md](style-state-diagram.md) |
| `erDiagram` | CDT data model, entity relationships | `parse_cdts.py` (partial) | [style-er-diagram.md](style-er-diagram.md) |
| `block-beta` | Site navigation map (grid layout) | `generate_navigation.py` | [style-block-beta.md](style-block-beta.md) |
| `flowchart` (Palette B) | BPMN Process Models | `pm2mermaid.py` | [type-mapping.md](type-mapping.md) |
| `flowchart` (Palette A) | Dependency graphs, security hierarchy, role assignments | `extract_integrations.py`, `extract_role_maps.py` | (this file) |
| `C4Context` | System context: users, app, external systems | `extract_integrations.py` | [style-c4-diagram.md](style-c4-diagram.md) |
| `pie` | Object distribution by type | `generate_inventory.py` | Mermaid built-in |

## Quick summary

| Diagram | Styling | Custom colors | Direction | Max recommended complexity |
|----------|---------|----------------------|-----------|---------------------------|
| `architecture-beta` | Fixed per type | No | Edges T/B/L/R | ~15 services |
| `sequenceDiagram` | box colors, rect highlights | Yes (box rgba) | Always vertical | ~10 participants, ~30 messages |
| `stateDiagram-v2` | classDef + class | Yes | direction LR/TB | ~15 states |
| `erDiagram` | classDef + class | Yes | TB/LR | ~20 entities |
| `block-beta` | classDef + class | Yes | Grid (columns) | ~30 blocks |
| `flowchart` | classDef + class | Yes | LR/TD/RL/BT | ~50 nodes (with subgraphs) |
| `C4Context` | UpdateElementStyle | Yes | Auto-layout | ~10 systems |
| `pie` | showData | Global theme | N/A (circular) | ~15 categories |

---

## Palette A -- Architecture / Integrations / Navigation / Security

Used in: `04-appian-architecture.md`, `07-appian-integrations.md`, `05-appian-navigation.md`, `08-appian-security.md`, `12-appian-health.md`

| Color | Type | classDef |
|-------|------|----------|
| **Red** `#EB5757` | Sites (UI entry points) | `site` |
| **Green** `#6FCF97` | Process Models | `processModel` |
| **Blue** `#2D9CDB` | Web APIs | `webApi` |
| **Purple** `#BB6BD9` | Data Stores | `dataStore` |
| **Orange** `#F2994A` | Connected Systems | `connSystem` |
| **Yellow** `#F2C94C` | External Systems | `extSystem` |
| **Gray** `#BDBDBD` | Groups | `group` |
| **Lilac** `#E0AFF5` | Record Types | `recordType` |

### classDef (copy to the end of the diagram)

```
  classDef site fill:#EB5757,stroke:#C43E3E,color:#fff,stroke-width:2px
  classDef processModel fill:#6FCF97,stroke:#4AA86B,color:#fff,stroke-width:1px
  classDef webApi fill:#2D9CDB,stroke:#1A7AB5,color:#fff,stroke-width:2px
  classDef dataStore fill:#BB6BD9,stroke:#9544B5,color:#fff,stroke-width:1px
  classDef connSystem fill:#F2994A,stroke:#D4782E,color:#fff,stroke-width:1px
  classDef extSystem fill:#F2C94C,stroke:#D4A82E,color:#333,stroke-width:2px
  classDef group fill:#BDBDBD,stroke:#828282,color:#333,stroke-width:1px
  classDef recordType fill:#E0AFF5,stroke:#BB6BD9,color:#333,stroke-width:1px
```

---

## Palette B -- Process Models (BPMN 2.0)

Used in: `docs/process-models/*.md`

## Colors per node type (BPMN 2.0)

| Color | BPMN Type | Shape | classDef | Appian nodes |
|-------|-----------|-------|----------|-------------|
| **Green** `#4CAF50` | Start Event | `sm-circ` | `startEvent` | `core.0` Start Node |
| **Red** `#F44336` | End Event | `dbl-circ` | `endEvent` | `core.1` End Node |
| **Yellow** `#FFC107` | Timer / Message | `sm-circ` | `timerEvent` | `core.7` Intermediate Event |
| **Orange** `#FF9800` | Gateway | `diamond` | `gateway` | `core.2` AND, `core.3` OR, `core.4` XOR, `core.5` Complex |
| **Dark blue** `#1565C0` | Subprocess / Call Activity | `fr-rect` | `subprocess` | `internal.38` SUB_PROC, Start Process |
| **Light blue** `#2D9CDB` | User Task | `rounded` | `userTask` | `internal.17` User Input Task |
| **Light orange** `#F2994A` | Service Task | `rect` | `serviceTask` | Call Integration, SFTP, Kafka, SAP |
| **Gray** `#E0E0E0` | Script Task | `rect` | `scriptTask` | `internal.16` Script Task, others |
| **Pink** `#F06292` | Send Task | `rect` | `sendTask` | Send E-Mail, Send Push Notification |
| **Purple** `#BB6BD9` | Data Store ops | `cyl` | `dataStore` | Write/Delete/Query Data Store, Stored Procedure |

## classDef (copy to the end of each Mermaid diagram)

```
  classDef startEvent fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
  classDef endEvent fill:#F44336,stroke:#C62828,color:#fff,stroke-width:2px
  classDef timerEvent fill:#FFC107,stroke:#F57F17,color:#333,stroke-width:2px
  classDef gateway fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:2px
  classDef subprocess fill:#1565C0,stroke:#0D47A1,color:#fff,stroke-width:2px
  classDef userTask fill:#2D9CDB,stroke:#1A7AB5,color:#fff,stroke-width:1px
  classDef serviceTask fill:#F2994A,stroke:#D4782E,color:#fff,stroke-width:1px
  classDef scriptTask fill:#E0E0E0,stroke:#9E9E9E,color:#333,stroke-width:1px
  classDef sendTask fill:#F06292,stroke:#C2185B,color:#fff,stroke-width:1px
  classDef dataStore fill:#BB6BD9,stroke:#9544B5,color:#fff,stroke-width:1px
```

## Class assignment (compact format)

After the `classDef` block, group nodes by class:

```
  class N0 startEvent
  class N1 endEvent
  class N3,N7 gateway
  class N5 subprocess
  class N4 userTask
  class N8,N9 serviceTask
  class N10,N11 scriptTask
  class N12 sendTask
  class N2,N6 dataStore
```

## Arrow styles (Palette B -- Process Models)

| Style | Syntax | Use |
|-------|--------|-----|
| Normal | `N0 --> N1` | Standard flow |
| **Thick** | `N0 ==> N1` | Main flow (Start -> first node -> main gateway) |
| Dotted | `N0 -.-> N1` | Alternative / error flow |
| With label | `N0 -->\|"Yes"\| N1` | XOR gateway outputs (condition) |
| Dotted with label | `N0 -.->\|"Error"\| N1` | Error flow with description |

## Click links (navigation between diagrams)

Subprocess nodes MUST have a click link to the subprocess diagram:

```
click N15 "./RC_PM_IntegracionCatalogoServicios.md" "Ver diagrama del subproceso"
```

---

## Mermaid diagram types per document

| Document | Mermaid type | Auto-generated | Description |
|-----------|-------------|:-------------:|-------------|
| `04-appian-architecture.md` | `architecture-beta` | Manual | Service/group view with icons and directional edges |
| `07-appian-integrations.md` (API flow) | `sequenceDiagram` | `extract_integrations.py` | Temporal request/response sequence per CS |
| `07-appian-integrations.md` (dependencies) | `flowchart LR` + Palette A | `extract_integrations.py` | Object dependency graph |
| `07-appian-integrations.md` (context) | `C4Context` | `extract_integrations.py` | C4 diagram: persons, app, external systems |
| `06-appian-data.md` | `erDiagram` | `parse_cdts.py` (partial) | CDT entity-relationship model |
| `12-appian-health.md` (states) | `stateDiagram-v2` | `analyze_health.py` | Lifecycle inferred from discovered states |
| `03-appian-inventory.md` | `pie` | `generate_inventory.py` | Object distribution by type |
| `05-appian-navigation.md` | `block-beta` | `generate_navigation.py` | Grid layout of Sites and pages |
| `08-appian-security.md` (hierarchy) | `flowchart TD` + Palette A | `extract_role_maps.py` | Group hierarchy |
| `08-appian-security.md` (permissions) | `flowchart LR` + Palette A | `extract_role_maps.py` | Group -> Role -> Object type assignment |
| `docs/process-models/*.md` | `flowchart` + Palette B | `pm2mermaid.py` | BPMN process diagrams |

## Usage

- Every `.md` diagram in `docs/process-models/` MUST include the `classDef` and `class` assignments.
- Every diagram MUST link to the shared legend with: `> See [color legend](./_legend.md)`
- Do NOT insert the legend as a subgraph inside the diagram (wastes space and complicates large diagrams).
