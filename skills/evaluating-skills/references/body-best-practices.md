# SKILL.md Body Best Practices

Audit criteria for the markdown body of SKILL.md.

## Contents
- [Conciseness and token budget](#conciseness-and-token-budget)
- [Progressive disclosure](#progressive-disclosure)
- [Degrees of freedom](#degrees-of-freedom)
- [Workflows and feedback loops](#workflows-and-feedback-loops)
- [Content guidelines](#content-guidelines)

---

## Conciseness and token budget

| Rule | Spec |
|------|------|
| Max body length | 500 lines (including frontmatter). If over, content MUST be moved to references/ |
| No obvious knowledge | Do not explain what Claude already knows (what is XML, what is a PDF, etc.) |
| Token justification | Every paragraph must justify its cost. Ask: "Does this paragraph add value Claude cannot infer?" |

### Red flags for bloat
- Explaining general programming concepts
- Repeating information available in references
- Long inline examples that could be in references/
- Sections only needed for a specific phase but always loaded

## Progressive disclosure

Three-level loading system:

1. **Metadata** (name + description) — always in context (~100 words)
2. **SKILL.md body** — loaded when skill triggers (<500 lines)
3. **Bundled resources** — loaded as needed by Claude (unlimited)

### Rules

| Rule | Spec |
|------|------|
| Reference depth | All reference files MUST link directly from SKILL.md (one level deep) |
| No nested references | Avoid SKILL.md -> ref-A.md -> ref-B.md chains. If ref-A links to ref-B, SKILL.md must also link to ref-B |
| TOC for large refs | Reference files > 100 lines MUST have a table of contents at the top |
| SKILL.md as index | SKILL.md should act as an overview/index that points to details in separate files |

### Patterns to check

- **Pattern 1**: High-level guide with references (SKILL.md links to FORMS.md, REFERENCE.md, etc.)
- **Pattern 2**: Domain-specific organization (content split by domain, Claude loads only what's needed)
- **Pattern 3**: Conditional details (basic content inline, advanced content in references)

## Degrees of freedom

Match specificity to task fragility:

| Freedom level | When to use | Examples |
|---------------|-------------|---------|
| **High** (heuristics) | Multiple valid approaches, context-dependent | Narrative docs, architecture decisions |
| **Medium** (templates with params) | Preferred pattern exists, some variation OK | Diagram styling, enrichment instructions |
| **Low** (exact scripts) | Fragile operations, consistency critical | XML parsing, file generation, validation |

### What to check
- Are scripts given low freedom? (they should be)
- Are narrative/creative tasks given high freedom? (they should be)
- Are there unnecessary options where a single approach would suffice?

## Workflows and feedback loops

| Rule | Spec |
|------|------|
| Progress tracking | Complex workflows MUST have a copiable checklist for tracking progress |
| Feedback loops | Explicit validate -> correct -> repeat cycles |
| Interruption handling | "Resume from here if interrupted" guidance |
| Dependency ordering | Clear statement of which steps depend on which |

## Content guidelines

| Rule | Spec |
|------|------|
| No time-sensitive info | Avoid version-pinned URLs, dates that will become stale |
| Consistent terminology | Same term for the same concept throughout the skill |
| Concrete examples | Real examples, not abstract descriptions |
| No Windows backslash paths | Always use forward slashes in paths |
| No extraneous files | No README.md, CHANGELOG.md, INSTALLATION_GUIDE.md in the skill |
