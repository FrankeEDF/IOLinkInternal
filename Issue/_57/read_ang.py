#!/usr/bin/env python3
"""
read_ang.py – Liest eine ODT-Vorlage und gibt alle Benutzer-Variablen aus.
Verwendung: python read_ang.py [datei.odt]
"""

import itertools
import os
import subprocess
import sys
from odf.opendocument import load
from odf import text, table as odftable
from odf.namespaces import TEXTNS

# OpenOffice/LibreOffice Programm-Verzeichnisse (werden automatisch durchsucht)
_OO_PROG_CANDIDATES = [
    r"C:\Program Files\LibreOffice\program",
    r"C:\Program Files (x86)\LibreOffice\program",
    r"C:\Program Files\OpenOffice 4\program",
    r"C:\Program Files (x86)\OpenOffice 4\program",
    r"C:\Program Files\OpenOffice.org 4\program",
    r"C:\Program Files (x86)\OpenOffice.org 4\program",
]

# Inline-Skript, das mit OO/LO-Python via UNO eine ODT→PDF-Konvertierung macht
_UNO_CONVERT_SCRIPT = r"""
import sys, os, uno
from com.sun.star.beans import PropertyValue

def to_url(path):
    return uno.systemPathToFileUrl(os.path.abspath(path))

input_path, output_path = sys.argv[1], sys.argv[2]

import officehelper
ctx  = officehelper.bootstrap()
smgr = ctx.ServiceManager
desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

p_hidden       = PropertyValue(); p_hidden.Name = "Hidden";     p_hidden.Value = True
p_filter       = PropertyValue(); p_filter.Name = "FilterName"; p_filter.Value = "writer_pdf_Export"

doc = desktop.loadComponentFromURL(to_url(input_path), "_blank", 0, (p_hidden,))
doc.storeToURL(to_url(output_path), (p_filter,))
doc.close(True)
print("OK:" + output_path)
"""


def _find_oo_python() -> tuple[str, str] | None:
    """Sucht das Python-Executable im OO/LO-Programmverzeichnis.
    Gibt (python_exe, prog_dir) zurück oder None."""
    for prog in _OO_PROG_CANDIDATES:
        for py in ("python.exe", "python3.exe", "python"):
            exe = os.path.join(prog, py)
            if os.path.isfile(exe):
                return exe, prog
    return None


def convert_to_pdf(odt_path: str, pdf_path: str | None = None) -> str | None:
    """Konvertiert eine ODT-Datei mit OpenOffice/LibreOffice (UNO) in PDF.

    pdf_path: Zieldatei (optional). Wenn None, wird die ODT-Datei mit .pdf-Endung verwendet.
    Gibt den Pfad zur erzeugten PDF zurück, oder None bei Fehler.
    """
    found = _find_oo_python()
    if not found:
        print("FEHLER: OpenOffice/LibreOffice Python nicht gefunden.")
        return None
    oo_python, prog_dir = found

    odt_abs  = os.path.abspath(odt_path)
    expected = pdf_path or (os.path.splitext(odt_abs)[0] + ".pdf")
    expected = os.path.abspath(expected)

    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                     delete=False, encoding="utf-8") as f:
        f.write(_UNO_CONVERT_SCRIPT)
        tmp_script = f.name

    try:
        env = os.environ.copy()
        env["PATH"] = prog_dir + os.pathsep + env.get("PATH", "")
        env["PYTHONPATH"] = prog_dir + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [oo_python, tmp_script, odt_abs, expected],
            capture_output=True, text=True, env=env,
        )
    finally:
        os.unlink(tmp_script)

    if result.returncode != 0 or not os.path.isfile(expected):
        print(f"FEHLER bei PDF-Erzeugung:\n{result.stderr.strip() or result.stdout.strip()}")
        return None

    print(f"PDF gespeichert: {expected}")
    return expected

_table_counter = itertools.count(1)
_TABLE_WIDTH_CM_FALLBACK = 17.0  # Fallback wenn Seitenformat nicht lesbar


