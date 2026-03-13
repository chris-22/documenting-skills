---
name: liquibase-process-script
description: >-
  Generate a Liquibase formatted SQL DML script to register a new process in the
  process_paas schema for this repository (or similar ones using the same
  structure). Use when the user asks to "add a new process" or "generate the DML
  script for a process". Creates dml/NNN-insert-<entity>-<slug>.sql with
  idempotent INSERTs (SELECT ... WHERE NOT EXISTS) plus rollback, DEV context by
  default (customizable), and detects the next NNN by scanning
  src/main/resources/dml. Uses the template in assets/ with placeholder
  substitution. No external runtime scripts required.
---

# Liquibase process DML (generator)

This skill enables an AI agent to consistently author a Liquibase formatted SQL file like the provided example to onboard a new process. The output is a single file under src/main/resources/dml, automatically picked up by DATAchangelog.yaml (includeAll: dml).

## What it produces

- A new file: `src/main/resources/dml/NNN-insert-<entity-lower>-<process-slug>.sql`
- Header with `--liquibase formatted sql` and a `--changeset` line
- Idempotent INSERTs using `SELECT ... WHERE NOT EXISTS` for all rows
- Rollback section with DELETE statements for each inserted row
- `COMMIT;` at the end

## Required inputs

- entity (string): e.g. `ORDR`
- processName (string): e.g. `Order Processing`

## Optional inputs and defaults

- description: defaults to processName
- context: DEV (default). Accepts CERT, PRO, or empty (no context on changeset)
- idProcess: if not provided, leave placeholder `<<ID_PROCESS>>` and add a warning comment at the top
- owner: ACME (default)
- group: ACME (default)
- accessPointId: 1 (default)
- processDefinitionId: defaults to CamelCase of processName without spaces (e.g., `OrderProcessing`)
- realm: BAMOE (default)
- originApp: BAMOE (default)
- dns: if not provided, leave placeholder `<<DNS>>`
- user: author NT for creation/modification fields; default `unknown` if not available
- includeTasks: false (default). If false, omit Task and Task Action sections entirely.
- includeEvents: false (default). If false, omit Process Event section. If true but no tasks, ensure events are still meaningful.
- statuses: list of status entries to create for the process. If not provided initially, the agent MUST ask. Each entry:
  - id_status (int)
  - pr_status_name (string)
  - pr_status_description (string, optional)
  - pr_status_type (int, default 1)
  - pr_stage (int or NULL, default NULL)


## Interactive prompting (ask for missing values)

When the initial request does not provide some values, ask clarifying questions before generating the file. Batch related questions to minimize back-and-forth (max 4 questions per batch), propose sensible defaults, and allow freeform input when needed.

Ask in this order and with these defaults:

1) Core identification
  - entity (required): e.g., ORDR (4-char code). If missing, ask for it.
  - processName (required): e.g., Order Processing. If missing, ask for it.
  - idProcess (recommended): ask for a concrete integer. Offer the option to leave a placeholder `<<ID_PROCESS>>` if the user can’t provide it yet.

2) Environment and scope
  - context: offer [DEV (default), CERT, PRO, none]. If omitted, use DEV.
  - dns: ask for the service DNS URL; if unknown, allow placeholder `<<DNS>>`.

3) Optional behavior
  - includeTasks: [No (default), Yes]. If Yes, ask whether to use a minimal Manual Task with actions [Complete, Cancel], or collect custom tasks/actions.
  - includeEvents: [No (default), Yes]. If Yes, ask event name/description/origin (default originApp=BAMOE) and IDs.
  - statuses: Ask whether to use defaults or provide a custom list.
    - Offer defaults: two statuses —
      - id_status=0, name="Pending User Action", type=1, stage=NULL
      - id_status=1, name="Completed", type=1, stage=NULL
    - Or collect a custom list: for each status, ask id_status, name, description (optional), type (default 1), stage (optional/NULL).
    - Validate uniqueness of id_status within the process.

4) Ownership and metadata (show defaults)
  - owner/group: default ACME/ACME
  - accessPointId: default 1
  - processDefinitionId: propose CamelCase(processName), allow override
  - user: default `unknown` (or current NT if available)

Guidance:
- Combine the above into 1–2 batched questions where possible. Use single-select options with a recommended default. Enable freeform input if the user needs a custom value.
- If the user declines to provide idProcess or dns, proceed with placeholders but clearly warn the user the script should not run before replacing them.
- Do not create more than needed: if includeTasks=false and includeEvents=false, use the no-tasks template to keep output minimal.
- Always ask for statuses. If the user does not care, use the two-status default above.

## File naming and numbering

- Use prefix `100-`
- Compute the next middle number `XYZ` (3 digits) by listing existing `src/main/resources/dml/100-*.sql` files, extracting their XYZ, and selecting `max + 1`
- Build file base: `100-XYZ-insert-<entity-lower>-<slug(processName)>`

## Changeset header

- Always include: `--liquibase formatted sql`
- Use: `--changeset <FILENAME>:01` where `<FILENAME>` is the file name
- Append ` context:<CONTEXT>` if a context value is provided

## Template and placeholders

- Choose template based on options:
  - If `includeTasks=false` (default): use `assets/process_template_no_tasks.sql`.
  - If `includeTasks=true`: use `assets/process_template.sql`.
  In both cases, replace placeholders below.
- Placeholders mapping:
  - `{{FILENAME}}` => computed file name
  - `{{AUTHOR}}` => `01`
  - `{{CONTEXT_CLAUSE}}` => empty or ` context:<CONTEXT>`
  - `{{ENTITY}}` => `entity`
  - `{{ID_PROCESS}}` => `idProcess` or `<<ID_PROCESS>>`
  - `{{PROCESS_NAME}}` => `processName`
  - `{{DESCRIPTION}}` => `description || processName`
  - `{{OWNER}}` => `owner`
  - `{{GROUP}}` => `group`
  - `{{ACCESS_POINT_ID}}` => `accessPointId`
  - `{{PROCESS_DEFINITION_ID}}` => `processDefinitionId`
  - `{{DNS}}` => `dns` or `<<DNS>>`
  - `{{REALM}}` => `realm`
  - `{{ORIGIN_APP}}` => `originApp`
  - `{{USER}}` => `user` or `unknown`
  - `{{STATUSES_BLOCK}}` => SQL INSERT statements for each requested status (idempotent with WHERE NOT EXISTS). Omit entirely if none.
  - `{{STATUSES_ROLLBACK_BLOCK}}` => SQL DELETE statements for the same statuses. Omit entirely if none.

## Safety and validation

- If the computed file name already exists, increment XYZ and retry
- If `idProcess` is missing, inject a clear warning comment near the top of the file
- Keep all INSERTs idempotent (guarded by NOT EXISTS)
- Keep rollback statements aligned with the guarding keys

## Example prompt to trigger this skill

"Create a new process DML in DEV: entity=ORDR, processName=Order Processing, idProcess=1, dns=http://..." -> Generates `100-0XY-insert-ORDR-order-processing.sql` with idempotent rows and rollback.

To skip tasks: "Create a new process DML in DEV without tasks: entity=ORDR, processName=Order Processing, idProcess=1, dns=http://..." -> Uses the no-tasks template.
