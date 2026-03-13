# Mermaid Validator — Complete Check Reference

## Contents
- [All diagram types](#all-diagram-types)
- [flowchart (Palette A & B)](#flowchart-palette-a--b)
- [sequenceDiagram](#sequencediagram)
- [stateDiagram-v2](#statediagram-v2)
- [erDiagram](#erdiagram)
- [block-beta](#block-beta)
- [C4Context / C4Container / C4Component / C4Dynamic / C4Deployment](#c4context--c4container--c4component--c4dynamic--c4deployment)
- [pie](#pie)
- [architecture-beta](#architecture-beta)

---

## All diagram types

| Check | Severity | Auto-fix |
|-------|----------|----------|
| Unrecognized diagram type | Error | — |
| Unbalanced double quotes in labels | Error | ✅ Adds closing quote |

## flowchart (Palette A & B)

| Check | Severity | Auto-fix |
|-------|----------|----------|
| Reserved words as node IDs (`end`, `default`, etc.) | Error | ✅ Renames to `{word}_node` |
| Unclosed `subgraph` blocks | Error | ✅ Appends missing `end` |
| Invalid shape names (pre-v11.3) | Warning | — |
| Pipe `\|` character in labels (breaks syntax) | Error | ✅ Replaces with `&#124;` |
| Orphan nodes (defined but not in any edge) | Warning | — |

## sequenceDiagram

| Check | Severity | Auto-fix |
|-------|----------|----------|
| Unclosed `loop`/`alt`/`opt`/`par`/`critical`/`break` blocks | Error | ✅ Appends `end` |
| `end` without matching block opener | Error | — |
| `else` outside `alt` block | Warning | — |
| `and` outside `par` block | Warning | — |
| `Note` without `right of`/`left of`/`over` | Error | — |
| Unbalanced quotes in participant aliases | Error | ✅ Adds closing quote |
| Empty diagram (no participants or messages) | Warning | — |

## stateDiagram-v2

| Check | Severity | Auto-fix |
|-------|----------|----------|
| Wrong arrow type (`->`, `==>` instead of `-->`) | Error | ✅ Replaces with `-->` |
| Invalid `direction` value (must be LR/RL/TB/BT) | Error | — |
| Unclosed composite `state { ... }` blocks | Error | ✅ Appends `}` |
| `Note` without `right of`/`left of` | Error | — |
| No transitions found | Warning | — |

## erDiagram

| Check | Severity | Auto-fix |
|-------|----------|----------|
| Unclosed entity `{ ... }` blocks | Error | ✅ Appends `}` |
| Invalid attribute format inside entity block | Warning | — |
| Relationship without label after `:` | Warning | — |
| Empty diagram | Warning | — |

## block-beta

| Check | Severity | Auto-fix |
|-------|----------|----------|
| Missing `columns N` declaration | Warning | — |
| Unclosed nested `block ... end` | Error | ✅ Appends `end` |
| `end` without matching `block` | Error | — |
| Unbalanced quotes in block labels | Error | ✅ Adds closing quote |

## C4Context / C4Container / C4Component / C4Dynamic / C4Deployment

| Check | Severity | Auto-fix |
|-------|----------|----------|
| Unknown C4 keyword (not in official spec) | Warning | — |
| `Rel()` references undefined alias | Warning | — |
| Unclosed Boundary `{ ... }` blocks | Error | ✅ Appends `}` |
| Unbalanced quotes in element definitions | Error | ✅ Adds closing `")` |
| Unbalanced parentheses | Error | ✅ Adds closing `)` |
| No elements defined | Warning | — |

## pie

| Check | Severity | Auto-fix |
|-------|----------|----------|
| Label not in double quotes | Error | ✅ Adds quotes |
| Value <= 0 (Mermaid rejects) | Error | — |
| Non-numeric value | Error | — |
| Empty label | Warning | — |
| No data entries | Warning | — |

## architecture-beta

| Check | Severity | Auto-fix |
|-------|----------|----------|
| `group`/`service` without icon | Error | ✅ Adds `(server)` |
| Non-standard icon name | Warning | — |
| Invalid characters in labels (`-`, `[`, `]`, etc.) | Error | ✅ Replaces with spaces |
| Edge references undefined service/group | Warning | — |
