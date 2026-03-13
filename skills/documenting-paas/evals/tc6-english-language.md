# TC6: Documentation in English Language

## Prompt

```
Generate complete technical documentation for this project in English. Include wiki and HTML.
```

## Context

- Project has `pom.xml` with Quarkus + Kogito dependencies
- At least one `.bpmn` file with Service Tasks
- Multiple REST client configurations
- User explicitly requests English language

## Expected Output

1. **Master document** saved in `docs/` as `.md` — all in English
2. **Wiki files** in `docs/wiki/` — all in English
3. **HTML file** in `docs/` as `.html` — all in English

## Assertions

- [ ] Master document section headings are in English (e.g., "Architecture Overview", not "Vision General de la Arquitectura")
- [ ] Table headers are in English (e.g., "Field | Type | Description", not "Campo | Tipo | Descripcion")
- [ ] Notes use English prefix (e.g., `> **NOTE**:`, not `> **NOTA**:`)
- [ ] JSON comment annotations are in English (e.g., "// Anonymized real request", not "// Request real anonimizado")
- [ ] Technical terms remain untranslated: Java class names, configKeys, field names, event codes
- [ ] Wiki `Home.md` content is in English
- [ ] Wiki `_Sidebar.md` labels are in English
- [ ] HTML file content is in English
- [ ] All three outputs (master doc, Wiki, HTML) use the same language consistently
- [ ] Phase 2 summary was presented in the user's language (English)
