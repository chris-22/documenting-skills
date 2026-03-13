# TC2: REST-only Project (No BPMN)

## Prompt

```
Generate technical documentation for this REST API service.
```

## Context

- Project has `pom.xml` with Spring Boot or Quarkus (no Kogito/jBPM)
- No `.bpmn` or `.dmn` files present
- REST controllers with `@Path`/`@RequestMapping` endpoints
- JPA entities with database configuration
- External REST client integrations

## Expected Output

1. **Master document** saved in `docs/` as `.md`
2. **Wiki files** generated
3. **HTML file** generated

## Assertions

- [ ] Master document does NOT contain "BPMN", "Service Task", or "Process Variables" sections
- [ ] Master document contains REST endpoint documentation with HTTP method, path, DTOs
- [ ] Master document contains JSON request/response examples for each endpoint
- [ ] Master document contains architecture diagram focused on REST layers (not BPMN orchestration)
- [ ] Master document contains data flow diagram between components/services
- [ ] DTO tables include all fields from actual Java classes
- [ ] Environment configuration table is present
- [ ] Document structure adapts: no process flow section, focus on API and data model
- [ ] Phase 2 summary correctly identified the project as non-BPMN
- [ ] Quality validation (Phase 5) passes with BPMN criteria marked N/A
