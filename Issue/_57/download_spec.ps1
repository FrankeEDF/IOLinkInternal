# PDF herunterladen und mit Datum-Uhrzeit im Dateinamen speichern
# Verwendung: .\download_spec.ps1 <URL> [YYYY-MM-DD-HH-MM]
# Beispiel:   .\download_spec.ps1 "https://github.com/user-attachments/files/26274894/Software.Spezifikation_RFID.to.MBS_V04.pdf"
# Mit Datum:  .\download_spec.ps1 "https://..." "2026-03-26-14-03"

param(
    [Parameter(Mandatory=$true)]
    [string]$Url,

    [Parameter(Mandatory=$false)]
    [string]$DateTime
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Datum-Uhrzeit: Parameter oder aktuell
if (-not $DateTime) {
    $DateTime = Get-Date -Format "yyyy-MM-dd-HH-mm"
}

# Originaldateiname aus URL extrahieren
$Orig = [System.IO.Path]::GetFileNameWithoutExtension([Uri]::UnescapeDataString((Split-Path -Leaf $Url)))
$OutFile = Join-Path $ScriptDir "${Orig}_${DateTime}.pdf"

Write-Host "Lade herunter: $Url"
Write-Host "Zieldatei:     $OutFile"

try {
    Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing
    Write-Host "OK: $(Split-Path -Leaf $OutFile)"
} catch {
    Write-Error "Fehler beim Download: $_"
    if (Test-Path $OutFile) { Remove-Item $OutFile }
    exit 1
}
