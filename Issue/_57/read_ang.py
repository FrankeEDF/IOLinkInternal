#!/usr/bin/env python3
"""
read_ang.py – Liest eine ODT-Vorlage und gibt alle Benutzer-Variablen aus.
Verwendung: python read_ang.py [datei.odt]
"""

import sys
from odf.opendocument import load
from odf import text
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
