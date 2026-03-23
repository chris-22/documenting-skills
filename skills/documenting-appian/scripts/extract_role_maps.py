#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Phase E — Extract role maps from all Appian objects and generate security matrix.

Scans all XML files in the Appian app root for <roleMap> elements, resolves group
UUIDs and object names using docs/_uuid-index.json, and produces docs/08-appian-security.md.

v2: Resolves Process Model names via <pm><meta><name> parsing and marks
unresolved groups with TODO(unresolved-group: UUID).
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
DEFAULT_OUT = os.path.join("docs", "08-appian-security.md")


def load_index(index_file):
    if not os.path.exists(index_file):
        return {}
    with open(index_file, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_group(uuid, index):
    entry = index.get(uuid, {})
    name = entry.get("name", "")
    if name:
        return name
    return f"TODO(unresolved-group: {uuid})"


def get_pm_name(filepath):
    """Extract Process Model name from <pm><meta><name><string-map>."""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        for elem in root.iter():
            if strip_ns(elem.tag) == "pm":
                meta = find_child(elem, "meta")
                if meta is None:
                    return None
                name_el = find_child(meta, "name")
                if name_el is None:
                    return None
                smap = find_child(name_el, "string-map")
                if smap is None:
                    return None
                for pair in list(smap):
                    if strip_ns(pair.tag) != "pair":
                        continue
                    val = find_child(pair, "value")
                    v = text(val)
                    if v and not v.startswith("="):
                        return v
    except Exception:
        pass
    return None


def extract_object_name(filepath, root, index=None):
    """Try to extract the object name from various Appian XML patterns."""
    root_tag = strip_ns(root.tag)

    # Process Models: use dedicated parser
    if "processModel" in root_tag.lower() or "processmodel" in root_tag.lower():
        pm_name = get_pm_name(filepath)
        if pm_name:
            return pm_name, "processModel"

    # Process Model Folders: <processModelFolder><name>
    if "processModelFolder" in root_tag:
        for child in root:
            if strip_ns(child.tag) == "processModelFolder":
                name_el = find_child(child, "name")
                if name_el is not None and text(name_el):
                    return text(name_el), "processModelFolder"

    for child in root:
        tag = strip_ns(child.tag)
        # name= attribute (webApi, site, recordType, tempoReport)
        name = child.attrib.get("name", "")
        if name:
            return name, tag
        # <name> sub-element (dataStore, connectedSystem)
        name_el = find_child(child, "name")
        if name_el is not None and text(name_el):
            return text(name_el), tag

    # Fallback: try UUID index
    if index:
        basename = os.path.splitext(os.path.basename(filepath))[0]
        entry = index.get(basename, {})
        if entry.get("name"):
            return entry["name"], entry.get("type", "unknown")

    return os.path.basename(filepath), "unknown"


def extract_role_maps(filepath):
    """Extract all roleMap entries from an XML file."""
    results = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception:
        return results

    obj_name, obj_type = extract_object_name(filepath, root, _extract_index)

    for elem in root.iter():
        if strip_ns(elem.tag) == "roleMap":
            for role_el in list(elem):
                if strip_ns(role_el.tag) != "role":
                    continue
                role_name = role_el.attrib.get("name", "")
                inherit = role_el.attrib.get("inherit", "false")
                allow_all = role_el.attrib.get("allowForAll", "false")
                groups_el = find_child(role_el, "groups")
                group_uuids = []
                if groups_el is not None:
                    for g in list(groups_el):
                        if strip_ns(g.tag) == "groupUuid":
                            group_uuids.append(text(g))
                users_el = find_child(role_el, "users")
                user_count = len(list(users_el)) if users_el is not None else 0

                if group_uuids or allow_all == "true" or user_count > 0:
                    results.append({
                        "object": obj_name,
                        "objectType": obj_type,
                        "file": filepath,
                        "role": role_name,
                        "groups": group_uuids,
                        "allowForAll": allow_all == "true",
                        "inherit": inherit == "true",
                    })
    return results


def build_group_hierarchy(app_dir, index):
    """Read group/*.xml to extract parent relationships and generate Mermaid hierarchy diagram."""
    groups = []  # list of {name, uuid, parentUuid}
    for f in sorted(glob.glob(os.path.join(app_dir, "group", "*.xml"))):
        try:
            tree = ET.parse(f)
            root = tree.getroot()
        except Exception:
            continue
        for child in root:
            tag = strip_ns(child.tag)
            if tag in ("group", "content"):
                name = text(find_child(child, "groupName")) or text(find_child(child, "name"))
                uuid = text(find_child(child, "uuid")) or text(find_child(child, "groupUuid"))
                parent = text(find_child(child, "parentUuid")) or ""
                if not name and uuid:
                    entry = index.get(uuid, {})
                    name = entry.get("name", uuid)
                if name:
                    groups.append({"name": name, "uuid": uuid, "parentUuid": parent})

    if not groups:
        return ""

    # Build uuid->name map
    uuid_to_name = {g["uuid"]: g["name"] for g in groups}
    # Classify groups for coloring
    admin_kw = ["admin", "administrad"]
    geo_kw = ["espa", "mexico", "general"]
    tech_kw = ["webapi", "web_api"]

    def classify(name):
        nl = name.lower()
        if any(k in nl for k in admin_kw):
            return "admin"
        if any(k in nl for k in geo_kw):
            return "geo"
        if any(k in nl for k in tech_kw):
            return "tech"
        return "role"

    lines = []
    lines.append("## Jerarqu\u00eda de grupos")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart TD")

    # Node definitions
    for g in groups:
        safe_id = g["name"].replace(" ", "_").replace("-", "_")
        lines.append(f'    {safe_id}["{g["name"]}"]')

    lines.append("")

    # Edges (parent -> child)
    for g in groups:
        if g["parentUuid"] and g["parentUuid"] in uuid_to_name:
            parent_name = uuid_to_name[g["parentUuid"]]
            parent_id = parent_name.replace(" ", "_").replace("-", "_")
            child_id = g["name"].replace(" ", "_").replace("-", "_")
            lines.append(f"    {parent_id} --> {child_id}")

    lines.append("")

    # classDef
    lines.append('    classDef admin fill:#F44336,stroke:#C62828,color:#fff,stroke-width:2px')
    lines.append('    classDef role fill:#2D9CDB,stroke:#1A7AB5,color:#fff,stroke-width:1px')
    lines.append('    classDef geo fill:#6FCF97,stroke:#4AA86B,color:#fff,stroke-width:1px')
    lines.append('    classDef tech fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:1px')

    # class assignments
    classified = {"admin": [], "role": [], "geo": [], "tech": []}
    for g in groups:
        cls = classify(g["name"])
        safe_id = g["name"].replace(" ", "_").replace("-", "_")
        classified[cls].append(safe_id)

    for cls, ids in classified.items():
        if ids:
            lines.append(f"    class {','.join(ids)} {cls}")

    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def build_role_assignment_diagram(all_roles, index):
    """Generate a flowchart TD showing Group -> Role -> Object type assignments.

    Fully generic: reads from the collected roleMap entries, groups objects by type,
    and shows which groups have which roles on which object types.
    Limits to top groups (by assignment count) to keep the diagram readable.
    """
    if not all_roles:
        return ""

    # Aggregate: group_name -> set of (role, object_type)
    group_summary = {}
    for entry in all_roles:
        for g_uuid in entry["groups"]:
            g_name = resolve_group(g_uuid, index)
            group_summary.setdefault(g_name, {"roles": set(), "obj_types": set(), "count": 0})
            group_summary[g_name]["roles"].add(entry["role"])
            group_summary[g_name]["obj_types"].add(entry["objectType"])
            group_summary[g_name]["count"] += 1

    if not group_summary:
        return ""

    # Limit to top 10 groups by assignment count for readability
    top_groups = sorted(group_summary.items(), key=lambda x: x[1]["count"], reverse=True)[:10]

    # Collect unique roles and object types from top groups
    all_obj_types = set()
    all_role_names = set()
    for _, info in top_groups:
        all_role_names.update(info["roles"])
        all_obj_types.update(info["obj_types"])

    def _sid(name):
        """Sanitize ID for Mermaid."""
        s = name.replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
        s = s.replace(":", "_").replace(",", "_").replace(".", "_")
        # Prefix to avoid reserved words
        if s.lower() in ("end", "default", "class", "style", "graph", "subgraph"):
            s = s + "_node"
        return s

    lines = []
    lines.append("## Diagrama de asignación de permisos")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart LR")

    # Subgraph for groups
    lines.append('    subgraph Grupos')
    for g_name, _ in top_groups:
        gid = "G_" + _sid(g_name)
        safe = g_name.replace('"', "'")
        # Truncate long TODO names
        if len(safe) > 50:
            safe = safe[:47] + "..."
        lines.append(f'        {gid}["{safe}"]')
    lines.append("    end")
    lines.append("")

    # Subgraph for roles
    lines.append('    subgraph Roles')
    for role in sorted(all_role_names):
        rid = "R_" + _sid(role)
        lines.append(f'        {rid}["{role}"]')
    lines.append("    end")
    lines.append("")

    # Subgraph for object types
    lines.append('    subgraph Tipos_de_Objeto')
    for ot in sorted(all_obj_types):
        oid = "O_" + _sid(ot)
        lines.append(f'        {oid}["{ot}"]')
    lines.append("    end")
    lines.append("")

    # Edges: Group -> Role (deduplicated)
    seen_gr = set()
    for g_name, info in top_groups:
        gid = "G_" + _sid(g_name)
        for role in info["roles"]:
            rid = "R_" + _sid(role)
            key = (gid, rid)
            if key not in seen_gr:
                lines.append(f"    {gid} --> {rid}")
                seen_gr.add(key)

    # Edges: Role -> Object Type (from all_roles, deduplicated)
    seen_ro = set()
    for entry in all_roles:
        rid = "R_" + _sid(entry["role"])
        oid = "O_" + _sid(entry["objectType"])
        key = (rid, oid)
        if key not in seen_ro:
            lines.append(f"    {rid} --> {oid}")
            seen_ro.add(key)

    lines.append("")
    lines.append('    classDef grp fill:#BDBDBD,stroke:#828282,color:#333,stroke-width:1px')
    lines.append('    classDef rl fill:#2D9CDB,stroke:#1A7AB5,color:#fff,stroke-width:1px')
    lines.append('    classDef obj fill:#6FCF97,stroke:#4AA86B,color:#fff,stroke-width:1px')

    grp_ids = ["G_" + _sid(g) for g, _ in top_groups]
    role_ids = ["R_" + _sid(r) for r in sorted(all_role_names)]
    obj_ids = ["O_" + _sid(o) for o in sorted(all_obj_types)]
    if grp_ids:
        lines.append(f"    class {','.join(grp_ids)} grp")
    if role_ids:
        lines.append(f"    class {','.join(role_ids)} rl")
    if obj_ids:
        lines.append(f"    class {','.join(obj_ids)} obj")

    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = make_parser(
        "Extract role maps from all Appian objects and generate security matrix.",
        default_output=DEFAULT_OUT, needs_app_dir=True, needs_index=True,
        examples=[
            "python extract_role_maps.py",
            "python extract_role_maps.py --output custom-security.md",
            "python extract_role_maps.py --dry-run",
        ],
    )
    args = parser.parse_args()
    validate_args(args, needs_app_dir=True, needs_index=True)
    global _extract_index
    index = load_index(args.index)
    _extract_index = index

    all_roles = []
    folders = [
        "connectedSystem", "dataStore", "webApi", "site", "recordType",
        "tempoReport", "processModel", "processModelFolder", "group",
        "content",
    ]
    for folder in folders:
        folder_files = glob.glob(os.path.join(args.app_dir, folder, "*.xml"))
        # content/ has subdirectories — also scan recursively
        if folder == "content":
            folder_files += glob.glob(os.path.join(args.app_dir, folder, "**", "*.xml"), recursive=True)
            folder_files = sorted(set(folder_files))
        verbose(args, f"  {folder}/: {len(folder_files)} files")
        for f in folder_files:
            all_roles.extend(extract_role_maps(f))
    verbose(args, f"Extracted {len(all_roles)} role assignments total")

    # Build group hierarchy diagram
    hierarchy_md = build_group_hierarchy(args.app_dir, index)

    # Build matrix
    lines = [
        f"# {get_app_name()} — Matriz de permisos (auto-generado)",
        "",
        f"Total asignaciones: **{len(all_roles)}**",
        "",
    ]

    if hierarchy_md:
        lines.append(hierarchy_md)
        lines.append("")

    # Role assignment diagram (Group -> Role -> Object Type)
    assignment_md = build_role_assignment_diagram(all_roles, index)
    if assignment_md:
        lines.append(assignment_md)
        lines.append("")

    lines.extend([
        "## Matriz completa",
        "",
        "| Objeto | Tipo | Rol | Grupos asignados |",
        "|--------|------|-----|-----------------|",
    ])

    for entry in sorted(all_roles, key=lambda x: (x["objectType"], x["object"], x["role"])):
        groups_resolved = [resolve_group(g, index) for g in entry["groups"]]
        groups_str = ", ".join(groups_resolved) if groups_resolved else ""
        if entry["allowForAll"]:
            groups_str = "(ALL USERS)" + (", " + groups_str if groups_str else "")
        lines.append(
            f"| {entry['object']} | {entry['objectType']} | {entry['role']} | {groups_str} |"
        )

    lines.append("")

    # Group summary: which groups appear in which roles
    group_roles = {}
    for entry in all_roles:
        for g_uuid in entry["groups"]:
            g_name = resolve_group(g_uuid, index)
            group_roles.setdefault(g_name, set()).add(entry["role"])

    lines.append("## Resumen por grupo")
    lines.append("")
    lines.append("| Grupo | Roles asignados | Objetos |")
    lines.append("|-------|----------------|---------|")
    for g_name in sorted(group_roles.keys()):
        roles = sorted(group_roles[g_name])
        obj_count = sum(1 for e in all_roles if any(resolve_group(gu, index) == g_name for gu in e["groups"]))
        lines.append(f"| {g_name} | {', '.join(roles)} | {obj_count} |")
    lines.append("")

    # Empty roleMaps (objects with no groups assigned)
    lines.append("## Objetos sin grupos en roleMap")
    lines.append("")
    objects_with_roles = {e["object"] for e in all_roles}
    # Scan all objects to find those without any role map entry with groups
    all_objects = set()
    for folder in folders:
        for f in glob.glob(os.path.join(args.app_dir, folder, "*.xml")):
            try:
                tree = ET.parse(f)
                root = tree.getroot()
                name, _ = extract_object_name(f, root, index)
                all_objects.add(name)
            except Exception:
                pass

    orphans = all_objects - objects_with_roles
    if orphans:
        for o in sorted(orphans):
            lines.append(f"- {o}")
    else:
        lines.append("*(Todos los objetos tienen al menos un grupo asignado)*")
    lines.append("")

    lines.append("## Evidencias")
    lines.append("")
    lines.append(f"- Escaneados {len(all_roles)} asignaciones de rol en `{args.app_dir}/*/`")
    lines.append(f"- Grupos resueltos via `{args.index}`")
    lines.append("")

    write_output(args, "\n".join(lines), label=f"Role maps: {len(all_roles)} assignments")

    print(f"Role maps: {len(all_roles)} assignments -> {args.output}")


if __name__ == "__main__":
    sys.exit(main() or 0)
