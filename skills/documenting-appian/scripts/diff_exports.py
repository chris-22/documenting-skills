#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Compare two UUID index JSON files and generate a changelog.

Migrated from appian-diff-docs skill to automation-scripts.

Usage:
  python diff_exports.py <baseline.json> <new.json>

Produces docs/appian-changelog.md
"""
import argparse
import json
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from app_info import get_app_name
from cli_common import make_parser, write_output, verbose, EXIT_PATH_NOT_FOUND

OUT_FILE = os.path.join("docs", "appian-changelog.md")

TYPE_TO_DOCS = {
    "application": ["01-appian-overview.md"],
    "connectedSystem": ["07-appian-integrations.md", "09-appian-deployment.md"],
    "dataStore": ["06-appian-data.md", "09-appian-deployment.md"],
    "dataStoreEntity": ["06-appian-data.md"],
    "datatype": ["06-appian-data.md"],
    "group": ["08-appian-security.md"],
    "processModel": ["04-appian-architecture.md", "process-models/"],
    "recordType": ["06-appian-data.md", "09-appian-deployment.md"],
    "site": ["05-appian-navigation.md", "04-appian-architecture.md"],
    "tempoReport": ["03-appian-inventory.md", "05-appian-navigation.md"],
    "translationSet": ["10-appian-i18n.md"],
    "translationString": ["10-appian-i18n.md"],
    "webApi": ["07-appian-integrations.md", "04-appian-architecture.md"],
}


def main():
    parser = make_parser(
        "Compare two UUID index snapshots and generate a changelog.",
        default_output=OUT_FILE, needs_app_dir=False, needs_index=False,
        extra_args=[
            {"flags": ["baseline"], "help": "Path to baseline UUID index JSON"},
            {"flags": ["new"], "help": "Path to new UUID index JSON"},
        ],
        examples=[
            "python diff_exports.py docs/_uuid-index-baseline.json docs/_uuid-index.json",
            "python diff_exports.py --dry-run baseline.json new.json",
            "python diff_exports.py -o custom-changelog.md baseline.json new.json",
        ],
    )
    args = parser.parse_args()

    if not os.path.exists(args.baseline):
        print(f"Error: baseline file '{args.baseline}' not found.", file=sys.stderr)
        sys.exit(EXIT_PATH_NOT_FOUND)
    if not os.path.exists(args.new):
        print(f"Error: new index file '{args.new}' not found.", file=sys.stderr)
        sys.exit(EXIT_PATH_NOT_FOUND)

    with open(args.baseline, "r", encoding="utf-8") as f:
        baseline = json.load(f)
    with open(args.new, "r", encoding="utf-8") as f:
        new_idx = json.load(f)

    verbose(args, f"Baseline: {len(baseline)} entries, New: {len(new_idx)} entries")
    baseline_uuids = set(baseline.keys())
    new_uuids = set(new_idx.keys())

    added_uuids = new_uuids - baseline_uuids
    deleted_uuids = baseline_uuids - new_uuids
    common_uuids = baseline_uuids & new_uuids

    verbose(args, f"Added: {len(added_uuids)}, Deleted: {len(deleted_uuids)}, Common: {len(common_uuids)}")

    renamed = []
    for uuid in common_uuids:
        old_name = baseline[uuid].get("name", "")
        new_name = new_idx[uuid].get("name", "")
        if old_name != new_name and old_name and new_name:
            renamed.append({
                "uuid": uuid, "old_name": old_name,
                "new_name": new_name, "type": new_idx[uuid].get("type", "unknown"),
            })

    added = [{"uuid": u, **new_idx[u]} for u in added_uuids]
    deleted = [{"uuid": u, **baseline[u]} for u in deleted_uuids]

    affected_docs = set()
    for item in added + deleted + renamed:
        obj_type = item.get("type", "unknown")
        for doc in TYPE_TO_DOCS.get(obj_type, ["03-appian-inventory.md"]):
            affected_docs.add(doc)

    lines = [
        f"# {get_app_name()} — Changelog (auto-generado)",
        "", f"Comparación: `{args.baseline}` → `{args.new}`", "",
        "| Métrica | Valor |", "|---------|-------|",
        f"| Objetos en baseline | {len(baseline)} |",
        f"| Objetos en nueva versión | {len(new_idx)} |",
        f"| Nuevos | {len(added)} |",
        f"| Eliminados | {len(deleted)} |",
        f"| Renombrados | {len(renamed)} |", "",
    ]

    if added:
        lines.append("## Objetos nuevos")
        lines.append("")
        lines.append("| Nombre | Tipo | UUID |")
        lines.append("|--------|------|------|")
        for item in sorted(added, key=lambda x: (x.get("type", ""), x.get("name", ""))):
            lines.append(f"| {item.get('name', '')} | {item.get('type', '')} | `{item['uuid'][:40]}` |")
        lines.append("")

    if deleted:
        lines.append("## Objetos eliminados")
        lines.append("")
        lines.append("| Nombre | Tipo | UUID |")
        lines.append("|--------|------|------|")
        for item in sorted(deleted, key=lambda x: (x.get("type", ""), x.get("name", ""))):
            lines.append(f"| {item.get('name', '')} | {item.get('type', '')} | `{item['uuid'][:40]}` |")
        lines.append("")

    if renamed:
        lines.append("## Objetos renombrados")
        lines.append("")
        lines.append("| Nombre anterior | Nombre nuevo | Tipo |")
        lines.append("|----------------|-------------|------|")
        for item in sorted(renamed, key=lambda x: x.get("type", "")):
            lines.append(f"| {item['old_name']} | {item['new_name']} | {item['type']} |")
        lines.append("")

    if affected_docs:
        lines.append("## Documentos afectados (requieren actualización)")
        lines.append("")
        for doc in sorted(affected_docs):
            lines.append(f"- `docs/{doc}`")
        lines.append("")

    if not added and not deleted and not renamed:
        lines.append("## Sin cambios detectados")
        lines.append("")
        lines.append("Las dos versiones del export son idénticas en cuanto a objetos.")
        lines.append("")

    write_output(args, "\n".join(lines), label=f"Changelog: +{len(added)} -{len(deleted)} ~{len(renamed)}")
    print(f"Changelog: +{len(added)} -{len(deleted)} ~{len(renamed)} -> {args.output}")


if __name__ == "__main__":
    sys.exit(main() or 0)
