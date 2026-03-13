# Triggering Analysis Guide

How to audit a skill's description for correct triggering behavior.

## Contents
- [Should-trigger analysis](#should-trigger-analysis)
- [Should-NOT-trigger analysis](#should-not-trigger-analysis)
- [Cross-skill ambiguity analysis](#cross-skill-ambiguity-analysis)
- [Implicit trigger coverage](#implicit-trigger-coverage)

---

## Should-trigger analysis

Generate 5 realistic queries (mix of ES and EN, formal and casual) that SHOULD activate the skill. For each:

| Column | What to write |
|--------|---------------|
| Query | A realistic user prompt |
| Trigger? | Should be YES for all in this section |
| Keyword match | Which words in the description match the query |

### Query patterns to test
- **Direct request**: "Generate X for Y" (formal, explicit)
- **Casual request**: "oye puedes hacerme X" / "hey can you do X"
- **Implicit request**: describes the need without naming the skill's domain
- **Partial request**: asks for only one capability of the skill
- **English equivalent**: same intent in the other language

## Should-NOT-trigger analysis

Generate 5 realistic queries that are SIMILAR but should NOT activate the skill. For each:

| Column | What to write |
|--------|---------------|
| Query | A realistic user prompt that's adjacent but wrong |
| Trigger? | Should be NO for all in this section |
| Correct skill | Which skill (if any) should handle this instead |

### Anti-patterns to test
- **Same domain, different action**: e.g., "deploy X" vs "document X"
- **Same action, different domain**: e.g., "document Java project" vs "document Appian export"
- **Development vs documentation**: e.g., "create a new process" vs "document existing processes"
- **Similar keywords, wrong context**: e.g., "BPMN diagram" for Kogito vs Appian

## Cross-skill ambiguity analysis

For each skill in the same workspace, check:

1. **Overlapping keywords**: Are there keywords that appear in both descriptions?
2. **Missing negative boundaries**: Does skill A say "NOT for X" but skill B doesn't say "NOT for Y"?
3. **Generic prompts**: Would a vague prompt like "document this" or "generate diagrams" correctly route?

### Ambiguity risk levels

| Risk | Description | Action |
|------|-------------|--------|
| High | Same keywords, no negative boundaries, generic prompts misroute | Add explicit negative boundaries to BOTH skills |
| Medium | Some overlap but context (file presence, project type) disambiguates | Document the discriminator in the audit |
| Low | Different domains, minimal keyword overlap | No action needed |

## Implicit trigger coverage

Check if the description handles:
- Users who don't know the skill's name
- Users who describe the outcome, not the process
- Users who use domain jargon vs generic terms
- Users who ask in a different language than the description

The description should include phrases like:
- "even without explicitly mentioning X"
- "or any variant of..."
- "including... but not limited to..."
