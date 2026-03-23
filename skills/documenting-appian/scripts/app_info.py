#!/usr/bin/env python3
"""
Shared utility — Detect Appian application name and metadata from the export.

Reads application/*.xml (relative to app root) to extract the app name, UUID, and
description. Used by all automation scripts to generate application-agnostic
document titles.

The application manifest XML structure (verified from real exports):
  <applicationHaul>
    <application>
      <name>APP_NAME</name>
      <uuid>UUID</uuid>
      <description>...</description>
    </application>
  </applicationHaul>
"""
import os
import glob
import xml.etree.ElementTree as ET

APP_DIR = "."


def _strip_ns(tag):
    return tag.split("}", 1)[-1] if "}" in tag else tag


def get_app_info(app_dir=APP_DIR):
    """Return dict with application name, uuid, and description.

    Scans application/*.xml (relative to app_dir) for the main manifest.
    Falls back to directory name if no manifest is found.

    Returns:
        {"name": str, "uuid": str, "description": str}
    """
    pattern = os.path.join(app_dir, "application", "*.xml")
    for filepath in glob.glob(pattern):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            for child in root:
                tag = _strip_ns(child.tag)
                if tag == "application":
                    name_el = None
                    uuid_el = None
                    desc_el = None
                    for sub in list(child):
                        sub_tag = _strip_ns(sub.tag)
                        if sub_tag == "name":
                            name_el = sub
                        elif sub_tag == "uuid":
                            uuid_el = sub
                        elif sub_tag == "description":
                            desc_el = sub
                    name = (name_el.text or "").strip() if name_el is not None else ""
                    uuid = (uuid_el.text or "").strip() if uuid_el is not None else ""
                    desc = (desc_el.text or "").strip() if desc_el is not None else ""
                    if name:
                        return {"name": name, "uuid": uuid, "description": desc}
        except Exception:
            continue

    # Fallback: use parent directory name
    abs_path = os.path.abspath(app_dir)
    parent = os.path.basename(os.path.dirname(abs_path))
    return {"name": parent or "Appian Application", "uuid": "", "description": ""}


def get_app_name(app_dir=APP_DIR):
    """Convenience function — return just the application name string."""
    return get_app_info(app_dir)["name"]
