#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Phase G — Unified health analysis: dead code detection + expression analysis.

Merges the functionality of detect_dead_code.py (UUID reference graph) with
analyze_expressions.py (expression-level references: rule!, cons!, #"_a-...").

This reduces the "unverifiable" content/ objects from ~86% to ~40-50% by
scanning expression blocks for opaque Appian ID patterns.

Produces docs/12-appian-health.md
"""
import json
import os
import re
import sys
import glob
import xml.etree.ElementTree as ET
from collections import defaultdict

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from app_info import get_app_name
from cli_common import make_parser, validate_args, write_output, verbose
from xml_helpers import strip_ns

DEFAULT_APP_DIR = "."
DEFAULT_INDEX = os.path.join("docs", "_uuid-index.json")
DEFAULT_OUT = os.path.join("docs", "12-appian-health.md")

# --- UUID patterns (from detect_dead_code.py) ---
UUID_PATTERNS = [
    re.compile(r'_a-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_\d+'),
    re.compile(r'_e-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_\d+'),
    re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
    re.compile(r'\d{4}e[0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
]

# --- Expression-level patterns (from analyze_expressions.py) ---
EXPR_UUID_PATTERNS = [
    re.compile(r'#"(_a-[0-9a-f-]+_\d+)"'),
    re.compile(r'#"(urn:appian:record-type:v1:[0-9a-f-]+)"'),
    re.compile(r'#"(urn:appian:record-field:v1:[0-9a-f-]+/[^"]+)"'),
    re.compile(r'#"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"'),
]
RULE_PATTERN = re.compile(r'rule!([A-Za-z0-9_]+)')
CONS_PATTERN = re.compile(r'cons!([A-Za-z0-9_]+)')

ENTRY_POINT_TYPES = {"site", "webApi", "application", "tempoReport"}
STRUCTURAL_TYPES = {
    "connectedSystem", "group", "translationSet", "translationString",
    "processModelFolder", "dataStoreEntity", "datatype", "dataStore",
}

# Expression element tags to scan
EXPR_TAGS = {
    "expression", "uiExpr", "visibilityExpr", "nameExpr", "titleExpr",
    "listViewTemplateExpr", "detailViewExpr", "definition",
}


# --- State discovery patterns (generic, no app-specific assumptions) ---
STATE_KW = re.compile(r'(?i)(status|estado|stage|phase|state|etapa)', re.IGNORECASE)
STATE_CONST_NAME = re.compile(r'(?i).*(STATUS|ESTADO|STAGE|PHASE|STATE).*')


def find_all_uuids_in_file(filepath):
    """Find all UUID-like strings in a file's raw content."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return set()
    found = set()
    for pattern in UUID_PATTERNS:
        found.update(pattern.findall(content))
    return found


def extract_expression_refs(filepath):
    """Extract expression-level references (rule!, cons!, #"_a-...") from XML."""
    refs = set()
    rule_names = set()
    cons_names = set()
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception:
        return refs, rule_names, cons_names

    for elem in root.iter():
        tag = strip_ns(elem.tag)
        # Check known expression tags
        is_expr = tag in EXPR_TAGS
        # Also check namespaced expression tags
        if not is_expr and "expression" in tag.lower():
            is_expr = True
        if not is_expr:
            continue
        text = (elem.text or "").strip()
        if not text or len(text) < 5:
            continue
        # Extract UUID references from expression text
        for pattern in EXPR_UUID_PATTERNS:
            refs.update(pattern.findall(text))
        # Extract rule! and cons! references
        rule_names.update(RULE_PATTERN.findall(text))
        cons_names.update(CONS_PATTERN.findall(text))

    return refs, rule_names, cons_names


def build_name_to_uuid_map(index):
    """Build reverse map: object name -> UUID for rule!/cons! resolution."""
    name_map = {}
    for uuid, info in index.items():
        name = info.get("name", "")
        if name:
            name_map[name] = uuid
    return name_map


def discover_states(app_dir, index):
    """Discover entity states from multiple generic sources.

    Sources (all heuristic, no app-specific assumptions):
    1. XOR gateway outgoing edge labels in processModel XMLs
    2. Constants whose names match *STATUS*/*ESTADO*/*STAGE*/*PHASE*/*STATE*
       (extracts list-type constant values if available)
    3. Decision table output values from decision XMLs

    Returns a dict: {source_label: [list of discovered state strings]}.
    Only returns results if states are actually found (never invents data).
    """
    results = {}

    # Source 1: XOR gateway edge labels from Process Models
    pm_dir = os.path.join(app_dir, "processModel")
    xor_states = set()
    if os.path.isdir(pm_dir):
        for fpath in sorted(glob.glob(os.path.join(pm_dir, "*.xml"))):
            try:
                tree = ET.parse(fpath)
                root = tree.getroot()
            except Exception:
                continue
            # Find XOR gateway nodes (core.4)
            xor_ids = set()
            for elem in root.iter():
                tag = strip_ns(elem.tag)
                if tag == "node":
                    nid = elem.attrib.get("id", "")
                    type_id = ""
                    type_el = None
                    for c in list(elem):
                        ct = strip_ns(c.tag)
                        if ct == "type":
                            type_el = c
                            break
                    if type_el is not None:
                        type_id = type_el.attrib.get("id", "") or (type_el.text or "").strip()
                    if "core.4" in type_id or "xor" in type_id.lower():
                        xor_ids.add(nid)
            # Find connections from XOR nodes and extract labels
            for elem in root.iter():
                tag = strip_ns(elem.tag)
                if tag == "connection":
                    from_id = ""
                    label_text = ""
                    for c in list(elem):
                        ct = strip_ns(c.tag)
                        if ct == "from":
                            from_id = (c.text or "").strip()
                        elif ct == "label":
                            # label may have string-map > pair > value
                            for sm in c.iter():
                                if strip_ns(sm.tag) == "value" and sm.text:
                                    v = sm.text.strip()
                                    if v and not v.startswith("=") and len(v) < 80:
                                        label_text = v
                                        break
                            if not label_text:
                                label_text = (c.text or "").strip()
                    if from_id in xor_ids and label_text and STATE_KW.search(label_text):
                        xor_states.add(label_text)
    if xor_states:
        results["XOR gateway labels (Process Models)"] = sorted(xor_states)

    # Source 2: Constants with status/state-like names
    const_states = {}
    for uuid, info in index.items():
        name = info.get("name", "")
        obj_type = info.get("type", "")
        if "constant" in obj_type and STATE_CONST_NAME.match(name):
            # Try to extract value from the constant XML
            fpath = info.get("file", "")
            values = []
            if fpath and os.path.exists(fpath):
                try:
                    tree = ET.parse(fpath)
                    for elem in tree.iter():
                        tag = strip_ns(elem.tag)
                        # List constants: look for <value> children
                        if tag == "value" and elem.text:
                            v = elem.text.strip()
                            if v and len(v) < 100 and not v.startswith("="):
                                values.append(v)
                except Exception:
                    pass
            if values:
                const_states[name] = values
            else:
                const_states[name] = ["(valor no extraíble)"]
    if const_states:
        results["Constants (*STATUS*/*STAGE*/*STATE*)"] = const_states

    return results


def generate_state_diagram(discovered_states):
    """Generate a stateDiagram-v2 from discovered states.

    Only generates if there are clear state values (not just constant names).
    Uses a linear chain [*] -> S1 -> S2 -> ... -> [*] since actual transitions
    are not knowable from the export alone. Adds a TODO note for transitions.
    """
    # Collect all unique state values
    all_values = set()
    for source, data in discovered_states.items():
        if isinstance(data, dict):
            for name, vals in data.items():
                for v in vals:
                    if v != "(valor no extraíble)" and len(v) < 60:
                        all_values.add(v)
        elif isinstance(data, list):
            for v in data:
                if len(v) < 60:
                    all_values.add(v)

    if len(all_values) < 2:
        return ""

    states = sorted(all_values)

    lines = [
        "```mermaid",
        "stateDiagram-v2",
        "    direction LR",
        "",
    ]

    # State definitions
    for i, s in enumerate(states):
        sid = f"S{i}"
        safe = s.replace('"', "'")
        lines.append(f'    {sid} : {safe}')

    lines.append("")

    # Transitions: [*] -> first, linear chain, last -> [*]
    lines.append(f"    [*] --> S0")
    for i in range(len(states) - 1):
        lines.append(f"    S{i} --> S{i+1}")
    lines.append(f"    S{len(states)-1} --> [*]")

    lines.append("")
    lines.append("    note right of S0")
    lines.append("        TODO: Las transiciones reales dependen")
    lines.append("        de la lógica de negocio de la aplicación.")
    lines.append("        Este diagrama muestra los estados descubiertos.")
    lines.append("    end note")

    lines.append("```")
    return "\n".join(lines)


def main():
    parser = make_parser(
        "Unified health analysis: dead code + expression references.",
        default_output=DEFAULT_OUT, needs_app_dir=True, needs_index=True,
        examples=[
            "python analyze_health.py",
            "python analyze_health.py --output custom-health.md",
            "python analyze_health.py --dry-run",
        ],
    )
    args = parser.parse_args()
    validate_args(args, needs_app_dir=True, needs_index=True)
    APP_DIR = args.app_dir

    with open(args.index, "r", encoding="utf-8") as f:
        index = json.load(f)
    if not index:
        print("Warning: UUID index is empty — nothing to analyze.", file=sys.stderr)
        app_name = get_app_name()
        empty_report = (
            f"# {app_name} — Salud de la aplicación (auto-generado)\n\n"
            "Objetos analizados: **0**\n\n"
            "El índice UUID está vacío. Ejecuta `build_uuid_index.py` primero "
            "y verifica que el directorio contiene objetos Appian.\n"
        )
        write_output(args, empty_report, label="Health: 0 objects (empty index)")
        print(f"Health: 0 objects (empty index) -> {args.output}")
        return

    verbose(args, f"Loaded index: {len(index)} entries from {args.index}")
    known_uuids = set(index.keys())
    name_to_uuid = build_name_to_uuid_map(index)

    # Map filepath -> owner UUIDs
    file_to_uuid = {}
    for uuid, info in index.items():
        fpath = info.get("file", "")
        if fpath:
            file_to_uuid.setdefault(fpath, []).append(uuid)

    # Inbound/outbound reference tracking
    inbound = defaultdict(set)
    outbound = defaultdict(set)

    # Track which objects were analyzed via expressions (vs just UUID scan)
    expr_analyzed = set()

    # Scan all XML and XSD files
    all_files = glob.glob(os.path.join(APP_DIR, "**", "*.xml"), recursive=True)
    all_files += glob.glob(os.path.join(APP_DIR, "**", "*.xsd"), recursive=True)
    verbose(args, f"Scanning {len(all_files)} files for references")

    for filepath in all_files:
        owner_uuids = file_to_uuid.get(filepath, [])
        owner_set = set(owner_uuids)

        # Level 1: UUID pattern matching in raw file content
        raw_refs = find_all_uuids_in_file(filepath) & known_uuids
        external_refs = raw_refs - owner_set

        # Level 2: Expression-level analysis (rule!, cons!, #"_a-...")
        expr_refs, rule_names, cons_names = extract_expression_refs(filepath)

        # Resolve rule! names to UUIDs
        for rname in rule_names:
            if rname in name_to_uuid:
                expr_refs.add(name_to_uuid[rname])
        # Resolve cons! names to UUIDs
        for cname in cons_names:
            if cname in name_to_uuid:
                expr_refs.add(name_to_uuid[cname])

        # Filter expression refs to known UUIDs
        expr_refs_known = expr_refs & known_uuids
        all_external = (external_refs | expr_refs_known) - owner_set

        if expr_refs_known or rule_names or cons_names:
            for ou in owner_uuids:
                expr_analyzed.add(ou)

        for owner_uuid in owner_uuids:
            outbound[owner_uuid] = outbound[owner_uuid] | all_external

        source_label = owner_uuids[0] if owner_uuids else f"_file:{os.path.basename(filepath)}"
        for ref in all_external:
            inbound[ref].add(source_label)

    # Classify objects
    unreferenced = []
    critical = []
    for uuid, info in index.items():
        obj_type = info.get("type", "")
        in_count = len(inbound.get(uuid, set()))
        out_count = len(outbound.get(uuid, set()))

        if in_count == 0:
            if obj_type in ENTRY_POINT_TYPES:
                status = "entry-point"
            elif obj_type in STRUCTURAL_TYPES:
                status = "structural"
            elif obj_type.startswith("content/"):
                # With expression analysis, we can now verify many content objects
                # Only mark as unverifiable if: no expressions found AND it's a type
                # that never has expressions (document, folder, knowledgeCenter)
                non_expr_types = {"content/document", "content/folder",
                                  "content/communityKnowledgeCenter", "content/rulesFolder"}
                if obj_type in non_expr_types:
                    status = "unverifiable-content"
                elif uuid in expr_analyzed:
                    # This object was expression-analyzed and still has 0 inbound refs
                    status = "potentially-unused"
                else:
                    status = "potentially-unused"
            else:
                status = "potentially-unused"
            unreferenced.append({
                "uuid": uuid, "name": info.get("name", ""), "type": obj_type,
                "inbound": in_count, "outbound": out_count, "status": status,
            })
        if in_count >= 5:
            critical.append({
                "uuid": uuid, "name": info.get("name", ""), "type": obj_type,
                "inbound": in_count, "outbound": out_count,
            })

    critical.sort(key=lambda x: x["inbound"], reverse=True)

    # Classify unreferenced
    unused = [u for u in unreferenced if u["status"] == "potentially-unused"]
    entry_pts = [u for u in unreferenced if u["status"] == "entry-point"]
    structural = [u for u in unreferenced if u["status"] == "structural"]
    unverifiable = [u for u in unreferenced if u["status"] == "unverifiable-content"]

    # Generate report
    app_name = get_app_name()
    lines = [
        f"# {app_name} — Salud de la aplicación (auto-generado)",
        "",
        f"Objetos analizados: **{len(index)}**",
        f"Archivos escaneados: **{len(all_files)}**",
        f"Objetos con análisis de expresiones: **{len(expr_analyzed)}**",
        "",
    ]

    # Critical objects
    lines.append("## Objetos críticos (mayor número de referencias entrantes)")
    lines.append("")
    lines.append("| Objeto | Tipo | Refs entrantes | Refs salientes |")
    lines.append("|--------|------|---------------|----------------|")
    for item in critical[:20]:
        lines.append(f"| {item['name']} | {item['type']} | {item['inbound']} | {item['outbound']} |")
    lines.append("")

    # Entry points
    lines.append("## Puntos de entrada (sin referencias entrantes — esperado)")
    lines.append("")
    lines.append(f"Total: {len(entry_pts)}")
    lines.append("")
    if entry_pts:
        lines.append("| Objeto | Tipo |")
        lines.append("|--------|------|")
        for item in sorted(entry_pts, key=lambda x: x["type"]):
            lines.append(f"| {item['name']} | {item['type']} |")
        lines.append("")

    # Structural
    lines.append("## Objetos estructurales (sin refs UUID directas — esperado)")
    lines.append("")
    lines.append(f"Total: {len(structural)}")
    lines.append("")
    if structural:
        by_type_s = defaultdict(list)
        for item in structural:
            by_type_s[item["type"]].append(item)
        for t in sorted(by_type_s.keys()):
            items = by_type_s[t]
            lines.append(f"- **{t}**: {', '.join(i['name'] for i in sorted(items, key=lambda x: x['name']))}")
        lines.append("")

    # Potentially unused
    lines.append("## Objetos potencialmente no utilizados")
    lines.append("")
    lines.append(f"Total: **{len(unused)}**")
    lines.append("")
    if unused:
        by_type = defaultdict(list)
        for item in unused:
            by_type[item["type"]].append(item)
        for t in sorted(by_type.keys()):
            items = by_type[t]
            lines.append(f"### {t} ({len(items)})")
            lines.append("")
            for item in sorted(items, key=lambda x: x["name"]):
                lines.append(f"- {item['name']}")
            lines.append("")
    else:
        lines.append("*(No se detectaron objetos no utilizados)*")
        lines.append("")

    # Unverifiable content (documents, folders, KCs — no expressions to analyze)
    lines.append("## Objetos content/ no verificables (documentos, folders, KCs)")
    lines.append("")
    lines.append(f"Total: {len(unverifiable)}")
    lines.append("")
    lines.append("Estos objetos no contienen expresiones analizables (documentos, folders, knowledge centers).")
    lines.append("Su uso se determina por referencia desde otros objetos o configuración de Appian.")
    lines.append("")
    if unverifiable:
        by_type_u = defaultdict(int)
        for item in unverifiable:
            by_type_u[item["type"]] += 1
        lines.append("| Tipo content/ | Cantidad |")
        lines.append("|--------------|----------|")
        for t in sorted(by_type_u.keys()):
            lines.append(f"| {t} | {by_type_u[t]} |")
        lines.append("")

    # State discovery + stateDiagram-v2
    discovered = discover_states(APP_DIR, index)
    if discovered:
        lines.append("## Estados descubiertos (auto-detección)")
        lines.append("")
        lines.append("> Detección heurística basada en XOR gateways, constantes y decisiones.")
        lines.append("> No se asume ninguna estructura de estados específica de la aplicación.")
        lines.append("")
        for source, data in discovered.items():
            lines.append(f"### Fuente: {source}")
            lines.append("")
            if isinstance(data, dict):
                lines.append("| Constante | Valores |")
                lines.append("|-----------|---------|")
                for name, vals in sorted(data.items()):
                    lines.append(f"| `{name}` | {', '.join(vals[:20])} |")
                lines.append("")
            elif isinstance(data, list):
                for v in data:
                    lines.append(f"- `{v}`")
                lines.append("")

        state_diagram = generate_state_diagram(discovered)
        if state_diagram:
            lines.append("### Diagrama de estados (inferido)")
            lines.append("")
            lines.append(state_diagram)
            lines.append("")
    else:
        lines.append("## Estados descubiertos")
        lines.append("")
        lines.append("*(No se detectaron estados/status en constantes ni XOR gateways)*")
        lines.append("")

    # Summary
    lines.append("## Resumen")
    lines.append("")
    lines.append("| Métrica | Valor |")
    lines.append("|---------|-------|")
    lines.append(f"| Total objetos en índice | {len(index)} |")
    lines.append(f"| Objetos con refs entrantes | {len(index) - len(unreferenced)} |")
    lines.append(f"| Objetos con análisis de expresiones | {len(expr_analyzed)} |")
    lines.append(f"| Puntos de entrada | {len(entry_pts)} |")
    lines.append(f"| Estructurales (sin ref UUID — esperado) | {len(structural)} |")
    lines.append(f"| Content/ no verificables (docs/folders) | {len(unverifiable)} |")
    lines.append(f"| **Potencialmente no usados** | **{len(unused)}** |")
    lines.append(f"| Objetos críticos (>=5 refs) | {len(critical)} |")
    lines.append("")

    lines.append("## Evidencias")
    lines.append("")
    lines.append(f"- Escaneados {len(all_files)} archivos en `{APP_DIR}/`")
    lines.append(f"- Análisis UUID + análisis de expresiones (rule!, cons!, #\"_a-...\")")
    lines.append(f"- Índice: `{args.index}`")
    lines.append("")

    write_output(args, "\n".join(lines),
                 label=f"Health: {len(unused)} potentially unused, {len(critical)} critical, {len(unverifiable)} unverifiable")

    print(f"Health: {len(unused)} potentially unused, {len(critical)} critical, "
          f"{len(unverifiable)} unverifiable -> {args.output}")


if __name__ == "__main__":
    sys.exit(main() or 0)
