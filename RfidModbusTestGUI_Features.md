# MultiIO RFID Test-Tool - Funktionsübersicht

## Überblick

Das **MultiIO RFID Test-Tool** stellt Funktionen zur Validierung der RFID-Funktionen des MultiIO-Systems über Modbus RTU zur Verfügung. Das Tool bietet direkten Zugriff auf alle RFID-relevanten MultiIO-Register für Test-, Diagnose- und Inbetriebnahmezwecke.

## Technische Spezifikationen

### Systemanforderungen
- **Betriebssystem**: Windows 10/11, Linux
- **Python-Version**: 3.6+
- **Schnittstelle**: RS485/Modbus RTU über USB-zu-Serial-Adapter
- **MultiIO-Kompatibilität**: Alle MultiIO-Versionen mit RFID-Support
- **Fenstergröße**: 1200x900 Pixel

### MultiIO-Kommunikation
- **Protokoll**: Modbus RTU (gemäß MultiIO-Spezifikation)
- **Standard-Baudrate**: 57600 bps (MultiIO-Standard)
- **Weitere Baudraten**: 9600, 19200, 38400, 115200 bps
- **Konfiguration**: 8 Datenbits, Even Parity, 1 Stoppbit
- **MultiIO Slave-ID**: 1
- **Automatische COM-Port-Erkennung**

## Verfügbare Funktionen

### Tag-Informationen
**RFID-Tag-Erkennung und -Identifikation**
- Kontinuierliche UID-Überwachung mit konfigurierbarem Polling
- Tag-Typ-Erkennung (MIFARE Classic 1K/4K, Ultralight, DESFire EV1)
- ATQA/SAK-Decoder für detaillierte Tag-Eigenschaften
- Real-Zeit-Anzeige der Tag-Präsenz
- Unterstützung für 4-Byte und 7-Byte UIDs

**Polling-Funktionen**
- Kontinuierliche Tag-Überwachung im Hintergrund
- Fehlerbehandlung mit Stopp bei Verbindungsproblemen
- Konfigurierbare Polling-Intervalle


### MIFARE-Operationen
**MIFARE Classic R/W-Funktionalität**

**Schlüsselverwaltung**
- Separate Konfiguration für Key A und Key B (je 6 Bytes)
- Standard-Schlüssel (Factory Default): FFFFFFFFFFFF
- Automatische Schlüssel-Validierung
- Key A/B-Auswahl für Lese-/Schreiboperationen

**Block-Operationen**
- Selektive Block-Adressierung (0-255 für MIFARE 4K)
- Intelligente Trailer-Block-Erkennung mit Warnung
- Sichere Datenvalidierung (16-Byte-Blöcke)
- Hex-zu-ASCII-Konvertierung
- Block-Typ-Klassifizierung (UID, Daten, Trailer)

**Sicherheitsfeatures**
- Trailer-Block-Schutz (verhindert versehentliches Sperren)
- Schlüssel-Format-Validierung
- Automatische Fehlerbehandlung und Recovery

### LED-Steuerung
**Externe LED-Ansteuerung über MultiIO**
- Direkte Steuerung externer LEDs über Modbus-Register
- Register 1027: LED-Nummer (1-8)
- Register 1028: LED-Status (0=Aus, 1=Ein)
- Real-Zeit-LED-Kontrolle
- Status-Feedback und Fehlerbehandlung

### Tunnel-Modus
**Direkter RFID-Befehlsmodus (Funktionsblock 3)**

**TX (Senden)**
- Rohe RFID-Kommando-Übertragung
- Hex-Eingabe für beliebige RFID-Protokollbefehle
- Automatische Datenvalidierung und Formatierung
- Unterstützung für herstellerspezifische Kommandos

**RX (Empfangen)**  
- Real-Zeit-Antwortdaten vom RFID-Reader
- Hex-Darstellung der Rohdaten
- Timestamps für Timing-Analyse
- Vollständige Protokoll-Transparenz

**Status-Überwachung**
- Live-Status der Tunnel-Kommunikation
- Fehlercode-Anzeige
- Übertragungsstatistiken

### Manueller Register-Zugriff
**Direkte Modbus-Register-Manipulation**
- Beliebige Register-Adressierung (1-65535)
- Einzel- und Multi-Register-Operationen
- Lesen und Schreiben von Registerwerten
- Dezimale und hexadezimale Darstellung
- Register-Batch-Operationen
- Fehlerdiagnose auf Register-Ebene

### Kommunikations-Log
**Umfassende Protokollierung und Diagnose**

**Standard-Logging**
- Chronologische Anzeige aller Operationen
- Detaillierte Fehlermeldungen mit Timestamps
- Operationsergebnisse und Status-Updates
- Log-Größenbegrenzung

**Raw-Data-Modus**
- Vollständige Modbus RTU Frame-Anzeige
- TX/RX-Datenströme in Echtzeit
- Hex-Dump aller übertragenen Bytes
- RTU-Frame-Timing-Analyse
- CRC-Validierung und Protokoll-Debugging


## Funktionsbausteine (FB)

