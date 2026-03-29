wir bedanken uns für Ihre Anfrage und freuen uns, Ihnen auf Basis der von Ihnen übermittelten Unterlagen

* Scan_RFID-to-MBS.pdf

* Datenblatt_RRJ_RFID_V05_240202.pdf

* Software.Spezifikation_RFID.to.MBS_V04.pdf in 5 Versionen

sowie der ausgetauschten Mails, geführten Telefonate und Teamkonferenzen und Themenbearbeitung über GitHub das folgende
Angebot unterbreiten zu dürfen.

# Angebot: Umsetzung Erweiterte Spezifikation V04

Übersicht der Dokumente Software.Spezifikation_RFID.to.MBS_V04.pdf von der Firma Schlegel GmbH & Co. KG:

| Version Nr. | Datum - Uhrzeit   | Kontext                                 |
|-------------|-------------------|-----------------------------------------|
| **1**       | 2026-03-23  08:36 | Initiale V04 - "Änderungen in blau"     |
| **2**       | 2026-03-24  16:34 | Korrektur: FB3 Automatismen             |
| **3**       | 2026-03-25  07:50 | Korrektur: FB3 Baudrate-Telegramme      |
| **4**       | 2026-03-25  12:32 | Korrektur: FB3 LED-Default              |
| **5**       | 2026-03-26  14:03 | Korrektur: ACCESS Bytes (0x08) entfernt |

Nach aufwändiger Analyse der V04-Spezifikation wurde festgestellt, dass **14 von 15 blau markierten Anforderungen
umgesetzt werden können**. Die Anforderung (ACCESS Bytes 0x08) basiert auf einem Missverständnis Seitend des
Auftraggebers und entfällt. Die Anforderung wurde in der letzten Version (**5**) der Spezifikation entfernt.

## Anforderungen aus der Spezifikation

Alle **blau markierten** Änderungen aus der V04-Spezifikation werden wie folgt implementiert:

### Funktionsbaustein 0 (FB0) - Offline

- **LED Status OFF** (keine LED im Reader und Leuchtring)

### Funktionsbaustein 1 (FB1) - UID Abfrage

- **LED grün beim Aktivieren (Offline Mode)**
- **LED-Steuerung über Reader**

### Funktionsbaustein 2 (FB2) - Mifare Classic

- **LED grün beim Aktivieren (Offline Mode)**
- **LED-Steuerung: wechsel zwischen Offline Mode und LED - Farb Ansteuerung**
- **Key A/B Default: FF FF FF FF FF FF**
- **ACCESS Bytes (0x08)** - entfällt nach Klärung (NICHT nötig)

### Funktionsbaustein 3 (FB3) - Tunnel Mode

- **Baudrate fest auf 115200, Änderung gesperrt**
- **Telegramme zum Setzen der Baudrate abfangen und verhindern**
- **Key A/B Default: FF FF FF FF FF FF**
- **Zyklisch-/Einzel-Senden wird abgeschaltet** (sporadische Telegramme stören/verhindern einwandfreie Funktion des
  Tunnel Modes)
- **dadurch keine automatische LED-Steuerung (Offline Mode)**

### Systemneustart Defaults

- **Baudrate: Erkennung und automatische Korrektur auf 115200 kBd**
- **Zyklisch Senden: ON**
- **LED über Reader (Offline Mode)**
- **FB1 aktiv beim Start**

### Umfang

**Von 15 blau markierten Anforderungen:**

- **14 werden implementiert** (inkl. Baudrate-Telegramm-Sperre in FB3)
- **1 entfällt** (ACCESS Bytes 0x08 - nach Klärung nicht erforderlich)

## Leistungsumfang

### 1. Analyse und Klärung (bereits erfolgt)

- Vollständige Analyse der V04-Spezifikation
- **Extraktion und Dokumentation aller 15 blau markierten Änderungen**
- **Systematischer Abgleich jeder Anforderung:**
    - FB0: LED OFF Verhalten
    - FB1: LED grün, Default beim Start
    - FB2: LED grün, Key A/B Defaults, LED Offline, ACCESS Bytes
    - FB3: Baudrate-Sperre, **Klärung dass zyklische Telegramme im Tunnel Mode zwingend verboten sind** (sporadische
      Telegramme stören/verhindern Funktion)
    - Systemneustart: Alle Default-Werte