def _parse_dim_cm(value: str) -> float:
    """Wandelt eine ODF-Maßangabe ('21.001cm', '210mm', '595.28pt') in cm um."""
    v = (value or "").strip()
    if v.endswith("cm"):  return float(v[:-2])
    if v.endswith("mm"):  return float(v[:-2]) / 10.0
    if v.endswith("in"):  return float(v[:-2]) * 2.54
    if v.endswith("pt"):  return float(v[:-2]) * 2.54 / 72.0
    return 0.0


def _usable_width_cm(doc_odt, fallback: float = _TABLE_WIDTH_CM_FALLBACK, _debug: bool = False) -> float:
    """Ermittelt die nutzbare Textbreite aus der Seitenformatierung des Dokuments.

    Sucht den Standard-Master-Page-Stil, liest dessen page-layout und berechnet
    Seitenbreite − linker Rand − rechter Rand.
    """
    from odf import style as odfstyle
    from odf.namespaces import FONS

    def dbg(*args):
        if _debug:
            print("  [page-width]", *args)

    master_pages = doc_odt.masterstyles.getElementsByType(odfstyle.MasterPage)
    dbg(f"master_pages gefunden: {len(master_pages)}")
    if not master_pages:
        dbg("→ Fallback (keine master pages)")
        return fallback

    layout_name = None
    for mp in master_pages:
        mp_name = (mp.getAttribute("name") or "").lower()
        ln = mp.getAttribute("pagelayoutname") or ""
        dbg(f"MasterPage name={mp_name!r}  pagelayoutname={ln!r}")
        if not ln:
            continue
        layout_name = ln
        if mp_name in ("standard", "default page style", "standardseite"):
            dbg(f"→ Standard-Seite erkannt, nutze layout={ln!r}")
            break

    if not layout_name:
        dbg("→ Fallback (kein layout_name)")
        return fallback

    page_layouts = doc_odt.automaticstyles.getElementsByType(odfstyle.PageLayout)
    dbg(f"PageLayouts in styles: {[p.getAttribute('name') for p in page_layouts]}")
    pl = next((p for p in page_layouts if p.getAttribute("name") == layout_name), None)
    if not pl:
        dbg(f"→ Fallback (PageLayout {layout_name!r} nicht gefunden)")
        return fallback

    props_list = pl.getElementsByType(odfstyle.PageLayoutProperties)
    if not props_list:
        dbg("→ Fallback (keine PageLayoutProperties)")
        return fallback

    p = props_list[0]
    raw_w  = p.attributes.get((FONS, "page-width"),  "")
    raw_ml = p.attributes.get((FONS, "margin-left"), "")
    raw_mr = p.attributes.get((FONS, "margin-right"), "")
    dbg(f"page-width={raw_w!r}  margin-left={raw_ml!r}  margin-right={raw_mr!r}")

    width   = _parse_dim_cm(raw_w)
    m_left  = _parse_dim_cm(raw_ml)
    m_right = _parse_dim_cm(raw_mr)
    usable  = width - m_left - m_right
    dbg(f"→ {width:.3f} - {m_left:.3f} - {m_right:.3f} = {usable:.3f} cm")

    return usable if usable > 1 else fallback


def _token_text_len(token) -> int:
    """Schätzt die Textlänge eines Mistletoe-Tokens (rekursiv)."""
    try:
        import mistletoe.span_token as st
        if isinstance(token, st.RawText):
            return len(token.content)
    except ImportError:
        pass
    if hasattr(token, "children") and token.children:
        return sum(_token_text_len(c) for c in token.children)
    if hasattr(token, "content"):
        return len(str(token.content))
    return 0


def _col_widths_cm(max_lens: list[int], total_cm: float = _TABLE_WIDTH_CM_FALLBACK) -> list[float]:
    """Verteilt total_cm proportional zu den max. Zeichenlängen je Spalte."""
    if not max_lens:
        return []
    adjusted = [max(l, 1) for l in max_lens]
    total = sum(adjusted)
    return [total_cm * l / total for l in adjusted]


