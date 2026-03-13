# Instruction: Liquibase DML Script Generator

Generate Liquibase-formatted SQL files to register new processes in the `process_paas` schema.

## Output

`src/main/resources/dml/100-NNN-insert-<entity-lower>-<slug>.sql` with:
- Header `--liquibase formatted sql` + `--changeset`
- Idempotent INSERTs (`SELECT ... WHERE NOT EXISTS`)
- Rollback with DELETE statements
- `COMMIT;` at the end

## Required inputs

- **entity** (string): 4-character code (e.g. `ORDR`)
- **processName** (string): process name (e.g. `Order Processing`)

## Defaults

- context: `DEV` | owner/group: `ACME` | accessPointId: `1`
- processDefinitionId: CamelCase of processName
- Default statuses: Pending User Action (id=0), Completed (id=1)
- Prefix `100-`, sequential numbering detecting existing max

## Rules

- Idempotent INSERTs (guarded by NOT EXISTS)
- If idProcess or dns is missing, use placeholder with warning
- Ask the user for missing values (max 4 questions per batch)
