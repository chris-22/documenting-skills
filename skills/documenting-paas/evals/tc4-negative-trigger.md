# TC4: Negative Trigger — Should NOT Activate

## Prompt

```
Add a new Kafka consumer to this project that listens to the payments topic.
```

## Context

- Project has `pom.xml` with Quarkus + Kafka dependencies
- Existing consumers in `src/main/java`
- This is a code generation request, NOT a documentation request

## Expected Output

- Skill does NOT trigger
- No documentation files are generated or modified

## Assertions

- [ ] No files created in `docs/`
- [ ] No files created or modified in `{repo}.wiki/`
- [ ] No HTML file generated
- [ ] The request is handled by Claude's general coding capabilities, not this skill

---

## Additional Non-triggering Prompts

These prompts should also NOT activate this skill:

1. `Fix the bug in the authentication flow` — debugging request
2. `Write unit tests for the GBO integration service` — testing request
3. `Deploy this project to the PRE environment` — operations request
4. `Refactor the DTO classes to use records` — code refactoring request