def _add_column_styles(doc_odt, widths_cm: list[float]) -> list[str]:
    """Legt pro Spalte einen TableColumn-Stil an und gibt die Namen zurück."""
    from odf import style as odfstyle
    idx = next(_table_counter)
    names = []
    for i, w in enumerate(widths_cm):
        name = f"MD_Col_{idx}_{i}"
        s = odfstyle.Style(name=name, family="table-column")
        s.addElement(odfstyle.TableColumnProperties(columnwidth=f"{w:.3f}cm"))
        doc_odt.automaticstyles.addElement(s)
        names.append(name)
    return names

DEFAULT_FILE = "Angebot_Blank_libre.odt"


def get_user_variables(odt_path: str) -> dict[str, str]:
    """Gibt alle text:user-field-decl Variablen aus dem Dokument zurück."""
    doc = load(odt_path)
    decls = doc.text.getElementsByType(text.UserFieldDecl)

    variables: dict[str, str] = {}
    for decl in decls:
        name = decl.getAttribute("name")
        value = (
            decl.getAttribute("stringvalue")
            or decl.getAttribute("value")
            or ""
        )
        variables[name] = value

    return variables


def get_user_field_refs(odt_path: str) -> list[str]:
    """Gibt alle Stellen zurück, an denen Benutzer-Variablen verwendet werden."""
    doc = load(odt_path)
    gets = doc.text.getElementsByType(text.UserFieldGet)
    return [g.getAttribute("name") for g in gets if g.getAttribute("name")]


def set_user_variables(odt_path: str, updates: dict[str, str], out_path: str) -> None:
    """Setzt Benutzer-Variablen auf neue Werte und speichert als neues Dokument."""
    doc = load(odt_path)
    decls = doc.text.getElementsByType(text.UserFieldDecl)

    changed = []
    for decl in decls:
        name = decl.getAttribute("name")
        if name in updates:
            new_val = updates[name]
            # setAttribute validiert gegen Whitelist → direkt ins Dict schreiben
            decl.attributes[(TEXTNS, "string-value")] = new_val
            decl.attributes[(TEXTNS, "value-type")] = "string"
            changed.append(name)

    # Auch die Anzeige-Felder (UserFieldGet) aktualisieren
    gets = doc.text.getElementsByType(text.UserFieldGet)
    for get in gets:
        name = get.getAttribute("name")
        if name in updates:
            # Textinhalt des Elements ersetzen
            # childNodes can contain plain strings (from addText), not just Elements,
            # so removeChild() would fail on them. Clear the list directly instead.
            get.childNodes.clear()
            get.addText(updates[name])

    doc.save(out_path)
    print(f"Gespeichert: {out_path}")
    for name in changed:
        print(f"  {name} = {updates[name]!r}")
    missing = [n for n in updates if n not in changed]
    for name in missing:
        print(f"  WARNUNG: Variable '{name}' nicht gefunden!")


def insert_text_between_markers(
    odt_path: str,
    start_var: str,
    end_var: str,
    new_lines: list[str],
    out_path: str,
) -> None:
    """Fügt Absätze zwischen zwei Marker-Variablen ein.

    Bestehende Absätze zwischen start_var und end_var werden entfernt
    und durch new_lines ersetzt (jeder Eintrag = ein Absatz).
    """
    doc = load(odt_path)

    start_para = None
    end_para = None

    for node in doc.text.childNodes:
        if not hasattr(node, "getElementsByType"):
            continue
        for g in node.getElementsByType(text.UserFieldGet):
            if g.getAttribute("name") == start_var:
                start_para = node
            if g.getAttribute("name") == end_var:
                end_para = node

    if not start_para or not end_para:
        print(f"WARNUNG: Marker '{start_var}' oder '{end_var}' nicht gefunden!")
        return

    children = list(doc.text.childNodes)
    si = children.index(start_para)
    ei = children.index(end_para)

    # Bestehenden Inhalt zwischen den Markern entfernen
    for node in children[si + 1 : ei]:
        doc.text.removeChild(node)

    # Neue Absätze vor end_para einfügen
    for line in new_lines:
        p = text.P()
        p.addText(line)
        doc.text.insertBefore(p, end_para)

    doc.save(out_path)
    print(f"Gespeichert: {out_path}")
    print(f"  {len(new_lines)} Absatz/Absätze zwischen '{start_var}' und '{end_var}' eingefügt.")


