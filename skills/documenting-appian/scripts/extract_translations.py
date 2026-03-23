#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Phase F — Extract translation strings and sets from Appian export.

Reads translationString/*.xml and translationSet/*.xml (relative to app root)
and produces docs/10-appian-i18n.md with a table of all strings and their values per locale.
"""
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
DEFAULT_OUT = os.path.join("docs", "10-appian-i18n.md")


def parse_translation_set(filepath):
    """Parse a translationSet XML."""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception:
        return None

    for child in root:
        tag = strip_ns(child.tag)
        if tag == "translationSet":
            uuid = child.attrib.get("{http://www.appian.com/ae/types/2009}uuid", "")
            name = child.attrib.get("name", "")
            desc = ""
            # Locales: multiple <a:enabledLocales> elements, each with <a:localeLanguageTag>
            locales = []
            for el in list(child):
                el_tag = strip_ns(el.tag)
                if el_tag == "enabledLocales":
                    lang_tag_el = find_child(el, "localeLanguageTag")
                    if lang_tag_el is not None:
                        locales.append(text(lang_tag_el))
                elif el_tag == "defaultLocale":
                    pass  # Already captured in enabledLocales
            return {"uuid": uuid, "name": name, "description": desc, "locales": locales, "file": filepath}
    return None


def parse_translation_string(filepath):
    """Parse a translationString XML and extract UUID + values per locale.

    Appian structure:
      <translationString a:uuid="...">
        <a:translationSetUuid>...</a:translationSetUuid>
        <translationTexts>
          <translatedText>
            <a:translationLocale><a:localeLanguageTag>en-GB</a:localeLanguageTag></a:translationLocale>
            <a:translatedText>English text</a:translatedText>
          </translatedText>
          ...
        </translationTexts>
      </translationString>
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception:
        return None

    for child in root:
        tag = strip_ns(child.tag)
        if tag == "translationString":
            uuid = child.attrib.get("{http://www.appian.com/ae/types/2009}uuid", "")

            values = {}
            # Find translationTexts > translatedText elements
            for elem in child.iter():
                if strip_ns(elem.tag) == "translatedText" and strip_ns(elem.tag) != "translationTexts":
                    locale_str = ""
                    translated = ""
                    for sub in elem.iter():
                        sub_tag = strip_ns(sub.tag)
                        if sub_tag == "localeLanguageTag":
                            locale_str = text(sub)
                        elif sub_tag == "translatedText" and sub != elem:
                            translated = text(sub)
                    if locale_str and translated:
                        values[locale_str] = translated

            # Use UUID as key (translation strings don't have a "key" field — they are referenced by UUID)
            # Try to derive a human-readable key from the first English value
            key = uuid
            en_val = values.get("en-GB", values.get("en", ""))
            if en_val and len(en_val) < 60:
                key = en_val

            return {"uuid": uuid, "key": key, "values": values, "file": filepath}
    return None


def main():
    parser = make_parser(
        "Extract translation strings and sets from Appian export.",
        default_output=DEFAULT_OUT, needs_app_dir=True, needs_index=False,
        examples=[
            "python extract_translations.py",
            "python extract_translations.py --output custom-i18n.md",
            "python extract_translations.py --dry-run",
        ],
    )
    args = parser.parse_args()
    validate_args(args)

    # Parse translation sets
    set_files = sorted(glob.glob(os.path.join(args.app_dir, "translationSet", "*.xml")))
    verbose(args, f"Found {len(set_files)} translation set files")
    sets = []
    for f in set_files:
        result = parse_translation_set(f)
        if result:
            sets.append(result)

    # Parse translation strings
    str_files = sorted(glob.glob(os.path.join(args.app_dir, "translationString", "*.xml")))
    verbose(args, f"Found {len(str_files)} translation string files")
    strings = []
    for f in str_files:
        result = parse_translation_string(f)
        if result:
            strings.append(result)
    verbose(args, f"Parsed {len(sets)} sets, {len(strings)} strings")

    # Collect all locales
    all_locales = set()
    for s in strings:
        all_locales.update(s["values"].keys())
    for ts in sets:
        all_locales.update(ts.get("locales", []))
    locale_list = sorted(all_locales)

    lines = [
        f"# {get_app_name()} — Cadenas de traducción (auto-generado)",
        "",
    ]

    # Translation Sets
    lines.append("## Translation Sets")
    lines.append("")
    if sets:
        for ts in sets:
            lines.append(f"- **{ts['name']}** (`{ts['uuid']}`)")
            if ts["description"]:
                lines.append(f"  - Descripción: {ts['description']}")
            lines.append(f"  - Locales: {', '.join(ts['locales']) if ts['locales'] else 'N/A'}")
    else:
        lines.append("*(No se encontraron translation sets)*")
    lines.append("")

    # Locales summary
    lines.append("## Locales detectados")
    lines.append("")
    for loc in locale_list:
        count = sum(1 for s in strings if loc in s["values"] and s["values"][loc])
        lines.append(f"- **`{loc}`**: {count} cadenas con valor")
    lines.append("")

    # Translation Strings table
    lines.append(f"## Translation Strings ({len(strings)})")
    lines.append("")

    if strings:
        # Build header
        header = "| Clave |"
        separator = "|-------|"
        for loc in locale_list:
            header += f" {loc} |"
            separator += "------|"
        lines.append(header)
        lines.append(separator)

        for s in sorted(strings, key=lambda x: x["key"]):
            row = f"| `{s['key']}` |"
            for loc in locale_list:
                val = s["values"].get(loc, "")
                # Truncate long values
                if len(val) > 50:
                    val = val[:47] + "..."
                # Escape pipe characters
                val = val.replace("|", "\\|")
                row += f" {val} |"
            lines.append(row)
    else:
        lines.append("*(No se encontraron translation strings)*")
    lines.append("")

    lines.append("## Evidencias")
    lines.append("")
    lines.append(f"- `{args.app_dir}/translationSet/` ({len(sets)} archivos)")
    lines.append(f"- `{args.app_dir}/translationString/` ({len(strings)} archivos)")
    lines.append("")

    write_output(args, "\n".join(lines), label=f"Translations: {len(sets)} sets, {len(strings)} strings, {len(locale_list)} locales")

    print(f"Translations: {len(sets)} sets, {len(strings)} strings, {len(locale_list)} locales -> {args.output}")


if __name__ == "__main__":
    sys.exit(main() or 0)
