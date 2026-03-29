"""
Konvertiert ANGEBOTSTEXT.md -> ANGEBOTSTEXT_neu.pdf via LaTeX
Benötigt: pandoc + MiKTeX (werden via winget installiert falls nötig)
"""
import sys
import subprocess
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
INPUT_MD   = SCRIPT_DIR / "ANGEBOTSTEXT.md"
TEMPLATE   = SCRIPT_DIR / "angebot_template.tex"
OUT_PDF    = SCRIPT_DIR / "ANGEBOTSTEXT_neu.pdf"

def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)

def check_or_install(tool, winget_id):
    if shutil.which(tool):
        print(f"OK: {tool} gefunden")
        return True
    print(f"{tool} nicht gefunden – installiere via winget ({winget_id})...")
    r = subprocess.run(["winget", "install", "--id", winget_id, "-e", "--silent"],
                       capture_output=False)
    # PATH neu laden
    import os
    path_machine = subprocess.run(
        ["powershell", "-Command",
         "[System.Environment]::GetEnvironmentVariable('Path','Machine')"],
        capture_output=True, text=True).stdout.strip()
    path_user = subprocess.run(
        ["powershell", "-Command",
         "[System.Environment]::GetEnvironmentVariable('Path','User')"],
        capture_output=True, text=True).stdout.strip()
    os.environ["PATH"] = path_machine + ";" + path_user + ";" + os.environ.get("PATH","")
    if shutil.which(tool):
        print(f"OK: {tool} installiert")
        return True
    print(f"FEHLER: {tool} konnte nicht installiert werden.")
    return False

# --- Tools prüfen / installieren ---
if not check_or_install("pandoc", "JohnMacFarlane.Pandoc"):
    sys.exit(1)

# MiKTeX: pdflatex oder xelatex
latex_bin = shutil.which("pdflatex") or shutil.which("xelatex")
if not latex_bin:
    check_or_install("pdflatex", "MiKTeX.MiKTeX")
    latex_bin = shutil.which("pdflatex") or shutil.which("xelatex")
    if not latex_bin:
        print("FEHLER: Kein LaTeX gefunden. Bitte MiKTeX manuell installieren: https://miktex.org/download")
        sys.exit(1)

latex_cmd = Path(latex_bin).stem
print(f"LaTeX: {latex_bin}")

# --- Schritt 1: MD -> .tex (Zwischendatei) ---
OUT_TEX = SCRIPT_DIR / "ANGEBOTSTEXT_neu.tex"
print(f"\nSchritt 1: MD -> TEX ({OUT_TEX.name})")

cmd_tex = [
    "pandoc", str(INPUT_MD),
    "--template", str(TEMPLATE),
    "--standalone",
    "-V", "lang=de",
    "-o", str(OUT_TEX),
]
result = subprocess.run(cmd_tex, capture_output=True, text=True, cwd=str(SCRIPT_DIR))
if result.returncode != 0 or not OUT_TEX.exists():
    print(f"FEHLER TEX:\n{result.stderr}")
    sys.exit(1)
print(f"OK: {OUT_TEX.name} ({OUT_TEX.stat().st_size // 1024} KB) — für Overleaf/Online-Preview verwendbar")

# --- Schritt 2: .tex -> PDF ---
print(f"\nSchritt 2: TEX -> PDF ({OUT_PDF.name})")
cmd_pdf = [latex_cmd, "-interaction=nonstopmode", OUT_TEX.name]
result = subprocess.run(cmd_pdf, capture_output=True, text=True, cwd=str(SCRIPT_DIR))

if OUT_PDF.exists():
    print(f"OK: {OUT_PDF.name} ({OUT_PDF.stat().st_size // 1024} KB)")
    print(f"Pfad: {OUT_PDF}")
else:
    print("FEHLER LaTeX:")
    # Letzte 50 Zeilen der Log-Ausgabe
    log = result.stdout or result.stderr
    print("\n".join(log.splitlines()[-50:]))
    sys.exit(1)