def insert_table_between_markers(
    odt_path: str,
    start_var: str,
    end_var: str,
    rows: list[list[str]],
    out_path: str,
) -> None:
    """Fügt eine Tabelle zwischen zwei Marker-Variablen ein.

    rows: 2D-Liste, z.B. [["Kopf1","Kopf2"], ["Wert1","Wert2"], ...]
    Bestehende Absätze zwischen den Markern werden entfernt.
    """
    doc = load(odt_path)

    start_para = None
    end_para = None

    for node in doc.text.childNodes:
        if not hasattr(node, "getElementsByType"):
            continue
        for g in node.getElementsByType(text.UserFieldGet):
            if g.getAttribute("name") == start_var:
                start_para = node
            if g.getAttribute("name") == end_var:
                end_para = node

    if not start_para or not end_para:
        print(f"WARNUNG: Marker '{start_var}' oder '{end_var}' nicht gefunden!")
        return

    children = list(doc.text.childNodes)
    si = children.index(start_para)
    ei = children.index(end_para)

    # Bestehenden Inhalt zwischen den Markern entfernen
    for node in children[si + 1 : ei]:
        doc.text.removeChild(node)

    # Tabelle aufbauen
    page_w = _usable_width_cm(doc)
    _ensure_md_styles(doc, table_width_cm=page_w)
    t = odftable.Table(stylename="MD_Table")
    num_cols = max(len(row) for row in rows) if rows else 0
    max_lens = [max((len(str(r[c])) if c < len(r) else 0 for r in rows), default=1)
                for c in range(num_cols)]
    col_names = _add_column_styles(doc, _col_widths_cm(max_lens, total_cm=page_w))
    for name in col_names:
        t.addElement(odftable.TableColumn(stylename=name))
    for i, row_data in enumerate(rows):
        row = odftable.TableRow()
        para_style = "Tabellen Überschrift" if i == 0 else "Tabellen Inhalt"
        for cell_data in row_data:
            cell = odftable.TableCell(stylename="MD_TableCell")
            p = text.P(stylename=para_style)
            p.addText(str(cell_data))
            cell.addElement(p)
            row.addElement(cell)
        t.addElement(row)

    doc.text.insertBefore(t, end_para)

    doc.save(out_path)
    print(f"Gespeichert: {out_path}")
    print(f"  Tabelle mit {len(rows)} Zeile(n) zwischen '{start_var}' und '{end_var}' eingefügt.")


def _ensure_md_styles(doc_odt, table_width_cm: float | None = None) -> None:
    """Fügt Zeichen- und Tabellenstile für MD-Formatierungen ins Dokument ein (idempotent)."""
    from odf import style as odfstyle

    existing = {
        s.getAttribute("name")
        for s in doc_odt.automaticstyles.childNodes
        if hasattr(s, "getAttribute")
        and not isinstance(s.getAttribute("name"), type(None))
    }
    try:
        existing.discard(None)
    except Exception:
        pass

    # Zeichenstile
    char_styles = [
        ("MD_Bold",   {"fontweight": "bold",   "fontweightasian": "bold",   "fontweightcomplex": "bold"}),
        ("MD_Italic", {"fontstyle": "italic",  "fontstyleasian": "italic",  "fontstylecomplex": "italic"}),
        ("MD_Code",   {"fontfamily": "Courier New", "fontfamilyasian": "Courier New",
                       "fontfamilycomplex": "Courier New"}),
    ]
    for name, props in char_styles:
        if name not in existing:
            s = odfstyle.Style(name=name, family="text")
            s.addElement(odfstyle.TextProperties(**props))
            doc_odt.automaticstyles.addElement(s)

    # Tabellenstil
    if "MD_Table" not in existing:
        w = table_width_cm if table_width_cm is not None else _usable_width_cm(doc_odt)
        s = odfstyle.Style(name="MD_Table", family="table")
        s.addElement(odfstyle.TableProperties(align="left", width=f"{w:.3f}cm"))
        doc_odt.automaticstyles.addElement(s)

    # Zellstil mit Rahmen
    if "MD_TableCell" not in existing:
        s = odfstyle.Style(name="MD_TableCell", family="table-cell")
        s.addElement(odfstyle.TableCellProperties(
            border="0.05pt solid #000000",
            padding="0.049cm",
        ))
        doc_odt.automaticstyles.addElement(s)


