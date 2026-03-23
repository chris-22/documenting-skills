#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Utility — List all Process Model names from the Appian export.

Quick-reference script that prints one line per Process Model:
  <filename>|<process_name>

Useful for:
- Verifying PM name extraction before generating diagrams
- Quick inventory of Process Models without running the full UUID index
- Debugging pm2mermaid.py output (comparing expected vs actual names)
"""
import json
import re
import os
import sys
import glob

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from cli_common import make_parser, verbose, EXIT_PATH_NOT_FOUND

DEFAULT_PM_DIR = "processModel"


def extract_pm_name(filepath):
    """Extract Process Model name from XML using regex (namespace-safe).

    Priority: Spanish (lang=es, country="") > any non-empty value.
    Skips dynamic expressions (starting with '=').
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        content = fh.read()

    meta_match = re.search(r"<meta>(.*?)</meta>", content, re.DOTALL)
    if not meta_match:
        return "UNKNOWN"

    name_match = re.search(
        r"<name>\s*<string-map>(.*?)</string-map>",
        meta_match.group(1),
        re.DOTALL,
    )
    if not name_match:
        return "UNKNOWN"

    pairs_text = name_match.group(1)

    # Extract locale + value pairs
    pair_pattern = re.compile(
        r'<pair>\s*<locale[^/]*?lang="([^"]*)"[^/]*?country="([^"]*)"[^/]*/>\s*'
        r"<value>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</value>\s*</pair>",
        re.DOTALL,
    )
    best_name = "UNKNOWN"
    for lang, country, val in pair_pattern.findall(pairs_text):
        val = val.strip()
        if not val or val.startswith("="):
            continue
        if lang == "es" and not country:
            return val  # Best match: generic Spanish
        if best_name == "UNKNOWN":
            best_name = val

    # Fallback: simple value extraction if locale regex didn't match
    if best_name == "UNKNOWN":
        values = re.findall(
            r"<value>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</value>", pairs_text
        )
        for v in values:
            v = v.strip()
            if v and not v.startswith("="):
                best_name = v
                break

    return best_name


def main():
    parser = make_parser(
        "List all Process Model names from the Appian export (quick reference).",
        default_output="-",  # stdout by default
        needs_app_dir=False, needs_index=False,
        extra_args=[
            {"flags": ["--dir"], "default": DEFAULT_PM_DIR,
             "help": f"Path to processModel/ directory (default: {DEFAULT_PM_DIR})"},
            {"flags": ["--tsv"], "action": "store_true",
             "help": "Output in TSV format with header row"},
            {"flags": ["--json"], "action": "store_true",
             "help": "Output in JSON format (array of objects)"},
        ],
        examples=[
            "python list_process_models.py",
            "python list_process_models.py --dir processModel",
            "python list_process_models.py --tsv",
            "python list_process_models.py --tsv --verbose",
            "python list_process_models.py --json",
        ],
    )
    args = parser.parse_args()

    pm_dir = args.dir
    if not os.path.isdir(pm_dir):
        print(f"Error: directory '{pm_dir}' not found. Use --dir to specify the processModel/ path.", file=sys.stderr)
        sys.exit(EXIT_PATH_NOT_FOUND)

    files = sorted(glob.glob(os.path.join(pm_dir, "*.xml")))
    if not files:
        print(f"Error: no XML files found in '{pm_dir}'.", file=sys.stderr)
        sys.exit(EXIT_PATH_NOT_FOUND)

    verbose(args, f"Scanning {len(files)} XML files in {pm_dir}")

    if args.json:
        entries = []
        for f in files:
            name = extract_pm_name(f)
            basename = os.path.basename(f)
            uuid = basename.replace(".xml", "")
            verbose(args, f"  {basename} -> {name}")
            entries.append({"file": basename, "name": name, "uuid": uuid})
        print(json.dumps(entries, ensure_ascii=False, indent=2))
    elif args.tsv:
        print("Filename\tProcess Name\tUUID")
        for f in files:
            name = extract_pm_name(f)
            basename = os.path.basename(f)
            uuid = basename.replace(".xml", "")
            verbose(args, f"  {basename} -> {name}")
            print(f"{basename}\t{name}\t{uuid}")
    else:
        for f in files:
            name = extract_pm_name(f)
            basename = os.path.basename(f)
            verbose(args, f"  {basename} -> {name}")
            print(f"{basename}|{name}")

    print(f"\nTotal: {len(files)} process models", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main() or 0)
