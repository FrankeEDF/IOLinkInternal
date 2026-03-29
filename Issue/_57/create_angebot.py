"""
Konvertiert ANGEBOTSTEXT.md -> ODT und PDF
Benötigt: pip install pypandoc
"""

import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
INPUT_MD   = SCRIPT_DIR / "ANGEBOTSTEXT.md"
OUT_ODT    = SCRIPT_DIR / "ANGEBOTSTEXT_neu.odt"
OUT_PDF    = SCRIPT_DIR / "ANGEBOTSTEXT_neu.pdf"
REF_ODT    = SCRIPT_DIR / "Angebot_Blank.odt"

# --- pypandoc installieren falls nötig ---
try:
    import pypandoc
except ImportError:
    print("Installiere pypandoc...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypandoc"])
    import pypandoc

# --- pandoc binary prüfen / herunterladen ---
try:
    version = pypandoc.get_pandoc_version()
    print(f"pandoc: {version}")
except OSError:
    print("Lade pandoc herunter...")
    pypandoc.download_pandoc()
    version = pypandoc.get_pandoc_version()
    print(f"pandoc: {version}")

# --- MD -> ODT ---
print(f"Erstelle ODT: {OUT_ODT.name}")
extra_args = []
if REF_ODT.exists():
    extra_args = [f"--reference-doc={REF_ODT}"]
    print(f"Verwende Formatvorlage: {REF_ODT.name}")

pypandoc.convert_file(
    str(INPUT_MD),
    "odt",
    outputfile=str(OUT_ODT),
    extra_args=extra_args,
)

if OUT_ODT.exists():
    print(f"OK: {OUT_ODT.name} ({OUT_ODT.stat().st_size // 1024} KB)")
else:
    print("FEHLER: ODT nicht erstellt.")
    sys.exit(1)

print("\nFertig.")
print(f"ODT: {OUT_ODT}")
