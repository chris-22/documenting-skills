#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Phase D — Parse all CDT XSD files and generate field-level documentation.

Reads datatype/*.xsd (relative to app root) and produces docs/06-appian-data.md with:
- CDT name, description, DB table/schema
- Field table: name, XSD type, nullable, JPA annotations (@Id, @Column, @OneToMany)
- Relationships between CDTs (fields referencing other CDT types)
"""
import os
import re
import sys
import glob
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from collections import defaultdict

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from app_info import get_app_name
from cli_common import make_parser, validate_args, write_output, verbose

DEFAULT_APP_DIR = "datatype"
DEFAULT_OUT = os.path.join("docs", "06-appian-data.md")

NS_XSD = "http://www.w3.org/2001/XMLSchema"


def decode_filename(filepath):
    """Decode URL-encoded XSD filename to get CDT name and namespace."""
    fname = os.path.basename(filepath)
    decoded = unquote(fname).replace(".xsd", "")
    if "}" in decoded:
        name = decoded.split("}")[-1]
        namespace = decoded.split("}")[0].lstrip("{")
    else:
        name = decoded
        namespace = ""
    return name, namespace


def parse_xsd(filepath):
    """Parse a CDT XSD and return structured info."""
    name, namespace = decode_filename(filepath)
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception:
        return {"name": name, "namespace": namespace, "file": filepath,
                "description": "", "table": "", "schema": "", "fields": [], "jpa_raw": ""}

    # Find complexType
    ct = root.find(f"{{{NS_XSD}}}complexType")
    if ct is None:
        return {"name": name, "namespace": namespace, "file": filepath,
                "description": "", "table": "", "schema": "", "fields": [], "jpa_raw": ""}

    # Extract @Table annotation
    table_name = ""
    schema_name = ""
    description = ""
    jpa_raw = ""

    annotation = ct.find(f"{{{NS_XSD}}}annotation")
    if annotation is not None:
        for appinfo in annotation.findall(f"{{{NS_XSD}}}appinfo"):
            source = appinfo.attrib.get("source", "")
            if source == "appian.jpa":
                jpa_raw = (appinfo.text or "").strip()
                # Parse @Table(name="...", schema="...")
                m = re.search(r'@Table\(([^)]+)\)', jpa_raw)
                if m:
                    params = m.group(1)
                    nm = re.search(r'name\s*=\s*"([^"]*)"', params)
                    sm = re.search(r'schema\s*=\s*"([^"]*)"', params)
                    table_name = nm.group(1) if nm else ""
                    schema_name = sm.group(1) if sm else ""
        doc_el = annotation.find(f"{{{NS_XSD}}}documentation")
        if doc_el is not None:
            description = (doc_el.text or "").strip()

    # Extract fields from sequence
    fields = []
    seq = ct.find(f"{{{NS_XSD}}}sequence")
    if seq is not None:
        for elem in seq.findall(f"{{{NS_XSD}}}element"):
            field_name = elem.attrib.get("name", "")
            field_type = elem.attrib.get("type", "")
            nullable = elem.attrib.get("nillable", "false")
            max_occurs = elem.attrib.get("maxOccurs", "1")

            # Clean up type
            if field_type.startswith("xsd:"):
                field_type = field_type[4:]
            elif field_type.startswith(f"{{{NS_XSD}}}"):
                field_type = field_type.split("}")[-1]

            # Check for JPA annotations on the field
            field_jpa = ""
            is_pk = False
            is_fk = False
            column_info = ""
            fa = elem.find(f"{{{NS_XSD}}}annotation")
            if fa is not None:
                for fai in fa.findall(f"{{{NS_XSD}}}appinfo"):
                    if fai.attrib.get("source") == "appian.jpa":
                        field_jpa = (fai.text or "").strip()
                        if "@Id" in field_jpa:
                            is_pk = True
                        if "@OneToMany" in field_jpa or "@ManyToOne" in field_jpa:
                            is_fk = True
                        # Extract @Column details
                        cm = re.search(r'@Column\(([^)]+)\)', field_jpa)
                        if cm:
                            column_info = cm.group(1)

            # Detect CDT references (type contains namespace prefix)
            is_cdt_ref = ":" in field_type and not field_type.startswith("xsd")
            if is_cdt_ref:
                # Extract CDT name from namespace:type
                ref_cdt = field_type.split(":")[-1] if ":" in field_type else field_type

            fields.append({
                "name": field_name,
                "type": field_type,
                "nullable": nullable == "true",
                "maxOccurs": max_occurs,
                "isPK": is_pk,
                "isFK": is_fk,
                "isCdtRef": is_cdt_ref,
                "cdtRef": field_type.split(":")[-1] if is_cdt_ref else "",
                "columnInfo": column_info,
                "jpa": field_jpa,
            })

    return {
        "name": name,
        "namespace": namespace,
        "file": filepath,
        "description": description,
        "table": table_name,
        "schema": schema_name,
        "fields": fields,
        "jpa_raw": jpa_raw,
    }


def main():
    parser = make_parser(
        "Parse CDT XSD files and generate field-level documentation.",
        default_output=DEFAULT_OUT, needs_app_dir=True, needs_index=False,
        examples=[
            "python parse_cdts.py",
            "python parse_cdts.py --app-dir datatype",
            "python parse_cdts.py --dry-run",
        ],
    )
    args = parser.parse_args()
    validate_args(args)
    xsd_dir = os.path.join(args.app_dir, "datatype") if args.app_dir != DEFAULT_APP_DIR else DEFAULT_APP_DIR
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    xsd_files = sorted(glob.glob(os.path.join(xsd_dir, "*.xsd")))
    verbose(args, f"Found {len(xsd_files)} XSD files in {xsd_dir}")

    cdts = [parse_xsd(f) for f in xsd_files]
    verbose(args, f"Parsed {len(cdts)} CDTs, {sum(len(c['fields']) for c in cdts)} fields total")

    # Collect schemas and tables
    schemas = set()
    relationships = []

    lines = [
        f"# {get_app_name()} — CDTs: detalle de campos (auto-generado)",
        "",
        f"Total CDTs: **{len(cdts)}**",
        "",
    ]

    # Summary table
    lines.append("## Resumen de CDTs")
    lines.append("")
    lines.append("| CDT | Tabla BD | Schema | Campos | PK | Descripción |")
    lines.append("|-----|---------|--------|--------|-----|-------------|")
    for cdt in cdts:
        pk_fields = [f["name"] for f in cdt["fields"] if f["isPK"]]
        pk_str = ", ".join(pk_fields) if pk_fields else "—"
        desc = cdt["description"][:60] + "..." if len(cdt["description"]) > 60 else cdt["description"]
        lines.append(
            f"| {cdt['name']} | `{cdt['table']}` | `{cdt['schema']}` | "
            f"{len(cdt['fields'])} | {pk_str} | {desc} |"
        )
        if cdt["schema"]:
            schemas.add(cdt["schema"])
    lines.append("")

    # Schema summary
    lines.append("## Esquemas de BD")
    lines.append("")
    for s in sorted(schemas):
        count = sum(1 for c in cdts if c["schema"] == s)
        lines.append(f"- **`{s}`**: {count} CDTs")
    no_schema = sum(1 for c in cdts if not c["schema"])
    if no_schema:
        lines.append(f"- *(sin esquema)*: {no_schema} CDTs")
    lines.append("")

    # Detail per CDT
    lines.append("## Detalle por CDT")
    lines.append("")
    for cdt in cdts:
        lines.append(f"### {cdt['name']}")
        lines.append("")
        if cdt["description"]:
            lines.append(f"> {cdt['description']}")
            lines.append("")
        meta = []
        if cdt["table"]:
            meta.append(f"**Tabla**: `{cdt['table']}`")
        if cdt["schema"]:
            meta.append(f"**Schema**: `{cdt['schema']}`")
        meta.append(f"**Campos**: {len(cdt['fields'])}")
        lines.append(" | ".join(meta))
        lines.append("")

        if cdt["fields"]:
            lines.append("| Campo | Tipo | Nullable | PK | JPA |")
            lines.append("|-------|------|----------|-----|-----|")
            for f in cdt["fields"]:
                pk = "PK" if f["isPK"] else ""
                fk = "FK→" + f["cdtRef"] if f["isCdtRef"] else ""
                jpa_short = f["columnInfo"] or f["jpa"][:40] if f["jpa"] else ""
                type_str = f["type"]
                if f["maxOccurs"] != "1":
                    type_str += "[]"
                nullable = "Si" if f["nullable"] else "No"
                label = pk or fk or ""
                lines.append(f"| {f['name']} | `{type_str}` | {nullable} | {label} | {jpa_short} |")
            lines.append("")

            # Collect relationships
            for f in cdt["fields"]:
                if f["isCdtRef"]:
                    relationships.append((cdt["name"], f["cdtRef"], f["name"]))

    # Relationships summary
    if relationships:
        lines.append("## Relaciones entre CDTs")
        lines.append("")
        lines.append("| CDT origen | Campo | CDT destino |")
        lines.append("|-----------|-------|-------------|")
        for src, dst, field in relationships:
            lines.append(f"| {src} | {field} | {dst} |")
        lines.append("")

    lines.append("## Evidencias")
    lines.append("")
    lines.append(f"- `{xsd_dir}/*.xsd` ({len(cdts)} archivos)")
    lines.append("")

    write_output(args, "\n".join(lines), label=f"CDT detail: {len(cdts)} CDTs, {sum(len(c['fields']) for c in cdts)} fields")

    print(f"CDT detail: {len(cdts)} CDTs, {sum(len(c['fields']) for c in cdts)} fields -> {args.output}")


if __name__ == "__main__":
    sys.exit(main() or 0)
