# Evaluations Audit Guide

Criteria for auditing the `evals/` directory of a skill.

## Contents
- [Directory structure](#directory-structure)
- [Test case quality](#test-case-quality)
- [Trigger queries](#trigger-queries)
- [Proposing test cases](#proposing-test-cases-when-evals-is-missing)

---

## Directory structure

Check for presence and quality of:

| File/Dir | Purpose | Required? |
|----------|---------|:---------:|
| `evals/evals.json` | Test cases with prompts, expected outputs, assertions | Recommended |
| `evals/trigger-queries.json` | Should-trigger and should-NOT-trigger queries with train/validation split | Recommended |
| `evals/files/` | Test fixtures (minimal inputs, edge cases, corrupted data) | Optional |

## Test case quality

For each test case in `evals.json`, verify:

| Criterion | What to check |
|-----------|---------------|
| **Realistic prompt** | Would a real user write this? Mix formal/casual, ES/EN |
| **Expected output** | Specific enough to verify (file names, section names, content patterns) |
| **Assertions** | Each assertion is independently verifiable (file exists, section contains X) |
| **Rubric** | Defines what "good" looks like for subjective quality |

### Coverage categories

A well-covered skill should have test cases for:

| Category | Example |
|----------|---------|
| Full workflow (happy path) | "Generate everything end to end" |
| Single capability | "Only generate the inventory" |
| Edge cases | Minimal input, corrupted data, empty directories |
| Casual language | "oye hazme X" / "hey can you do X" |
| Negative cases | Prompts that should NOT trigger the skill |
| --dry-run | Verify no side effects |
| Incremental updates | "Only update what changed" |

### Assertion accuracy

Check that assertions use correct:
- **File names**: Match the skill's current naming convention (e.g., numeric prefixes)
- **File paths**: Match the skill's current installation location
- **Section names**: Match actual output format of scripts

## Trigger queries

For `trigger-queries.json`, verify:

| Criterion | What to check |
|-----------|---------------|
| **Train/validation split** | Queries are labeled as `"set": "train"` or `"set": "validation"` |
| **Balance** | Mix of should-trigger (true) and should-NOT-trigger (false) |
| **Languages** | Both ES and EN if the skill is bilingual |
| **Casual language** | Includes informal phrasing ("oye", "hey", slang) |
| **Adjacent domains** | Should-NOT-trigger includes queries for related but different skills |

## Proposing test cases when evals/ is missing

If no `evals/` directory exists, propose 3 test cases per skill:

### Template for a test case

```json
{
  "id": 1,
  "prompt": "Realistic user prompt in natural language",
  "files": ["input/files/or/directories"],
  "expected_output": "Description of expected result",
  "assertions": [
    "Specific verifiable assertion 1",
    "Specific verifiable assertion 2"
  ],
  "rubric": {
    "dimension_name": "What good looks like for this dimension"
  }
}
```

### Template for a negative test case

```json
{
  "id": 99,
  "prompt": "Prompt that should NOT trigger this skill",
  "should_trigger": false,
  "rationale": "Why this should not trigger",
  "assertions": [
    "The skill does NOT activate",
    "No skill-specific outputs are generated"
  ]
}
```
