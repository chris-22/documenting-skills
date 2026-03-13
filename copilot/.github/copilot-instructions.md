# Instructions for GitHub Copilot

This project follows conventions for development with Quarkus, Kogito/BAMOE, and Process PaaS.

## General conventions

- **Stack**: Java 17 + Quarkus + Kogito/BAMOE 9 + PostgreSQL
- **Code style**: Google Java Format (2 spaces, max 100 chars/line, braces on same line)
- **Principles**: Clean Code + SOLID, small methods, composition over inheritance
- **Commits**: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`)
- **Branches**: `feature/*`, `fix/*` → PR to `development`

## Technical documentation

When asked to document the project, follow the 7-phase workflow:
1. Discovery (exhaustive analysis of pom.xml, config, BPMN, Java, tests, CI/CD)
2. Structuring (design docs/ structure)
3-5. Content generation with Mermaid diagrams
6-7. Publishing to Wiki + HTML

Use Mermaid diagrams: flowchart, sequenceDiagram, erDiagram, C4Context, stateDiagram.
Generate content based only on code evidence.

## Liquibase DML scripts

To register new processes in `process_paas`:
- File in `src/main/resources/dml/NNN-insert-<entity>-<slug>.sql`
- Idempotent INSERTs with `SELECT ... WHERE NOT EXISTS`
- Rollback with DELETE statements
- Prefix `100-`, number sequentially

## Available Prompt Files

This project includes prompt files in `.github/prompts/` that you can invoke with `#`:
- `#document-project` — Technical documentation for Java/Quarkus projects
- `#document-appian` — Documentation for Appian XML exports
- `#liquibase-process` — Liquibase DML script generator
- `#publish-wiki` — Publish Markdown to Wiki + HTML
- `#audit-skill` — Audit agent skills
