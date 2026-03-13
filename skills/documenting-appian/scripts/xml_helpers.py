#!/usr/bin/env python3
"""Shared XML parsing helpers for automation scripts.

Provides namespace-agnostic helpers used across multiple scripts to avoid
code duplication of strip_ns(), find_child(), find_children(), text(), pick_fname().
"""


def strip_ns(tag):
    """Remove XML namespace prefix from a tag name."""
    return tag.split("}", 1)[-1] if "}" in tag else tag


def find_child(elem, name):
    """Find first direct child element matching the given local name (namespace-agnostic)."""
    for c in list(elem):
        if strip_ns(c.tag) == name:
            return c
    return None


def find_children(elem, name):
    """Return all direct children whose local tag matches *name*."""
    return [c for c in list(elem) if strip_ns(c.tag) == name]


def text(child):
    """Extract stripped text content from an element, returning '' if None."""
    return (child.text or "").strip() if child is not None else ""


def pick_fname(node):
    """Pick best display name from fname string-map preferring Spanish locale (lang=es, country="")."""
    fname = find_child(node, 'fname')
    if fname is None:
        return ''
    smap = find_child(fname, 'string-map')
    if smap is None:
        return ''
    best = ''
    for pair in find_children(smap, 'pair'):
        loc = find_child(pair, 'locale')
        val = find_child(pair, 'value')
        if loc is not None:
            lang = (loc.attrib.get('lang') or '').lower()
            country = (loc.attrib.get('country') or '')
            if lang == 'es' and country == '':
                return (val.text or '').strip() if val is not None else ''
        best = (val.text or '').strip() if val is not None else best
    return best
