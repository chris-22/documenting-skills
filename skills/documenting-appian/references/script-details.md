# Script Details — Extended Documentation

Detailed reference for scripts with non-obvious behavior. For basic usage, run any script with `--help`.
All scripts share common flags via `cli_common.py`: `--app-dir`, `--index`, `--output`, `--dry-run`, `--verbose`.

## Contents
- [cli_common.py — Shared CLI framework](#cli_commonpy--shared-cli-framework)
- [analyze_health.py — Classification heuristics](#analyze_healthpy--classification-heuristics)
- [generate_deployment.py — ICF template format](#generate_deploymentpy--icf-template-format)
- [validate_docs.py — Checks and auto-fix](#validate_docspy--checks-and-auto-fix)
- [diff_exports.py — Change detection + affected docs](#diff_exportspy--change-detection--affected-docs)

---

## cli_common.py — Shared CLI framework

Not a standalone script. Imported by all other scripts.

| Function | Purpose |
|----------|---------|
| `make_parser(description, default_output, ...)` | Standardized argparse with `--app-dir`, `--index`, `--output`, `--dry-run`, `--verbose` |
| `validate_args(args, ...)` | Validates paths; creates output dir; exits code 2 on missing paths |
| `write_output(args, content, label)` | Writes to `args.output`; respects `--dry-run` |
| `verbose(args, msg)` | Prints to stderr only when `--verbose` is active |

Exit codes: 0=OK, 1=bad args, 2=path not found, 3=data error.

---

## analyze_health.py — Classification heuristics

### Analysis levels

1. **UUID reference graph** — Scans all XML for UUID patterns (`_a-...`, `urn:appian:...`). Builds directed reference graph.
2. **Expression analysis** — Scans expression tags (`expression`, `uiExpr`, `visibilityExpr`, `nameExpr`, `titleExpr`, `listViewTemplateExpr`, `detailViewExpr`, `definition`) for `rule!Name`, `cons!Name`, `#"_a-..."`, `#"urn:appian:record-type:..."`.
3. **Classification** — Categorizes every object:
   - **entry-point**: Sites, Web APIs, application, tempoReport
   - **structural**: Connected systems, groups, translation sets/strings, data stores, datatypes, PM folders
   - **unverifiable-content**: Objects in `content/` (binary/opaque)
   - **critical/referenced**: ≥1 incoming reference
   - **potentially-unused**: 0 incoming references

### Key heuristics

- `content/` objects → always "unverifiable-content" (never "unused")
- Structural types → never "unused" even with 0 refs
- Expression scanner reduces unverifiable from ~86% to ~40-50%

---

## generate_deployment.py — ICF template format

Produces two files:
- `docs/09-appian-deployment.md` — JDBC data sources, checklist, risks
- `docs/appian-import-customization-template.properties` — ICF with actual UUIDs

ICF format:
```properties
#connectedSystem.<uuid>.baseUrl=
#connectedSystem.<uuid>.username=
#content.<uuid>.VALUE=
#recordType.<uuid>.forceSync=true
```

---

## validate_docs.py — Checks and auto-fix

| Check | Validates |
|-------|-----------|
| File existence | 11 required + 3 optional docs files |
| Internal links | `[text](target)` → file exists |
| TODO counts | `TODO(unknown)`, `TODO(unresolved-ref:...)` |
| Mermaid syntax | Reserved word IDs, unmatched blocks (deep validation via `mermaid_validator.py`) |
| Secrets scan | Password/token/API key/Bearer/Basic patterns |

Use `--fix` to auto-correct fixable Mermaid issues. Output appended to `docs/README.md`.

---

## diff_exports.py — Change detection + affected docs

| Change type | Detection |
|-------------|-----------|
| New | UUID in new, not in baseline |
| Deleted | UUID in baseline, not in new |
| Renamed | Same UUID, different `name` |

### Affected docs mapping (TYPE_TO_DOCS)

| Object type | Affected docs |
|-------------|---------------|
| `processModel` | `04-appian-architecture.md`, `process-models/` |
| `connectedSystem` | `07-appian-integrations.md`, `09-appian-deployment.md` |
| `datatype` | `06-appian-data.md` |
| `dataStore` | `06-appian-data.md`, `09-appian-deployment.md` |
| `group` | `08-appian-security.md` |
| `webApi` | `07-appian-integrations.md`, `04-appian-architecture.md` |
| `site` | `05-appian-navigation.md`, `04-appian-architecture.md` |
| `recordType` | `06-appian-data.md`, `09-appian-deployment.md` |
| `translationSet/String` | `10-appian-i18n.md` |

---

## pm2mermaid.py — Divergent CLI

Unlike all other scripts, `pm2mermaid.py` uses its **own argparse** (not `cli_common.make_parser()`).

| Flag | Equivalent in other scripts | Notes |
|------|-----------------------------|-------|
| positional `xml_path` | `--app-dir` | Single XML file **or** omitted for legend-only mode |
| `--out <file>` | `--output` | Exact output path |
| `--dir <dir>` | — | Output directory (filename auto-derived from PM name) |
| `--legend` | — | Copy `assets/_legend.md` to output dir |
| `--no-validate` | — | Skip Mermaid syntax validation |
| `--dry-run` | same | Preview without writing |
| `--verbose` | same | Detailed stderr output |

**Batch usage** (all PMs):
```bash
# $base must be set to the scripts/ directory (see bash-commands.md for auto-detection)
for f in processModel/*.xml; do
  python "$base/pm2mermaid.py" "$f" --dir docs/process-models --legend
done
```

**Output structure**: BPMN `flowchart` diagram with `classDef` Palette B colors, `class` assignments, legend link, `## Evidencias` section. See [type-mapping.md](type-mapping.md) for shape/color mapping rules.

---

## Other scripts — Output structure summary

Each script's output structure is documented here for agent reference when enriching auto-generated docs.

| Script | Output sections |
|--------|----------------|
| `generate_navigation.py` | Site properties table, pages table, `block-beta` diagram, Evidencias |
| `extract_integrations.py` | CS detail, outbound integrations table, `flowchart LR`, `sequenceDiagram` per CS, `C4Context`, ICF notes, Evidencias |
| `extract_role_maps.py` | Group hierarchy `flowchart TD` (admin/role/geo/tech colors), role assignment `flowchart LR`, full matrix, per-group summary, orphan objects, Evidencias |
| `extract_translations.py` | Translation sets, strings table (key × locale), Evidencias |
| `list_process_models.py` | Pipe-delimited (default), `--tsv`, or `--json` output |
