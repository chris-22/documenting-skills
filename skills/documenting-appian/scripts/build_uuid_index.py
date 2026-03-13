#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Phase A — Build UUID cross-reference index from all Appian export artifacts.

Scans application_files/ and produces docs/_uuid-index.json with:
  { uuid: { "name": str, "type": str, "file": str, "description": str } }

Handles: XML objects (name= attribute, <name> element, <group><name>),
         XSD CDTs (URL-encoded filenames), Data Store entities.

v2: Adds description extraction, unknown folder discovery, and summary metadata.
"""
import json
import os
import re
import sys
import glob
import xml.etree.ElementTree as ET
from urllib.parse import unquote

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from cli_common import make_parser, validate_args, write_output, verbose
from xml_helpers import strip_ns, find_child, text

DEFAULT_APP_DIR = "application_files"
DEFAULT_OUT_FILE = os.path.join("docs", "_uuid-index.json")

_VERBOSE = False  # set from args in main()


def _extract_description(elem):
    """Extract description from an element, trying multiple tag patterns."""
    for tag_name in ("description", "desc"):
        for child in list(elem):
            if strip_ns(child.tag) == tag_name:
                t = text(child)
                if t:
                    return t
                # Could be a string-map (process models)
                smap = find_child(child, "string-map")
                if smap is not None:
                    return _extract_string_map_value_inline(smap)
    return ""


def _extract_string_map_value_inline(smap_el):
    """Inline version for use in _extract_description before main func is defined."""
    if smap_el is None:
        return ""
    best = ""
    for pair in list(smap_el):
        if strip_ns(pair.tag) != "pair":
            continue
        val = find_child(pair, "value")
        v = text(val)
        if v and not v.startswith("="):
            if not best:
                best = v
    return best


def extract_from_xml(filepath, obj_type):
    """Extract uuid and name from a standard Appian XML haul file."""
    entries = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as exc:
        if _VERBOSE:
            print(f"  [warning] Skipping {filepath}: {exc}", file=sys.stderr)
        return entries

    root_tag = strip_ns(root.tag)

    # Try name= attribute on the main element (webApi, site, recordType, tempoReport)
    for child in root:
        tag = strip_ns(child.tag)
        uuid_val = child.attrib.get("{http://www.appian.com/ae/types/2009}uuid", "")
        name_val = child.attrib.get("name", "")
        if uuid_val and name_val:
            desc = _extract_description(child)
            entries.append({"uuid": uuid_val, "name": name_val, "type": obj_type, "file": filepath, "description": desc})

        # Also check <uuid> and <name> sub-elements (dataStore, connectedSystem, application)
        uuid_el = find_child(child, "uuid")
        name_el = find_child(child, "name")
        if text(uuid_el) and text(name_el):
            desc = _extract_description(child)
            entries.append({"uuid": text(uuid_el), "name": text(name_el), "type": obj_type, "file": filepath, "description": desc})

        # Data Store entities
        if tag in ("dataStore",):
            entities_el = find_child(child, "entities")
            if entities_el is not None:
                for entity in list(entities_el):
                    if strip_ns(entity.tag) == "entity":
                        e_uuid = text(find_child(entity, "uuid"))
                        e_name = text(find_child(entity, "name"))
                        e_type = text(find_child(entity, "type"))
                        if e_uuid:
                            entries.append({
                                "uuid": e_uuid,
                                "name": e_name or e_type,
                                "type": "dataStoreEntity",
                                "file": filepath,
                                "cdtType": e_type,
                            })

    # Groups have <group><name>
    if "group" in root_tag.lower():
        for child in root:
            tag = strip_ns(child.tag)
            if tag == "group":
                g_uuid = text(find_child(child, "uuid"))
                g_name = text(find_child(child, "name"))
                g_desc = _extract_description(child)
                if g_uuid:
                    entries.append({"uuid": g_uuid, "name": g_name, "type": "group", "file": filepath, "description": g_desc})

    return entries


def _extract_string_map_value(smap_el):
    """Extract best value from a <string-map> element (es generic > es any > en > first)."""
    if smap_el is None:
        return ""
    best = ""
    for pair in list(smap_el):
        if strip_ns(pair.tag) != "pair":
            continue
        val = find_child(pair, "value")
        v = text(val)
        if v and not v.startswith("="):
            loc = find_child(pair, "locale")
            lang = (loc.attrib.get("lang", "") if loc is not None else "").lower()
            country = loc.attrib.get("country", "") if loc is not None else ""
            if lang == "es" and not country:
                return v
            if not best:
                best = v
    return best


def extract_from_process_model(filepath):
    """Extract uuid, name, and description from processModel XML."""
    entries = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as exc:
        if _VERBOSE:
            print(f"  [warning] Skipping PM {filepath}: {exc}", file=sys.stderr)
        return entries

    for elem in root.iter():
        if strip_ns(elem.tag) == "pm":
            meta = find_child(elem, "meta")
            if meta is None:
                continue
            uuid_val = text(find_child(meta, "uuid"))
            name_el = find_child(meta, "name")
            smap = find_child(name_el, "string-map") if name_el is not None else None
            name_val = _extract_string_map_value(smap)
            desc_el = find_child(meta, "desc")
            desc_smap = find_child(desc_el, "string-map") if desc_el is not None else None
            desc_val = _extract_string_map_value(desc_smap)
            if uuid_val:
                entries.append({"uuid": uuid_val, "name": name_val or uuid_val, "type": "processModel", "file": filepath, "description": desc_val})
            break
    return entries


def extract_from_xsd(filepath):
    """Extract CDT name from URL-encoded XSD filename."""
    fname = os.path.basename(filepath)
    decoded = unquote(fname).replace(".xsd", "")
    # Extract name after } if present
    if "}" in decoded:
        name = decoded.split("}")[-1]
        namespace = decoded.split("}")[0].lstrip("{")
    else:
        name = decoded
        namespace = ""
    return [{"uuid": decoded, "name": name, "type": "datatype", "file": filepath, "namespace": namespace}]


def extract_from_content(filepath):
    """Extract uuid, name, and description from content XML (docs, folders, KCs)."""
    entries = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as exc:
        if _VERBOSE:
            print(f"  [warning] Skipping content {filepath}: {exc}", file=sys.stderr)
        return entries
    for child in root:
        tag = strip_ns(child.tag)
        uuid_el = find_child(child, "uuid")
        name_el = find_child(child, "name")
        if text(uuid_el) and text(name_el):
            desc = _extract_description(child)
            entries.append({"uuid": text(uuid_el), "name": text(name_el), "type": f"content/{tag}", "file": filepath, "description": desc})
    return entries


def main():
    parser = make_parser(
        "Build UUID cross-reference index from Appian export artifacts.",
        default_output=DEFAULT_OUT_FILE, needs_app_dir=True, needs_index=False,
        examples=[
            "python build_uuid_index.py",
            "python build_uuid_index.py --app-dir /other/export",
            "python build_uuid_index.py --dry-run",
        ],
    )
    args = parser.parse_args()
    validate_args(args, needs_app_dir=True, needs_index=False)
    global _VERBOSE
    _VERBOSE = getattr(args, "verbose", False)
    APP_DIR = args.app_dir
    index = {}

    # Map folder -> object type  (uses APP_DIR from args)
    folder_types = {
        "connectedSystem": "connectedSystem",
        "dataStore": "dataStore",
        "webApi": "webApi",
        "site": "site",
        "recordType": "recordType",
        "tempoReport": "tempoReport",
        "translationSet": "translationSet",
        "translationString": "translationString",
        "application": "application",
        "processModelFolder": "processModelFolder",
    }

    # Standard XML folders
    for folder, obj_type in folder_types.items():
        pattern = os.path.join(APP_DIR, folder, "*.xml")
        files = glob.glob(pattern)
        verbose(args, f"  {folder}/: {len(files)} files")
        for f in files:
            for entry in extract_from_xml(f, obj_type):
                index[entry["uuid"]] = entry

    # Process Models (special parsing)
    pm_files = glob.glob(os.path.join(APP_DIR, "processModel", "*.xml"))
    verbose(args, f"  processModel/: {len(pm_files)} files")
    for f in pm_files:
        for entry in extract_from_process_model(f):
            index[entry["uuid"]] = entry

    # CDTs (XSD files)
    xsd_files = glob.glob(os.path.join(APP_DIR, "datatype", "*.xsd"))
    verbose(args, f"  datatype/: {len(xsd_files)} XSD files")
    for f in xsd_files:
        for entry in extract_from_xsd(f):
            index[entry["uuid"]] = entry

    # Content objects
    content_files = glob.glob(os.path.join(APP_DIR, "content", "*.xml"))
    verbose(args, f"  content/: {len(content_files)} files")
    for f in content_files:
        for entry in extract_from_content(f):
            index[entry["uuid"]] = entry

    # Groups
    group_files = glob.glob(os.path.join(APP_DIR, "group", "*.xml"))
    verbose(args, f"  group/: {len(group_files)} files")
    for f in group_files:
        for entry in extract_from_xml(f, "group"):
            index[entry["uuid"]] = entry

    content = json.dumps(index, ensure_ascii=False, indent=2)
    write_output(args, content, label=f"UUID index: {len(index)} entries")

    print(f"UUID index: {len(index)} entries -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
