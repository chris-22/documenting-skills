"""
Appian Process Model XML parser.

Extracts nodes, edges, subprocess links and process metadata from an
Appian export processModel XML file.
"""
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional

from xml_helpers import strip_ns, find_child, find_children, text
from node_classifier import detect_shape


def sanitize_filename(name: str) -> str:
    """Safe filename preserving accents, removing invalid Windows chars, replacing spaces with hyphens."""
    INVALID_WIN_CHARS = set('<>:"/\\|?*')
    if not name:
        return 'process'
    s = ''.join(ch for ch in name if ch not in INVALID_WIN_CHARS)
    s = s.strip().rstrip('. ')
    s = s.replace(' ', '-')
    if len(s) > 120:
        s = s[:120]
    return s or 'process'


def pick_process_name(pm_block) -> str:
    """Pick the most descriptive process name across locales.
    Preference order: Spanish (lang=es), then English (lang=en), then longest value.
    """
    meta = find_child(pm_block, 'meta')
    if meta is None:
        return ''
    candidates: List[Tuple[str, str, str]] = []  # (lang, country, value)
    # Use only <name> for documentation. <process-name> may contain dynamic expressions.
    for field in ('name',):
        cont = find_child(meta, field)
        smap = find_child(cont, 'string-map') if cont is not None else None
        if smap is None:
            continue
        for pair in find_children(smap, 'pair'):
            loc = find_child(pair, 'locale')
            val = find_child(pair, 'value')
            value = (val.text or '').strip() if val is not None else ''
            if not value:
                continue
            # Ignore expression-like values (e.g., starting with '=')
            if value.startswith('='):
                continue
            lang = (loc.attrib.get('lang') or '').lower() if loc is not None else ''
            country = (loc.attrib.get('country') or '') if loc is not None else ''
            candidates.append((lang, country, value))
    if not candidates:
        # fallback: uuid
        uuid = text(find_child(meta, 'uuid'))
        return uuid or ''

    def score(item: Tuple[str, str, str]) -> Tuple[int, int, int]:
        lang, country, value = item
        is_es = 1 if lang == 'es' else 0
        is_en = 1 if lang == 'en' else 0
        length = len(value)
        return (is_es, is_en, length)

    best = sorted(candidates, key=score, reverse=True)[0][2]
    return best


def get_subprocess_uuid_from_node(node) -> Optional[str]:
    """Extract the target subprocess UUID from a SUB_PROC node if present."""
    ac = find_child(node, 'ac')
    acps = find_child(ac, 'acps') if ac is not None else None
    if acps is None:
        return None
    for acp in find_children(acps, 'acp'):
        name_attr = acp.attrib.get('name')
        if name_attr == 'pmUUID':
            val = find_child(acp, 'value')
            uuid = text(val)
            if uuid:
                return uuid
        if name_attr == 'pmID':
            val = find_child(acp, 'value')
            if val is not None:
                for k, v in val.attrib.items():
                    if k.endswith('id') and v:
                        return v
    return None


def find_process_xml_by_uuid(base_dir: str, uuid: str) -> Optional[str]:
    """Locate the XML file for a subprocess given its UUID."""
    if not uuid:
        return None
    candidate = os.path.join(base_dir, f"{uuid}.xml")
    return candidate if os.path.exists(candidate) else None


def parse_process(xml_path: str) -> Tuple[str, str, Dict[str, Tuple[str, str, str]], List[Tuple[str, str]], Dict[str, str]]:
    """Parse an Appian processModel XML and return (uuid, name, nodes, edges, clicks).

    Returns:
        uuid:   Process UUID
        pname:  Human-readable process name
        nodes:  {gid: (shape, label, css_class)}
        edges:  [(from_gid, to_gid), ...]
        clicks: {gid: subprocess_uuid}
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Find pm block
    pmp = None
    for child in root.iter():
        if strip_ns(child.tag) == 'pm':
            pmp = child
            break
    if pmp is None:
        raise RuntimeError('No <pm> found in XML: %s' % xml_path)

    meta = find_child(pmp, 'meta')
    uuid = text(find_child(meta, 'uuid')) if meta is not None else os.path.basename(xml_path)
    pname = pick_process_name(pmp)

    nodes_el = find_child(pmp, 'nodes')
    nodes: Dict[str, Tuple[str, str, str]] = {}  # id -> (shape, label, css_class)
    edges: List[Tuple[str, str]] = []
    clicks: Dict[str, str] = {}  # gid -> subprocess uuid

    if nodes_el is not None:
        for node in find_children(nodes_el, 'node'):
            gid = text(find_child(node, 'guiId'))
            if not gid:
                gid = str(len(nodes))
            shape, label, css_class = detect_shape(node)
            nodes[gid] = (shape, label, css_class)
            # connections
            cons = find_child(node, 'connections')
            if cons is not None:
                for con in find_children(cons, 'connection'):
                    to = text(find_child(con, 'to'))
                    if to:
                        edges.append((gid, to))
            # detect subprocess and capture link target
            if shape == 'fr-rect':
                sub_uuid = get_subprocess_uuid_from_node(node)
                if sub_uuid:
                    clicks[gid] = sub_uuid

    return (uuid, pname, nodes, edges, clicks)
