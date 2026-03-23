#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Phase D — Extract Connected Systems and Outbound Integrations.

Parses connectedSystem/*.xml and content/*.xml (outboundIntegration),
resolves references via UUID index, and produces docs/07-appian-integrations.md
with tables and a Mermaid dependency diagram.
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
DEFAULT_OUT = os.path.join("docs", "07-appian-integrations.md")

NS_A = "http://www.appian.com/ae/types/2009"


def resolve(uuid, index):
    entry = index.get(uuid, {})
    return entry.get("name", uuid)


def extract_connected_system(filepath):
    """Extract Connected System details from XML."""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception:
        return None

    cs_el = None
    for child in root:
        if strip_ns(child.tag) == "connectedSystem":
            cs_el = child
            break
    if cs_el is None:
        return None

    name = text(find_child(cs_el, "name"))
    uuid = text(find_child(cs_el, "uuid"))
    desc = text(find_child(cs_el, "description"))
    int_type = text(find_child(cs_el, "integrationType"))

    # Extract shared config (baseUrl, authType)
    base_url = ""
    auth_type = ""
    config = find_child(cs_el, "sharedConfigParameters")
    if config is not None:
        for child in list(config):
            tag = strip_ns(child.tag)
            # Dictionary children
            for c in list(child) if hasattr(child, '__iter__') else []:
                ctag = strip_ns(c.tag)
                if ctag == "baseUrl":
                    base_url = text(c)
                elif ctag == "authType":
                    auth_type = text(c)
            # Direct children of config
            if tag == "baseUrl":
                base_url = text(child)
            elif tag == "authType":
                auth_type = text(child)
        # Try deeper: config may be a Dictionary element
        for child in config.iter():
            ctag = strip_ns(child.tag)
            if ctag == "baseUrl" and not base_url:
                base_url = text(child)
            elif ctag == "authType" and not auth_type:
                auth_type = text(child)

    return {
        "name": name, "uuid": uuid, "description": desc,
        "integrationType": int_type, "baseUrl": base_url,
        "authType": auth_type, "file": filepath,
    }


def extract_outbound_integrations(index):
    """Find outbound integrations from UUID index (content/outboundIntegration)."""
    integrations = []
    for uuid, info in index.items():
        if info.get("type") == "content/outboundIntegration":
            integrations.append({
                "name": info.get("name", ""),
                "uuid": uuid,
                "file": info.get("file", ""),
                "description": info.get("description", ""),
            })
    return sorted(integrations, key=lambda x: x["name"])


def _safe_id(name):
    """Sanitize a name for use as a Mermaid node/participant ID."""
    return name.replace(" ", "_").replace("-", "_").replace(".", "_")


def generate_mermaid(connected_systems, integrations):
    """Generate Mermaid dependency diagram (flowchart LR, Palette A)."""
    lines = [
        "```mermaid",
        "flowchart LR",
        "    classDef csClass fill:#FDEBD0,stroke:#CA6F1E,color:#000",
        "    classDef intClass fill:#D6EAF8,stroke:#2E86C1,color:#000",
        "    classDef extClass fill:#F2F3F4,stroke:#566573,color:#000",
        "",
    ]

    for cs in connected_systems:
        safe_name = cs["name"].replace('"', "'")
        cs_id = _safe_id(cs["name"])
        auth = cs["authType"] or "unknown"
        lines.append(f'    {cs_id}["CS: {safe_name}<br/>{auth}"]:::csClass')

    for intg in integrations:
        safe_name = intg["name"].replace('"', "'")
        int_id = _safe_id(intg["name"])
        lines.append(f'    {int_id}["INT: {safe_name}"]:::intClass')

    if connected_systems:
        ext_name = "External Systems"
        if connected_systems[0].get("baseUrl"):
            domain = connected_systems[0]["baseUrl"].split("/")[2] if "/" in connected_systems[0]["baseUrl"] else connected_systems[0]["baseUrl"]
            ext_name = domain
        lines.append(f'    EXT["{ext_name}"]:::extClass')

    lines.append("")

    for intg in integrations:
        int_id = _safe_id(intg["name"])
        if connected_systems:
            cs_id = _safe_id(connected_systems[0]["name"])
            lines.append(f"    {int_id} --> {cs_id}")

    for cs in connected_systems:
        cs_id = _safe_id(cs["name"])
        lines.append(f"    {cs_id} --> EXT")

    lines.append("```")
    return "\n".join(lines)


def generate_sequence_diagrams(connected_systems, integrations):
    """Generate one Mermaid sequenceDiagram per Connected System.

    Shows temporal request/response flow: App -> Integration -> CS -> External.
    Fully generic: derived from CS XML metadata + UUID index, no app-specific knowledge.
    Returns a list of (cs_name, mermaid_str) tuples.
    """
    if not connected_systems:
        return []

    results = []
    for cs in connected_systems:
        cs_name = cs["name"]
        base_url = cs.get("baseUrl", "")
        auth = cs.get("authType", "unknown")
        domain = base_url.split("/")[2] if base_url and len(base_url.split("/")) > 2 else "External API"

        # Find integrations that belong to this CS (heuristic: name prefix match)
        cs_prefix = cs_name.replace("CS_", "").replace("_CS_", "")
        cs_intgs = [i for i in integrations]  # all integrations link to some CS

        if not cs_intgs:
            continue

        lines = [
            "```mermaid",
            "sequenceDiagram",
            f"    participant App as Appian App",
            f"    participant CS as {cs_name}",
            f"    participant Ext as {domain}",
            "",
        ]

        if auth:
            lines.append(f"    Note over CS,Ext: Auth: {auth}")
            lines.append("")

        for intg in cs_intgs:
            safe_name = intg["name"].replace('"', "'")
            lines.append(f"    App->>+CS: {safe_name}")
            lines.append(f"    CS->>+Ext: HTTP request")
            lines.append(f"    Ext-->>-CS: response")
            lines.append(f"    CS-->>-App: result")
            lines.append("")

        lines.append("```")
        results.append((cs_name, "\n".join(lines)))

    return results


def generate_c4_context(connected_systems, site_names=None):
    """Generate a C4Context diagram showing the system boundaries.

    Fully generic: derives Person (users), System (app), System_Ext (per CS).
    site_names: optional list of site display names for user-facing boundaries.
    """
    if not connected_systems:
        return ""

    lines = [
        "```mermaid",
        "C4Context",
        '    title System Context Diagram',
        "",
        '    Person(user, "Appian User", "Interacts via Site")',
        '    System(app, "Appian Application", "Process Models, Interfaces, Rules")',
        "",
    ]

    for i, cs in enumerate(connected_systems):
        cs_id = f"ext{i}"
        base_url = cs.get("baseUrl", "")
        domain = base_url.split("/")[2] if base_url and len(base_url.split("/")) > 2 else cs["name"]
        auth = cs.get("authType", "")
        desc = f"{cs['integrationType'] or 'HTTP'} / {auth}" if auth else cs["integrationType"] or "HTTP"
        safe_name = cs["name"].replace('"', "'")
        lines.append(f'    System_Ext({cs_id}, "{domain}", "{safe_name} — {desc}")')

    lines.append("")
    lines.append('    Rel(user, app, "Uses")')
    for i, cs in enumerate(connected_systems):
        cs_id = f"ext{i}"
        lines.append(f'    Rel(app, {cs_id}, "Integrates via {cs["name"]}")')

    lines.append("```")
    return "\n".join(lines)


def main():
    parser = make_parser(
        "Extract Connected Systems and Outbound Integrations.",
        default_output=DEFAULT_OUT, needs_app_dir=True, needs_index=True,
        examples=[
            "python extract_integrations.py",
            "python extract_integrations.py --output custom-integrations.md",
            "python extract_integrations.py --dry-run",
        ],
    )
    args = parser.parse_args()
    validate_args(args, needs_app_dir=True, needs_index=True)

    with open(args.index, "r", encoding="utf-8") as f:
        index = json.load(f)

    # Extract Connected Systems
    cs_dir = os.path.join(args.app_dir, "connectedSystem")
    cs_files = sorted(glob.glob(os.path.join(cs_dir, "*.xml")))
    verbose(args, f"Found {len(cs_files)} Connected System files in {cs_dir}")
    connected_systems = []
    for csf in cs_files:
        cs = extract_connected_system(csf)
        if cs:
            connected_systems.append(cs)

    verbose(args, f"Parsed {len(connected_systems)} Connected Systems")

    # Extract Outbound Integrations from index
    integrations = extract_outbound_integrations(index)
    verbose(args, f"Found {len(integrations)} Outbound Integrations in index")

    app_name = get_app_name()
    lines = [f"# {app_name} — Integraciones y configuración (auto-generado)", ""]

    # Connected Systems table
    lines.append("## Connected Systems")
    lines.append("")
    if connected_systems:
        for cs in connected_systems:
            lines.append(f"### {cs['name']}")
            lines.append("")
            lines.append("| Propiedad | Valor |")
            lines.append("|-----------|-------|")
            lines.append(f"| **UUID** | `{cs['uuid']}` |")
            lines.append(f"| **Tipo** | {cs['integrationType']} |")
            lines.append(f"| **Base URL** | `{cs['baseUrl']}` |")
            lines.append(f"| **Autenticación** | {cs['authType']} |")
            if cs["description"]:
                lines.append(f"| **Descripción** | {cs['description']} |")
            lines.append("")
            lines.append("> ⚠️ **Import Customization requerida**: `baseUrl`, `username` y `password` son específicos de entorno.")
            lines.append("")
    else:
        lines.append("*(No se encontraron Connected Systems en el export)*")
        lines.append("")

    # Outbound Integrations table
    lines.append("## Outbound Integrations")
    lines.append("")
    if integrations:
        lines.append(f"Total: **{len(integrations)}**")
        lines.append("")
        lines.append("| Nombre | UUID | Descripción |")
        lines.append("|--------|------|-------------|")
        for intg in integrations:
            uuid_short = intg["uuid"][:45] + "..." if len(intg["uuid"]) > 48 else intg["uuid"]
            desc = intg["description"][:80] + "..." if len(intg["description"]) > 83 else intg["description"]
            lines.append(f"| {intg['name']} | `{uuid_short}` | {desc} |")
        lines.append("")
    else:
        lines.append("*(No se encontraron Outbound Integrations en el export)*")
        lines.append("")

    # Mermaid dependency diagram (flowchart)
    if connected_systems or integrations:
        lines.append("## Diagrama de dependencias de integración")
        lines.append("")
        lines.append(generate_mermaid(connected_systems, integrations))
        lines.append("")

    # Mermaid sequence diagrams (one per CS)
    seq_diagrams = generate_sequence_diagrams(connected_systems, integrations)
    if seq_diagrams:
        lines.append("## Diagramas de secuencia (flujo temporal por Connected System)")
        lines.append("")
        for cs_name, seq_md in seq_diagrams:
            lines.append(f"### {cs_name}")
            lines.append("")
            lines.append(seq_md)
            lines.append("")

    # C4 Context diagram
    c4_md = generate_c4_context(connected_systems)
    if c4_md:
        lines.append("## Diagrama de contexto (C4)")
        lines.append("")
        lines.append(c4_md)
        lines.append("")

    # Import Customization notes
    lines.append("## Notas de Import Customization")
    lines.append("")
    lines.append("<!-- AGENT: enrich this section with environment-specific URLs and deployment notes -->")
    lines.append("")
    if connected_systems:
        for cs in connected_systems:
            lines.append(f"- **{cs['name']}**: verificar `baseUrl`, `username`, `password` por entorno")
    lines.append("")

    lines.append("## Evidencias")
    lines.append("")
    lines.append(f"- `{cs_dir}/` ({len(cs_files)} archivos)")
    lines.append(f"- `{args.index}` (integrations de content/)")
    lines.append("")

    cs_count = len(connected_systems)
    int_count = len(integrations)
    write_output(args, "\n".join(lines),
                 label=f"Integrations: {cs_count} CS, {int_count} integrations")
    print(f"Integrations: {cs_count} CS, {int_count} integrations -> {args.output}")


if __name__ == "__main__":
    sys.exit(main() or 0)
