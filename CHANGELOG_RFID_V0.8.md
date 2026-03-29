# Aenderungen in Version RFID_0.8

**Erstes RFID-Release des MultiIOMaster-Projekts**
**52 Commits**, **144 Dateien geaendert** (+15.125 / -1.613 Zeilen)

## Uebersicht

Version RFID_0.8 ist das initiale Release des MultiIOMaster-Projekts (Projektstart: 30.01.2025).
Das Projekt baut auf der SAM4S-Firmware auf und erweitert diese um RFID-Funktionalitaet
(Funktionsbloecke FB0-FB2), Modbus-Integration, USB CDC und eine Test-GUI.

## Detaillierte Aenderungen

### 1. Projektaufbau MultiIOMaster (30.01.2025 - 03.02.2025)
**Commits:** bfbf82a, 73d5ac9, 76cccdd, 456872a, 4baf843

- Neues Multi-Projekt-Layout angelegt (CDC_Rfid_SAM4S, MultiIOMaster_SAM4S)
- USB CDC-Schnittstelle integriert (cdc_interface.cpp, 390 Zeilen)
- Erste lauffaehige TestVersion erstellt
- Ozone Debug-Skript hinzugefuegt
- Spezifikation Software_Spezifikation_RFID_to_MBS_V01.pdf hinterlegt

**Betroffene Dateien:**
- Firmware/src/sam4s/cdc_interface.cpp (+390, neu)
- Firmware/src/sam4s/Config/CDC_Rfid_SAM4S/ (neues Projekt-Verzeichnis)

### 2. RFID-Unterstuetzung (13.02.2025 - 14.02.2025)
**Commits:** d1217f5, 831454f, 8cb1bf9, 8c114f9, ac51c3e, b0dbeb7

- RFID-Reader ueber dedizierten Task und USART-Konfiguration eingebunden
- RFID-Telegramm-Parsing mit Pruefsummenberechnung implementiert
- Neue Datenklassen: RfidTagData, RfidReader, RfidReaderTelegram
- Modbus-Slave fuer RFID-Datenhaltung erweitert
- CRC-Handling verbessert und Modbus-Kommunikation bereinigt

**Betroffene Dateien:**
- Firmware/src/RfidReader.cpp (+130, neu)
- Firmware/src/RfidTagData.h (+128, neu)
- Firmware/src/RfidReaderTelegram.cpp (+109, neu)
- Firmware/src/modbusSlave.cpp (~741 Zeilen ueberarbeitet)
- Firmware/src/sam4s/uart_sam.c (+212, neu)

### 3. PWM / Dimming (16.02.2025 - 20.02.2025)
**Commits:** c4417aa, cd2fe2c, 0b0b6a0, e21e64d, 3b00094

- PWM-Kanaele 1 und 2 konfiguriert (200 Hz, Sync-Mode)
- Dimm-Tabelle implementiert
- PWM-Kanal-Logging hinzugefuegt, ungenutzter Code entfernt

**Betroffene Dateien:**
- Firmware/src/sam4s/OutputPWM.cpp (+136, neu)

### 4. RfidControl-Klasse und Modbus-Integration (17.07.2025)
**Commits:** df70826, 9c18e7e, f10cfcd

- Neue RfidControl-Klasse fuer zentrales RFID-Kommandomanagement
- Integration in Modbus und bestehende RFID-Reader-Komponenten
- USB-Seriennummernsteuerung ueber PA29-Pin implementiert
- CMake: Mindestversion auf 3.10, Pfade und Toolchain-Erkennung korrigiert

**Betroffene Dateien:**
- Firmware/src/RfidControl.cpp (+885, neu)
- Firmware/src/RfidControl.h (+180, neu)
- Firmware/CMakeLists.txt (erweitert)

### 5. Funktionsbaustein FB2 und RfidCommands (20.07.2025)
**Commits:** 981af1a, b71b33d

- FB2 (MIFARE Classic Lesen/Schreiben) implementiert
- RfidData in RfidTagData umbenannt und erweitert
- Modbus-Handling und kritische Sektionen in RfidControl optimiert
- RfidCommands.cpp/.h mit vollstaendiger RFID-Befehlsimplementierung

**Betroffene Dateien:**
- Firmware/src/RfidCommands.cpp (+466, neu)
- Firmware/src/RfidCommands.h (+626, neu)

### 6. Test-GUI (30.08.2025)
**Commits:** 6befd5c, 3df66a8, 7957910, 7e9da8c

- RFID Modbus Test-GUI implementiert (Windows-Anwendung)
- Non-modales Fehler-Handling und Feedback-Mechanismus
- Modbus-Dokumentation aktualisiert, ungenutzte RFID-Funktionen entfernt

### 7. Refactoring und Finalisierung V0.8 (31.08.2025 - 02.09.2025)
**Commits:** 38ee070, 30df13a, 366f795, 746b601, ca69c0a, 873134d, 022aac5, a4c5b2a, 339dff1

- Umfangreiches Refactoring aller RFID- und Modbus-Komponenten
- Clear-Methode und neue Fehlerbehandlungsmethoden in RfidControl
- Schluessel-Verwaltung verfeinert, Sleep-Mode hinzugefuegt
- Typos korrigiert, Logging verbessert
- RFID-Spezifikation (ModbusSpecRFID_Add.md) aktualisiert

## Statistik

### Wichtigste neue/geaenderte Dateien
| Datei | Zeilen |
|-------|--------|
| Firmware/src/RfidControl.cpp | +885 (neu) |
| Firmware/src/modbusSlave.cpp | ~741 ueberarbeitet |
| Firmware/src/RfidCommands.h | +626 (neu) |
| Firmware/src/RfidCommands.cpp | +466 (neu) |
| Firmware/src/sam4s/cdc_interface.cpp | +390 (neu) |
| Firmware/src/main_master.cpp | ~234 ueberarbeitet |
| Firmware/src/sam4s/uart_sam.c | +212 (neu) |
| Firmware/src/ModbusStream.h | ~200 ueberarbeitet |
| Firmware/src/RfidControl.h | +180 (neu) |
| Firmware/src/sam4s/OutputPWM.cpp | +136 (neu) |
| Firmware/src/RfidReader.cpp | +130 (neu) |
| Firmware/src/RfidTagData.h | +128 (neu) |
| Firmware/src/RfidReaderTelegram.cpp | +109 (neu) |
| documentation/Modbus/ModbusSpecRFID_Add.md | +161 (neu) |

**Gesamt:** +15.125 / -1.613 Zeilen, 144 Dateien, 52 Commits

## Funktionsbloecke

| FB | Wert | Funktion |
|----|------|----------|
| FB0 | 0 | RFID Erkennung abgeschaltet (Standby Mode) |
| FB1 | 1 | Lesen der UID eines erkannten RFID Tags |
| FB2 | 2 | FB1 + Lesen/Schreiben MIFARE Classic Speicherblock |

---

**Version:** RFID_0.8
**Datum:** 02.09.2025
**Tag:** RFID_0.8
**Projektstart:** 30.01.2025
**Nachfolger:** RFID_V0.9
