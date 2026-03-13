# Scripts Audit Checklist

Criteria for evaluating scripts in `scripts/` directory.

## Contents
- [Per-script checklist](#per-script-checklist)
- [Shared framework assessment](#shared-framework-assessment)
- [Severity classification](#severity-classification)

---

## Per-script checklist

For each standalone script in `scripts/`, verify:

| # | Criterion | Pass condition | Severity if missing |
|---|-----------|----------------|:-------------------:|
| 1 | **Self-contained** | No external dependencies not declared in PEP 723 metadata or requirements | Critical |
| 2 | **--help documented** | Running with `--help` shows: description, usage, options, examples, exit codes | Important |
| 3 | **Descriptive errors** | Error messages include: what failed, which path/input, suggested fix | Important |
| 4 | **Structured output** | Output is structured (JSON, Markdown tables, delimited) not free-form text | Improvement |
| 5 | **Idempotent** | Safe to run multiple times with same result (overwrites, not appends) | Important |
| 6 | **--dry-run** | Supports `--dry-run` for preview without side effects | Important |
| 7 | **Distinct exit codes** | Different codes for: success, bad args, path not found, data error | Improvement |
| 8 | **No interactive prompts** | All input via CLI arguments, no stdin prompts | Critical |
| 9 | **Output control** | Summary by default, `--verbose` for detail. Large outputs capped or paginated | Improvement |
| 10 | **PEP 723 metadata** | `# /// script` block with `requires-python` and `dependencies` | Improvement |

## Shared framework assessment

If scripts share a common CLI framework (e.g., `cli_common.py`), evaluate:

| Criterion | What to check |
|-----------|---------------|
| **Consistency** | Do all scripts use the shared framework? Document any divergences |
| **Standardized flags** | Are common flags (`--output`, `--verbose`, `--dry-run`) uniform across scripts? |
| **Error handling** | Does the framework provide centralized path validation and error reporting? |
| **Exit codes** | Are exit codes defined once and reused? |

### Divergence documentation

If a script intentionally diverges from the shared framework (e.g., different argparse):
- Is the divergence documented in SKILL.md or a reference file?
- Is it justified? (e.g., fundamentally different CLI pattern)

## Severity classification

- **Critical**: Script will fail or behave unexpectedly in normal usage
- **Important**: Best practice violation that impacts usability or reliability
- **Improvement**: Optimization that improves quality but isn't required

## Shared modules (non-standalone)

For shared modules (imported by scripts, not run directly):
- Are they documented as "not standalone" in SKILL.md?
- Do they have docstrings explaining their purpose?
- Is there code duplication between modules that should be consolidated?
