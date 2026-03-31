#!/usr/bin/env python3
"""
read_ang.py – Liest eine ODT-Vorlage und gibt alle Benutzer-Variablen aus.
Verwendung: python read_ang.py [datei.odt]
"""

import sys
from odf.opendocument import load
from odf import text, table as odftable
from odf.namespaces import TEXTNS

DEFAULT_FILE = "Angebot_Blank_2.odt"


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
    t = odftable.Table()
    num_cols = max(len(row) for row in rows) if rows else 0
    for _ in range(num_cols):
        t.addElement(odftable.TableColumn())
    for row_data in rows:
        row = odftable.TableRow()
        for cell_data in row_data:
            cell = odftable.TableCell()
            p = text.P()
            p.addText(str(cell_data))
            cell.addElement(p)
            row.addElement(cell)
        t.addElement(row)

    doc.text.insertBefore(t, end_para)

    doc.save(out_path)
    print(f"Gespeichert: {out_path}")
    print(f"  Tabelle mit {len(rows)} Zeile(n) zwischen '{start_var}' und '{end_var}' eingefügt.")


def _ensure_md_styles(doc_odt) -> None:
    """Fügt Zeichenstile für MD-Formatierungen ins Dokument ein (idempotent)."""
    from odf import style as odfstyle

    styles_needed = [
        ("MD_Bold",       {"fontweight": "bold",   "fontweightasian": "bold",   "fontweightcomplex": "bold"}),
        ("MD_Italic",     {"fontstyle": "italic",  "fontstyleasian": "italic",  "fontstylecomplex": "italic"}),
        ("MD_Code",       {"fontfamily": "Courier New", "fontfamilyasian": "Courier New",
                           "fontfamilycomplex": "Courier New"}),
    ]
    existing = {
        s.getAttribute("name")
        for s in doc_odt.automaticstyles.childNodes
        if hasattr(s, "getAttribute")
    }
    for name, props in styles_needed:
        if name not in existing:
            s = odfstyle.Style(name=name, family="text")
            s.addElement(odfstyle.TextProperties(**props))
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
        p = text.P()
        _md_inline(p, token.children)
        return p

    if isinstance(token, bt.Table):
        t = odftable.Table()
        all_rows = []
        if token.header:
            all_rows.append(token.header.children)
        for row in token.children:
            all_rows.append(row.children)
        num_cols = max((len(r) for r in all_rows), default=0)
        for _ in range(num_cols):
            t.addElement(odftable.TableColumn())
        for row_cells in all_rows:
            tr = odftable.TableRow()
            for cell in row_cells:
                tc = odftable.TableCell()
                p = text.P()
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
    _ensure_md_styles(doc)

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