- Tiefenanalyse der Firmware-Architektur:
    - Register-Handling und Trigger-Logik
    - RFID-Authentifizierung und Block-Schreiben
    - LED-Steuerung und Funktionsbausteinwechsel
    - Default-Werte bei Systemneustart
    - Modbus-Dokumentation
- **Identifikation des Missverständnisses bzgl. ACCESS Bytes (0x08)**
- Multiple Iterationen mit Rückfragen und Korrekturen im wesentlichen über GitHub
- Klärung über die tatsächliche Implementierung

**Ergebnis:**

- **14 Anforderungen spezifiziert und dokumentiert**
- **1 Anforderung (ACCESS Bytes 0x08) als nicht erforderlich identifiziert:**
    - Die Firmware muss Key A/B NICHT zu einem Datenblock zusammenbauen
    - ACCESS Bytes funktionieren bereits über Register 1018-1025 (identisch zu allen anderen Blöcken)
    - Separate Register sind weder nötig noch sinnvoll
- **Wichtige Klärung zu FB3 (Tunnel Mode):**
    - Zyklische und Einzel-Senden-Telegramme MÜSSEN zwingend abgeschaltet werden
    - Sporadische automatische Telegramme stören/verhindern die einwandfreie Funktion im Tunnel Mode
    - Diese Klärung ist essenziell für die korrekte Implementierung

### 2. Firmware-Implementierung

#### 2.1 Funktionsbaustein 0 (FB0)

- LED Status OFF beim Aktivieren
- Keine automatische LED-Steuerung

#### 2.2 Funktionsbaustein 1 (FB1)

- LED grün beim Aktivieren (Offline Mode)
- LED-Steuerung über Reader aktivieren
- FB1 als Default beim Systemneustart

#### 2.3 Funktionsbaustein 2 (FB2)

- LED grün beim Aktivieren (Offline Mode)
- LED-Steuerung über Reader aktivieren
- Key A/B Default-Werte: FF FF FF FF FF FF
- LED Offline Funktion (0x14) implementieren

#### 2.4 Funktionsbaustein 3 (FB3)

- Baudrate fest auf 115200, Änderungen sperren
- **Telegramme zum Setzen der Baudrate abfangen und verhindern**
- Key A/B Default-Werte: FF FF FF FF FF FF
- Einzel- und Zyklisch-Senden abschalten
- Keine automatische LED-Steuerung

#### 2.5 Systemneustart

- Baudrate-Erkennung und automatische Korrektur auf 115200
- Zyklisch Senden: ON
- LED über Reader (Offline Mode)
- FB1 aktivieren

#### 2.6 Testing und Debugging

- Funktionstest aller 4 Funktionsbausteine und Änderungen
- Wechsel zwischen Funktionsbausteinen
- Systemneustart-Verhalten
- LED-Verhalten

### 3. GUI Test Tool Erweiterung

- Anpassung des GUI Test Tools an die geänderten Funktionsbausteine
- Default-Werte anzeigen und setzen (Key A/B: FF FF FF FF FF FF)
- Baudrate-Sperre in FB3 visualisieren und testen
- Zyklisch-Senden Steuerung mit und ohne Ansteuerung der LED
- Test der Farbe und aktivieren der Offline LED Ansteuerung Funktion (0x14, ...) für FB2

### 4. Dokumentation erweitern

- Dokumentations für Trailer Blocks lesen / schreiben
- Bestehende Modbus-Dokumentation referenzieren und anpassen

## Konditionen für Abschluss

Für den Abschluss dieser Implementierung gelten folgende Bedingungen:

### 1. Testplan vorlegen und GUI Test Tool verwenden

Der Kunde verpflichtet sich, vor Abnahme einen Testplan vorzulegen, der mindestens folgende Szenarien abdeckt:

**Funktionsbausteine:**

- **Test FB0:** LED OFF beim Aktivieren
- **Test FB1:** LED grün, UID Abfrage funktioniert
- **Test FB2:** LED grün, Mifare Classic lesen/schreiben,
- **Test FB2:** LED Offline mode
- **Test FB2:** LED LED Farb-Modi
- **Test FB3:** Tunnel Mode, Baudrate gesperrt
- **Test Systemneustart:** Baudrate Korrektur auf 115200, FB1 aktiv, Zyklisch Senden ON

