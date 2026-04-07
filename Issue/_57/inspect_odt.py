#!/usr/bin/env python3
"""inspect_odt.py – Zeigt Tabellenstile und Struktur einer ODT-Datei."""

import sys
from odf.opendocument import load
from odf import table as odftable

DEFAULT_FILE = "Angebot_Blank_2.odt"
path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE

doc = load(path)

print("=== Vorhandene Tabellen im Dokument ===")
tables = doc.text.getElementsByType(odftable.Table)
if not tables:
    print("  (keine)")
for i, t in enumerate(tables):
    print(f"Tabelle {i}: style={t.getAttribute('stylename')!r}")
    col_qname  = odftable.TableColumn().qname
    row_qname  = odftable.TableRow().qname
    cell_qname = odftable.TableCell().qname
    for child in t.childNodes:
        if child.qname == col_qname:
            print(f"  TableColumn: style={child.getAttribute('stylename')!r}")
        elif child.qname == row_qname:
            print(f"  TableRow:    style={child.getAttribute('stylename')!r}")
            for cell in child.childNodes:
                if cell.qname == cell_qname:
                    print(f"  TableCell:   style={cell.getAttribute('stylename')!r}")
                    break
            break

print()
print("=== Tabellenstile in doc.styles ===")
found = False
for s in doc.styles.childNodes:
    if hasattr(s, "getAttribute"):
        try:
            family = s.getAttribute("family") or ""
            name   = s.getAttribute("name")   or ""
        except ValueError:
            continue
        if "table" in family.lower():
            print(f"  family={family!r:25}  name={name!r}")
            found = True
if not found:
    print("  (keine)")

print()
print("=== Tabellenstile in doc.automaticstyles ===")
found = False
for s in doc.automaticstyles.childNodes:
    if hasattr(s, "getAttribute"):
        try:
            family = s.getAttribute("family") or ""
            name   = s.getAttribute("name")   or ""
        except ValueError:
            continue
        if "table" in family.lower():
            print(f"  family={family!r:25}  name={name!r}")
            found = True
if not found:
    print("  (keine)")
