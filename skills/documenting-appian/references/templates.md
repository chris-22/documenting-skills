# Output Templates — Agent-Written Documents

Skeleton structures for the 4 docs that require agent narrative (not auto-generated).
Adapt sections based on what the export contains. Standard Markdown tables/headers omitted — only non-obvious structure shown.

## Contents
- [01-appian-overview.md](#01-appian-overviewmd)
- [02-appian-glossary.md](#02-appian-glossarymd)
- [11-appian-interfaces.md](#11-appian-interfacesmd)
- [README.md](#readmemd)

---

## 01-appian-overview.md

Required sections: Application identity (table: Name, UUID, Description, Prefix convention, Primary language), Purpose and scope, Naming conventions, Folder structure, Dependencies, Complexity metrics, Evidencias.

**Key non-obvious content:**
- **Dependencies**: identify the parent/base application by checking `<parentUuid>` in manifest, shared-prefix patterns in expressions, and external CDT/DS/group references. This is **critical for deployment**.
- **Naming conventions**: build from observed prefixes — see "Appian technical prefixes" table below.
- **Complexity metrics**: copy summary from `03-appian-inventory.md` after Phase B.

---

## 02-appian-glossary.md

Required sections: Business concepts, Domain acronyms, External systems, Roles and actors, Workflow states, Appian technical prefixes, Evidencias.

**Key non-obvious content:**
- **Workflow states**: infer from CDT fields named `Estado`/`Stage`/`Status` and XOR gateway labels in PMs.
- **Domain acronyms**: actively investigate by reading XSD `<annotation>` tags and CDT descriptions. Do NOT leave as `TODO(unknown)` if context provides enough clues (e.g., `rccdtcatalogo<acronym>` → the acronym likely refers to a catalog entity).
- **Appian technical prefixes** (always include):

| Prefix | Object type |
|--------|------------|
| PM | Process Model |
| CDT | Custom Data Type |
| DS | Data Store |
| WA | Web API |
| CS | Connected System |
| RT | Record Type |
| FRM | Interface |
| RGL | Expression Rule |
| CONS | Constant |
| DEC | Decision |
| INT | Integration |
| SEC | Section |

---

## 11-appian-interfaces.md

Required sections: Interfaces (classified as: main screens, task forms, reusable components, potentially unused), Expression rules summary (grouped by category: validation, query, utility), Decisions summary, Constants summary, Content folder structure (tree format), Evidencias.

**Key non-obvious content:**
- **Content folder structure**: render as tree (not flat table) showing Knowledge Center → folders → rules hierarchy.
- **Interface classification**: cross-reference with site pages (main screens), PM task assignments (task forms), and health analysis (potentially unused).

---

## README.md

Required sections: Document index (table linking all docs), How to regenerate (see SKILL.md Quick start), Documentation quality (auto-populated by `validate_docs.py`).

The quality section is auto-appended by `validate_docs.py` — no need to write it manually.