def _md_inline(parent, children) -> None:
    """Fügt Inline-Tokens rekursiv als ODT-Elemente in parent ein."""
    import mistletoe.span_token as st

    if not children:
        return
    for child in children:
        if isinstance(child, st.RawText):
            # In MD ist ein einzelner Zeilenumbruch ein Leerzeichen (soft line break)
            parent.addText(child.content.replace("\n", " "))
        elif isinstance(child, st.Strong):
            span = text.Span(stylename="MD_Bold")
            _md_inline(span, child.children)
            parent.addElement(span)
        elif isinstance(child, st.Emphasis):
            span = text.Span(stylename="MD_Italic")
            _md_inline(span, child.children)
            parent.addElement(span)
        elif isinstance(child, st.InlineCode):
            span = text.Span(stylename="MD_Code")
            raw = child.children[0].content if child.children else ""
            span.addText(raw)
            parent.addElement(span)
        elif isinstance(child, st.LineBreak):
            # soft=True → einzelner Zeilenumbruch im MD = Leerzeichen
            # soft=False → harter Umbruch (zwei Leerzeichen am Zeilenende) = echter Umbruch
            if getattr(child, "soft", True):
                parent.addText(" ")
            else:
                parent.addElement(text.LineBreak())
        elif hasattr(child, "children") and child.children:
            _md_inline(parent, child.children)
        elif hasattr(child, "content"):
            parent.addText(str(child.content))


def _md_block(doc_odt, token):
    """Konvertiert ein Mistletoe-Block-Token in ein ODT-Element (oder None)."""
    import mistletoe.block_token as bt

    if isinstance(token, bt.Heading):
        lvl = min(token.level, 6)
        h = text.H(outlinelevel=lvl, stylename=f"Heading {lvl}")
        _md_inline(h, token.children)
        return h

    if isinstance(token, bt.Paragraph):
        p = text.P(stylename="Textkörper")
        _md_inline(p, token.children)
        return p

    if isinstance(token, bt.Table):
        t = odftable.Table(stylename="MD_Table")
        header_rows = [token.header.children] if token.header else []
        data_rows   = [row.children for row in token.children]
        all_rows    = header_rows + data_rows
        num_cols = max((len(r) for r in all_rows), default=0)
        max_lens = [max((_token_text_len(r[c]) if c < len(r) else 0 for r in all_rows), default=1)
                    for c in range(num_cols)]
        col_names = _add_column_styles(doc_odt, _col_widths_cm(max_lens, total_cm=_usable_width_cm(doc_odt)))
        for name in col_names:
            t.addElement(odftable.TableColumn(stylename=name))
        for is_header, rows in ((True, header_rows), (False, data_rows)):
            para_style = "Tabellen Überschrift" if is_header else "Tabellen Inhalt"
            for row_cells in rows:
                tr = odftable.TableRow()
                for cell in row_cells:
                    tc = odftable.TableCell(stylename="MD_TableCell")
                    p = text.P(stylename=para_style)
                    _md_inline(p, cell.children)
                    tc.addElement(p)
                    tr.addElement(tc)
                t.addElement(tr)
        return t

    if isinstance(token, bt.List):
        lst = text.List()
        for item in token.children:
            li = text.ListItem()
            for child in item.children:
                el = _md_block(doc_odt, child)
                if el is not None:
                    li.addElement(el)
            lst.addElement(li)
        return lst

    if isinstance(token, bt.CodeFence):
        p = text.P()
        p.addText(token.children[0].content if token.children else "")
        return p

    return None


