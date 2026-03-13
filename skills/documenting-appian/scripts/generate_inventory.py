#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Phase B — Generate complete object inventory + complexity metrics as Markdown.

Reads docs/_uuid-index.json and produces docs/03-appian-inventory.md with
objects grouped by type, including complexity metrics for Process Models.

v3: Merges complexity_metrics.py functionality. Includes Description column.
"""
import json
import os
import sys
import glob
import xml.etree.ElementTree as ET

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from app_info import get_app_name
from cli_common import make_parser, validate_args, write_output, verbose
from xml_helpers import strip_ns

DEFAULT_OUT = os.path.join("docs", "03-appian-inventory.md")


def count_elements(filepath, tag_name):
    """Count occurrences of a tag (namespace-agnostic) in an XML file."""
    count = 0
    try:
        tree = ET.parse(filepath)
        for elem in tree.iter():
            if strip_ns(elem.tag) == tag_name:
                count += 1
    except Exception:
        pass
    return count


def count_history(filepath):
    return count_elements(filepath, "historyInfo")


def get_pm_complexity(index, app_dir):
    """Compute complexity metrics for Process Models."""
    pm_items = [info for info in index.values() if info.get("type") == "processModel"]
    metrics = []
    for item in pm_items:
        fpath = item.get("file", "")
        if not os.path.exists(fpath):
            fpath = os.path.join(app_dir, os.path.basename(fpath)) if not os.path.sep in fpath else fpath
        if not os.path.exists(fpath):
            continue
        nodes = count_elements(fpath, "node")
        connections = count_elements(fpath, "connection")
        pvs = count_elements(fpath, "pv")
        history = count_history(fpath)
        metrics.append({
            "name": item.get("name", ""), "nodes": nodes,
            "connections": connections, "pvs": pvs, "history": history,
        })
    return metrics


def main():
    parser = make_parser(
        "Generate complete object inventory + complexity metrics as Markdown.",
        default_output=DEFAULT_OUT, needs_app_dir=True, needs_index=True,
        examples=[
            "python generate_inventory.py",
            "python generate_inventory.py --output custom-inventory.md",
            "python generate_inventory.py --dry-run",
        ],
    )
    args = parser.parse_args()
    validate_args(args, needs_app_dir=True, needs_index=True)

    with open(args.index, "r", encoding="utf-8") as f:
        index = json.load(f)
    verbose(args, f"Loaded index: {len(index)} entries from {args.index}")

    # Group by type
    by_type = {}
    for uuid, info in index.items():
        t = info.get("type", "unknown")
        by_type.setdefault(t, []).append(info)

    # Sort types
    type_order = [
        "application", "connectedSystem", "dataStore", "dataStoreEntity",
        "datatype", "group", "processModel", "processModelFolder",
        "recordType", "site", "tempoReport", "translationSet",
        "translationString", "webApi",
    ]
    sorted_types = [t for t in type_order if t in by_type]
    sorted_types += [t for t in sorted(by_type.keys()) if t not in sorted_types]

    app_name = get_app_name()
    lines = [f"# {app_name} — Inventario completo de objetos (auto-generado)", ""]
    total = 0

    # Summary table
    lines.append("## Resumen")
    lines.append("")
    lines.append("| Tipo | Cantidad |")
    lines.append("|------|----------|")
    for t in sorted_types:
        count = len(by_type[t])
        total += count
        lines.append(f"| {t} | {count} |")
    lines.append(f"| **Total** | **{total}** |")
    lines.append("")

    # Pie chart of object distribution
    if len(sorted_types) > 1:
        lines.append("### Distribución por tipo")
        lines.append("")
        lines.append("```mermaid")
        lines.append("pie showData")
        lines.append(f'    title Objetos por tipo ({total} total)')
        for t in sorted_types:
            count = len(by_type[t])
            lines.append(f'    "{t}" : {count}')
        lines.append("```")
        lines.append("")

    # Detail tables per type
    for t in sorted_types:
        items = by_type[t]
        lines.append(f"## {t} ({len(items)})")
        lines.append("")
        lines.append("| Nombre | UUID | Descripci\u00f3n | Archivo |")
        lines.append("|--------|------|-------------|---------|")
        for item in sorted(items, key=lambda x: x.get("name", "")):
            name = item.get("name", "")
            uuid = item.get("uuid", "")
            fpath = item.get("file", "")
            desc = item.get("description", "")
            # Truncate UUID for readability
            uuid_short = uuid[:40] + "..." if len(uuid) > 43 else uuid
            # Truncate description for table readability
            desc_short = desc[:80] + "..." if len(desc) > 83 else desc
            # Escape pipe characters in description
            desc_short = desc_short.replace("|", "\\|")
            lines.append(f"| {name} | `{uuid_short}` | {desc_short} | `{fpath}` |")
        lines.append("")

    verbose(args, f"Grouped into {len(sorted_types)} types, {total} total objects")

    # Complexity metrics section
    pm_metrics = get_pm_complexity(index, args.app_dir)
    if pm_metrics:
        pm_nodes = [p["nodes"] for p in pm_metrics if p["nodes"] > 0]
        pm_avg = sum(pm_nodes) / len(pm_nodes) if pm_nodes else 0
        pm_max = max(pm_nodes) if pm_nodes else 0

        lines.append("## M\u00e9tricas de complejidad")
        lines.append("")
        lines.append("| M\u00e9trica | Valor |")
        lines.append("|---------|-------|")
        lines.append(f"| Process Models | {len(pm_metrics)} (avg nodos: {pm_avg:.1f}, max: {pm_max}) |")
        lines.append(f"| Total objetos indexados | {total} |")
        lines.append("")

        complex_pms = sorted([p for p in pm_metrics if p["nodes"] > 20], key=lambda x: x["nodes"], reverse=True)
        if complex_pms:
            lines.append("### Process Models complejos (> 20 nodos)")
            lines.append("")
            lines.append("| Process Model | Nodos | Conexiones | Variables | Historial |")
            lines.append("|--------------|-------|-----------|-----------|-----------|")
            for p in complex_pms:
                lines.append(f"| {p['name']} | {p['nodes']} | {p['connections']} | {p['pvs']} | {p['history']} |")
            lines.append("")

        heavy_pms = sorted([p for p in pm_metrics if p["pvs"] > 5], key=lambda x: x["pvs"], reverse=True)
        if heavy_pms:
            lines.append("### Process Models con muchas variables (> 5 PVs)")
            lines.append("")
            lines.append("| Process Model | Variables | Nodos |")
            lines.append("|--------------|-----------|-------|")
            for p in heavy_pms:
                lines.append(f"| {p['name']} | {p['pvs']} | {p['nodes']} |")
            lines.append("")

        most_changed = sorted(pm_metrics, key=lambda x: x["history"], reverse=True)[:10]
        if most_changed:
            lines.append("### Objetos m\u00e1s modificados (top 10)")
            lines.append("")
            lines.append("| Objeto | Versiones |")
            lines.append("|--------|-----------|")
            for p in most_changed:
                lines.append(f"| {p['name']} | {p['history']} |")
            lines.append("")

    lines.append("## Evidencias")
    lines.append("")
    lines.append(f"- Generado automáticamente desde `{args.index}` ({total} entradas)")
    lines.append("")

    write_output(args, "\n".join(lines), label=f"Inventory: {total} objects")

    print(f"Inventory: {total} objects -> {args.output}")


if __name__ == "__main__":
    sys.exit(main() or 0)
