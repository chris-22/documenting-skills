# Frontmatter Specification

Audit criteria for YAML frontmatter fields in SKILL.md.

## Contents
- [name](#name)
- [description](#description)
- [compatibility](#compatibility)
- [Extra fields](#extra-fields)

---

## name

| Rule | Spec |
|------|------|
| Max length | 64 characters |
| Allowed chars | Lowercase alphanumeric + hyphens only |
| No consecutive hyphens | `my--skill` is invalid |
| Must match parent directory | Directory `foo-bar/SKILL.md` requires `name: foo-bar` |
| Preferred form | Gerund (`documenting-x`, `evaluating-x`) over noun (`x-generator`, `x-publisher`) |

## description

| Rule | Spec |
|------|------|
| Max length | 1024 characters |
| WHAT it does | First sentence describes the skill's function |
| WHEN to use it | Explicit trigger conditions: "Use when...", "Triggers when..." |
| Triggering keywords | Include verbs/nouns users would naturally say |
| Third person | "Generates...", "Analyzes..." (never "I can..." or "You can...") |
| Specific, not vague | List concrete artifacts, file types, object types |
| Implicit coverage | "even without explicitly mentioning X" if applicable |
| Negative boundary | "NOT for X (use other-skill instead)" to disambiguate |

### Description quality checklist

1. Does it answer "What does this skill do?" in the first sentence?
2. Does it list 3+ trigger keywords that a user would naturally say?
3. Does it explicitly say when NOT to use it (if other similar skills exist)?
4. Would a generic prompt like "help me with X" correctly trigger this skill?
5. Is every word earning its place? (no filler, no redundant phrases)

## compatibility

| Rule | Spec |
|------|------|
| Max length | 500 characters |
| When to include | Only if there are real environment requirements (runtime, OS, packages) |
| Content | Runtime version, required packages, OS constraints |
| Omit if | No special requirements beyond what Claude has by default |

## Extra fields

Per the skill-creator spec: **Do not include any other fields in YAML frontmatter** beyond `name`, `description`, and optionally `compatibility`.

Fields like `allowed-tools`, `metadata`, `version` are NOT part of the official spec. Flag them as deviations if found.
