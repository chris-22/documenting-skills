# Instruction: Enterprise Project Technical Documentation

Generate comprehensive technical documentation for Java/Quarkus/Spring/BAMOE projects following a 7-phase workflow.

## Workflow

1. **Discovery**: Analyze pom.xml, Dockerfile, application.yml, BPMN files, Java code, tests, CI/CD
2. **Structuring**: Design `docs/` structure (ARCHITECTURE.md, DATA-MODEL.md, INTEGRATIONS.md, BPMN-PROCESS.md)
3. **Content Generation**: Generate each document with Mermaid diagrams (flowchart, sequenceDiagram, erDiagram, C4Context)
4. **Cross-referencing**: Link documents to each other, reference source files
5. **Quality**: Verify completeness, consistency, Mermaid syntax
6. **Wiki**: Publish to GitHub Wiki (Home.md, _Sidebar.md, per-section pages)
7. **HTML**: Generate standalone HTML with rendered Mermaid

## Rules

- All content based on code evidence (do not invent)
- Use tables for endpoints, DTOs, configurations
- Mermaid diagrams whenever they add visual value
- Document in the same language the user requests
