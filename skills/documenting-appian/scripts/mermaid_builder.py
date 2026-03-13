"""
Mermaid flowchart code generation from parsed Appian process model data.

Handles layout selection, subgraph grouping, edge styling, legend and
clickable subprocess links.
"""
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Dict, List, Tuple

from xml_helpers import strip_ns, find_child
from node_classifier import sanitize_label
from parser import pick_process_name, find_process_xml_by_uuid, sanitize_filename
from constants import CLASS_DEFS, LEGEND_ITEMS


def build_mermaid(
    uuid: str,
    nodes: Dict[str, Tuple[str, str, str]],
    edges: List[Tuple[str, str]],
    click_hrefs: Dict[str, str],
    output_dir: str,
    pm_base_dir: str,
) -> str:
    """Build complete Mermaid flowchart string from parsed process data."""

    node_count = len(nodes)
    # Strategy 1: TD for >30 nodes, LR for smaller
    layout = 'TD' if node_count > 30 else 'LR'
    lines: List[str] = [f"flowchart {layout}"]

    # Identify start node and main gateway for thick arrows
    start_gid = None
    for gid, (shape, _, _css) in nodes.items():
        if shape == 'sm-circ':
            start_gid = gid
            break

    # Build outgoing edges index for XOR label detection
    outgoing: Dict[str, List[str]] = defaultdict(list)
    for frm, to in edges:
        outgoing[frm].append(to)

    # Find first node after start (for thick arrow chain)
    first_after_start = outgoing.get(start_gid, [None])[0] if start_gid else None
    # Find main gateway (first AND/XOR after start chain)
    main_gateway_gid = None
    if first_after_start:
        for to_gid in outgoing.get(first_after_start, []):
            if to_gid in nodes and nodes[to_gid][0] == 'diamond':
                main_gateway_gid = to_gid
                break

    # Thick arrow edges (start -> first -> main gateway)
    thick_edges = set()
    if start_gid and first_after_start:
        thick_edges.add((start_gid, first_after_start))
    if first_after_start and main_gateway_gid:
        thick_edges.add((first_after_start, main_gateway_gid))

    # --- Subgraph grouping for >30 nodes ---
    subgraph_nodes, subgraphs = _compute_subgraphs(nodes, edges, outgoing, node_count)

    # Nodes: output top-level nodes first, then subgraph blocks
    sort_key = lambda x: int(x) if x.isdigit() else x
    for gid in sorted(nodes, key=sort_key):
        if gid in subgraph_nodes:
            continue
        shape, label, _css = nodes[gid]
        label_str = sanitize_label(label) or ''
        lines.append(f"  N{gid}@{{ shape: {shape}, label: \"{label_str}\" }}")

    # Output subgraphs
    if subgraphs:
        lines.append("")
        for sg_id, sg_info in subgraphs.items():
            sg_label = sanitize_label(sg_info['name'])
            lines.append(f'  subgraph {sg_id}["{sg_label}"]')
            for gid in sorted(sg_info['gids'], key=sort_key):
                shape, label, _css = nodes[gid]
                label_str = sanitize_label(label) or ''
                lines.append(f'    N{gid}@{{ shape: {shape}, label: \"{label_str}\" }}')
            lines.append("  end")
            lines.append("")

    # Edges (dedupe) with thick arrows, XOR labels, dotted error flows
    _append_edges(lines, edges, nodes, outgoing, thick_edges)

    # classDef + class assignments
    lines.append("")
    lines.append(CLASS_DEFS)
    lines.append("")
    class_groups: Dict[str, List[str]] = defaultdict(list)
    for gid in nodes:
        _shape, _label, css_class = nodes[gid]
        class_groups[css_class].append(f"N{gid}")
    for css_class, node_ids in class_groups.items():
        lines.append(f"  class {','.join(node_ids)} {css_class}")

    # Visual legend subgraph
    _append_legend(lines, class_groups)

    # Clickable links to subprocess diagrams
    _append_click_links(lines, click_hrefs, pm_base_dir, output_dir)

    return "\n".join(lines)


# ── Private helpers ──────────────────────────────────────────────────

