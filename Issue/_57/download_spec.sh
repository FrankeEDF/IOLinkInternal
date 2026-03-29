#!/bin/bash
# PDF herunterladen und mit Datum-Uhrzeit im Dateinamen speichern
# Verwendung: ./download_spec.sh <URL> [YYYY-MM-DD-HH-MM]
# Beispiel:   ./download_spec.sh https://github.com/user-attachments/files/26274894/...pdf
# Beispiel mit Datum: ./download_spec.sh <URL> 2026-03-26-14-03

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

URL="$1"
if [ -z "$URL" ]; then
    echo "Fehler: Keine URL angegeben."
    echo "Verwendung: $0 <URL> [YYYY-MM-DD-HH-MM]"
    exit 1
fi

# Datum-Uhrzeit: Parameter 2 oder aktuell
if [ -n "$2" ]; then
    DATETIME="$2"
else
    DATETIME=$(date +"%Y-%m-%d-%H-%M")
fi

# Originaldateiname aus URL extrahieren und bereinigen
ORIG=$(basename "$URL" | sed 's/%[0-9A-Fa-f][0-9A-Fa-f]/_/g')
BASE="${ORIG%.pdf}"

OUTFILE="${SCRIPT_DIR}/${BASE}_${DATETIME}.pdf"

echo "Lade herunter: $URL"
echo "Zieldatei:     $OUTFILE"

curl -L --fail --progress-bar -o "$OUTFILE" "$URL"

if [ $? -eq 0 ]; then
    echo "OK: $(basename "$OUTFILE")"
else
    echo "Fehler beim Download."
    rm -f "$OUTFILE"
    exit 1
fi
