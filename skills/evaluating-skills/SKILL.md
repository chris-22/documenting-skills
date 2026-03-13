---
name: evaluating-skills
description: >
  Performs comprehensive audits of agent skills against the official agentskills.io
  specification and skill-creator best practices. Evaluates frontmatter (name, description,
  compatibility), SKILL.md body (conciseness, progressive disclosure, degrees of freedom,
  workflows, content guidelines), scripts (self-contained, --help, errors, idempotency,
  --dry-run, exit codes), triggering accuracy (should/should-not trigger, cross-skill
  ambiguity), and evaluations (evals/ directory, test case quality).
  Triggers when the task involves auditing, evaluating, reviewing, analyzing, or improving
  any agent skill -- even without explicitly mentioning "audit" or "specification."
  Also activates for skill quality checks, compliance verification, triggering analysis,
  and skill improvement recommendations.
  NOT for creating new skills from scratch (use skill-creator instead).
---

# Skill: evaluating-skills

## Goal

Produce a structured audit report for any skill, evaluating compliance with the agentskills.io spec and skill-creator best practices. Deliver actionable findings with severity levels and a prioritized action plan.

## Audit workflow

Copy this checklist before starting. Update after each phase.

```
Skill Audit Progress:
- [ ] Phase 1: Discover -- list all skill files, count lines, identify coexisting skills
- [ ] Phase 2: Frontmatter -- audit name, description, compatibility, extra fields
- [ ] Phase 3: Body -- conciseness, progressive disclosure, freedom, workflows, content
- [ ] Phase 4: Scripts -- per-script checklist (if scripts/ exists)
- [ ] Phase 5: Triggering -- should/should-not trigger, cross-skill ambiguity
- [ ] Phase 6: Evals -- evals/ directory, test case quality, assertion accuracy
- [ ] Phase 7: Report -- compliance table, prioritized findings, action plan
- [ ] Phase 8: Execute fixes (if user requests)
```

## Phase 1: Discover

1. Read the target skill's `SKILL.md`.
2. List all files in the skill directory: `scripts/`, `references/`, `assets/`, `evals/`.
3. Count lines in SKILL.md, count reference files, count scripts.
4. List all OTHER skills in the same `.agents/skills/` directory (needed for Phase 5 cross-skill analysis). Read their `SKILL.md` frontmatter only (first 20 lines).

## Phase 2: Frontmatter

Audit `name`, `description`, `compatibility`, and extra fields against the spec.
See [references/frontmatter-spec.md](references/frontmatter-spec.md) for all rules and checklist.

Key checks:
- `name`: <=64 chars, lowercase+hyphens, matches directory, no consecutive hyphens
- `description`: <=1024 chars, WHAT+WHEN+keywords+third person+specific+negative boundary
- `compatibility`: only if real requirements exist, <=500 chars
- No extra fields beyond name/description/compatibility

## Phase 3: Body

Audit the SKILL.md body for conciseness, progressive disclosure, degrees of freedom, workflows, and content quality.
See [references/body-best-practices.md](references/body-best-practices.md) for all rules.

Key checks:
- Body < 500 lines. If over, identify what to move to references/
- Every paragraph justifies its token cost
- All references one level deep from SKILL.md
- References > 100 lines have TOC
- Degrees of freedom match task fragility (low for scripts, high for narrative)
- Copiable checklist for complex workflows
- No time-sensitive info, consistent terminology, no Windows paths

## Phase 4: Scripts

If `scripts/` exists, audit each standalone script against the checklist.
See [references/scripts-checklist.md](references/scripts-checklist.md) for per-script criteria.

Key checks per script: self-contained, `--help` with examples, descriptive errors, structured output, idempotent, `--dry-run`, distinct exit codes, no interactive prompts, `--verbose` / summary default.

If scripts share a framework (e.g., `cli_common.py`), assess consistency and document divergences.

**Skip this phase** if the skill has no scripts/ directory.

## Phase 5: Triggering

Analyze the description's triggering accuracy.
See [references/triggering-guide.md](references/triggering-guide.md) for methodology.

1. Generate 5 should-trigger queries (mix ES/EN, formal/casual)
2. Generate 5 should-NOT-trigger queries (adjacent domains, same keywords but wrong context)
3. For each coexisting skill (from Phase 1), check for keyword overlap and missing negative boundaries
4. Rate cross-skill ambiguity as High/Medium/Low

## Phase 6: Evals

Audit the `evals/` directory if it exists. If not, propose 3 test cases.
See [references/evals-guide.md](references/evals-guide.md) for criteria and templates.

Key checks:
- evals.json with realistic prompts, verifiable assertions, rubrics
- trigger-queries.json with train/validation split, both languages
- Test fixtures for edge cases
- Assertion accuracy: filenames, paths, section names match current skill state

## Phase 7: Report

Generate the audit report using the template in [assets/audit-report-template.md](assets/audit-report-template.md).

The report MUST contain:
1. **Compliance table**: skill x criterion with pass/fail per item
2. **Prioritized findings** grouped by severity:
   - **Critical**: violates spec or causes triggering failures
   - **Important**: best practice not followed, impacts quality/tokens
   - **Improvement**: recommended optimization
3. **Action plan**: concrete tasks ordered by impact/effort, with file(s), specific change, effort estimate (S/M/L)

Output the report to `docs/audit-{skill-name}.md` in the current workspace.

## Phase 8: Execute fixes

Only if the user explicitly requests execution after reviewing the report.
Apply fixes from the action plan in priority order. After each fix, update the checklist.

## Authoring conventions

- **Output language**: match the user's language (if they write in Spanish, report in Spanish)
- **Evidence-based**: every finding must reference specific file + line number
- **No invented findings**: if everything passes, say so. Do not manufacture issues
- **Concise tables**: prefer tables over prose for structured data
- **Score**: always calculate `passed/total (%)` for the compliance summary
