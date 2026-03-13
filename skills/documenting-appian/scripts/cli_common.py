#!/usr/bin/env python3
"""Shared CLI helpers for automation scripts. Provides argparse setup and validation.

Exit codes:
    0 — Success
    1 — Invalid arguments (argparse handles this automatically)
    2 — Required path not found (app-dir, index file)
    3 — Data error during processing
"""
import argparse
import os
import sys

EXIT_OK = 0
EXIT_BAD_ARGS = 1      # argparse default for invalid arguments
EXIT_PATH_NOT_FOUND = 2
EXIT_DATA_ERROR = 3

EXIT_CODE_DOC = (
    "Exit codes:\n"
    "  0  Success\n"
    "  1  Invalid arguments\n"
    "  2  Required path not found (app-dir, index file)\n"
    "  3  Data error during processing"
)


SKILL_VERSION = "2.0.0"


def make_parser(description, default_output, needs_app_dir=True, needs_index=False, extra_args=None, examples=None):
    """Create a standardized argparse.ArgumentParser for automation scripts.

    Args:
        description: Script description for --help.
        default_output: Default output file path.
        needs_app_dir: If True, add --app-dir argument.
        needs_index: If True, add --index argument for _uuid-index.json.
        extra_args: List of dicts with extra add_argument kwargs.
        examples: Optional list of example command strings for --help epilog.

    Returns:
        argparse.ArgumentParser (not yet parsed).
    """
    epilog_parts = [EXIT_CODE_DOC]
    if examples:
        epilog_parts.append("Examples:\n" + "\n".join(f"  {ex}" for ex in examples))
    epilog = "\n\n".join(epilog_parts)
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s (documenting-appian v{SKILL_VERSION})",
    )
    if needs_app_dir:
        parser.add_argument(
            "--app-dir", default="application_files",
            help="Path to application_files/ directory (default: application_files)",
        )
    if needs_index:
        parser.add_argument(
            "--index", default=os.path.join("docs", "_uuid-index.json"),
            help="Path to UUID index JSON (default: docs/_uuid-index.json)",
        )
    parser.add_argument(
        "--output", "-o", default=default_output,
        help=f"Output file path (default: {default_output})",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview what would be written without creating/modifying files.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show detailed processing info to stderr (default: summary only).",
    )
    if extra_args:
        for ea in extra_args:
            ea = dict(ea)
            flags = ea.pop("flags")
            parser.add_argument(*flags, **ea)
    return parser


def verbose(args, msg):
    """Print a message to stderr only when --verbose is active."""
    if getattr(args, "verbose", False):
        print(msg, file=sys.stderr)


def validate_args(args, needs_app_dir=True, needs_index=False):
    """Validate parsed args. Exits with EXIT_PATH_NOT_FOUND on missing paths."""
    if needs_app_dir and not os.path.isdir(args.app_dir):
        print(f"Error: directory '{args.app_dir}' not found. Run from the repo root or use --app-dir.", file=sys.stderr)
        sys.exit(EXIT_PATH_NOT_FOUND)
    if needs_index and not os.path.exists(args.index):
        print(f"Error: '{args.index}' not found. Run build_uuid_index.py first.", file=sys.stderr)
        sys.exit(EXIT_PATH_NOT_FOUND)
    if not getattr(args, "dry_run", False):
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)


def write_output(args, content, label=None):
    """Write content to args.output, respecting --dry-run.

    Args:
        args: Parsed argparse namespace (must have .output and .dry_run).
        content: String content to write.
        label: Optional label for the dry-run summary (e.g. "UUID index: 1197 entries").

    Returns:
        True if written, False if dry-run.
    """
    if getattr(args, "dry_run", False):
        summary = label or f"{len(content)} characters"
        print(f"[dry-run] Would write to {args.output} ({summary})")
        return False
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    return True
