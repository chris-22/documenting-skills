#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Appian Process Model → Mermaid (flowchart) generator
Reads Appian processModel XML and outputs Mermaid code approximating BPMN.

Usage:
  python .github/skills/documenting-appian/scripts/pm2mermaid.py <path/to/processModel.xml> [--out docs/process-models/<uuid>.md]

Notes:
- Only reads the export; no writes to application_files/.
- Mermaid shapes use v11.3+ expanded syntax (shape metadata). If your renderer is older, replace with classic shapes.

Module structure:
  xml_utils.py        – XML parsing helpers (strip_ns, find_child, text, pick_fname)
  constants.py        – Shared constants (shapes, classDefs, legend, palette)
  node_classifier.py  – BPMN node classification (detect_shape, sanitize_label)
  parser.py           – Process model XML parser (parse_process, pick_process_name)
  mermaid_builder.py  – Mermaid code generation (build_mermaid)
  pm2mermaid.py       – CLI entry point (this file)
"""
import argparse
import sys
import os

# Allow sibling-module imports when running as a script
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from constants import DEFAULT_OUTPUT_DIR
from parser import parse_process, sanitize_filename
from mermaid_builder import build_mermaid
from mermaid_validator import validate_mermaid_block

# cli_common is now a sibling module in the same scripts/ directory.
from cli_common import EXIT_PATH_NOT_FOUND, EXIT_DATA_ERROR


def write_legend(out_dir, dry_run=False):
    """Copy the legend to the output directory if it doesn't exist.

    Prefers references/legend.md (authoritative, always up-to-date) over
    assets/_legend.md (legacy static copy kept as fallback).
    """
    legend_dst = os.path.join(out_dir, '_legend.md')
    if os.path.exists(legend_dst):
        return
    legend_src = os.path.join(_SCRIPT_DIR, '..', 'references', 'legend.md')
    if not os.path.exists(legend_src):
        legend_src = os.path.join(_SCRIPT_DIR, '..', 'assets', '_legend.md')
    if os.path.exists(legend_src):
        if dry_run:
            print(f"[dry-run] Would copy _legend.md to {out_dir}")
            return
        import shutil
        os.makedirs(out_dir, exist_ok=True)
        shutil.copy2(legend_src, legend_dst)
        print(f"Wrote {legend_dst}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Mermaid flowchart (BPMN) from Appian Process Model XML.",
        epilog="Exit codes:\n"
               "  0  Success\n"
               "  1  Invalid arguments\n"
               "  2  Required path not found\n"
               "  3  Data error during processing\n"
               "\n"
               "Examples:\n"
               "  python pm2mermaid.py application_files/processModel/UUID.xml\n"
               "  python pm2mermaid.py UUID.xml --dir docs/process-models --legend\n"
               "  python pm2mermaid.py UUID.xml --out docs/process-models/MyProcess.md\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("xml_path", nargs="?", help="Path to processModel XML file")
    parser.add_argument("--out", dest="out_md", default=None,
                        help="Exact output .md file path")
    parser.add_argument("--dir", dest="out_dir", default=None,
                        help="Output directory (filename derived from process name)")
    parser.add_argument("--legend", action="store_true",
                        help="Copy shared legend template to output directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be written without creating/modifying files.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed processing info to stderr.")
    parser.add_argument("--no-validate", action="store_true",
                        help="Skip Mermaid syntax validation and auto-fix.")
    args = parser.parse_args()

    # Legend-only mode: --legend --dir <dir> without xml_path
    if args.legend and args.out_dir and not args.xml_path:
        write_legend(args.out_dir, dry_run=args.dry_run)
        return
    if not args.xml_path:
        parser.error("xml_path is required (unless using --legend --dir for legend-only mode)")

    xml_path = args.xml_path
    if not os.path.exists(xml_path):
        print(f"Error: file '{xml_path}' not found.", file=sys.stderr)
        sys.exit(EXIT_PATH_NOT_FOUND)

    out_dir = args.out_dir
    out_md = args.out_md

    if args.legend and out_dir:
        write_legend(out_dir, dry_run=args.dry_run)

    pm_base = os.path.dirname(xml_path)
    if getattr(args, 'verbose', False):
        print(f"Parsing {xml_path}...", file=sys.stderr)
    try:
        uuid, pname, nodes, edges, clicks = parse_process(xml_path)
    except Exception as exc:
        print(f"Error: failed to parse '{xml_path}': {exc}", file=sys.stderr)
        sys.exit(EXIT_DATA_ERROR)

    # Decide output path
    if out_md is None and out_dir is not None:
        if not args.dry_run:
            os.makedirs(out_dir, exist_ok=True)
        fname = sanitize_filename(pname or uuid) + '.md'
        out_md = os.path.join(out_dir, fname)

    if getattr(args, 'verbose', False):
        print(f"  Process: {pname or uuid} ({len(nodes)} nodes, {len(edges)} edges)", file=sys.stderr)
    try:
        mermaid = build_mermaid(uuid, nodes, edges, clicks, out_dir or DEFAULT_OUTPUT_DIR, pm_base)
    except Exception as exc:
        print(f"Error: failed to build Mermaid for '{xml_path}': {exc}", file=sys.stderr)
        sys.exit(EXIT_DATA_ERROR)

    # Validate and auto-fix Mermaid syntax
    if not args.no_validate:
        issues, fixed_mermaid = validate_mermaid_block(mermaid)
        if issues:
            errors = [i for i in issues if i.severity == 'error']
            warnings = [i for i in issues if i.severity == 'warning']
            title_short = (pname or uuid)[:40]
            if errors:
                print(f"  ⚠️  {title_short}: {len(errors)} error(s) auto-corregido(s), {len(warnings)} warning(s)", file=sys.stderr)
                for e in errors:
                    print(f"      🔧 {e}", file=sys.stderr)
            elif warnings:
                print(f"  ℹ️  {title_short}: {len(warnings)} warning(s)", file=sys.stderr)
            mermaid = fixed_mermaid

    if out_md:
        title = pname or uuid
        content = (f"## Process Model {title}\n\n"
                   f"> Ver [leyenda de colores](./_legend.md)\n\n"
                   f"```mermaid\n{mermaid}\n```\n\n"
                   f"## Evidencias\n\n"
                   f"- XML: {xml_path}\n")
        if getattr(args, 'dry_run', False):
            print(f"[dry-run] Would write to {out_md} (Process Model: {title})")
        else:
            out_parent = os.path.dirname(out_md)
            if out_parent:
                os.makedirs(out_parent, exist_ok=True)
            with open(out_md, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Wrote {out_md}")
    else:
        print(mermaid)


if __name__ == '__main__':
    sys.exit(main() or 0)
