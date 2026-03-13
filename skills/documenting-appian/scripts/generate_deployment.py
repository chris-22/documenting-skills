#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Phase F — Generate deployment documentation and Import Customization File template.

Scans Connected Systems, constants (env-specific), patches.xml, and the UUID index
to produce docs/09-appian-deployment.md and docs/appian-import-customization-template.properties.
"""
import json
import os
import re
import sys
import glob
import xml.etree.ElementTree as ET

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from app_info import get_app_name
from cli_common import make_parser, validate_args, write_output, verbose
from xml_helpers import strip_ns, find_child, text

DEFAULT_APP_DIR = "application_files"
DEFAULT_INDEX = os.path.join("docs", "_uuid-index.json")
DEFAULT_OUT = os.path.join("docs", "09-appian-deployment.md")
ICF_OUT = os.path.join("docs", "appian-import-customization-template.properties")

NS_A = "http://www.appian.com/ae/types/2009"


def get_type_counts(index):
    """Count objects by top-level type."""
    counts = {}
    for info in index.values():
        t = info.get("type", "unknown").split("/")[0]
        counts[t] = counts.get(t, 0) + 1
    return counts


def find_connected_systems(app_dir):
    """Extract CS details for ICF template."""
    systems = []
    for f in sorted(glob.glob(os.path.join(app_dir, "connectedSystem", "*.xml"))):
        try:
            tree = ET.parse(f)
            root = tree.getroot()
        except Exception:
            continue
        for child in root:
            if strip_ns(child.tag) == "connectedSystem":
                name = text(find_child(child, "name"))
                uuid = text(find_child(child, "uuid"))
                base_url = ""
                auth_type = ""
                for elem in child.iter():
                    if strip_ns(elem.tag) == "baseUrl" and not base_url:
                        base_url = text(elem)
                    if strip_ns(elem.tag) == "authType" and not auth_type:
                        auth_type = text(elem)
                systems.append({"name": name, "uuid": uuid, "baseUrl": base_url, "authType": auth_type})
    return systems


def find_data_stores(app_dir, index):
    """Extract Data Store details: JNDI key, autoUpdateSchema, entity count."""
    stores = []
    for f in sorted(glob.glob(os.path.join(app_dir, "dataStore", "*.xml"))):
        try:
            tree = ET.parse(f)
            root = tree.getroot()
        except Exception:
            continue
        # The root is <dataStoreHaul>, child is <dataStore>
        for child in root:
            tag = strip_ns(child.tag)
            if tag in ("dataStore", "content"):
                name = text(find_child(child, "name"))
                uuid = text(find_child(child, "uuid"))
                ds_key = ""
                auto_update = ""
                entity_count = 0
                for elem in child.iter():
                    etag = strip_ns(elem.tag)
                    if etag == "dataSourceKey" and not ds_key:
                        ds_key = text(elem)
                    if etag == "autoUpdateSchema" and not auto_update:
                        auto_update = text(elem)
                    if etag == "entity":
                        entity_count += 1
                if not name:
                    fname = os.path.basename(f).replace(".xml", "")
                    entry = index.get(fname, {})
                    name = entry.get("name", fname)
                stores.append({
                    "name": name, "uuid": uuid, "file": f,
                    "jdbcKey": ds_key or "TODO(unknown)",
                    "autoUpdate": auto_update or "false",
                    "entityCount": entity_count,
                })
    return stores


def find_env_constants(index):
    """Find constants that are likely environment-specific (credentials, URLs, emails)."""
    env_keywords = ["email", "url", "token", "username", "password", "sender",
                    "host", "endpoint", "api_key", "jira", "testing"]
    env_constants = []
    for uuid, info in index.items():
        if info.get("type") != "content/constant":
            continue
        name = info.get("name", "").lower()
        if any(kw in name for kw in env_keywords):
            env_constants.append({"name": info["name"], "uuid": uuid, "file": info.get("file", "")})
    return sorted(env_constants, key=lambda x: x["name"])


def find_record_types(index):
    """Find record types for forceSync entries."""
    return [{"name": info["name"], "uuid": uuid}
            for uuid, info in index.items() if info.get("type") == "recordType"]


def parse_patches(app_dir, index):
    """Parse patches.xml if it exists."""
    patches_file = os.path.join(app_dir, "patches.xml")
    if not os.path.exists(patches_file):
        return []
    patches = []
    try:
        tree = ET.parse(patches_file)
        root = tree.getroot()
        for elem in root.iter():
            if strip_ns(elem.tag) == "uuid":
                uuid = text(elem)
                if uuid:
                    entry = index.get(uuid, {})
                    patches.append({
                        "uuid": uuid,
                        "name": entry.get("name", uuid),
                        "type": entry.get("type", "unknown"),
                    })
    except Exception:
        pass
    return patches


def generate_icf(connected_systems, env_constants, record_types):
    """Generate Import Customization File template."""
    lines = [
        "## ============================================================",
        f"## Import Customization File — {get_app_name()}",
        "## ============================================================",
        "## Generar un fichero por entorno (DESA, PRE, PRO).",
        "## Descomentar y rellenar las propiedades necesarias.",
        "## ============================================================",
        "",
    ]
    for cs in connected_systems:
        lines.append(f"## ---- Connected System: {cs['name']} ----")
        lines.append(f"## UUID: {cs['uuid']}")
        lines.append(f"## Tipo: {cs['authType'] or 'HTTP'}")
        if cs["baseUrl"]:
            lines.append(f"## Base URL actual: {cs['baseUrl']}")
        lines.append(f"#connectedSystem.{cs['uuid']}.baseUrl=")
        lines.append(f"#connectedSystem.{cs['uuid']}.username=")
        lines.append(f"#connectedSystem.{cs['uuid']}.password=")
        lines.append("")

    for const in env_constants:
        lines.append(f"## ---- Constante: {const['name']} ----")
        lines.append(f"## UUID: {const['uuid']}")
        lines.append(f"#content.{const['uuid']}.VALUE=")
        lines.append("")

    for rt in record_types:
        lines.append(f"## ---- Record Type: {rt['name']} (force sync after deploy) ----")
        lines.append(f"## UUID: {rt['uuid']}")
        lines.append(f"#recordType.{rt['uuid']}.forceSync=true")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = make_parser(
        "Generate deployment documentation and ICF template.",
        default_output=DEFAULT_OUT, needs_app_dir=True, needs_index=True,
        examples=[
            "python generate_deployment.py",
            "python generate_deployment.py --output custom-deploy.md",
            "python generate_deployment.py --dry-run",
        ],
    )
    args = parser.parse_args()
    validate_args(args, needs_app_dir=True, needs_index=True)

    with open(args.index, "r", encoding="utf-8") as f:
        index = json.load(f)
    verbose(args, f"Loaded index: {len(index)} entries from {args.index}")

    app_name = get_app_name()
    app_dir = args.app_dir
    type_counts = get_type_counts(index)
    connected_systems = find_connected_systems(app_dir)
    data_stores = find_data_stores(app_dir, index)
    env_constants = find_env_constants(index)
    record_types = find_record_types(index)
    patches = parse_patches(app_dir, index)
    verbose(args, f"Found {len(connected_systems)} CS, {len(data_stores)} DS, {len(env_constants)} env constants, {len(record_types)} RT, {len(patches)} patches")

    # Count total files
    total_files = 0
    for pattern in ["**/*.xml", "**/*.xsd"]:
        total_files += len(glob.glob(os.path.join(app_dir, pattern), recursive=True))

    lines = [f"# {app_name} — Despliegue (auto-generado)", ""]

    # Package contents
    lines.append("## Contenido del paquete")
    lines.append("")
    lines.append("| Tipo de objeto | Cantidad |")
    lines.append("|---------------|----------|")
    for t in sorted(type_counts.keys()):
        lines.append(f"| {t} | {type_counts[t]} |")
    lines.append(f"| **Total objetos** | **{len(index)}** |")
    lines.append(f"| **Total archivos** | **~{total_files}** |")
    lines.append("")

    # Import Customization requirements
    lines.append("## Requisitos de Import Customization")
    lines.append("")

    if connected_systems:
        lines.append("### Connected Systems")
        lines.append("")
        for cs in connected_systems:
            lines.append(f"- **{cs['name']}** (`{cs['uuid']}`)")
            lines.append(f"  - Base URL: `{cs['baseUrl']}`")
            lines.append(f"  - Auth: {cs['authType'] or 'TODO(unknown)'}")
            lines.append(f"  - ⚠️ Verificar `baseUrl`, `username`, `password` por entorno")
            lines.append("")

    # JDBC Data Sources
    if data_stores:
        jdbc_groups = {}
        for ds in data_stores:
            key = ds["jdbcKey"]
            jdbc_groups.setdefault(key, []).append(ds)

        lines.append("### JDBC Data Sources")
        lines.append("")
        lines.append("| JNDI Key | Data Stores | Auto-Update Schema | Entidades | Acción |")
        lines.append("|----------|-------------|-------------------|-----------|--------|")
        for key, dss in sorted(jdbc_groups.items()):
            ds_names = ", ".join(d["name"] for d in dss)
            total_entities = sum(d["entityCount"] for d in dss)
            auto_vals = set(d["autoUpdate"] for d in dss)
            auto_str = ", ".join(auto_vals)
            action = "Verificar JNDI en entorno destino"
            if "false" in auto_vals:
                action += "; tablas deben pre-existir (autoUpdate=false)"
            lines.append(f"| `{key}` | {ds_names} | {auto_str} | {total_entities} | {action} |")
        lines.append("")

        lines.append("### Data Stores (detalle)")
        lines.append("")
        lines.append("| Data Store | UUID | JNDI Key | Auto-Update | Entidades |")
        lines.append("|-----------|------|----------|-------------|-----------|")
        for ds in data_stores:
            uuid_short = ds["uuid"][:45] + "..." if len(ds["uuid"]) > 48 else ds["uuid"]
            lines.append(f"| {ds['name']} | `{uuid_short}` | `{ds['jdbcKey']}` | {ds['autoUpdate']} | {ds['entityCount']} |")
        lines.append("")

    if env_constants:
        lines.append("### Constantes de entorno")
        lines.append("")
        lines.append("| Constante | UUID |")
        lines.append("|-----------|------|")
        for const in env_constants:
            uuid_short = const["uuid"][:45] + "..." if len(const["uuid"]) > 48 else const["uuid"]
            lines.append(f"| {const['name']} | `{uuid_short}` |")
        lines.append("")

    if record_types:
        lines.append("### Record Types (forceSync)")
        lines.append("")
        for rt in record_types:
            lines.append(f"- **{rt['name']}** (`{rt['uuid']}`) — considerar `forceSync=true` tras despliegue")
        lines.append("")

    # Patches
    if patches:
        lines.append("## Parches (patches.xml)")
        lines.append("")
        lines.append("| Objeto | Tipo | UUID |")
        lines.append("|--------|------|------|")
        for p in patches:
            lines.append(f"| {p['name']} | {p['type']} | `{p['uuid'][:45]}` |")
        lines.append("")

    # Risks placeholder
    lines.append("## Riesgos de importación")
    lines.append("")
    lines.append("<!-- AGENT: enrich with object-specific risks per type (see deployment-risks.md in skill references) -->")
    lines.append("")

    # Checklist placeholder
    lines.append("## Checklist de despliegue")
    lines.append("")
    lines.append("### Pre-importación")
    lines.append("")
    lines.append("- [ ] Verificar dependencias externas disponibles en el entorno destino")
    lines.append("- [ ] Preparar fichero Import Customization (`appian-import-customization-template.properties`)")
    if connected_systems:
        lines.append("- [ ] Verificar conectividad a sistemas externos")
    lines.append("- [ ] Verificar JDBC data sources configurados")
    lines.append("")
    lines.append("### Importación")
    lines.append("")
    lines.append("- [ ] Importar paquete con fichero de personalización")
    lines.append("- [ ] Verificar que no hay errores en el log de importación")
    lines.append("- [ ] Verificar publicación de Process Models")
    lines.append("")
    lines.append("### Post-importación")
    lines.append("")
    lines.append("- [ ] Smoke test: navegación del site")
    lines.append("- [ ] Smoke test: flujo principal (crear/modificar)")
    if connected_systems:
        lines.append("- [ ] Smoke test: integración con sistemas externos")
    lines.append("- [ ] Verificar permisos por rol")
    lines.append("")

    lines.append("## Evidencias")
    lines.append("")
    lines.append(f"- `{app_dir}/` ({total_files} archivos)")
    lines.append(f"- `{args.index}`")
    lines.append("")

    write_output(args, "\n".join(lines), label=f"Deployment: {len(connected_systems)} CS, {len(data_stores)} DS, {len(env_constants)} env constants")

    # Generate ICF template
    verbose(args, f"Generating ICF template: {len(connected_systems)} CS entries, {len(env_constants)} constants, {len(record_types)} RT forceSync")
    icf_content = generate_icf(connected_systems, env_constants, record_types)
    icf_path = os.path.join(os.path.dirname(args.output), "appian-import-customization-template.properties")
    if not getattr(args, "dry_run", False):
        os.makedirs(os.path.dirname(icf_path) or ".", exist_ok=True)
        with open(icf_path, "w", encoding="utf-8") as f:
            f.write(icf_content)
        print(f"ICF template -> {icf_path}")
    else:
        print(f"[dry-run] Would write ICF template to {icf_path}")

    cs_count = len(connected_systems)
    const_count = len(env_constants)
    print(f"Deployment: {cs_count} CS, {const_count} env constants -> {args.output}")


if __name__ == "__main__":
    sys.exit(main() or 0)
