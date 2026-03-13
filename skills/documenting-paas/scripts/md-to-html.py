#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["markdown"]
# ///
"""
Markdown to HTML converter with Mermaid diagram support.

Converts a Markdown file to a standalone HTML file with:
- GitHub-like CSS styling
- Mermaid JS CDN for automatic diagram rendering
- Table of contents with internal anchor links
- Responsive layout

Dependencies:
    pip install markdown

Usage:
    python md-to-html.py input.md output.html [--title "Project Name"]
    python md-to-html.py input.md output.html --title "My Project - Technical Documentation"
    python md-to-html.py input.md output.html --offline  # Embed Mermaid JS inline (no CDN)
    python md-to-html.py input.md output.html --dry-run  # Preview without writing
    python md-to-html.py input.md output.html --json     # Structured JSON output
    python md-to-html.py input.md output.html --verbose  # Extra debug information
    python md-to-html.py input.md output.html --quiet    # Suppress non-error output

Exit codes:
    0 - Success
    1 - Input file not found or invalid arguments
    2 - Missing required dependency (pip install markdown)
    3 - Conversion or write error
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

EXIT_OK = 0
EXIT_INPUT_ERROR = 1
EXIT_DEPENDENCY_ERROR = 2
EXIT_CONVERSION_ERROR = 3

MERMAID_VERSION = "10.9.1"
MERMAID_CDN_URL = f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.min.js"

try:
    import markdown
    from markdown.extensions.toc import TocExtension
except ImportError:
    print("Error: 'markdown' package is required. Install it with: pip install markdown")
    sys.exit(EXIT_DEPENDENCY_ERROR)


def load_html_template(skill_dir: str) -> str:
    """Load the HTML template from the assets directory."""
    template_path = os.path.join(skill_dir, "assets", "html-template.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return get_default_template()


def get_default_template() -> str:
    """Return the default HTML template if the asset file is not found."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{TITLE}}</title>
  {{MERMAID_SCRIPT}}
  <!-- Mermaid CDN: {MERMAID_CDN_URL} -->
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.6; color: #1f2328; max-width: 980px; margin: 0 auto; padding: 20px 40px; }
    h1, h2 { border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }
    h1 { font-size: 2em; } h2 { font-size: 1.5em; } h3 { font-size: 1.25em; }
    table { border-collapse: collapse; width: 100%; margin: 16px 0; }
    th, td { border: 1px solid #d0d7de; padding: 6px 13px; text-align: left; }
    th { background: #f6f8fa; font-weight: 600; }
    tr:nth-child(even) { background: #f6f8fa; }
    code { background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 6px; font-size: 85%; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }
    pre { background: #f6f8fa; padding: 16px; overflow-x: auto; border-radius: 6px; line-height: 1.45; }
    pre code { background: transparent; padding: 0; font-size: 85%; }
    pre.mermaid { background: transparent; border: none; text-align: center; }
    blockquote { border-left: 4px solid #d0d7de; color: #656d76; margin: 16px 0; padding: 0 1em; }
    hr { border: none; border-top: 1px solid #d0d7de; margin: 24px 0; }
    a { color: #0969da; text-decoration: none; } a:hover { text-decoration: underline; }
    .header-meta { color: #656d76; font-size: 0.9em; margin-bottom: 24px; }
    @media print { body { max-width: 100%; } pre.mermaid svg { max-width: 100%; } }
  </style>
</head>
<body>
  <div class="markdown-body">
    <div class="header-meta">
      <strong>{{PROJECT_NAME}}</strong> | Generated: {{DATE}}
    </div>
    {{CONTENT}}
  </div>
</body>
</html>"""


def convert_mermaid_blocks(html_content: str) -> str:
    """
    Convert Mermaid code blocks to <pre class="mermaid"> for Mermaid JS rendering.

    The markdown library converts ```mermaid blocks to:
      <pre><code class="language-mermaid">...</code></pre>
    
    Mermaid JS expects:
      <pre class="mermaid">...</pre>
    """
    # Pattern 1: <pre><code class="language-mermaid">...</code></pre>
    pattern1 = re.compile(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        re.DOTALL
    )
    html_content = pattern1.sub(r'<pre class="mermaid">\1</pre>', html_content)

    # Pattern 2: <pre><code class="mermaid">...</code></pre> (some markdown libs)
    pattern2 = re.compile(
        r'<pre><code class="mermaid">(.*?)</code></pre>',
        re.DOTALL
    )
    html_content = pattern2.sub(r'<pre class="mermaid">\1</pre>', html_content)

    return html_content


def extract_title_from_markdown(md_content: str) -> str:
    """Extract the first H1 heading from the markdown content as the title."""
    match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Technical Documentation"


def extract_metadata(md_content: str) -> dict:
    """Extract metadata (Project, Version, etc.) from the markdown header."""
    metadata = {}
    patterns = {
        "project": r'\*\*Projec?t[oe]?\*\*:\s*`([^`]+)`',
        "version": r'\*\*Versi[oó]n\*\*:\s*(.+)',
        "stack": r'\*\*Stack\*\*:\s*(.+)',
        "date": r'\*\*(?:Fecha de generaci[oó]n|Generated)\*\*:\s*(.+)',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, md_content)
        if match:
            metadata[key] = match.group(1).strip()
    return metadata


def convert_md_to_html(input_path: str, output_path: str, title: str = None,
                       offline: bool = False, dry_run: bool = False,
                       json_output: bool = False, verbose: bool = False,
                       quiet: bool = False):
    """
    Convert a Markdown file to a standalone HTML file with Mermaid support.

    Args:
        input_path: Path to the input .md file
        output_path: Path to the output .html file
        title: Optional title for the HTML document
        offline: If True, embed Mermaid JS inline instead of using CDN
        dry_run: If True, preview conversion without writing the output file
        json_output: If True, emit structured JSON instead of plain text
        verbose: If True, emit extra debug information
        quiet: If True, suppress all non-error output
    """
    # Read input markdown
    with open(input_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Extract title and metadata
    if not title:
        title = extract_title_from_markdown(md_content)
    metadata = extract_metadata(md_content)

    if verbose:
        print(f"[DEBUG] Input: {input_path} ({len(md_content)} chars)")
        print(f"[DEBUG] Extracted title: {title}")
        print(f"[DEBUG] Metadata: {metadata}")

    # Convert markdown to HTML
    extensions = [
        "tables",
        "fenced_code",
        TocExtension(permalink=False, toc_depth=3),
        "meta",
        "sane_lists",
    ]
    md = markdown.Markdown(extensions=extensions)
    html_body = md.convert(md_content)

    # Convert mermaid code blocks to <pre class="mermaid">
    html_body = convert_mermaid_blocks(html_body)

    # Load template
    skill_dir = str(Path(__file__).resolve().parent.parent)
    template = load_html_template(skill_dir)
    if verbose:
        template_path = os.path.join(skill_dir, "assets", "html-template.html")
        source = "asset" if os.path.exists(template_path) else "default"
        print(f"[DEBUG] Template source: {source}")

    # Mermaid script (CDN or inline)
    mermaid_init = "<script>mermaid.initialize({startOnLoad: true, theme: 'default', securityLevel: 'loose'});</script>"
    if offline:
        mermaid_js_path = os.path.join(os.path.dirname(os.path.abspath(input_path)), "mermaid.min.js")
        if os.path.exists(mermaid_js_path):
            with open(mermaid_js_path, "r", encoding="utf-8") as mf:
                mermaid_js_content = mf.read()
            mermaid_script = f"<script>{mermaid_js_content}</script>\n  {mermaid_init}"
        else:
            mermaid_script = (
                '<script>\n'
                '  console.error("Mermaid JS not found. Diagrams will not render.");\n'
                f'  console.error("Download mermaid.min.js from {MERMAID_CDN_URL}");\n'
                '  console.error("Place it next to the input .md file and re-run with --offline");\n'
                '</script>'
            )
            if not quiet:
                print(f"Warning: mermaid.min.js not found at {mermaid_js_path}")
                print(f"  Download it from: {MERMAID_CDN_URL}")
                print("  Place it next to the input .md file and re-run with --offline")
    else:
        mermaid_script = (
            f'<script src="{MERMAID_CDN_URL}"></script>\n'
            f'  {mermaid_init}'
        )

    # Replace template placeholders
    project_name = metadata.get("project", title)
    version = metadata.get("version", "")
    date = metadata.get("date", datetime.now().strftime("%Y-%m-%d"))

    html_output = template.replace("{{TITLE}}", title)
    html_output = html_output.replace("{{PROJECT_NAME}}", project_name)
    html_output = html_output.replace("{{VERSION}}", version)
    html_output = html_output.replace("{{DATE}}", date)
    html_output = html_output.replace("{{CONTENT}}", html_body)
    html_output = html_output.replace("{{MERMAID_SCRIPT}}", mermaid_script)

    # If using the asset template (which already has mermaid script), don't duplicate
    # The asset template has hardcoded CDN links, so we only inject for default template

    # Result metadata
    result = {
        "status": "ok",
        "output": os.path.abspath(output_path),
        "title": title,
        "project": project_name,
        "mermaid_mode": "offline" if offline else "cdn",
        "dry_run": dry_run,
    }

    if dry_run:
        result["status"] = "dry_run"
        if json_output:
            print(json.dumps(result, indent=2))
        elif not quiet:
            print(f"[DRY RUN] Would generate: {output_path}")
            print(f"  Title: {title}")
            print(f"  Project: {project_name}")
            print(f"  Mermaid: {'Inline (offline)' if offline else 'CDN'}")
        return

    # Write output
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_output)
    except OSError as e:
        if json_output:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            print(f"Error: Failed to write output file: {e}")
        sys.exit(EXIT_CONVERSION_ERROR)

    if json_output:
        print(json.dumps(result, indent=2))
    elif not quiet:
        print(f"HTML generated successfully: {output_path}")
        print(f"  Title: {title}")
        print(f"  Project: {project_name}")
        print(f"  Mermaid: {'Inline (offline)' if offline else 'CDN'}")
        if verbose:
            file_size = os.path.getsize(output_path)
            print(f"  File size: {file_size:,} bytes")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to standalone HTML with Mermaid diagram support.",
        epilog="""Examples:
  python md-to-html.py input.md output.html
  python md-to-html.py input.md output.html --title "My Project - Docs"
  python md-to-html.py input.md output.html --offline
  python md-to-html.py input.md output.html --dry-run
  python md-to-html.py input.md output.html --json
  python md-to-html.py input.md output.html --verbose
  python md-to-html.py input.md output.html --quiet

Exit codes:
  0  Success
  1  Input file not found or invalid arguments
  2  Missing required dependency (pip install markdown)
  3  Conversion or write error
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="Input Markdown file path")
    parser.add_argument("output", help="Output HTML file path")
    parser.add_argument("--title", help="Document title (default: extracted from first H1)")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Embed Mermaid JS inline for offline use (no CDN dependency)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the conversion without writing the output file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output instead of plain text",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Emit extra debug information during conversion",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress all non-error output",
    )

    args = parser.parse_args()

    if args.verbose and args.quiet:
        print("Error: --verbose and --quiet are mutually exclusive")
        sys.exit(EXIT_INPUT_ERROR)

    if not os.path.exists(args.input):
        if args.json:
            print(json.dumps({"status": "error", "error": f"Input file not found: {args.input}"}, indent=2))
        else:
            print(f"Error: Input file not found: {args.input}")
        sys.exit(EXIT_INPUT_ERROR)

    convert_md_to_html(args.input, args.output, args.title, args.offline,
                       args.dry_run, args.json, args.verbose, args.quiet)


if __name__ == "__main__":
    main()
