# Alle Versionen der Spezifikation herunterladen (privates Repo - gh CLI Auth)
# Dateiname: Software.Spezifikation_RFID.to.MBS_V04_YYYY-MM-DD-HH-MM.pdf

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# GitHub Token via gh CLI holen
$GhToken = $null
try {
    $GhToken = (gh auth token 2>$null).Trim()
} catch {}

if (-not $GhToken) {
    Write-Host "WARNUNG: Kein gh-Token gefunden. Versuche ohne Authentifizierung..." -ForegroundColor Yellow
}

$Headers = @{}
if ($GhToken) {
    $Headers["Authorization"] = "token $GhToken"
    Write-Host "GitHub Auth: OK (gh CLI)" -ForegroundColor Green
}

$Versions = @(
    @{ DateTime = "2026-03-23-08-36"; Url = "https://github.com/user-attachments/files/26175902/Software.Spezifikation_RFID.to.MBS_V04.pdf" }
    @{ DateTime = "2026-03-24-16-34"; Url = "https://github.com/user-attachments/files/26219142/Software.Spezifikation_RFID.to.MBS_V04.pdf" }
    @{ DateTime = "2026-03-25-07-50"; Url = "https://github.com/user-attachments/files/26234236/Software.Spezifikation_RFID.to.MBS_V04.pdf" }
    @{ DateTime = "2026-03-25-12-32"; Url = "https://github.com/user-attachments/files/26241781/Software.Spezifikation_RFID.to.MBS_V04.pdf" }
    @{ DateTime = "2026-03-26-14-03"; Url = "https://github.com/user-attachments/files/26274894/Software.Spezifikation_RFID.to.MBS_V04.pdf" }
)

foreach ($v in $Versions) {
    $Base = [System.IO.Path]::GetFileNameWithoutExtension([Uri]::UnescapeDataString((Split-Path -Leaf $v.Url)))
    $OutFile = Join-Path $ScriptDir "${Base}_$($v.DateTime).pdf"

    if (Test-Path $OutFile) {
        Write-Host "Vorhanden:  $(Split-Path -Leaf $OutFile)" -ForegroundColor Yellow
        continue
    }

    Write-Host "Lade:       $(Split-Path -Leaf $OutFile)" -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $v.Url -OutFile $OutFile -Headers $Headers -UseBasicParsing
        Write-Host "OK:         $(Split-Path -Leaf $OutFile)" -ForegroundColor Green
    } catch {
        Write-Host "FEHLER:     $($v.DateTime) - $_" -ForegroundColor Red
        if (Test-Path $OutFile) { Remove-Item $OutFile }
    }
}

Write-Host ""
Write-Host "Fertig. Dateien in: $ScriptDir"
