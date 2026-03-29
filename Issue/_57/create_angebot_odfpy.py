"""
Konvertiert ANGEBOTSTEXT.md -> ANGEBOTSTEXT_neu.odt
Benutzt Angebot_Blank.odt als Template (Logo, Adressfeld, Seitenformat bleiben erhalten)
Benötigt: pip install odfpy
"""
import sys
import re
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
INPUT_MD  = SCRIPT_DIR / "ANGEBOTSTEXT.md"
TEMPLATE  = SCRIPT_DIR / "Angebot_Blank.odt"
OUT_ODT   = SCRIPT_DIR / "ANGEBOTSTEXT_neu.odt"

# --- odfpy installieren falls nötig ---
try:
    from odf.opendocument import load
    from odf.text import P, H, List, ListItem, Span
    from odf.table import Table, TableColumn, TableRow, TableCell
    from odf import text as odftext
    from odf.element import Element
except ImportError:
    print("Installiere odfpy...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "odfpy"])
    from odf.opendocument import load
    from odf.text import P, H, List, ListItem, Span
    from odf.table import Table, TableColumn, TableRow, TableCell
    from odf import text as odftext
    from odf.element import Element

import copy
from odf.namespaces import TEXTNS, TABLENS, STYLENS, OFFICENS

# ── Hilfsfunktionen ──────────────────────────────────────────────────────────

def make_p(doc, text_content, style="P18"):
    """Erstellt einen Textabsatz mit Inline-Formatting (**bold**)."""
    p = P(stylename=style)
    parts = re.split(r'(\*\*[^*]+\*\*)', text_content)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            inner = part[2:-2]
            span = Span(stylename="P13")
            span.addText(inner)
            p.addElement(span)
        else:
            p.addText(part)
    return p

def make_heading(doc, text_content, level):
    style = {1: "Heading_20_1", 2: "Heading_20_2", 3: "Heading_20_3"}.get(level, "Heading_20_3")
    h = H(outlinelevel=level, stylename=style)
    h.addText(text_content)
    return h

def make_list_item(doc, text_content, level=1):
    """Erstellt ein Listenelement."""
    p = make_p(doc, text_content, style="P20")
    li = ListItem()
    li.addElement(p)
    return li

def parse_table(lines):
    """Parst Markdown-Tabelle, gibt Liste von Zeilen (Liste von Zellen) zurück."""
    rows = []
    for line in lines:
        if re.match(r'\s*\|[-: |]+\|\s*', line):
            continue  # Trennzeile überspringen
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)
    return rows

def make_odf_table(doc, md_lines):
    """Erstellt eine ODF-Tabelle aus Markdown-Tabellenzeilen."""
    rows_data = parse_table(md_lines)
    if not rows_data:
        return None

    col_count = max(len(r) for r in rows_data)
    tbl = Table(name="Table")
    for _ in range(col_count):
        tbl.addElement(TableColumn())

    for i, row_cells in enumerate(rows_data):
        tr = TableRow()
        style = "Table_20_Heading" if i == 0 else "Table_20_Contents"
        for cell_text in row_cells:
            tc = TableCell()
            p = make_p(doc, cell_text, style=style)
            tc.addElement(p)
            tr.addElement(tc)
        # Fehlende Zellen auffüllen
        for _ in range(col_count - len(row_cells)):
            tc = TableCell()
            tc.addElement(P(stylename=style))
            tr.addElement(tc)
        tbl.addElement(tr)
    return tbl

# ── Markdown parsen ──────────────────────────────────────────────────────────

def parse_md(doc, md_text):
    """Konvertiert Markdown-Text zu Liste von ODF-Elementen."""
    elements = []
    lines = md_text.splitlines()
    i = 0
    current_list = None
    current_list_level = 0

    def flush_list():
        nonlocal current_list, current_list_level
        if current_list is not None:
            elements.append(current_list)
            current_list = None
            current_list_level = 0

    para_lines = []  # Sammelt Zeilen eines Fließtext-Absatzes

    def flush_para():
        if para_lines:
            text = " ".join(para_lines)
            elements.append(make_p(doc, text, style="P18"))
            para_lines.clear()

    while i < len(lines):
        line = lines[i]

        # Überschriften
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            flush_para(); flush_list()
            level = len(m.group(1))
            elements.append(make_heading(doc, m.group(2), level))
            i += 1
            continue

        # Horizontale Linie
        if re.match(r'^---+\s*$', line):
            flush_para(); flush_list()
            elements.append(P(stylename="Horizontal_20_Line"))
            i += 1
            continue

        # Tabelle erkennen
        if '|' in line and i + 1 < len(lines) and re.match(r'\s*\|[-: |]+\|\s*', lines[i+1]):
            flush_para(); flush_list()
            table_lines = []
            while i < len(lines) and ('|' in lines[i] or re.match(r'\s*\|[-: |]+\|\s*', lines[i])):
                table_lines.append(lines[i])
                i += 1
            tbl = make_odf_table(doc, table_lines)
            if tbl:
                elements.append(tbl)
            continue

        # Checkbox [ ] und [x]
        m = re.match(r'^- \[([ x])\]\s+(.*)', line)
        if m:
            flush_para(); flush_list()
            checked = "☑" if m.group(1) == "x" else "☐"
            elements.append(make_p(doc, f"{checked} {m.group(2)}", style="P18"))
            i += 1
            continue

        # Aufzählungsliste (- oder *)
        m = re.match(r'^(\s*)([-*])\s+(.*)', line)
        if m:
            flush_para()
            indent = len(m.group(1))
            level = indent // 2 + 1
            item_text = m.group(3)
            if current_list is None:
                current_list = List(stylename="L1")
                current_list_level = level
            li = make_list_item(doc, item_text, level)
            current_list.addElement(li)
            i += 1
            continue

        # Leerzeile → Absatz beenden
        if line.strip() == "":
            flush_para(); flush_list()
            i += 1
            continue

        # Fließtext-Zeile: sammeln statt sofort einfügen
        stripped = line.strip()
        if stripped:
            # Zeilenumbruch mit \ am Ende → harter Umbruch, sonst Leerzeichen
            if stripped.endswith('\\'):
                para_lines.append(stripped[:-1].rstrip())
                flush_para()
            else:
                para_lines.append(stripped)
        i += 1

    flush_para(); flush_list()
    return elements

# ── Haupt ────────────────────────────────────────────────────────────────────

print(f"Lade Template: {TEMPLATE.name}")
doc = load(str(TEMPLATE))

# Body-Text finden und letzten Standard-Absatz als Einfügepunkt nutzen
body = doc.text

# Letzten leeren Absatz entfernen (Platzhalter im Template)
children = list(body.childNodes)
last_p = None
for child in reversed(children):
    if child.qname == (TEXTNS, "p"):
        last_p = child
        break

# MD parsen
print(f"Parse Markdown: {INPUT_MD.name}")
md_text = INPUT_MD.read_text(encoding="utf-8")
elements = parse_md(doc, md_text)

# Elemente einfügen
print(f"Füge {len(elements)} Elemente ein...")
for el in elements:
    body.addElement(el)

# Speichern
doc.save(str(OUT_ODT))
print(f"\nOK: {OUT_ODT.name} ({OUT_ODT.stat().st_size // 1024} KB)")
print(f"Pfad: {OUT_ODT}")
