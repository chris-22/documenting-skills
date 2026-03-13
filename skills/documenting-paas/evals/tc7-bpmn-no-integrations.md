# TC7: BPMN Project Without External Integrations

## Prompt

```
Documenta este proyecto. Quiero la documentación técnica completa.
```

## Context

- Project has `pom.xml` with Quarkus + Kogito dependencies
- `.bpmn` file(s) with Service Tasks that operate on **internal** logic only (no REST clients)
- No external system integrations (no REST client configurations in `application.properties`)
- JPA entities with database persistence
- No backend JARs, no API Gateway calls

## Expected Output

1. **Master document** saved in `docs/` as `.md`
2. Structure adapts to internal-only architecture

## Assertions

- [ ] Master document does NOT contain "Sistema N" external integration sections
- [ ] Master document contains Architecture Overview focused on internal components (not external systems)
- [ ] Master document contains BPMN process flow diagram with Service Tasks
- [ ] Master document contains BPMN process variables table
- [ ] Master document contains domain model / JPA entity documentation
- [ ] Master document contains REST API endpoint documentation (entry point)
- [ ] Master document contains persistence / database configuration section
- [ ] Master document does NOT contain REST client configuration tables (configKey, URL DEV, URL PROD)
- [ ] Master document does NOT contain API Gateway references
- [ ] Architecture diagram shows internal layers only (Entry → BPMN → Service Tasks → Database)
- [ ] Phase 2 correctly identified the project as BPMN-with-no-external-integrations
- [ ] Error handling section documents BPMN errors if present, without external system error flows