def insert_md_between_markers(
    odt_path: str,
    start_var: str,
    end_var: str,
    md_text: str,
    out_path: str,
) -> None:
    """Parst Markdown und fügt den Inhalt zwischen zwei Marker-Variablen ein.

    Unterstützt: Überschriften (H1-H6), Absätze, **fett**, *kursiv*,
                 `inline-code`, Tabellen, Listen, Code-Blöcke.
    Benötigt: pip install mistletoe
    """
    import mistletoe
    from mistletoe.html_renderer import HtmlRenderer

    doc = load(odt_path)
    _ensure_md_styles(doc, table_width_cm=_usable_width_cm(doc))

    start_para = None
    end_para = None
    for node in doc.text.childNodes:
        if not hasattr(node, "getElementsByType"):
            continue
        for g in node.getElementsByType(text.UserFieldGet):
            if g.getAttribute("name") == start_var:
                start_para = node
            if g.getAttribute("name") == end_var:
                end_para = node

    if not start_para or not end_para:
        print(f"WARNUNG: Marker '{start_var}' oder '{end_var}' nicht gefunden!")
        return

    children = list(doc.text.childNodes)
    si = children.index(start_para)
    ei = children.index(end_para)
    for node in children[si + 1 : ei]:
        doc.text.removeChild(node)

    with HtmlRenderer():
        md_doc = mistletoe.Document(md_text)

    count = 0
    for token in md_doc.children:
        el = _md_block(doc, token)
        if el is not None:
            doc.text.insertBefore(el, end_para)
            count += 1

    doc.save(out_path)
    print(f"Gespeichert: {out_path}")
    print(f"  {count} ODT-Element(e) aus MD zwischen '{start_var}' und '{end_var}' eingefügt.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE

    print(f"Vorlage: {path}\n")



    variables = get_user_variables(path)
    if variables:
        print("Benutzer-Variablen (Deklarationen):")
        print("-" * 50)
        for name, value in sorted(variables.items()):
            print(f"  {name:<35} = {value!r}")
    else:
        print("Keine Benutzer-Variablen-Deklarationen gefunden.")

    print()

    refs = get_user_field_refs(path)
    used = sorted(set(refs))
    if used:
        print("Verwendete Variablen im Text:")
        print("-" * 50)
        for name in used:
            count = refs.count(name)
            print(f"  {name:<35} ({count}x verwendet)")
    else:
        print("Keine Variablen-Referenzen im Text gefunden.")

    # --- Test: AngebotsTextStart / AngebotsTextEnd auf "1111" setzen ---
    print()
    print("Test: Setze AngebotsTextStart und AngebotsTextEnd auf '1111' ...")
    out = path.replace(".odt", "_test.odt")
    set_user_variables(path, {"AngebotsTextStart": "1111", "AngebotsTextEnd": "2222"}, out)

    # --- Test: Text zwischen Markern einfügen ---
    print()
    print("Test: Füge Text zwischen AngebotsTextStart und AngebotsTextEnd ein ...")
    out2 = path.replace(".odt", "_test2.odt")
    insert_text_between_markers(
        path,
        "AngebotsTextStart",
        "AngebotsTextEnd",
        [
            "Das ist der erste eingefügte Absatz.",
            "Das ist der zweite eingefügte Absatz.",
        ],
        out2,
    )

    # --- Test: Tabelle zwischen Markern einfügen ---
    print()
    print("Test: Füge Tabelle zwischen AngebotsTextStart und AngebotsTextEnd ein ...")
    out3 = path.replace(".odt", "_test3.odt")
    insert_table_between_markers(
        path,
        "AngebotsTextStart",
        "AngebotsTextEnd",
        [
            ["Position", "Bezeichnung",  "Preis"],
            ["1",        "Artikel A",    "100,00 €"],
            ["2",        "Artikel B",    "250,00 €"],
            ["",         "Gesamt",       "350,00 €"],
        ],
        out3,
    )

    # --- Test: Markdown zwischen Markern einfügen ---
    print()
    print("Test: Füge Markdown zwischen AngebotsTextStart und AngebotsTextEnd ein ...")
    out4 = path.replace(".odt", "_test4.odt")
    md_file = __file__.replace("read_ang.py", "ANGEBOTSTEXT.md")
    with open(md_file, encoding="utf-8") as f:
        md_content = f.read()
    insert_md_between_markers(
        path,
        "AngebotsTextStart",
        "AngebotsTextEnd",
        md_content,
        out4,
    )

    # --- PDF erzeugen ---
    print()
    print("Erzeuge PDF aus MD-Dokument ...")
    convert_to_pdf(out4)
