#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Phase G — Validate generated documentation.

Checks: file existence, internal links, TODO counts, Mermaid syntax basics,
unfilled placeholders, and no-secrets scan. Appends a Documentation Quality
section to docs/README.md (or prints to stdout with --dry-run).
"""
import os
import re
import sys
import glob

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# mermaid_validator is now a sibling module in the same scripts/ directory.
from mermaid_validator import validate_markdown_file, validate_and_fix_file
HAS_DEEP_VALIDATOR = True

from app_info import get_app_name
from cli_common import make_parser, validate_args, write_output, verbose

DEFAULT_OUT = os.path.join("docs", "README.md")
DOCS_DIR = "docs"

EXPECTED_FILES = [
    "01-appian-overview.md",
    "02-appian-glossary.md",
    "04-appian-architecture.md",
    "05-appian-navigation.md",
    "03-appian-inventory.md",
    "06-appian-data.md",
    "07-appian-integrations.md",
    "08-appian-security.md",
    "09-appian-deployment.md",
    "12-appian-health.md",
    "_uuid-index.json",
]

OPTIONAL_FILES = [
    "10-appian-i18n.md",
    "11-appian-interfaces.md",
    "appian-import-customization-template.properties",
]

# Patterns that look like secrets
SECRET_PATTERNS = [
    re.compile(r'(?i)(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*\S{8,}'),
    re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*'),
    re.compile(r'Basic\s+[A-Za-z0-9+/]{20,}={0,2}'),
]

# Mermaid reserved words that cause rendering issues as node IDs
MERMAID_RESERVED = {"end", "default", "graph", "subgraph", "classDef", "class", "click"}


def check_file_existence(docs_dir):
    """Check which expected files exist."""
    results = []
    for f in EXPECTED_FILES:
        path = os.path.join(docs_dir, f)
        exists = os.path.exists(path)
        results.append(("✅" if exists else "❌", f, "obligatorio"))
    for f in OPTIONAL_FILES:
        path = os.path.join(docs_dir, f)
        exists = os.path.exists(path)
        results.append(("✅" if exists else "⬜", f, "opcional"))
    # Process models directory
    pm_dir = os.path.join(docs_dir, "process-models")
    pm_count = len(glob.glob(os.path.join(pm_dir, "*.md"))) if os.path.isdir(pm_dir) else 0
    results.append(("✅" if pm_count > 0 else "❌", f"process-models/ ({pm_count} archivos)", "obligatorio"))
    return results


def count_todos(docs_dir):
    """Count TODO markers in all markdown files."""
    todo_unknown = 0
    todo_unresolved = 0
    todo_agent = 0
    files_with_todos = []
    for f in glob.glob(os.path.join(docs_dir, "*.md")):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception:
            continue
        u = len(re.findall(r'TODO\(unknown\)', content))
        r = len(re.findall(r'TODO\(unresolved-(?:ref|group):', content))
        a = len(re.findall(r'<!-- AGENT:', content))
        if u + r + a > 0:
            files_with_todos.append((os.path.basename(f), u, r, a))
        todo_unknown += u
        todo_unresolved += r
        todo_agent += a
    return todo_unknown, todo_unresolved, todo_agent, files_with_todos


def check_mermaid_syntax(docs_dir, fix=False):
    """Validate Mermaid syntax in all markdown files.
    
    Uses deep validation from mermaid_validator (sibling module) if available,
    otherwise falls back to basic regex checks.
    """
    issues = []
    fixed_count = 0
    
    md_files = glob.glob(os.path.join(docs_dir, "**", "*.md"), recursive=True)
    
    if HAS_DEEP_VALIDATOR:
        for f in md_files:
            fname = os.path.relpath(f, docs_dir)
            try:
                block_issues = validate_and_fix_file(f, dry_run=not fix)
            except Exception as exc:
                issues.append(f"{fname}: error al validar — {exc}")
                continue
            for block_idx, block_issue_list in block_issues:
                for issue in block_issue_list:
                    prefix = "🔧" if issue.fix and fix else ""
                    issues.append(f"{prefix}{fname} bloque {block_idx} {issue}")
                    if issue.fix and fix:
                        fixed_count += 1
    else:
        # Fallback: basic checks
        for f in md_files:
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except Exception:
                continue
            fname = os.path.relpath(f, docs_dir)
            blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
            for i, block in enumerate(blocks):
                lines = block.strip().split("\n")
                for line_num, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if re.match(r'^(end)\s', stripped, re.IGNORECASE):
                        issues.append(f"{fname} block {i+1} L{line_num}: `end` usado como nodo")
                    quote_count = stripped.count('"')
                    if quote_count % 2 != 0:
                        issues.append(f"{fname} block {i+1} L{line_num}: comillas sin cerrar")
    
    return issues, fixed_count


def check_secrets(docs_dir):
    """Scan for potential secrets in documentation."""
    findings = []
    for f in glob.glob(os.path.join(docs_dir, "**", "*.md"), recursive=True):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception:
            continue
        fname = os.path.relpath(f, docs_dir)
        for pattern in SECRET_PATTERNS:
            matches = pattern.findall(content)
            if matches:
                findings.append(f"{fname}: {len(matches)} posible(s) secreto(s) detectado(s)")
    return findings


def check_internal_links(docs_dir):
    """Check that internal markdown links point to existing files."""
    broken = []
    for f in glob.glob(os.path.join(docs_dir, "*.md")):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception:
            continue
        fname = os.path.basename(f)
        # Find markdown links like [text](file.md) or [text](file.md#section)
        links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
        for text, target in links:
            if target.startswith("http") or target.startswith("#"):
                continue
            # Strip anchor
            target_file = target.split("#")[0]
            if not target_file:
                continue
            target_path = os.path.join(docs_dir, target_file)
            if not os.path.exists(target_path):
                broken.append(f"{fname}: enlace roto → `{target_file}`")
    return broken


def main():
    parser = make_parser(
        "Validate generated documentation and produce quality report.",
        default_output=DEFAULT_OUT, needs_app_dir=False, needs_index=False,
        extra_args=[
            {"flags": ["--fix"], "action": "store_true",
             "help": "Auto-fix Mermaid syntax issues in docs (default: report only)."},
        ],
        examples=[
            "python validate_docs.py",
            "python validate_docs.py --fix",
            "python validate_docs.py --output custom-readme.md",
            "python validate_docs.py --dry-run",
        ],
    )
    args = parser.parse_args()

    docs_dir = os.path.dirname(args.output) or DOCS_DIR

    # Run all checks
    verbose(args, f"Validating docs in {docs_dir}")
    file_results = check_file_existence(docs_dir)
    verbose(args, f"  File existence: {sum(1 for s,_,_ in file_results if s=='✅')}/{len(file_results)} present")
    todo_u, todo_r, todo_a, todo_files = count_todos(docs_dir)
    verbose(args, f"  TODOs: {todo_u} unknown, {todo_r} unresolved, {todo_a} agent placeholders")
    mermaid_issues, mermaid_fixed = check_mermaid_syntax(docs_dir, fix=getattr(args, 'fix', False))
    verbose(args, f"  Mermaid: {len(mermaid_issues)} issues, {mermaid_fixed} fixed")
    secret_findings = check_secrets(docs_dir)
    broken_links = check_internal_links(docs_dir)
    verbose(args, f"  Secrets: {len(secret_findings)} warnings, Links: {len(broken_links)} broken")

    # Generate quality section
    lines = [
        "",
        "## Calidad de la documentación (auto-validado)",
        "",
    ]

    # File existence
    missing = sum(1 for s, _, t in file_results if s == "❌")
    lines.append("### Completitud")
    lines.append("")
    lines.append("| Estado | Archivo | Tipo |")
    lines.append("|--------|---------|------|")
    for status, fname, ftype in file_results:
        lines.append(f"| {status} | `{fname}` | {ftype} |")
    lines.append("")

    # TODOs
    lines.append("### TODOs pendientes")
    lines.append("")
    total_todos = todo_u + todo_r + todo_a
    lines.append(f"| Tipo | Cantidad |")
    lines.append(f"|------|----------|")
    lines.append(f"| `TODO(unknown)` | {todo_u} |")
    lines.append(f"| `TODO(unresolved-ref/group)` | {todo_r} |")
    lines.append(f"| `<!-- AGENT -->` placeholders | {todo_a} |")
    lines.append(f"| **Total** | **{total_todos}** |")
    lines.append("")
    if todo_files:
        lines.append("| Archivo | unknown | unresolved | agent |")
        lines.append("|---------|---------|------------|-------|")
        for fname, u, r, a in sorted(todo_files):
            lines.append(f"| `{fname}` | {u} | {r} | {a} |")
        lines.append("")

    # Mermaid
    lines.append("### Sintaxis Mermaid")
    lines.append("")
    validator_type = "profunda (mermaid_validator)" if HAS_DEEP_VALIDATOR else "b\u00e1sica (regex)"
    lines.append(f"Validaci\u00f3n {validator_type}.")
    lines.append("")
    if mermaid_issues:
        errors = [i for i in mermaid_issues if "ERROR" in i or "error" in i.lower()]
        warnings = [i for i in mermaid_issues if i not in errors]
        if mermaid_fixed > 0:
            lines.append(f"🔧 **{mermaid_fixed} problema(s) auto-corregido(s)**")
            lines.append("")
        if errors:
            lines.append(f"⚠️ **{len(errors)} error(es) restante(s)**:")
            lines.append("")
            for issue in errors[:20]:
                lines.append(f"- {issue}")
            lines.append("")
        if warnings:
            lines.append(f"ℹ️ **{len(warnings)} warning(s)**:")
            lines.append("")
            for issue in warnings[:20]:
                lines.append(f"- {issue}")
    else:
        lines.append("✅ Sin problemas de sintaxis detectados.")
    lines.append("")

    # Secrets
    lines.append("### Verificación de secretos")
    lines.append("")
    if secret_findings:
        lines.append(f"⚠️ **{len(secret_findings)} posible(s) secreto(s)**:")
        lines.append("")
        for finding in secret_findings:
            lines.append(f"- {finding}")
    else:
        lines.append("✅ No se detectaron credenciales, API keys ni tokens.")
    lines.append("")

    # Internal links
    lines.append("### Enlaces internos")
    lines.append("")
    if broken_links:
        lines.append(f"⚠️ **{len(broken_links)} enlace(s) roto(s)**:")
        lines.append("")
        for bl in broken_links:
            lines.append(f"- {bl}")
    else:
        lines.append("✅ Todos los enlaces internos apuntan a archivos existentes.")
    lines.append("")

    quality_section = "\n".join(lines)

    # Append to README.md or print
    readme_path = args.output
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            existing = f.read()
        # Remove existing quality section if present (check both ES and legacy EN markers)
        marker = "## Calidad de la documentación"
        marker_legacy = "## Documentation Quality"
        if marker in existing:
            existing = existing[:existing.index(marker)].rstrip()
        elif marker_legacy in existing:
            existing = existing[:existing.index(marker_legacy)].rstrip()
        content = existing + "\n" + quality_section
    else:
        content = f"# {get_app_name()} — Documentación técnica\n" + quality_section

    if getattr(args, "dry_run", False):
        print(f"[dry-run] Would update {readme_path}")
        print(quality_section)
    else:
        os.makedirs(os.path.dirname(readme_path) or ".", exist_ok=True)
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)

    mermaid_str = f"{len(mermaid_issues)} Mermaid issues" + (f" ({mermaid_fixed} fixed)" if mermaid_fixed else "")
    summary = (f"Validation: {missing} missing files, {total_todos} TODOs, "
               f"{mermaid_str}, {len(secret_findings)} secret warnings, "
               f"{len(broken_links)} broken links")
    print(f"{summary} -> {readme_path}")


if __name__ == "__main__":
    sys.exit(main() or 0)
