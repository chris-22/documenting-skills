# Audit Report: Skill `{SKILL_NAME}`

> Date: {DATE} | Spec: agentskills.io + skill-creator best practices
> Skill dir: `{SKILL_DIR}`
> Files audited: SKILL.md ({LINES} lines), {REF_COUNT} references, {SCRIPT_COUNT} scripts, evals/ ({EVAL_COUNT} test cases)
> Coexisting skills audited for triggering: {OTHER_SKILLS}

---

## 1. Frontmatter

### 1.1 `name: {SKILL_NAME}`

| Criterion | Value | Result |
|-----------|-------|--------|
| <=64 chars | {CHAR_COUNT} chars | {PASS_FAIL} |
| Lowercase alphanumeric + hyphens only | `{SKILL_NAME}` | {PASS_FAIL} |
| No consecutive hyphens | {YES_NO} | {PASS_FAIL} |
| Matches parent directory | {DIR_NAME}/ | {PASS_FAIL} |
| Gerund form (best practice) | {YES_NO} | {PASS_FAIL} |

### 1.2 `description` (~{DESC_CHARS} chars)

| Criterion | Value | Result |
|-----------|-------|--------|
| <=1024 chars | {DESC_CHARS} chars | {PASS_FAIL} |
| Describes WHAT | {FIRST_SENTENCE} | {PASS_FAIL} |
| Describes WHEN | {TRIGGER_PHRASE} | {PASS_FAIL} |
| Trigger keywords | {KEYWORDS} | {PASS_FAIL} |
| Third person | {YES_NO} | {PASS_FAIL} |
| Specific | {YES_NO} | {PASS_FAIL} |
| Implicit coverage | {YES_NO} | {PASS_FAIL} |
| Negative boundary | {BOUNDARY_OR_MISSING} | {PASS_FAIL} |

### 1.3 `compatibility`

| Criterion | Value | Result |
|-----------|-------|--------|
| Exists? | {YES_NO} | {PASS_FAIL} |
| <=500 chars | {CHARS} | {PASS_FAIL} |
| Real requirement? | {DESCRIPTION} | {PASS_FAIL} |

### 1.4 Extra fields

| Criterion | Result |
|-----------|--------|
| No extra fields beyond name/description/compatibility | {PASS_FAIL} |

---

## 2. Body of SKILL.md

### 2.1 Conciseness

| Criterion | Value | Result |
|-----------|-------|--------|
| Body < 500 lines | {LINE_COUNT} lines | {PASS_FAIL} |
| No obvious Claude-knowledge | {YES_NO} | {PASS_FAIL} |
| Every paragraph justifies token cost | {YES_NO} | {PASS_FAIL} |

### 2.2 Progressive Disclosure

| Criterion | Result |
|-----------|--------|
| All refs one level deep from SKILL.md | {PASS_FAIL} |
| Refs > 100 lines have TOC | {PASS_FAIL} |
| SKILL.md acts as index/overview | {PASS_FAIL} |

### 2.3 Degrees of Freedom

| Area | Freedom | Correct? |
|------|---------|----------|
| {AREA_1} | {HIGH_MED_LOW} | {PASS_FAIL} |
| {AREA_2} | {HIGH_MED_LOW} | {PASS_FAIL} |

### 2.4 Workflows and Feedback Loops

| Criterion | Result |
|-----------|--------|
| Copiable progress checklist | {PASS_FAIL} |
| Explicit feedback loops | {PASS_FAIL} |
| Interruption handling | {PASS_FAIL} |

### 2.5 Content Guidelines

| Criterion | Result |
|-----------|--------|
| No time-sensitive info | {PASS_FAIL} |
| Consistent terminology | {PASS_FAIL} |
| Concrete examples | {PASS_FAIL} |
| No Windows backslash paths | {PASS_FAIL} |
| No extraneous files | {PASS_FAIL} |

---

## 3. Scripts

### 3.1 Per-script Compliance

| Criterion | {SCRIPT_1} | {SCRIPT_2} | {SCRIPT_N} |
|-----------|:---:|:---:|:---:|
| Self-contained | {PASS_FAIL} | {PASS_FAIL} | {PASS_FAIL} |
| --help with examples | {PASS_FAIL} | {PASS_FAIL} | {PASS_FAIL} |
| Descriptive errors | {PASS_FAIL} | {PASS_FAIL} | {PASS_FAIL} |
| Structured output | {PASS_FAIL} | {PASS_FAIL} | {PASS_FAIL} |
| Idempotent | {PASS_FAIL} | {PASS_FAIL} | {PASS_FAIL} |
| --dry-run | {PASS_FAIL} | {PASS_FAIL} | {PASS_FAIL} |
| Distinct exit codes | {PASS_FAIL} | {PASS_FAIL} | {PASS_FAIL} |
| No interactive prompts | {PASS_FAIL} | {PASS_FAIL} | {PASS_FAIL} |
| --verbose / summary | {PASS_FAIL} | {PASS_FAIL} | {PASS_FAIL} |

---

## 4. Triggering

### 4.1 Should-trigger queries

| Query | Trigger? | Keyword match |
|-------|:--------:|--------|
| {QUERY_1} | {YES} | {MATCH} |
| {QUERY_2} | {YES} | {MATCH} |

### 4.2 Should-NOT-trigger queries

| Query | Trigger? | Correct skill |
|-------|:--------:|--------|
| {QUERY_1} | {NO} | {SKILL} |
| {QUERY_2} | {NO} | {SKILL} |

### 4.3 Cross-skill Ambiguity

| Scenario | Risk | Mitigation |
|----------|:----:|------------|
| {SCENARIO} | {HIGH_MED_LOW} | {MITIGATION} |

---

## 5. Evaluations

| Criterion | Result |
|-----------|--------|
| evals/ exists | {PASS_FAIL} |
| evals.json with test cases | {PASS_FAIL} ({COUNT} cases) |
| trigger-queries.json | {PASS_FAIL} ({COUNT} queries) |
| Test fixtures | {PASS_FAIL} |
| Assertion accuracy | {PASS_FAIL} |

---

## 6. Compliance Summary

| # | Criterion | Result |
|---|-----------|:------:|
| 1-4 | Frontmatter (name, description, compatibility, extras) | {EMOJI} |
| 5-12 | Body (conciseness, disclosure, freedom, workflows, content) | {EMOJI} |
| 13-21 | Scripts (9 criteria) | {EMOJI} |
| 22-24 | Triggering (should, should-not, ambiguity) | {EMOJI} |
| 25-26 | Evals (existence, accuracy) | {EMOJI} |

**Score: {PASS}/{TOTAL} criteria passed ({PERCENT}%)**

## 7. Prioritized Findings

### Critical (violates spec or causes triggering failures)

| # | Finding | File(s) | Impact |
|---|---------|---------|--------|
| C-{N} | {FINDING} | {FILE} | {IMPACT} |

### Important (best practice not followed, impacts quality/tokens)

| # | Finding | File(s) | Impact |
|---|---------|---------|--------|
| I-{N} | {FINDING} | {FILE} | {IMPACT} |

### Improvement (recommended optimization)

| # | Finding | File(s) | Impact |
|---|---------|---------|--------|
| M-{N} | {FINDING} | {FILE} | {IMPACT} |

## 8. Action Plan

| # | Task | File(s) | Specific change | Effort |
|:-:|------|---------|-----------------|:------:|
| 1 | {TASK} | {FILE} | {CHANGE} | S/M/L |

---

## Executive Summary

{2-3 sentences summarizing the skill's maturity level, score, key strengths, and immediate actions needed.}
