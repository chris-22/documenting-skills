# Quality Criteria

Quality checklist with pass/fail criteria to verify the generated documentation during Phase 5 (Validation).

## Table of Contents

- [1. Completeness](#1-completeness)
- [2. Accuracy](#2-accuracy)
- [3. Examples](#3-examples)
- [4. Diagrams](#4-diagrams)
- [5. Navigability](#5-navigability)
- [6. Self-containment](#6-self-containment)
- [7. Anonymization & Security](#7-anonymization--security)
- [8. Wiki Publishing](#8-wiki-publishing)
- [9. HTML Export](#9-html-export)
- [Validation Procedure](#validation-procedure)

---

## 1. Completeness

| # | Criterion | Pass/Fail |
|---|---|---|
| 1.1 | Each documented REST endpoint has: HTTP method, path, Content-Type | |
| 1.2 | Each endpoint has a request DTO table with all fields | |
| 1.3 | Each endpoint has a response DTO table with all fields | |
| 1.4 | Each endpoint has a request JSON example | |
| 1.5 | Each endpoint has a response JSON example | |
| 1.6 | Each BPMN Service Task has: Java interface, method, inputs, outputs | |
| 1.7 | Each Service Task has documented post-execution decision logic | |
| 1.8 | All BPMN errors are cataloged with their errorCode | |
| 1.9 | All gateways have their conditions documented | |
| 1.10 | BPMN process variables are listed with full Java type | |
| 1.11 | At least one **architecture** diagram exists | |
| 1.12 | At least one **process flow** diagram exists | |
| 1.13 | At least one **data flow** diagram exists | |
| 1.14 | Environments (dev/cert/pre/pro) are documented with URLs | |
| 1.15 | Error patterns are explained with flow diagrams | |
| 1.16 | Table of contents reflects ALL document sections | |
| 1.17 | Common headers are documented in a table | |

## 2. Accuracy

| # | Criterion | Pass/Fail |
|---|---|---|
| 2.1 | Java class names match exactly with source code | |
| 2.2 | REST client configKeys match `application.properties` / `.yml` | |
| 2.3 | Java types for DTO fields are correct (not generic) | |
| 2.4 | Event codes match between the catalog and each system's sections | |
| 2.5 | URLs per environment match actual configuration | |
| 2.6 | Dependency versions match `pom.xml` / `build.gradle` | |
| 2.7 | REST endpoint paths match `@Path` / `@RequestMapping` in code | |
| 2.8 | DTO inheritance/composition structure is correctly reflected | |

## 3. Examples

| # | Criterion | Pass/Fail |
|---|---|---|
| 3.1 | JSON example for each endpoint (request + response) | |
| 3.2 | JSONs are realistic and domain-coherent (not `"string"`, `0`, `true`) | |
| 3.3 | Example JSONs include nested fields when the DTO has them | |
| 3.4 | HTTP request examples include relevant headers | |
| 3.5 | If WireMock mocks are available, they were used as example source | |
| 3.6 | Example data is consistent across sections (same entityId, requestId, etc.) | |

## 4. Diagrams

| # | Criterion | Pass/Fail |
|---|---|---|
| 4.1 | All ` ```mermaid ` blocks have valid syntax | |
| 4.2 | Architecture diagram shows all system layers | |
| 4.3 | Process flow diagram includes all phases and gateways | |
| 4.4 | Data flow diagram shows dependencies between systems | |
| 4.5 | Diagrams use patterns from `references/diagram-patterns.md` | |
| 4.6 | Node labels are descriptive and < 40 characters | |
| 4.7 | Diagrams have < 30 nodes each (split if larger) | |

## 5. Navigability

| # | Criterion | Pass/Fail |
|---|---|---|
| 5.1 | Table of contents with functional anchor links | |
| 5.2 | Consistent section numbering (1, 2, 3...) | |
| 5.3 | Consistent heading levels (`##` for main, `###` for subsections) | |
| 5.4 | `---` separators between main sections | |
| 5.5 | Each integration section follows the same subsection structure | |
| 5.6 | Code blocks with language hints (`json`, `java`, `mermaid`, etc.) | |

## 6. Self-containment

| # | Criterion | Pass/Fail |
|---|---|---|
| 6.1 | A new developer can fully understand the project from this document alone | |
| 6.2 | No references to external documents without contextual explanation | |
| 6.3 | All acronyms and technical terms are explained on first use | |
| 6.4 | Inter-system dependencies are explicitly documented | |
| 6.5 | Section order follows the logical sequence of the process/flow | |

## 7. Anonymization & Security

| # | Criterion | Pass/Fail |
|---|---|---|
| 7.1 | No real credentials, tokens, or API keys in examples | |
| 7.2 | Internal URLs use `{env}` placeholders instead of real hosts | |
| 7.3 | IDs in examples are fictitious but realistic | |
| 7.4 | Secrets referenced by name, without exposed values | |
| 7.5 | No PII data (real names, emails, phone numbers) in examples | |

## 8. Wiki Publishing

| # | Criterion | Pass/Fail |
|---|---|---|
| 8.1 | `Home.md` contains title, description, stack, and page links | |
| 8.2 | `_Sidebar.md` contains navigation with links to all sections | |
| 8.3 | Anchor links in `_Sidebar.md` use correct format: `PageName#anchor` | |
| 8.4 | Headings generate GitHub Wiki-compatible anchors (kebab-case) | |
| 8.5 | ` ```mermaid ` blocks are valid for native GitHub rendering | |

## 9. HTML Export

| # | Criterion | Pass/Fail |
|---|---|---|
| 9.1 | HTML is a single standalone file | |
| 9.2 | Mermaid JS loads from CDN and initializes with `startOnLoad: true` | |
| 9.3 | Mermaid blocks converted to `<pre class="mermaid">` | |
| 9.4 | GitHub-like CSS styles applied (font, table borders, code blocks) | |
| 9.5 | HTML table of contents with functional internal links | |
| 9.6 | Responsive: readable on screens from 1024px to 1920px | |
| 9.7 | Mermaid diagrams render as SVG when opened in browser | |

---

## Validation Procedure

1. Go through each criterion and mark Pass or Fail.
2. For each Fail, document the gap and fix it before finalizing.
3. Inform the user of any gap that cannot be automatically fixed (e.g., lack of access to external JARs, OpenAPI specs unavailable).
4. A document is considered **complete** when all applicable criteria are Pass.
5. Non-applicable criteria (e.g., BPMN in a project without BPMN) are marked as N/A.
