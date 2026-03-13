---
description: "Generate a Liquibase DML script to register a new process in process_paas (equivalent to the liquibase-process-script skill)"
---

# Liquibase DML Script Generator

Generate a Liquibase-formatted SQL file to register a new process in the `process_paas` schema.

## Instructions

### Output

A new file: `src/main/resources/dml/NNN-insert-<entity-lower>-<process-slug>.sql` with:
- Header `--liquibase formatted sql` + `--changeset`
- Idempotent INSERTs using `SELECT ... WHERE NOT EXISTS`
- Rollback section with DELETE statements
- `COMMIT;` at the end

### Required inputs

Ask the user if not provided:

1. **entity** (string, required): e.g. `ORDR` (4-character code)
2. **processName** (string, required): e.g. `Order Processing`

### Optional inputs (with defaults)

- **idProcess**: integer. If not provided, use placeholder `<<ID_PROCESS>>` with warning
- **context**: `DEV` (default). Accepts `CERT`, `PRO`, or empty
- **owner/group**: `ACME` / `ACME` (default)
- **accessPointId**: `1` (default)
- **processDefinitionId**: CamelCase of processName (e.g. `OrderProcessing`)
- **dns**: Service URL. If not provided, use placeholder `<<DNS>>`
- **statuses**: list of statuses. Default: two statuses (Pending User Action, Completed)
- **includeTasks**: `false` (default). If `true`, include Tasks and Actions section
- **includeEvents**: `false` (default). If `true`, include Events section

### File numbering

1. Use prefix `100-`
2. List existing files in `src/main/resources/dml/100-*.sql`
3. Extract the highest XYZ number and use `max + 1`
4. If the filename already exists, increment XYZ

### Rules

- All INSERTs must be idempotent (guarded by NOT EXISTS)
- Rollback must align with INSERT guard keys
- If `idProcess` or `dns` are missing, inject a clear warning comment
- Batch questions to the user in 1-2 rounds (max 4 questions per batch)

### Example prompt

```
Create a new process DML in DEV: entity=ORDR, processName=Order Processing, idProcess=1
```