def _compute_subgraphs(
    nodes: Dict[str, Tuple[str, str, str]],
    edges: List[Tuple[str, str]],
    outgoing: Dict[str, List[str]],
    node_count: int,
) -> Tuple[Dict[str, str], Dict[str, dict]]:
    """Trace branches from AND gateways to convergence node and return subgraph info.

    Returns:
        subgraph_nodes: {gid: subgraph_id}
        subgraphs:      {subgraph_id: {'name': str, 'gids': list}}
    """
    subgraph_nodes: Dict[str, str] = {}
    subgraphs: Dict[str, dict] = {}

    if node_count <= 30:
        return subgraph_nodes, subgraphs

    incoming_count: Dict[str, int] = defaultdict(int)
    for _, to in edges:
        incoming_count[to] += 1

    # Find AND gateways
    and_gateways = [
        gid for gid, (shape, label, _css) in nodes.items()
        if shape == 'diamond' and label.upper() == 'AND'
    ]
    for and_gid in and_gateways:
        branches = outgoing.get(and_gid, [])
        for branch_idx, branch_start in enumerate(branches):
            if branch_start not in nodes:
                continue
            # Trace forward collecting nodes until we hit a convergence node
            chain: List[str] = []
            queue = [branch_start]
            visited: set = set()
            while queue:
                curr = queue.pop(0)
                if curr in visited or curr not in nodes:
                    continue
                # Stop at convergence nodes (>3 incoming edges = join point)
                if incoming_count[curr] > 3 and curr != branch_start:
                    continue
                # Stop at other AND gateways
                if curr != branch_start and nodes.get(curr, ('', '', ''))[0] == 'diamond' and nodes.get(curr, ('', '', ''))[1].upper() == 'AND':
                    continue
                visited.add(curr)
                chain.append(curr)
                for next_gid in outgoing.get(curr, []):
                    queue.append(next_gid)

            if len(chain) < 2:
                continue
            # Name the subgraph by first cyl or fr-rect node
            sg_name = f"Branch {branch_idx + 1}"
            for c_gid in chain:
                c_shape, c_label, _c_css = nodes[c_gid]
                if c_shape in ('cyl', 'fr-rect') and c_label:
                    sg_name = c_label.replace('Write to ', '').replace('Escritura ', '').replace('BBDD ', '')
                    break
            sg_id = f"sg_{and_gid}_{branch_idx}"
            subgraphs[sg_id] = {'name': sg_name, 'gids': chain}
            for c_gid in chain:
                subgraph_nodes[c_gid] = sg_id

    return subgraph_nodes, subgraphs


def _append_edges(
    lines: List[str],
    edges: List[Tuple[str, str]],
    nodes: Dict[str, Tuple[str, str, str]],
    outgoing: Dict[str, List[str]],
    thick_edges: set,
) -> None:
    """Append edge declarations to *lines* with appropriate styling."""
    seen: set = set()
    for frm, to in edges:
        e = (frm, to)
        if e in seen:
            continue
        seen.add(e)

        frm_shape = nodes.get(frm, ('', '', ''))[0]
        frm_label = nodes.get(frm, ('', '', ''))[1].upper()
        to_shape = nodes.get(to, ('', '', ''))[0]
        to_label = nodes.get(to, ('', '', ''))[1]

        # Thick arrows for main flow
        if e in thick_edges:
            lines.append(f"  N{frm} ==> N{to}")
        # XOR gateway with exactly 2 outgoing edges: add labels
        elif frm_shape == 'diamond' and frm_label == 'XOR' and len(outgoing[frm]) == 2:
            idx = outgoing[frm].index(to)
            label_text = 'Si' if idx == 0 else 'No'
            lines.append(f'  N{frm} -->|"{label_text}"| N{to}')
        # Dotted arrows for error/exception flows
        elif 'error' in to_label.lower() or 'exception' in to_label.lower():
            lines.append(f"  N{frm} -.-> N{to}")
        # End node directly from a gateway = skip/error path (dotted)
        elif frm_shape == 'diamond' and to_shape in ('dbl-circ',):
            lines.append(f"  N{frm} -.-> N{to}")
        else:
            lines.append(f"  N{frm} --> N{to}")


def _append_legend(lines: List[str], class_groups: Dict[str, List[str]]) -> None:
    """Append a visual legend subgraph with one sample node per used CSS class."""
    used_classes = set(class_groups.keys())
    if not used_classes:
        return
    lines.append("")
    lines.append("  subgraph Leyenda")
    lines.append("    direction LR")
    legend_ids: List[Tuple[str, str]] = []
    for css_class, (shape, label) in LEGEND_ITEMS.items():
        if css_class in used_classes:
            lid = f"L_{css_class}"
            lines.append(f'    {lid}@{{ shape: {shape}, label: "{label}" }}')
            legend_ids.append((lid, css_class))
    lines.append("  end")
    for lid, css_class in legend_ids:
        lines.append(f"  class {lid} {css_class}")


def _append_click_links(
    lines: List[str],
    click_hrefs: Dict[str, str],
    pm_base_dir: str,
    output_dir: str,
) -> None:
    """Append clickable links pointing to subprocess diagram files."""
    for gid, sub_uuid in click_hrefs.items():
        sub_xml = find_process_xml_by_uuid(pm_base_dir, sub_uuid)
        if sub_xml:
            try:
                tree = ET.parse(sub_xml)
                sub_root = tree.getroot()
                sub_pm = None
                for child in sub_root.iter():
                    if strip_ns(child.tag) == 'pm':
                        sub_pm = child
                        break
                sub_name = pick_process_name(sub_pm) if sub_pm is not None else sub_uuid
                sub_file = sanitize_filename(sub_name) + '.md'
                rel = os.path.join(output_dir, sub_file).replace('\\', '/')
            except Exception:
                rel = os.path.join(output_dir, f"{sub_uuid}.md").replace('\\', '/')
        else:
            rel = os.path.join(output_dir, f"{sub_uuid}.md").replace('\\', '/')
        lines.append(f"  click N{gid} href \"{rel}\" \"Abrir subproceso\" _self")
