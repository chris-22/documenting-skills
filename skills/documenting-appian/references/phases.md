# Documentation Phases — Detailed Instructions (v2)

> Scripts handle data extraction; agent enriches with narrative, diagrams, and cross-references.
> For script→output mapping, see SKILL.md table. This file details **agent enrichment instructions** per phase.

## Contents
- [Phase A — Bootstrap](#phase-a----bootstrap)
- [Phase B — Inventory & Glossary](#phase-b----inventory--glossary)
- [Phase C — Architecture & Navigation](#phase-c----architecture--navigation)
- [Phase D — Data & Integrations](#phase-d----data--integrations)
- [Phase E — Security](#phase-e----security)
- [Phase F — Operations](#phase-f----operations)
- [Phase G — Health & Validation](#phase-g----health--validation)

---

## Phase A -- Bootstrap

**Scripts**: `build_uuid_index.py`
**Output**: `docs/_uuid-index.json`, `docs/01-appian-overview.md` (agent-written)

1. Run `build_uuid_index.py`.
2. Write `docs/01-appian-overview.md` (see [templates.md](templates.md#01-appian-overviewmd) for required sections).
3. **Critical**: identify the base/parent application — check `<parentUuid>` in manifest, shared-prefix patterns, external CDT/DS/group references not in this export. Document in `Dependencies` section.

Rule: unverifiable facts → `TODO(unknown)`.

## Phase B -- Inventory & Glossary

**Scripts**: `generate_inventory.py` (includes complexity metrics)
**Output**: `docs/03-appian-inventory.md` (auto-generated), `docs/02-appian-glossary.md` (agent-written)

1. Run `generate_inventory.py` — produces inventory table + complexity metrics. Review; no manual rewrite needed.
2. Write `docs/02-appian-glossary.md` (see [templates.md](templates.md#02-appian-glossarymd) for required sections).
   - **Always include "Acrónimos técnicos Appian"** with prefix-to-type mapping.
   - **Actively investigate domain acronyms**: read XSD `<annotation>` tags and CDT descriptions. Do NOT leave business acronyms as `TODO(unknown)` if context provides enough clues.

## Phase C -- Architecture & Navigation

**Scripts**: `generate_navigation.py`, `pm2mermaid.py` (batch)
**Output**: `docs/04-appian-architecture.md` (agent-written), `docs/05-appian-navigation.md` (auto + enriched), `docs/process-models/*.md` (auto-generated)

1. Run `generate_navigation.py` + `pm2mermaid.py` in batch for ALL PMs.
2. Enrich `05-appian-navigation.md` with visibility rule explanations.
3. Write `docs/04-appian-architecture.md` with:
   - **Entry points**: site pages, Web APIs (table: Web API | Method | URL alias | Description), scheduled processes
   - **Main flows** using **indented-text format** (mandatory):
     ```
     Site APP_MainSite (/page-slug)
       → APP_PM_HandleRequest (main form)
         → APP_PM_SaveData (persistence)
           → APP_PM_PostSave (post-save: tasks, notifications)
     ```
     **Completeness**: document ALL flow categories — user-facing, Web API, batch/scheduled, data export, reporting, escalation, bulk import. If 5+ batch processes, document each separately.
   - **Architecture diagram**: `flowchart TD` with subgraphs per layer (presentation, process, integration, data) using Palette A
   - **Process variables**: for core PMs, extract `<pv>` elements (name, type, parameter, required)
   - **Escalations/deadlines**: flag processes with `<deadline><enabled>true</enabled>`

## Phase D -- Data & Integrations

**Scripts**: `parse_cdts.py`, `extract_integrations.py`
**Output**: `docs/06-appian-data.md` (auto + enriched), `docs/07-appian-integrations.md` (auto + enriched)

1. Run `parse_cdts.py` + `extract_integrations.py`.
2. Enrich `docs/06-appian-data.md` — **mandatory**. The script only generates CDT field detail. Add ABOVE the CDT detail:
   - **Data Stores** table: DS Name | JNDI Key | Auto-Update Schema | Entity Count (from `dataStore/*.xml`)
   - **JDBC Data Sources summary**: group by `<dataSourceKey>` — critical for deployment
   - **Record Types**: fields, source data store, sync config (from `recordType/*.xml`)
   - **ER diagram** (`erDiagram`): infer CDT relationships from `{urn:com:appian:types:*}` type references in XSD
   - If no CDTs/Data Stores, document external dependencies with `TODO(unknown)`
3. Enrich `docs/07-appian-integrations.md` with:
   - Web API details: URL alias, HTTP method, payload (from `webApi/*.xml`)
   - CS environment URLs (DESA/PRE/PRO pattern from descriptions)
   - `sequenceDiagram` for API flows + Import Customization notes

## Phase E -- Security

**Scripts**: `extract_role_maps.py`
**Output**: `docs/08-appian-security.md` (auto + enriched)

1. Run `extract_role_maps.py` — produces permission matrix + group summary.
2. Enrich with:
   - **Group hierarchy diagram** (`flowchart TD` + Palette A) — **MANDATORY**. Read `group/*.xml` for `<parentUuid>`. Build tree: root → functional roles → geographic sub-groups. Color-code: admin=red, functional=blue, geographic=green, technical=orange.
   - Group inventory: name, type, parent, members, admins
   - FSE documentation if applicable (CDTs with `FSE`/`Security`/`Permission`/`Scope` in names)
   - Security observations: empty roleMaps, all-users access, test objects, **external/unresolved groups**

## Phase F -- Operations

**Scripts**: `extract_translations.py`, `generate_deployment.py`
**Output**: `docs/10-appian-i18n.md`, `docs/09-appian-deployment.md` + ICF template

1. Run `extract_translations.py` + `generate_deployment.py`.
2. Enrich `docs/10-appian-i18n.md` with usage patterns and maintenance recommendations.
3. Enrich `docs/09-appian-deployment.md` with:
   - **JDBC Data Sources table**: JNDI Key | Data Stores using it | Action required. Note `<autoUpdateSchema>` = `false` → tables must pre-exist.
   - External dependencies — **name the base application explicitly** (from Phase A) as prerequisite
   - Risks per object type (see [deployment-risks.md](deployment-risks.md)) + **application-specific risks**: unresolved group UUIDs, hardcoded visibility rules, dual JDBC sources, AWS Signature auth in CS
   - Pre/during/post-import checklist — **specific**: name actual JNDI keys, Web API endpoints, CS to test, Record Types to force-sync
   - Parse `patches.xml` if present (resolve UUIDs to names)
4. Write ICF template with actual UUIDs from the index.

## Phase G -- Health & Validation

**Scripts**: `analyze_health.py`
**Output**: `docs/12-appian-health.md` (auto-generated), `docs/11-appian-interfaces.md` (agent-written), `docs/README.md` validation section

1. Run `analyze_health.py` — produces health report with critical objects, potentially unused objects, and expression-level analysis (UUID + rule!/cons! references).
2. Review the health report; add narrative for key findings.
3. Write `docs/11-appian-interfaces.md` with:
   - Interface classification: main screens, task forms, reusable components, potentially unused
   - Decisions summary, expression rules summary, constants summary
   - Content folder structure **in tree format** (not flat table) showing KC → folders → rules folders hierarchy
4. Write/update `docs/README.md` with:
   - Index linking to all documents
   - Maintenance guide (how to regenerate)
   - **Documentation Quality** section: completeness check, TODO count, Mermaid validation, no-secrets verification

### TODO resolution pass (mandatory before validation)

Before running validation, the agent MUST attempt to resolve ALL `TODO(unknown)` markers by:
- Re-reading relevant XML files (CDT descriptions, field annotations, Connected System descriptions)
- Cross-referencing with translation strings for term definitions
- Inferring from CDT field names and table names (e.g., `rccdtcatalogo<acronym>` → the acronym likely refers to a catalog entity)
- Checking group XML for parent relationships to resolve hierarchy unknowns
- Only leave `TODO(unknown)` if the information is truly not available in the export files

### Validation checklist
- Every expected output file exists
- `docs/README.md` links to all documents
- All Mermaid blocks are syntactically valid (no `end` as node ID, proper escaping)
- Count all `TODO(unknown)` and `TODO(unresolved-ref: ...)` markers
- No credentials, API keys, or tokens in documentation
- Object names match between inventory and narrative docs
- `06-appian-data.md` includes Data Stores section with JNDI keys (not just CDTs)
- `08-appian-security.md` includes group hierarchy Mermaid diagram
- `09-appian-deployment.md` includes JDBC data sources table and application-specific risks
- `04-appian-architecture.md` Web APIs table includes HTTP method and URL alias