Die Software unterstützt alle vier RFID-Funktionsbausteine:

### FB0: RFID Standby
- RFID-System deaktiviert
- Minimaler Stromverbrauch
- System bereit für Konfiguration

### FB1: UID-Lesemodus  
- Kontinuierliche UID-Erkennung
- Automatische Tag-Typ-Bestimmung
- Optimiert für Präsenzerkennung

### FB2: MIFARE Read/Write
- Vollständige MIFARE Classic-Unterstützung
- Authentifizierung mit Key A/B
- Block-Lese-/Schreiboperationen
- LED-Steuerungsfunktionen

### FB3: Tunnel-Modus
- Direkter Zugriff auf RFID-Hardware
- Rohe Befehlsübertragung
- Herstellerspezifische Kommandos
- Vollständige Protokoll-Kontrolle

## Zusätzliche Funktionen

### Komfort-Funktionen
- **Verbindungswiederherstellung**: Wiederherstellung nach Verbindungsabbruch
- **Hot-Plug-Support**: Dynamische COM-Port-Erkennung
- **Fehler-Recovery**: Wiederherstellung nach Kommunikationsfehlern
- **Tab-basierte Navigation**: Strukturierte Benutzeroberfläche

### Diagnose und Debugging  
- **Timing-Analyse**: Zeitmessungen für MultiIO-Kommunikation
- **Fehlercode-Decoder**: Übersetzung von RFID- und Modbus-Fehlercodes
- **Verbindungs-Monitoring**: Überwachung der MultiIO-Modbus-Verbindung
- **Multi-Threading**: Parallele Verarbeitung von Tests

### Datenverarbeitung
- **Format-Konvertierung**: Hex ↔ ASCII ↔ Dezimal
- **Datenvalidierung**: Prüfung von Eingabedaten
- **Register-Mapping**: MultiIO-Register-Zuordnung gemäß Spezifikation
- **Error-Handling**: Modbus-Exception-Behandlung

## Anwendungsbereiche

### MultiIO-Systemtests
- **RFID-Funktionstests**: Testfunktionen für alle RFID-Funktionsbausteine des MultiIO
- **Modbus-Kommunikationstest**: Funktionen zur Überprüfung der MultiIO-Modbus-Schnittstelle
- **Register-Verifikation**: Zugriffsfunktionen für alle RFID-relevanten MultiIO-Register
- **Timing-Analyse**: Messfunktionen für MultiIO-Antwortzeiten

### MultiIO-Inbetriebnahme
- **Parametrierung**: Funktionen zur Konfiguration der MultiIO-RFID-Register
- **Funktionstest**: Werkzeuge zur Überprüfung der MultiIO-RFID-Integration
- **Fehlerdiagnose**: Hilfsmittel zur Analyse von MultiIO-Kommunikationsproblemen
- **Validierung**: Testfunktionen für die MultiIO-Firmware-Implementierung

### Test und Entwicklung
- **MultiIO-Entwicklung**: Testumgebung zur Unterstützung der RFID-Firmware-Entwicklung
- **Integrationstests**: Funktionen zur Validierung der MultiIO-Modbus-Integration
- **Fehleranalyse**: Werkzeuge zur detaillierten Untersuchung von MultiIO-RFID-Problemen
- **Protokollierung**: Funktionen zur Anzeige der MultiIO-Kommunikation

## Technische Eigenschaften

### MultiIO-spezifische Features
- **Vollständige Register-Abdeckung**: Alle RFID-Register des MultiIO zugänglich
- **Funktionsblock-Test**: Direkter Test aller vier MultiIO-RFID-Modi (FB0-FB3)
- **Modbus-Konformität**: Test gemäß MultiIO-Modbus-Spezifikation
- **Echtzeitüberwachung**: Live-Monitoring der MultiIO-Antworten

### Test-Features
- **Manuelle Testsequenzen**: Wiederholbare Testsequenzen für MultiIO
- **Fehlerprotokollierung**: Detaillierte Anzeige von MultiIO-Fehlern
- **Timing-Messungen**: Präzise Latenzmessungen der MultiIO-Kommunikation
- **Raw-Data-Analyse**: Direkter Einblick in MultiIO-Modbus-Frames

## Lieferumfang

### Software-Komponenten
- **Python-Skript** (RfidModbusTestGUI.py)
- **Abhängigkeiten-Liste** (requirements.txt)
- **Konfigurationsbeispiele** für MultiIO-Tests

### Dokumentation
- **MultiIO RFID-Register-Referenz**
- **Test-Anleitungen** für alle MultiIO-RFID-Funktionsbausteine
- **Beispiel-Testsequenzen** für typische Anwendungsfälle

### MultiIO-Integration
- **Kompatibel mit MultiIO-Firmware** (alle Versionen mit RFID)
- **Unterstützt alle MultiIO-RFID-Modi** (FB0-FB3)
- **Getestet mit MultiIO-Hardware**

---

*Das Test-Tool stellt Funktionen zur Validierung und Diagnose der MultiIO-RFID-Funktionalität zur Verfügung und unterstützt bei Tests, Inbetriebnahme und Fehleranalyse.*