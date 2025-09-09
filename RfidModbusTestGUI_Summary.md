# MultiIO RFID Test-Tool - Kurzbeschreibung

## Überblick

Das **MultiIO RFID Test-Tool** stellt Funktionen zur Validierung der RFID-Funktionen des MultiIO-Systems über Modbus RTU zur Verfügung. Das Tool bietet direkten Zugriff auf alle RFID-relevanten MultiIO-Register für Test-, Diagnose- und Inbetriebnahmezwecke.

## Technische Spezifikationen

### Systemanforderungen
- **Betriebssystem**: Windows 10/11, Linux
- **Schnittstelle**: RS485/Modbus RTU über USB-zu-Serial-Adapter
- **MultiIO-Kompatibilität**: Alle MultiIO-Versionen mit RFID-Support

### MultiIO-Kommunikation
- **Protokoll**: Modbus RTU (gemäß MultiIO-Spezifikation)
- **Standard-Baudrate**: 57600 bps (MultiIO-Standard)
- **Konfiguration**: 8 Datenbits, Even Parity, 1 Stoppbit
- **MultiIO Slave-ID**: 1

## Verfügbare Funktionen

### Tag-Informationen
- Kontinuierliche UID-Überwachung mit konfigurierbarem Polling
- Tag-Typ-Erkennung (MIFARE Classic 1K/4K, Ultralight, DESFire EV1)
- ATQA/SAK-Decoder für detaillierte Tag-Eigenschaften
- Real-Zeit-Anzeige der Tag-Präsenz

### MIFARE-Operationen
- Separate Konfiguration für Key A und Key B (je 6 Bytes)
- Selektive Block-Adressierung (0-255 für MIFARE 4K)
- Sichere Datenvalidierung (16-Byte-Blöcke)
- Hex-zu-ASCII-Konvertierung
- Trailer-Block-Schutz (verhindert versehentliches Sperren)

### LED-Steuerung
- Externe LED-Ansteuerung über MultiIO
- Direkte Steuerung externer LEDs über Modbus-Register
- Real-Zeit-LED-Kontrolle

### Tunnel-Modus
**Direkter RFID-Befehlsmodus (Funktionsblock 3)**
- Rohe RFID-Kommando-Übertragung
- Real-Zeit-Antwortdaten vom RFID-Reader
- Vollständige Protokoll-Transparenz

### Manueller Register-Zugriff
- Beliebige Register-Adressierung
- Einzel- und Multi-Register-Operationen
- Lesen und Schreiben von Registerwerten
- Dezimale und hexadezimale Darstellung

### Kommunikations-Log
**Standard-Logging**
- Chronologische Anzeige aller Operationen
- Detaillierte Fehlermeldungen mit Timestamps

**Raw-Data-Modus**
- Vollständige Modbus RTU Frame-Anzeige
- TX/RX-Datenströme in Echtzeit
- Hex-Dump aller übertragenen Bytes

## Funktionsbausteine (FB)

Die Software unterstützt alle vier RFID-Funktionsbausteine:
- **FB0**: RFID Standby (System deaktiviert)
- **FB1**: UID-Lesemodus (kontinuierliche UID-Erkennung)
- **FB2**: MIFARE Read/Write (vollständige MIFARE Classic-Unterstützung)
- **FB3**: Tunnel-Modus (direkter Zugriff auf RFID-Hardware)

## Anwendungsbereiche

### MultiIO-Systemtests
- Testfunktionen für alle RFID-Funktionsbausteine des MultiIO
- Funktionen zur Überprüfung der MultiIO-Modbus-Schnittstelle
- Zugriffsfunktionen für alle RFID-relevanten MultiIO-Register

### MultiIO-Inbetriebnahme
- Funktionen zur Konfiguration der MultiIO-RFID-Register
- Werkzeuge zur Überprüfung der MultiIO-RFID-Integration
- Hilfsmittel zur Analyse von MultiIO-Kommunikationsproblemen

### Test und Entwicklung
- Testumgebung zur Unterstützung der RFID-Firmware-Entwicklung
- Funktionen zur Validierung der MultiIO-Modbus-Integration
- Werkzeuge zur detaillierten Untersuchung von MultiIO-RFID-Problemen

## Lieferumfang

### Software-Komponenten
- **Python-Skript** (RfidModbusTestGUI.py)
- **Abhängigkeiten-Liste** (requirements.txt)
- **Konfigurationsbeispiele** für MultiIO-Tests

### Dokumentation
- **MultiIO RFID-Register-Referenz**
- **Test-Anleitungen** für alle MultiIO-RFID-Funktionsbausteine
- **Beispiel-Testsequenzen** für typische Anwendungsfälle

---

*Das Test-Tool stellt Funktionen zur Validierung und Diagnose der MultiIO-RFID-Funktionalität zur Verfügung und unterstützt bei Tests, Inbetriebnahme und Fehleranalyse.*