# Änderungen in Version 0.9

## Zusammenfassung der Änderungen seit Version 0.8

### Hauptänderungen

#### 1. RFID Tunnel Mode (Funktionsbaustein 3)
- Neuer FB3 implementiert für direkten RFID-UART Zugriff über Modbus
- Ermöglicht transparente Kommunikation zwischen Modbus-Master und RFID-Reader
- Erweiterte Debugging-Funktionen für Tunnel-Mode

#### 2. LED-Steuerung über Modbus
- Externe LED-Ring Kontrolle via Register 1027-1028 (Multi-Write only)
- Unterstützt verschiedene LED-Farben: Offline, Blau, Grün, Türkis, Aus
- Integration in RFID-Funktionsbausteine

#### 3. Verbesserte RFID-Funktionalität
- Überarbeitete UID-Behandlung mit verbessertem Logging
- Optimierte Fehlerbehandlung mit detaillierten Error Codes (Register 1026)
- Strukturierte Fehlercodes: Command Code + Exception Code

#### 4. Code-Refactoring
- RfidControl Klasse erheblich vereinfacht (von ~1000 auf ~500 Zeilen)
- Verbesserte Modularität und Wartbarkeit
- Klarere Trennung zwischen Funktionsbausteinen

#### 5. Erweiterte Modbus-Register
- **Register 1009**: FB-Auswahl (0=Standby, 1=UID, 2=MIFARE, 3=Tunnel)
- **Register 1026**: Detaillierte Fehlercodes
- **Register 1027-1028**: LED-Steuerung
- **Register 2030-2046**: RFID Reader Firmware Version

#### 6. Dokumentation
- Umfangreiche Erweiterung der ModbusSpecRFID_Add.md
- Detaillierte Beschreibung aller Funktionsbausteine
- Fehlercode-Tabellen und Beispiele

### Technische Details

#### Funktionsbausteine (FB)
| FB | Wert | Funktion |
|----|------|----------|
| 0  | 0    | RFID Erkennung abgeschaltet (Standby Mode) |
| 1  | 1    | Lesen der UID eines erkannten RFID Tags |
| 2  | 2    | FB1 + Lesen/Schreiben MIFARE Classic |
| 3  | 3    | FB1 + Tunnel Mode (RFID-UART über Modbus) |

#### Fehlercode-Struktur (Register 1026)
- **Low Byte**: RFID Telegramm Command Code (0x00 = interner Fehler)
- **High Byte**: Exception Code passend zum Command Code

#### LED-Steuerung Befehle
- 0x14: LED Ring Offline (Rot)
- 0x16: LED Ring Blau
- 0x17: LED Ring Grün
- 0x18: LED Ring Türkis
- 0x19: LED Ring Aus

### Commit-Historie
- 86012f5: Add external LED control functionality to Modbus and RFID
- 3d3daa4: Refactor RFID functionality and improve logging
- 676b788: Refactor RFID control for improved UID handling and logging
- 24941f5: Refactor Tunnel Mode in RFID control and enhance debugging
- ad7c268: Add Tunnel Mode functionality to RFID control with documentation updates
- 339dff1: V0.8: Update RFID specifications and adjust firmware configuration