**Trailer Blocks:**

- **Test 1:** Trailer Block lesen (z.B. Block 7)
- **Test 2:** Trailer Block schreiben mit neuen ACCESS Bits
- **Test 3:** Trailer Block schreiben mit neuen Keys
- **Test 4:** Fehlerfall - falsche Authentifizierung

**GUI Test Tool Verpflichtung:**

- Der Kunde verpflichtet sich, eventuelle Fehler mit dem **GUI Test Tool nachzuvollziehen**
- Das GUI Test Tool ermöglicht eine schnellere und präzisere Fehlerdiagnose
- Fehlermeldungen ohne GUI Test Tool Protokoll können nicht bearbeitet werden

### 2. Neue Issues ausschließlich über GitHub

Alle zukünftigen Anforderungen und Problem Meldungen erfolgen ausschließlich über:

- **GitHub Issues** im Repository
- **Verwendung der bereitgestellten Templates:**
    - Bug Report
    - Feature Request
    - Dokumentation Request

**Vorteil für beide Seiten:**

- Nachvollziehbare Kommunikation
- Klare Spezifikation
- Vermeidung von Missverständnissen
- Historische Nachvollziehbarkeit

## Lieferumfang

Nach Abschluss erhalten Sie:

1. **Dokumentation** (sofern nicht bereits erstellt und zugesandt)

    - Detaillierte Erklärung der einzelnen Missverständnisses aus den diversen V04, wenn gewünscht

2. **Firmware-Update**

    - Implementierung aller 14 Anforderungen
    - Testing und Debugging
    - Binärdateien über GitHub abrufbar
    - Quelltexte und Dokumentation über GitHub abrufbar
    - **GUI Test Tool Erweiterung**

    - Angepasst an alle geänderten Funktionsbausteine
    - LED-Steuerung für FB0, FB1, FB2, FB3 visualisiert und testbar
    - Default-Werte anzeigen und setzen
    - Baudrate-Sperre in FB3 testbar
    - LED Offline Funktion (0x14)
    - Funktionsbausteinwechsel testen

## Zeitplan

Nach Auftragserteilung und Erfüllung der Konditionen wird der Auftrag innerhalb von 6 Wochen abgeschlossen.
Frühester Start der Ausführung ist der 01.04.2026.

## Garantie

Nach Abschluss garantieren wir:

- Alle 14 Anforderungen sind vollständig implementiert
- Das System unterstützt vollständig das Schreiben von Trailer-Blöcken und damit auch die ACCESS Bits
- Die Dokumentation ist korrekt und vollständig
- GUI Test Tool funktioniert mit allen Funktionsbausteinen

**Voraussetzung:**
Der vom Kunden vorgelegte Testplan wird erfolgreich durchlaufen.

## Annahme und Mitwirkungspflichten

Mit Auftragserteilung bestätigt der Kunde:

- [ ] Testplan wird vor Abnahme vorgelegt
- [ ] **Fehler werden mit GUI Test Tool nachvollzogen**
- [ ] Zukünftige Issues nur über GitHub mit Templates

---

## Preisgestaltung

Aufwand: Firmware mit GUI Test Tool Erweiterung und Dokumentation

| ITem                              | ~ Aufwand |   |
|-----------------------------------|-----------|---|
| Prüfen der Spezifikation          | 10        | h |
| Änderungen an der Firmware        | 16        | h |
| Änderungen am Gui Tool            | 2         | h |
| Anpassen der Dokumentation        | 6         | h |
| Erstellen der Trailer Beschrebung | 2         | h |
| **Gesamt**                        | **36**    | h |


Kosten: €88 * 36h = €3168

**Angebotsgültig bis:** 10.04.2026

**Ansprechpartner:** Daniel Franke

**Datum:** [Heute]

Es gelten die AGB's der Firma Entwicklungsbüro Daniel Franke soweit nicht hiermit anderslautend vereinbart.
Zahlbar innerhalb 14 Tage nachLeistungserbringung und Rechnungsstellung, rein netto.
