# Issue #57: LED Ansteuerung unvollständig

**Status:** OPEN
**Author:** Schlege
**Labels:** waiting for reply
**Assignees:** Schlege
**Comments:** 46

## Hauptproblem

Die Funktion "LED Offline" mit Code 0x14 ist nicht umgesetzt. Diese Funktion ermöglicht die Ansteuerung der Status-LED über den Reader.

## Kernpunkte aus der Diskussion

### LED Offline vs LED OFF
- **LED OFF (0x15):** Schaltet die LEDs komplett aus
- **LED Offline (0x14):** Übergibt die LED-Steuerung an den Reader selbst (internes Reader-Management)

### Technische Umsetzung

Laut Schlege sollte über Kommandocode 0x23 (Einzelsenden) mit Byte 9 der Offline-Betrieb gesteuert werden:

- **Einzelsenden mit Reader-LED-Steuerung:**
  `50 00 05 23 FF 01 00 01 03 CRC`
  (Byte 9 = 0x03 aktiviert interne Reader-LED-Steuerung)

- **Einzelsenden ohne Reader-LED-Steuerung:**
  `50 00 05 23 FF 64 00 01 00 CRC`
  (Byte 9 = 0x00 deaktiviert interne Reader-LED-Steuerung)

### Dokumentation

Die Steuercodes stammen aus dem RFID Reader Datenblatt (Datenblatt_RRJ_RFID_V05_240202.pdf):
- 0x16 bis 0x19: LED-Farben (bereits implementiert)
- 0x14: LED Offline (fehlend)
- 0x15: LED OFF (bereits implementiert)

## Zusätzliche Anforderungen (Default-Werte)

Im Verlauf der Diskussion wurden weitere Default-Werte identifiziert:

### 1. LED-Verhalten beim Start (FB0, FB1, FB2)
- Beim Aktivieren bzw. Wechseln zwischen Funktionsblöcken soll die LED **grün** leuchten
- Farbgebung der LEDs soll über Reader intern laufen, solange keine weitere LED-Farbe gewünscht
- Gilt **NICHT für FB3** (Tunnel Mode)

### 2. Key A und Key B Default
- Register für Key A und Key B sollen beim Einschalten immer **FF FF FF FF FF FF** haben
- Dies ist der Standard-Auslieferungszustand der meisten Transponder

### 3. Baudrate Reset
- Baudrate am Reader sollte beim Neustart immer auf **115200 Baud** gesetzt werden
- Sicherstellung: Falls Anwender über FB3 die Baudrate ändert, wird sie nach Neustart wieder auf Standard zurückgesetzt

### 4. ACCESS Bytes (neue Anforderung)
- Bytes 54-56 oder 118-120 im Speicherblock
- Steuerung von Lese-/Schreibrechten auf Speicherblöcke
- Vergleichbar mit Key A/Key B, sollen aus Modbus-Registern in Speicherzellen geschrieben werden

## FB3 Tunnel Mode Besonderheiten

Im FB3 (Tunnel Mode) gelten Ausnahmen:
- Alle Automatismen werden abgeschaltet
- ATSAM sendet keine automatischen Telegramme
- Nur durchreichen von Telegrammen zwischen Modbus und RFID Reader
- LED-Default-Verhalten **nicht** in FB3 anwendbar
- Zyklisches Senden wird deaktiviert, damit Tunnel Mode funktioniert

## Spezifikations-Updates

Mehrere Versionen der Software-Spezifikation wurden im Issue ausgetauscht:
- Software Spezifikation_RFID to MBS_V04.pdf (mehrere Revisionen)
- Änderungen in blau markiert
- FB3-Ausnahmen hinzugefügt

## Offene Fragen

Am Ende des Issue-Threads:
- FrankeEDF fragt nach genauer Beschreibung des ACCESS-Bytes-Ablaufs
- Welche Modbus-Register?
- Was passiert beim Lesen/Schreiben?
- Welche RFID-Telegramme sind nötig?

## Dateien

Die folgenden Dateien wurden im Issue referenziert:
- `Software Spezifikation_RFID to MBS_V04.pdf` (mehrere Versionen)
- `Datenblatt_RRJ_RFID_V05_240202.pdf` (RFID Reader Dokumentation)
- `rfid_modbus_tunnel_led_control.pdf`
- `FB2_LED_Control.pdf`

## Screenshots im Issue

1. LED Offline Funktion Code 0x14
2. Modbus Tunnel LED Control
3. FB2 LED Control Tabelle
4. Spezifikation mit "wird eigenständig vom Reader gehändelt"
5. Einzelsenden Telegramm-Details
6. Einzelsenden mit externer LED-Ansteuerung
7. Korrekturbedarf Screenshots
8. FB3 Ausnahme-Hinweise
9. ACCESS Bytes Speicherblock-Übersicht

## Nächste Schritte

1. Implementierung LED Offline (0x14) Funktion
2. Default-Werte implementieren (LED grün, Keys FF, Baudrate 115200)
3. ACCESS Bytes Funktionalität klären und spezifizieren
4. FB3 Ausnahmen in Code berücksichtigen
