---
description: "Audit an agent skill against the agentskills.io specification (equivalent to the evaluating-skills skill)"
---

# Agent Skill Audit

Produce a structured audit report for any agent skill, evaluating compliance with the agentskills.io specification and best practices.

## Instructions

### Audit workflow

Follow these phases in order:

#### Phase 1: Discover
- Read the target skill's `SKILL.md`
- List all files: `scripts/`, `references/`, `assets/`, `evals/`
- Count SKILL.md lines, reference files, scripts
- List other coexisting skills (for cross-skill analysis in Phase 5)

#### Phase 2: Frontmatter
Audit `name`, `description`, `compatibility`:
- **name**: ≤64 chars, lowercase+hyphens, no consecutive hyphens
- **description**: ≤1024 chars, includes WHAT+WHEN+keywords, third person, negative boundaries
- **compatibility**: only if real requirements exist, ≤500 chars
- No extra unspecified fields

#### Phase 3: Body
- Body < 500 lines (if exceeded, identify what to move to references/)
- Every paragraph justifies its token cost
- References one level deep from SKILL.md
- Copiable checklist for complex workflows
- No time-sensitive info, consistent terminology

#### Phase 4: Scripts
If `scripts/` exists, audit each script:
- Self-contained, `--help` with examples, descriptive errors
- Structured output, idempotent, `--dry-run`, distinct exit codes

#### Phase 5: Triggering
- Generate 5 queries that SHOULD trigger the skill
- Generate 5 queries that SHOULD NOT trigger it
- Analyze keyword overlap with other coexisting skills
- Rate cross-skill ambiguity: High/Medium/Low

#### Phase 6: Evals
If `evals/` exists, audit quality. If not, propose 3 test cases.

#### Phase 7: Report
Generate report with:
1. **Compliance table**: skill × criterion with pass/fail
2. **Prioritized findings** by severity: Critical, Important, Improvement
3. **Action plan**: concrete tasks ordered by impact/effort

### Example prompt

```
Audit the documenting-appian skill
```
