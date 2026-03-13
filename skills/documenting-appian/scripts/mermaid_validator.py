# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Mermaid syntax validator and auto-fixer.

Validates generated Mermaid flowchart code for common issues that cause
rendering failures in GitHub, VS Code, and Mermaid Live Editor.

Can be used standalone or imported by pm2mermaid.py and validate_docs.py.

Usage (standalone):
  python mermaid_validator.py docs/process-models/*.md
  python mermaid_validator.py docs/process-models/*.md --fix
"""
import os
import re
import sys
from typing import List, Tuple, Optional

# ── Reserved words that cannot be used as bare node IDs ──
RESERVED_IDS = {
    "end", "default", "graph", "subgraph", "classDef", "class",
    "click", "style", "linkStyle", "direction", "callback",
}

# ── Valid diagram types ──
VALID_DIAGRAM_TYPES = {
    "flowchart LR", "flowchart RL", "flowchart TD", "flowchart TB",
    "flowchart BT", "flowchart",
    "erDiagram", "sequenceDiagram", "stateDiagram-v2", "stateDiagram",
    "gantt", "pie", "gitGraph", "mindmap",
    "block-beta", "architecture-beta",
    "C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment",
}

# ── sequenceDiagram valid arrow types (official docs) ──
SEQ_ARROWS = {
    "->", "-->", "->>", "-->>" , "-x", "--x", "-)", "--)",
    "<<->>" , "<<-->>" ,
}

# ── erDiagram valid relationship operators ──
ER_REL_PATTERN = re.compile(
    r'^\s*"?[\w\s]+"?\s+'
    r'([|}{o])([|}{o])(-{1,2}|\.\.)([-|}{o])([|}{o])'
    r'\s+"?[\w\s]+"?\s*:\s*'
)
ER_ATTR_PATTERN = re.compile(r'^\s+\w+\s+\w+')

# ── C4 valid element keywords ──
C4_KEYWORDS = {
    "Person", "Person_Ext",
    "System", "System_Ext", "SystemDb", "SystemDb_Ext", "SystemQueue", "SystemQueue_Ext",
    "Container", "Container_Ext", "ContainerDb", "ContainerDb_Ext", "ContainerQueue", "ContainerQueue_Ext",
    "Component", "Component_Ext", "ComponentDb", "ComponentDb_Ext", "ComponentQueue", "ComponentQueue_Ext",
    "Boundary", "Enterprise_Boundary", "System_Boundary", "Container_Boundary",
    "Rel", "Rel_U", "Rel_Up", "Rel_D", "Rel_Down", "Rel_L", "Rel_Left", "Rel_R", "Rel_Right",
    "Rel_Back", "BiRel",
    "UpdateElementStyle", "UpdateRelStyle", "UpdateLayoutConfig",
    "Deployment_Node", "Node", "Node_L", "Node_R",
}

# ── block-beta valid block shapes ──
BLOCK_SHAPES = {"[":"]" , "(":")", "{":"}", "((":"))", "[[": "]]", ">": "]",
                "{{":"}}", "[\\/":"\\/]", "[/": "\\]", "[\\": "/]", "[/": "/]"}

# ── Valid Mermaid v11 shapes ──
VALID_SHAPES = {
    "rect", "rounded", "stadium", "subroutine", "cyl", "circle",
    "asymmetric", "rhombus", "diamond", "hex", "lean-r", "lean-l",
    "trap-b", "trap-t", "dbl-circ", "sm-circ", "fr-rect", "fr-circ",
    "braces", "bolt", "doc", "notch-rect", "lin-rect", "sm-rect",
    "tri", "fork", "win-pane", "f-circ", "lin-doc", "notch-pent",
    "cross-circ", "tag-doc", "tag-rect", "flag", "bow-rect",
    "div-rect", "odd", "brace-r", "brace-l", "hourglass",
}

# ── Valid architecture-beta icons ──
ARCH_ICONS = {"cloud", "database", "disk", "internet", "server"}

# Characters that break architecture-beta labels inside []
# Includes: hyphens, brackets, braces, pipes, angle brackets, AND non-ASCII
# (accented chars like ó, á, ñ, etc. cause "unexpected character" parse errors)
ARCH_LABEL_BAD_CHARS = re.compile(r'[\-\[\]{}|<>]')
ARCH_LABEL_NON_ASCII = re.compile(r'[^\x00-\x7F]')


class MermaidIssue:
    """Represents a single validation issue found in Mermaid code."""
    def __init__(self, line_num: int, severity: str, message: str,
                 original: str = "", fix: str = ""):
        self.line_num = line_num
        self.severity = severity  # "error" or "warning"
        self.message = message
        self.original = original
        self.fix = fix

    def __str__(self):
        prefix = "ERROR" if self.severity == "error" else "WARN"
        return f"L{self.line_num} [{prefix}] {self.message}"


def validate_mermaid_block(mermaid_code: str) -> Tuple[List[MermaidIssue], str]:
    """
    Validate a Mermaid code block and return issues + auto-fixed code.

    Returns:
        (issues, fixed_code) — list of issues found, and the auto-corrected code.
    """
    issues: List[MermaidIssue] = []
    lines = mermaid_code.split("\n")
    fixed_lines = list(lines)  # copy for fixing

    if not lines:
        issues.append(MermaidIssue(0, "error", "Bloque Mermaid vacío"))
        return issues, mermaid_code

    # 1. Check diagram type declaration (first non-empty line)
    first_line = ""
    first_line_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped:
            first_line = stripped
            first_line_idx = i
            break

    diagram_type = ""
    for dt in VALID_DIAGRAM_TYPES:
        if first_line.startswith(dt):
            diagram_type = dt
            break
    if not diagram_type:
        issues.append(MermaidIssue(first_line_idx + 1, "error",
                                   f"Tipo de diagrama no reconocido: `{first_line[:40]}`"))

    # Route to type-specific validators
    if diagram_type == "architecture-beta":
        arch_issues, arch_fixed = _validate_architecture_beta(lines)
        return arch_issues, "\n".join(arch_fixed)

    if diagram_type == "sequenceDiagram":
        seq_issues, seq_fixed = _validate_sequence_diagram(lines)
        return seq_issues, "\n".join(seq_fixed)

    if diagram_type in ("stateDiagram-v2", "stateDiagram"):
        st_issues, st_fixed = _validate_state_diagram(lines)
        return st_issues, "\n".join(st_fixed)

    if diagram_type == "erDiagram":
        er_issues, er_fixed = _validate_er_diagram(lines)
        return er_issues, "\n".join(er_fixed)

    if diagram_type == "block-beta":
        bb_issues, bb_fixed = _validate_block_beta(lines)
        return bb_issues, "\n".join(bb_fixed)

    if diagram_type.startswith("C4"):
        c4_issues, c4_fixed = _validate_c4_diagram(lines, diagram_type)
        return c4_issues, "\n".join(c4_fixed)

    if diagram_type == "pie":
        pie_issues, pie_fixed = _validate_pie_chart(lines)
        return pie_issues, "\n".join(pie_fixed)

    # 2. Line-by-line checks (flowchart and other types)
    in_subgraph = 0
    node_ids_defined = set()
    node_ids_referenced = set()

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        if not stripped or stripped.startswith("%%"):
            continue

        # Track subgraph nesting
        if re.match(r'^\s*subgraph\s', stripped):
            in_subgraph += 1
        if stripped == "end" and in_subgraph > 0:
            in_subgraph -= 1
            continue

        # 2a. Reserved word as bare node ID (NOT inside subgraph end)
        for reserved in RESERVED_IDS:
            # Match: "end -->" or "end[" or bare "end" as node definition
            pattern = rf'^{reserved}(?:\s*-->|\s*---|\s*-\.->|\s*==>|\s*\[|\s*\(|\s*\{{|\s*@)'
            if re.match(pattern, stripped, re.IGNORECASE) and reserved != "end":
                fix_line = stripped.replace(reserved, f"{reserved}_node", 1)
                issues.append(MermaidIssue(line_num, "error",
                    f"`{reserved}` es palabra reservada Mermaid; renombrar nodo",
                    original=stripped, fix=fix_line))
                fixed_lines[i] = line.replace(reserved, f"{reserved}_node", 1)

        # 2b. Unbalanced double quotes in labels
        # Count quotes outside of shape metadata @{ ... }
        check_str = re.sub(r'@\{[^}]*\}', '', stripped)
        quote_count = check_str.count('"')
        if quote_count % 2 != 0:
            issues.append(MermaidIssue(line_num, "error",
                f"Comillas dobles sin cerrar ({quote_count} comillas encontradas)",
                original=stripped))
            # Auto-fix: add closing quote before end of line
            if stripped.count('"') % 2 != 0:
                fixed_lines[i] = line.rstrip() + '"'

        # 2c. Invalid shape in @{ shape: xxx }
        shape_match = re.search(r'@\{\s*shape:\s*(\w[\w-]*)', stripped)
        if shape_match:
            shape = shape_match.group(1)
            if shape not in VALID_SHAPES:
                issues.append(MermaidIssue(line_num, "warning",
                    f"Shape `{shape}` no reconocido (puede fallar en versiones < v11.3)",
                    original=stripped))

        # 2d. Special characters in labels that break rendering
        label_match = re.search(r'label:\s*"([^"]*)"', stripped)
        if label_match:
            label = label_match.group(1)
            # Pipes break Markdown tables inside mermaid
            if "|" in label and "-->|" not in stripped:
                fix_label = label.replace("|", "&#124;")
                issues.append(MermaidIssue(line_num, "error",
                    f"Carácter `|` en label rompe la sintaxis (usar `&#124;`)",
                    original=stripped,
                    fix=stripped.replace(label, fix_label)))
                fixed_lines[i] = line.replace(label, fix_label)
            # Unescaped # can cause issues
            if "#" in label and "&#" not in label and "<br/>" not in label:
                # Only flag if it looks problematic (not HTML entities)
                pass  # # is generally OK in labels

        # 2e. Edge label with unescaped quotes: -->|"text"| vs -->|text|
        edge_label_match = re.findall(r'-->\|([^|]*)\|', stripped)
        for elabel in edge_label_match:
            if '"' in elabel and not elabel.startswith('"'):
                issues.append(MermaidIssue(line_num, "warning",
                    f"Label de arista con comillas mixtas: `{elabel}`",
                    original=stripped))

        # 2f. Collect node IDs for orphan detection
        # Node definition patterns: N0@{...}, N0["..."], N0("..."), bare N0
        node_def = re.match(r'^\s*(N?\w+)(?:@\{|[\["(\{])', stripped)
        if node_def:
            nid = node_def.group(1)
            if nid not in RESERVED_IDS and not nid.startswith("classDef"):
                node_ids_defined.add(nid)

        # Node references in edges: N0 --> N1, N0 ==> N1, etc.
        edge_nodes = re.findall(r'(N\w+)\s*(?:-->|==>|-\.->|---)', stripped)
        edge_targets = re.findall(r'(?:-->|==>|-\.->|---)\s*(?:\|[^|]*\|\s*)?(N\w+)', stripped)
        node_ids_referenced.update(edge_nodes)
        node_ids_referenced.update(edge_targets)

    # 3. Unclosed subgraphs
    if in_subgraph > 0:
        issues.append(MermaidIssue(len(lines), "error",
            f"{in_subgraph} subgraph(s) sin cerrar — falta `end`"))
        for _ in range(in_subgraph):
            fixed_lines.append("  end")

    # 4. Orphan nodes (defined but never in an edge)
    defined_only = node_ids_defined - node_ids_referenced
    # Filter out legend nodes
    defined_only = {n for n in defined_only if not n.startswith("L_")}
    if defined_only and len(defined_only) <= 5:
        for nid in sorted(defined_only):
            issues.append(MermaidIssue(0, "warning",
                f"Nodo `{nid}` definido pero no conectado a ninguna arista"))

    fixed_code = "\n".join(fixed_lines)
    return issues, fixed_code


def _validate_sequence_diagram(lines: List[str]) -> Tuple[List[MermaidIssue], List[str]]:
    """Validate sequenceDiagram syntax (official Mermaid docs).

    Key rules:
    - Must have at least one participant/actor or message
    - Messages follow: Actor Arrow Actor : Message text
    - Valid arrows: ->, -->, ->>, -->> , -x, --x, -), --)
    - Activation +/- only on message arrows (->>+ , -->>-)
    - loop/alt/opt/par/critical/break blocks must close with `end`
    - Note must specify `right of`, `left of`, or `over`
    - Unbalanced quotes in participant aliases
    """
    issues: List[MermaidIssue] = []
    fixed = list(lines)
    participants = set()
    has_message = False
    block_stack = []  # track loop/alt/opt/par/critical/break nesting

    BLOCK_OPENERS = {"loop", "alt", "opt", "par", "critical", "break", "rect"}

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        if not stripped or stripped.startswith("%%") or stripped == "sequenceDiagram":
            continue

        # Participant / actor declarations
        p_match = re.match(r'^(participant|actor)\s+(\S+)(?:\s+as\s+(.*))?$', stripped)
        if p_match:
            participants.add(p_match.group(2))
            alias = p_match.group(3)
            if alias:
                q = alias.count('"')
                if q % 2 != 0:
                    issues.append(MermaidIssue(line_num, "error",
                        f"Comillas sin cerrar en alias de participante",
                        original=stripped))
                    fixed[i] = line.rstrip() + '"'
            continue

        # Block openers
        for opener in BLOCK_OPENERS:
            if stripped.startswith(opener + " ") or stripped == opener:
                block_stack.append((opener, line_num))
                break

        # Block closers
        if stripped == "end":
            if block_stack:
                block_stack.pop()
            else:
                issues.append(MermaidIssue(line_num, "error",
                    "`end` sin bloque abierto correspondiente (loop/alt/opt/par/critical/break)"))
            continue

        # `else` inside alt — valid only inside alt
        if stripped.startswith("else"):
            if not block_stack or block_stack[-1][0] != "alt":
                issues.append(MermaidIssue(line_num, "warning",
                    "`else` fuera de un bloque `alt`"))
            continue

        # `and` inside par
        if stripped.startswith("and "):
            if not block_stack or block_stack[-1][0] != "par":
                issues.append(MermaidIssue(line_num, "warning",
                    "`and` fuera de un bloque `par`"))
            continue

        # Note validation
        if stripped.startswith("Note ") or stripped.startswith("note "):
            if not re.match(r'(?i)^note\s+(right of|left of|over)\s+', stripped):
                issues.append(MermaidIssue(line_num, "error",
                    "Note debe usar `right of`, `left of` o `over`: " + stripped[:60],
                    original=stripped))
            continue

        # Title / autonumber — valid directives
        if stripped.startswith("title") or stripped.startswith("autonumber"):
            continue

        # Message lines: Actor Arrow Actor : text
        msg_match = re.match(r'^(\S+?)\s*(-{1,2}>{0,2}\+?-?|--?[x)>]{1,2}\+?-?|<<-{1,2}>{0,2})\s*(\S+?)\s*:\s*(.+)?', stripped)
        if msg_match:
            has_message = True
            src, arrow, tgt = msg_match.group(1), msg_match.group(2), msg_match.group(3)
            # Strip activation markers for arrow validation
            clean_arrow = arrow.rstrip("+-")
            # Check if arrow is known (relaxed: allow valid patterns)
            known = any(clean_arrow == a or clean_arrow.startswith(a) for a in SEQ_ARROWS)
            if not known and "--" not in clean_arrow and "->" not in clean_arrow:
                issues.append(MermaidIssue(line_num, "warning",
                    f"Tipo de flecha posiblemente no válido: `{arrow}`",
                    original=stripped))
            continue

        # Catch-all: warn about unrecognized lines (skip classDef, style, box)
        if not stripped.startswith(("classDef", "class ", "style", "box", "end", "title")):
            # Could be a valid construct we don't parse — only warn
            pass

    # Check unclosed blocks
    for opener, ln in block_stack:
        issues.append(MermaidIssue(ln, "error",
            f"Bloque `{opener}` abierto en línea {ln} sin cerrar con `end`"))
        fixed.append("    end")

    if not has_message and not participants:
        issues.append(MermaidIssue(1, "warning",
            "sequenceDiagram sin participantes ni mensajes"))

    return issues, fixed


def _validate_state_diagram(lines: List[str]) -> Tuple[List[MermaidIssue], List[str]]:
    """Validate stateDiagram-v2 syntax (official Mermaid docs).

    Key rules:
    - Transitions use `-->` (not `->` or `==>`)
    - Start/end use `[*]` syntax
    - Composite states use `state Name { ... }` — braces must balance
    - `note right of` / `note left of` syntax
    - `direction` must be LR or TB
    - `<<choice>>` and `<<fork>>` / `<<join>>` are valid stereotypes
    - Unbalanced quotes in state descriptions
    """
    issues: List[MermaidIssue] = []
    fixed = list(lines)
    brace_depth = 0
    has_transition = False
    state_ids = set()

    VALID_DIRECTIONS = {"LR", "RL", "TB", "BT"}

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        if not stripped or stripped.startswith("%%"):
            continue
        if stripped.startswith("stateDiagram"):
            continue

        # Direction
        dir_match = re.match(r'^direction\s+(\w+)', stripped)
        if dir_match:
            d = dir_match.group(1)
            if d not in VALID_DIRECTIONS:
                issues.append(MermaidIssue(line_num, "error",
                    f"direction `{d}` no válido — usar: {', '.join(sorted(VALID_DIRECTIONS))}",
                    original=stripped))
            continue

        # Composite state opening: state "Name" as alias { or state Name {
        if re.match(r'^state\s+.*\{$', stripped):
            brace_depth += 1
            continue

        # Closing brace
        if stripped == "}":
            if brace_depth > 0:
                brace_depth -= 1
            else:
                issues.append(MermaidIssue(line_num, "error",
                    "`}` sin `state ... {` correspondiente"))
            continue

        # Transitions: [*] --> S1, S1 --> S2, S2 --> [*]
        trans_match = re.match(r'^(\[?\*?\]?\w*)\s*(-->)\s*(\[?\*?\]?\w*)', stripped)
        if trans_match:
            has_transition = True
            src, arrow, tgt = trans_match.groups()
            if src and src != "[*]":
                state_ids.add(src.split(":")[0].strip())
            if tgt and tgt != "[*]":
                state_ids.add(tgt.split(":")[0].strip())
            continue

        # Wrong arrow types used in state diagrams
        wrong_arrow = re.match(r'^\S+\s*(->|==>|-\.->)\s*\S+', stripped)
        if wrong_arrow and "-->" not in stripped:
            arrow = wrong_arrow.group(1)
            fix_line = stripped.replace(arrow, "-->", 1)
            issues.append(MermaidIssue(line_num, "error",
                f"stateDiagram usa `-->` para transiciones, no `{arrow}`",
                original=stripped, fix=fix_line))
            fixed[i] = line.replace(arrow, "-->", 1)
            has_transition = True
            continue

        # State description: S1 : Description text
        desc_match = re.match(r'^(\w+)\s*:\s*(.+)', stripped)
        if desc_match:
            sid = desc_match.group(1)
            state_ids.add(sid)
            desc = desc_match.group(2)
            if desc.count('"') % 2 != 0:
                issues.append(MermaidIssue(line_num, "error",
                    "Comillas sin cerrar en descripción de estado",
                    original=stripped))
                fixed[i] = line.rstrip() + '"'
            continue

        # Note
        if stripped.startswith("note ") or stripped.startswith("Note "):
            if not re.match(r'(?i)^note\s+(right|left)\s+of\s+', stripped):
                issues.append(MermaidIssue(line_num, "error",
                    "Note debe usar `right of` o `left of`: " + stripped[:60],
                    original=stripped))
            continue

        # end note
        if stripped == "end note":
            continue

        # classDef / class
        if stripped.startswith("classDef") or stripped.startswith("class "):
            continue

        # <<choice>>, <<fork>>, <<join>>
        if "<<" in stripped and ">>" in stripped:
            continue

    # Unclosed composite states
    if brace_depth > 0:
        issues.append(MermaidIssue(len(lines), "error",
            f"{brace_depth} estado(s) compuesto(s) sin cerrar — falta `}}`"))
        for _ in range(brace_depth):
            fixed.append("}")

    if not has_transition:
        issues.append(MermaidIssue(1, "warning",
            "stateDiagram sin transiciones (`-->`)"))

    return issues, fixed


def _validate_er_diagram(lines: List[str]) -> Tuple[List[MermaidIssue], List[str]]:
    """Validate erDiagram syntax (official Mermaid docs).

    Key rules:
    - Relationships: ENTITY1 ||--o{ ENTITY2 : "label"
      Valid cardinality markers: |o, o|, ||, }o, o{, }|, |{
      Identification: -- (identifying/solid) or .. (non-identifying/dashed)
    - Entity blocks: ENTITY { type name PK "comment" }
    - Attribute types should be valid identifiers
    - Relationship label is required after `:` if relationship is specified
    - Unbalanced braces in entity blocks
    """
    issues: List[MermaidIssue] = []
    fixed = list(lines)
    entities = set()
    in_entity_block = False
    entity_name = ""
    brace_depth = 0
    has_content = False

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        if not stripped or stripped.startswith("%%") or stripped == "erDiagram":
            continue

        has_content = True

        # Entity block opening: EntityName {
        entity_open = re.match(r'^(\w+)\s*\{$', stripped)
        if entity_open:
            entity_name = entity_open.group(1)
            entities.add(entity_name)
            in_entity_block = True
            brace_depth += 1
            continue

        # Entity block closing
        if stripped == "}":
            if brace_depth > 0:
                brace_depth -= 1
                in_entity_block = brace_depth > 0
            else:
                issues.append(MermaidIssue(line_num, "error",
                    "`}` sin entidad abierta correspondiente"))
            continue

        # Inside entity block: attribute definitions
        if in_entity_block:
            # Valid formats (official Mermaid docs):
            #   Type name
            #   Type name PK
            #   Type name FK
            #   Type name PK "comment"
            #   Type name "comment"
            attr_match = re.match(r'^\w+\s+\w+(\s+(PK|FK|UK))?(\s+"[^"]*")?$', stripped)
            if not attr_match and stripped not in ("}",):
                issues.append(MermaidIssue(line_num, "warning",
                    f"Atributo con formato posiblemente incorrecto: `{stripped[:50]}`"))
            # Check unbalanced quotes
            if stripped.count('"') % 2 != 0:
                issues.append(MermaidIssue(line_num, "error",
                    "Comillas sin cerrar en atributo de entidad",
                    original=stripped))
                fixed[i] = line.rstrip() + '"'
            continue

        # Relationship lines: Entity1 ||--o{ Entity2 : "label"
        # Relaxed match: two words separated by relationship operators
        rel_match = re.match(
            r'^"?(\w[\w\s]*)"?\s+'
            r'([|}{o]{2}[-.][-.][-|}{o]{2})'
            r'\s+"?(\w[\w\s]*)"?\s*:\s*"?([^"]*)"?',
            stripped
        )
        if rel_match:
            e1, rel, e2, label = rel_match.groups()
            entities.add(e1.strip())
            entities.add(e2.strip())
            if not label.strip():
                issues.append(MermaidIssue(line_num, "warning",
                    f"Relación sin label después de `:` — recomendado añadir descripción"))
            continue

        # Bare entity name (no relationship, no block)
        bare_entity = re.match(r'^(\w+)\s*$', stripped)
        if bare_entity:
            entities.add(bare_entity.group(1))
            continue

        # Direction
        if stripped.startswith("direction"):
            continue

        # classDef / class
        if stripped.startswith("classDef") or stripped.startswith("class "):
            continue

        # Unrecognized line
        issues.append(MermaidIssue(line_num, "warning",
            f"Línea no reconocida en erDiagram: `{stripped[:50]}`"))

    if brace_depth > 0:
        issues.append(MermaidIssue(len(lines), "error",
            f"{brace_depth} bloque(s) de entidad sin cerrar — falta `}}`"))
        for _ in range(brace_depth):
            fixed.append("}")

    if not has_content:
        issues.append(MermaidIssue(1, "warning", "erDiagram vacío"))

    return issues, fixed


def _validate_block_beta(lines: List[str]) -> Tuple[List[MermaidIssue], List[str]]:
    """Validate block-beta diagram syntax (official Mermaid docs).

    Key rules:
    - Must declare `columns N` (N >= 1) after `block-beta`
    - Block IDs: id["label"], id("label"), id{"label"}, etc.
    - Spanning: id["label"]:N (N = number of columns to span)
    - `classDef` and `class` for styling
    - Nested blocks with `block ... end` or `block:id ... end`
    - Space blocks: `space` or `space:N`
    - Unbalanced quotes in labels
    """
    issues: List[MermaidIssue] = []
    fixed = list(lines)
    has_columns = False
    block_depth = 0
    block_ids = set()

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        if not stripped or stripped.startswith("%%") or stripped == "block-beta":
            continue

        # columns declaration
        col_match = re.match(r'^columns\s+(\d+)', stripped)
        if col_match:
            has_columns = True
            n = int(col_match.group(1))
            if n < 1:
                issues.append(MermaidIssue(line_num, "error",
                    "columns debe ser >= 1"))
            continue

        # Nested block opening
        if re.match(r'^block\b', stripped):
            block_depth += 1
            continue

        # Block closing
        if stripped == "end":
            if block_depth > 0:
                block_depth -= 1
            else:
                issues.append(MermaidIssue(line_num, "error",
                    "`end` sin bloque `block` correspondiente"))
            continue

        # Space block
        if re.match(r'^space(:\d+)?$', stripped):
            continue

        # classDef / class
        if stripped.startswith("classDef") or stripped.startswith("class "):
            continue

        # style
        if stripped.startswith("style "):
            continue

        # Block definition: ID["label"] or ID["label"]:N or ID(("label"))
        block_def = re.match(r'^(\w+)\s*[\["({]', stripped)
        if block_def:
            bid = block_def.group(1)
            block_ids.add(bid)
            # Check unbalanced quotes
            if stripped.count('"') % 2 != 0:
                issues.append(MermaidIssue(line_num, "error",
                    "Comillas sin cerrar en label de bloque",
                    original=stripped))
                fixed[i] = line.rstrip() + '"'
            continue

        # Edge: ID --> ID or ID -- "text" --> ID
        if "-->" in stripped or "---" in stripped:
            continue

    if not has_columns:
        issues.append(MermaidIssue(1, "warning",
            "block-beta sin declaración `columns N` — se usará 1 columna por defecto"))

    if block_depth > 0:
        issues.append(MermaidIssue(len(lines), "error",
            f"{block_depth} bloque(s) `block` sin cerrar — falta `end`"))
        for _ in range(block_depth):
            fixed.append("    end")

    return issues, fixed


def _validate_c4_diagram(lines: List[str], diagram_type: str) -> Tuple[List[MermaidIssue], List[str]]:
    """Validate C4 diagram syntax (official Mermaid docs).

    Key rules:
    - Elements use function-call syntax: Person(alias, "label", "description")
    - All aliases used in Rel() must be defined as elements
    - Boundary blocks: Boundary(alias, "label") { ... }
    - Braces must balance for boundaries
    - title is optional but recommended
    - Unbalanced quotes / parentheses in element definitions
    """
    issues: List[MermaidIssue] = []
    fixed = list(lines)
    defined_aliases = set()
    rel_aliases = set()
    brace_depth = 0
    has_elements = False

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        if not stripped or stripped.startswith("%%") or stripped.startswith("C4"):
            # C4Context, C4Container, etc. on first line
            if stripped.startswith("C4"):
                continue
            continue

        # title directive
        if stripped.startswith("title"):
            continue

        # Opening brace (boundary block)
        if stripped.endswith("{"):
            brace_depth += 1

        # Closing brace
        if stripped == "}":
            if brace_depth > 0:
                brace_depth -= 1
            else:
                issues.append(MermaidIssue(line_num, "error",
                    "`}` sin Boundary/block abierto correspondiente"))
            continue

        # Element definitions: Keyword(alias, "label", "description")
        elem_match = re.match(r'^(\w+)\((\w+)\s*,', stripped)
        if elem_match:
            keyword = elem_match.group(1)
            alias = elem_match.group(2)

            # Check keyword is known
            if keyword not in C4_KEYWORDS:
                issues.append(MermaidIssue(line_num, "warning",
                    f"Keyword C4 `{keyword}` no reconocido — ¿typo?"))

            # Track alias (elements vs relationships)
            if keyword.startswith("Rel") or keyword == "BiRel":
                # Rel(from, to, "label") — extract from and to
                rel_args = re.findall(r'\((\w+)\s*,\s*(\w+)', stripped)
                if rel_args:
                    rel_aliases.add(rel_args[0][0])
                    rel_aliases.add(rel_args[0][1])
            elif keyword.startswith("Update"):
                pass  # styling, not elements
            else:
                defined_aliases.add(alias)
                has_elements = True

            # Check balanced quotes
            if stripped.count('"') % 2 != 0:
                issues.append(MermaidIssue(line_num, "error",
                    "Comillas sin cerrar en definición C4",
                    original=stripped))
                fixed[i] = line.rstrip() + '")'

            # Check balanced parentheses
            if stripped.count('(') != stripped.count(')'):
                issues.append(MermaidIssue(line_num, "error",
                    "Paréntesis sin cerrar en definición C4",
                    original=stripped))
                if stripped.count('(') > stripped.count(')'):
                    fixed[i] = line.rstrip() + ')'
            continue

        # Boundary opening with brace on same line
        boundary_match = re.match(r'^(\w+_?Boundary)\(', stripped)
        if boundary_match:
            # Already handled above via elem_match or here
            continue

    # Check Rel references point to defined aliases
    undefined = rel_aliases - defined_aliases
    if undefined:
        for alias in sorted(undefined):
            issues.append(MermaidIssue(0, "warning",
                f"Rel referencia alias `{alias}` que no está definido como elemento"))

    if brace_depth > 0:
        issues.append(MermaidIssue(len(lines), "error",
            f"{brace_depth} Boundary/block sin cerrar — falta `}}`"))
        for _ in range(brace_depth):
            fixed.append("}")

    if not has_elements:
        issues.append(MermaidIssue(1, "warning",
            f"{diagram_type} sin elementos definidos"))

    return issues, fixed


def _validate_pie_chart(lines: List[str]) -> Tuple[List[MermaidIssue], List[str]]:
    """Validate pie chart syntax (official Mermaid docs).

    Key rules:
    - Starts with `pie` optionally followed by `showData`
    - Optional `title` on next line
    - Data entries: "label" : value (value must be positive number)
    - Labels must be in double quotes
    - Values must be > 0 (Mermaid rejects negative/zero)
    """
    issues: List[MermaidIssue] = []
    fixed = list(lines)
    has_data = False
    total_value = 0.0

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        if not stripped or stripped.startswith("%%"):
            continue

        # First line: pie [showData]
        if stripped.startswith("pie"):
            continue

        # Title
        if stripped.startswith("title"):
            continue

        # Data entry: "label" : value
        data_match = re.match(r'^"([^"]*)"\s*:\s*([+-]?[\d.]+)', stripped)
        if data_match:
            label = data_match.group(1)
            try:
                value = float(data_match.group(2))
            except ValueError:
                issues.append(MermaidIssue(line_num, "error",
                    f"Valor no numérico: `{data_match.group(2)}`",
                    original=stripped))
                continue
            if value <= 0:
                issues.append(MermaidIssue(line_num, "error",
                    f"Valor debe ser > 0, encontrado: {value}",
                    original=stripped))
            if not label:
                issues.append(MermaidIssue(line_num, "warning",
                    "Label vacío en entrada de pie chart"))
            has_data = True
            total_value += value
            continue

        # Data without quotes (common error)
        no_quote_match = re.match(r'^(\w[\w\s]*)\s*:\s*([\d.]+)', stripped)
        if no_quote_match:
            label = no_quote_match.group(1)
            fix_line = f'    "{label}" : {no_quote_match.group(2)}'
            issues.append(MermaidIssue(line_num, "error",
                f"Label de pie chart debe estar entre comillas dobles",
                original=stripped, fix=fix_line))
            fixed[i] = fix_line
            has_data = True
            continue

        # Unrecognized line
        issues.append(MermaidIssue(line_num, "warning",
            f"Línea no reconocida en pie chart: `{stripped[:50]}`"))

    if not has_data:
        issues.append(MermaidIssue(1, "warning", "pie chart sin datos"))

    return issues, fixed


# Map accented characters to ASCII equivalents for auto-fix (dict form — no length bugs)
_ACCENT_MAP = str.maketrans({
    'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
    'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
    'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
    'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
    'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
    'ñ': 'n', 'ç': 'c',
    'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A',
    'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
    'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
    'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
    'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
    'Ñ': 'N', 'Ç': 'C',
})


def _strip_accents(text: str) -> str:
    """Replace accented characters with ASCII equivalents."""
    return text.translate(_ACCENT_MAP)


def _validate_architecture_beta(lines: List[str]) -> Tuple[List[MermaidIssue], List[str]]:
    """Validate architecture-beta specific syntax rules.

    Key rules:
    - Labels inside [] cannot contain hyphens (-), they break the parser
    - Labels inside [] cannot contain non-ASCII chars (ó, á, ñ, etc.) — parser rejects them
    - group/service declarations must have icon: name(icon)[label]
    - IDs must be simple alphanumeric + underscore (no hyphens)
    - Edges use format: id:SIDE --> SIDE:id  (SIDE = T/B/L/R)
    """
    issues: List[MermaidIssue] = []
    fixed = list(lines)
    defined_ids = set()
    edge_ids = set()

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        if not stripped or stripped.startswith("%%") or stripped == "architecture-beta":
            continue

        # Check group declarations: group id(icon)[label] or group id[label]
        group_match = re.match(r'^group\s+(\w+)(?:\((\w+)\))?\[([^\]]*)\]', stripped)
        if group_match:
            gid, icon, label = group_match.groups()
            defined_ids.add(gid)
            if not icon:
                fix_line = stripped.replace(f"group {gid}[", f"group {gid}(server)[", 1)
                issues.append(MermaidIssue(line_num, "error",
                    f"group `{gid}` sin icono — se requiere (cloud|database|disk|internet|server)",
                    original=stripped, fix=fix_line))
                fixed[i] = line.replace(f"group {gid}[", f"group {gid}(server)[", 1)
            elif icon not in ARCH_ICONS:
                issues.append(MermaidIssue(line_num, "warning",
                    f"Icono `{icon}` no es estándar — usar: {', '.join(sorted(ARCH_ICONS))}",
                    original=stripped))
            # Check label for bad characters (hyphens, brackets, etc.)
            if ARCH_LABEL_BAD_CHARS.search(label):
                bad = set(ARCH_LABEL_BAD_CHARS.findall(label))
                fix_label = label
                for ch in bad:
                    fix_label = fix_label.replace(ch, " ")
                fix_label = re.sub(r'\s+', ' ', fix_label).strip()
                fix_line = stripped.replace(f"[{label}]", f"[{fix_label}]")
                issues.append(MermaidIssue(line_num, "error",
                    f"Label de group contiene caracteres no válidos {bad} — rompe el parser",
                    original=stripped, fix=fix_line))
                fixed[i] = line.replace(f"[{label}]", f"[{fix_label}]")
            # Check label for non-ASCII chars (accents like ó, á, ñ)
            if ARCH_LABEL_NON_ASCII.search(label):
                bad_chars = set(ARCH_LABEL_NON_ASCII.findall(label))
                fix_label = _strip_accents(label)
                fix_line = fixed[i].replace(f"[{label}]", f"[{fix_label}]")
                issues.append(MermaidIssue(line_num, "error",
                    f"Label de group contiene caracteres no-ASCII {bad_chars} — architecture-beta no los soporta",
                    original=stripped, fix=fix_line))
                fixed[i] = fixed[i].replace(f"[{label}]", f"[{fix_label}]")
            continue

        # Check service declarations: service id(icon)[label] in group
        svc_match = re.match(r'^service\s+(\w+)(?:\((\w+)\))?\[([^\]]*)\]', stripped)
        if svc_match:
            sid, icon, label = svc_match.groups()
            defined_ids.add(sid)
            if not icon:
                fix_line = stripped.replace(f"service {sid}[", f"service {sid}(server)[", 1)
                issues.append(MermaidIssue(line_num, "error",
                    f"service `{sid}` sin icono — se requiere (cloud|database|disk|internet|server)",
                    original=stripped, fix=fix_line))
                fixed[i] = line.replace(f"service {sid}[", f"service {sid}(server)[", 1)
            elif icon not in ARCH_ICONS:
                issues.append(MermaidIssue(line_num, "warning",
                    f"Icono `{icon}` no es estándar — usar: {', '.join(sorted(ARCH_ICONS))}",
                    original=stripped))
            # Check label for bad characters (hyphens, brackets, etc.)
            if ARCH_LABEL_BAD_CHARS.search(label):
                bad = set(ARCH_LABEL_BAD_CHARS.findall(label))
                fix_label = label
                for ch in bad:
                    fix_label = fix_label.replace(ch, " ")
                fix_label = re.sub(r'\s+', ' ', fix_label).strip()
                fix_line = stripped.replace(f"[{label}]", f"[{fix_label}]")
                issues.append(MermaidIssue(line_num, "error",
                    f"Label de service contiene caracteres no válidos {bad} — rompe el parser",
                    original=stripped, fix=fix_line))
                fixed[i] = line.replace(f"[{label}]", f"[{fix_label}]")
            # Check label for non-ASCII chars (accents like ó, á, ñ)
            if ARCH_LABEL_NON_ASCII.search(label):
                bad_chars = set(ARCH_LABEL_NON_ASCII.findall(label))
                fix_label = _strip_accents(label)
                fix_line = fixed[i].replace(f"[{label}]", f"[{fix_label}]")
                issues.append(MermaidIssue(line_num, "error",
                    f"Label de service contiene caracteres no-ASCII {bad_chars} — architecture-beta no los soporta",
                    original=stripped, fix=fix_line))
                fixed[i] = fixed[i].replace(f"[{label}]", f"[{fix_label}]")
            continue

        # Check junction: junction id in group
        junc_match = re.match(r'^junction\s+(\w+)', stripped)
        if junc_match:
            defined_ids.add(junc_match.group(1))
            continue

        # Check edges: id:SIDE --> SIDE:id
        edge_match = re.match(r'^(\w+):([TBLR])\s*-->\s*([TBLR]):(\w+)', stripped)
        if edge_match:
            src, _, _, tgt = edge_match.groups()
            edge_ids.add(src)
            edge_ids.add(tgt)
            if src not in defined_ids:
                issues.append(MermaidIssue(line_num, "warning",
                    f"Edge referencia `{src}` que no está definido como service/group",
                    original=stripped))
            if tgt not in defined_ids:
                issues.append(MermaidIssue(line_num, "warning",
                    f"Edge referencia `{tgt}` que no está definido como service/group",
                    original=stripped))
            continue

        # Check for malformed lines (not group, service, junction, edge, or empty)
        if not stripped.startswith(("group", "service", "junction", "%%")):
            # Could be an edge without proper format
            if "-->" in stripped:
                issues.append(MermaidIssue(line_num, "warning",
                    f"Edge con formato posiblemente incorrecto: `{stripped[:60]}`",
                    original=stripped))

    return issues, fixed


def validate_markdown_file(filepath: str) -> Tuple[List[Tuple[int, List[MermaidIssue]]], str]:
    """
    Validate all Mermaid blocks in a Markdown file.

    Returns:
        (block_issues, fixed_content)
        - block_issues: list of (block_index, issues) tuples
        - fixed_content: the markdown with auto-fixed mermaid blocks
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    all_issues = []
    # Find all mermaid blocks with their positions
    pattern = re.compile(r'(```mermaid\n)(.*?)(```)', re.DOTALL)
    fixed_content = content

    offset = 0
    for block_idx, match in enumerate(pattern.finditer(content)):
        mermaid_code = match.group(2)
        issues, fixed_code = validate_mermaid_block(mermaid_code)

        if issues:
            all_issues.append((block_idx + 1, issues))

        if fixed_code != mermaid_code:
            # Replace in the fixed content
            start = match.start(2) + offset
            end = match.end(2) + offset
            fixed_content = fixed_content[:start] + fixed_code + fixed_content[end:]
            offset += len(fixed_code) - len(mermaid_code)

    return all_issues, fixed_content


def validate_and_fix_file(filepath: str, dry_run: bool = False) -> List[Tuple[int, List[MermaidIssue]]]:
    """
    Validate a Markdown file and optionally fix issues in-place.

    Returns list of (block_index, issues) tuples.
    """
    block_issues, fixed_content = validate_markdown_file(filepath)

    if not block_issues:
        return []

    has_fixes = any(
        issue.fix or issue.message.startswith("Comillas") or "subgraph" in issue.message
        for _, issues in block_issues
        for issue in issues
    )

    if has_fixes and not dry_run:
        with open(filepath, "r", encoding="utf-8") as f:
            original = f.read()
        if fixed_content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fixed_content)

    return block_issues


# ── CLI entry point ──────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Validate Mermaid syntax in Markdown files and optionally fix issues.",
        epilog="Examples:\n"
               "  python mermaid_validator.py docs/process-models/*.md\n"
               "  python mermaid_validator.py docs/*.md --fix\n"
               "  python mermaid_validator.py docs/appian-architecture.md --fix --verbose\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("files", nargs="+", help="Markdown files to validate")
    parser.add_argument("--fix", action="store_true",
                        help="Auto-fix issues in-place where possible")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show details of each issue")
    args = parser.parse_args()

    # Expand globs on Windows
    import glob as _glob
    files = []
    for pattern in args.files:
        expanded = _glob.glob(pattern)
        files.extend(expanded if expanded else [pattern])

    total_errors = 0
    total_warnings = 0
    total_fixed = 0
    files_with_issues = 0

    for filepath in sorted(files):
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}", file=sys.stderr)
            continue

        block_issues = validate_and_fix_file(filepath, dry_run=not args.fix)
        if not block_issues:
            if args.verbose:
                print(f"✅ {filepath}")
            continue

        files_with_issues += 1
        fname = os.path.basename(filepath)

        for block_idx, issues in block_issues:
            errors = [i for i in issues if i.severity == "error"]
            warnings = [i for i in issues if i.severity == "warning"]
            total_errors += len(errors)
            total_warnings += len(warnings)

            if args.fix:
                fixed = [i for i in issues if i.fix]
                total_fixed += len(fixed)

            print(f"{'🔧' if args.fix else '❌'} {fname} block {block_idx}: "
                  f"{len(errors)} error(s), {len(warnings)} warning(s)")

            if args.verbose:
                for issue in issues:
                    marker = "  🔧" if issue.fix and args.fix else "  ⚠️" if issue.severity == "warning" else "  ❌"
                    print(f"{marker} {issue}")
                    if issue.fix and args.verbose:
                        print(f"     → fix: {issue.fix[:80]}")

    # Summary
    print(f"\n{'='*50}")
    print(f"Archivos analizados: {len(files)}")
    print(f"Archivos con problemas: {files_with_issues}")
    print(f"Errores: {total_errors}")
    print(f"Warnings: {total_warnings}")
    if args.fix:
        print(f"Auto-corregidos: {total_fixed}")
    if total_errors > 0 and not args.fix:
        print(f"\nUsa --fix para auto-corregir los problemas detectados.")
    sys.exit(1 if total_errors > 0 and not args.fix else 0)


if __name__ == "__main__":
    main()
