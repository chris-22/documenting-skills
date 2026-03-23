#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Phase C — Generate site navigation map from site XML files.

Parses site/*.xml, extracts pages with their target objects, resolves names
via UUID index, and produces docs/05-appian-navigation.md with table + Mermaid diagram.
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
from xml_helpers import strip_ns, find_child, text

DEFAULT_APP_DIR = "."
DEFAULT_INDEX = os.path.join("docs", "_uuid-index.json")
DEFAULT_OUT = os.path.join("docs", "05-appian-navigation.md")

NS_A = "http://www.appian.com/ae/types/2009"


def resolve_name(uuid, index):
    entry = index.get(uuid, {})
    return entry.get("name", uuid)


def resolve_type(uuid, index):
    entry = index.get(uuid, {})
    return entry.get("type", "unknown")


def extract_site_info(filepath, index):
    """Extract site metadata and pages from a site XML."""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception:
        return None

    site_el = None
    for child in root:
        if strip_ns(child.tag) == "site":
            site_el = child
            break
    if site_el is None:
        return None

    site_uuid = site_el.attrib.get(f"{{{NS_A}}}uuid", "")
    site_name = site_el.attrib.get("name", "")
    site_desc = text(find_child(site_el, "description"))
    url_stub = text(find_child(site_el, "urlStub"))
    display_name = text(find_child(site_el, "displayName")) or site_name
    header_bg = text(find_child(site_el, "headerBackgroundColor"))
    accent = text(find_child(site_el, "accentColor"))
    nav_layout = text(find_child(site_el, "primaryNavLayoutType"))
    button_shape = text(find_child(site_el, "buttonShape"))

    pages = []
    page_num = 0
    for child in list(site_el):
        if strip_ns(child.tag) != "page":
            continue
        page_num += 1
        page_uuid = child.attrib.get(f"{{{NS_A}}}uuid", "")

        # Page name: staticName or nameExpr
        static_name = text(find_child(child, "staticName"))
        name_expr = text(find_child(child, "nameExpr"))
        page_name = static_name if static_name else f"(dynamic: {name_expr[:60]}...)" if len(name_expr) > 60 else f"(dynamic: {name_expr})" if name_expr else f"Page {page_num}"

        page_url = text(find_child(child, "urlStub"))
        icon_id = text(find_child(child, "iconId"))
        page_width = text(find_child(child, "pageWidth"))
        visibility = text(find_child(child, "visibilityExpr"))

        # Target object
        ui_obj = find_child(child, "uiObject")
        target_uuid = ""
        target_type_attr = ""
        if ui_obj is not None:
            target_uuid = ui_obj.attrib.get(f"{{{NS_A}}}uuid", "")
            xsi_type = ""
            for k, v in ui_obj.attrib.items():
                if "type" in k.lower() and "}" in k:
                    xsi_type = v
                    break
            target_type_attr = xsi_type.split(":")[-1] if ":" in xsi_type else xsi_type

        target_name = resolve_name(target_uuid, index) if target_uuid else "TODO(unknown)"
        target_type = resolve_type(target_uuid, index) if target_uuid else target_type_attr

        # Simplify visibility
        vis_summary = "Siempre visible" if "true()" in visibility and "/*" not in visibility.split("true()")[0][-5:] else "Condicional (FSE/expresión)" if visibility else "Sin restricción"

        pages.append({
            "num": page_num,
            "name": page_name,
            "url": page_url,
            "target_uuid": target_uuid,
            "target_name": target_name,
            "target_type": target_type_attr or target_type,
            "icon": icon_id,
            "width": page_width,
            "visibility": vis_summary,
        })

    return {
        "uuid": site_uuid,
        "name": site_name,
        "display_name": display_name,
        "description": site_desc,
        "url_stub": url_stub,
        "header_bg": header_bg,
        "accent": accent,
        "nav_layout": nav_layout,
        "button_shape": button_shape,
        "pages": pages,
        "file": filepath,
    }


def generate_mermaid(site):
    """Generate a Mermaid block-beta diagram for site navigation.

    Uses a grid layout that mirrors the real top-bar navigation of the site.
    Row 1: site header (full-width).
    Row 2: one column per page (page names).
    Row 3: one column per page (target objects).
    """
    num_pages = len(site["pages"])
    if num_pages == 0:
        return ""

    lines = [
        "```mermaid",
        f"block-beta",
        f"    columns {num_pages}",
        "",
    ]

    # Row 1: site header spanning all columns
    safe_display = site["display_name"].replace('"', "'")
    lines.append(f'    SITE["{safe_display}"]:{num_pages}')
    lines.append("")

    # Row 2: page names (one per column)
    for p in site["pages"]:
        pid = f"P{p['num']}"
        safe_name = p["name"].replace('"', "'")
        # Truncate long dynamic names for readability
        if len(safe_name) > 40:
            safe_name = safe_name[:37] + "..."
        lines.append(f'    {pid}["/{p["url"]}\\n{safe_name}"]')
    lines.append("")

    # Row 3: target objects (one per column)
    for p in site["pages"]:
        tgt_id = f"T{p['num']}"
        safe_target = p["target_name"].replace('"', "'")
        ttype = "PM" if "ProcessModel" in p["target_type"] else "IF"
        lines.append(f'    {tgt_id}["{ttype}: {safe_target}"]')

    lines.append("")

    # Style definitions
    lines.append('    classDef siteClass fill:#E8DAEF,stroke:#7D3C98,color:#000')
    lines.append('    classDef pageClass fill:#D5F5E3,stroke:#1E8449,color:#000')
    lines.append('    classDef pmClass fill:#D6EAF8,stroke:#2E86C1,color:#000')
    lines.append('    classDef ifClass fill:#FDEBD0,stroke:#CA6F1E,color:#000')
    lines.append("")

    # Class assignments
    lines.append("    class SITE siteClass")
    page_ids = [f"P{p['num']}" for p in site["pages"]]
    lines.append(f"    class {','.join(page_ids)} pageClass")
    pm_ids = [f"T{p['num']}" for p in site["pages"] if "ProcessModel" in p["target_type"]]
    if_ids = [f"T{p['num']}" for p in site["pages"] if "ProcessModel" not in p["target_type"]]
    if pm_ids:
        lines.append(f"    class {','.join(pm_ids)} pmClass")
    if if_ids:
        lines.append(f"    class {','.join(if_ids)} ifClass")

    lines.append("```")
    return "\n".join(lines)


def main():
    parser = make_parser(
        "Generate site navigation map from Appian site XML files.",
        default_output=DEFAULT_OUT, needs_app_dir=True, needs_index=True,
        examples=[
            "python generate_navigation.py",
            "python generate_navigation.py --output custom-nav.md",
            "python generate_navigation.py --dry-run",
        ],
    )
    args = parser.parse_args()
    validate_args(args, needs_app_dir=True, needs_index=True)

    with open(args.index, "r", encoding="utf-8") as f:
        index = json.load(f)

    site_dir = os.path.join(args.app_dir, "site")
    site_files = sorted(glob.glob(os.path.join(site_dir, "*.xml")))
    verbose(args, f"Found {len(site_files)} site files in {site_dir}")

    if not site_files:
        print("No site files found.")
        return

    app_name = get_app_name()
    lines = [f"# {app_name} — Mapa de navegación del Site (auto-generado)", ""]

    site_count = 0
    for sf in site_files:
        site = extract_site_info(sf, index)
        if site is None:
            continue
        site_count += 1
        verbose(args, f"  Site '{site['display_name']}': {len(site['pages'])} pages")

        lines.append(f"## Site: {site['display_name']}")
        lines.append("")
        lines.append("| Propiedad | Valor |")
        lines.append("|-----------|-------|")
        lines.append(f"| **UUID** | `{site['uuid']}` |")
        lines.append(f"| **URL stub** | `/{site['url_stub']}` |")
        lines.append(f"| **Descripción** | {site['description']} |")
        lines.append(f"| **Layout** | {site['nav_layout']} |")
        lines.append(f"| **Color cabecera** | `{site['header_bg']}` |")
        lines.append(f"| **Color acento** | `{site['accent']}` |")
        lines.append(f"| **Forma botones** | {site['button_shape']} |")
        lines.append("")

        # Pages table
        lines.append("### Páginas")
        lines.append("")
        lines.append("| # | Nombre | URL Stub | Tipo objeto | Objeto destino | Icono | Visibilidad |")
        lines.append("|---|--------|----------|-------------|---------------|-------|-------------|")
        for p in site["pages"]:
            lines.append(
                f"| {p['num']} | {p['name']} | `/{p['url']}` | {p['target_type']} | {p['target_name']} | `{p['icon']}` | {p['visibility']} |"
            )
        lines.append("")

        # Mermaid diagram
        lines.append("### Diagrama de navegación")
        lines.append("")
        lines.append(generate_mermaid(site))
        lines.append("")

    lines.append("## Evidencias")
    lines.append("")
    lines.append(f"- `{site_dir}/` ({len(site_files)} archivos)")
    lines.append(f"- `{args.index}`")
    lines.append("")

    write_output(args, "\n".join(lines), label=f"Navigation: {site_count} sites")
    print(f"Navigation: {site_count} sites -> {args.output}")


if __name__ == "__main__":
    sys.exit(main() or 0)
