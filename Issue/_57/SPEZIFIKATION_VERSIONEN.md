# Software Spezifikation_RFID to MBS - Versionshistorie

## Übersicht aller Software.Spezifikation_RFID.to.MBS_V04_2026.pdf

| Nr. | Datum      | Uhrzeit (UTC) | Uhrzeit (MEZ) | Autor   | File-ID  | Kontext                                 |
|-----|------------|---------------|---------------|---------|----------|-----------------------------------------|
| 1   | 2026-03-23 | 07:36:16      | 08:36         | Schlege | 26175902 | Initiale V04 - "Änderungen in blau"     |
| 2   | 2026-03-24 | 15:34:59      | 16:34         | Schlege | 26219142 | Korrektur: FB3 Automatismen             |
| 3   | 2026-03-25 | 06:50:26      | 07:50         | Schlege | 26234236 | Korrektur: FB3 Baudrate-Telegramme      |
| 4   | 2026-03-25 | 11:32:29      | 12:32         | Schlege | 26241781 | Korrektur: FB3 LED-Default              |
| 5   | 2026-03-26 | 13:03:51      | 14:03         | Schlege | 26274894 | Korrektur: ACCESS Bytes (0x08) entfernt |

## Download-Links

### Version 1 (2026-03-23 08:36)

- **Link:** https://github.com/user-attachments/files/26175902/Software.Spezifikation_RFID.to.MBS_V04.pdf
- **Kontext:** Initiale V04 mit allen blauen Änderungen

### Version 2 (2026-03-24 16:34)

- **Link:** https://github.com/user-attachments/files/26219142/Software.Spezifikation_RFID.to.MBS_V04.pdf
- **Kontext:** Korrektur nach Franke-Anforderung zu FB3 Automatismen

### Version 3 (2026-03-25 07:50)

- **Link:** https://github.com/user-attachments/files/26234236/Software.Spezifikation_RFID.to.MBS_V04.pdf
- **Kontext:** Korrektur nach Franke-Anforderung zu Baudrate

### Version 4 (2026-03-25 12:32)

- **Link:** https://github.com/user-attachments/files/26241781/Software.Spezifikation_RFID.to.MBS_V04.pdf
- **Kontext:** Korrektur nach Franke-Anforderung zu LED-Defaults

### Version 5 (2026-03-26 14:03) - AKTUELL

- **Link:** https://github.com/user-attachments/files/26274894/Software.Spezifikation_RFID.to.MBS_V04.pdf
- **Kontext:** Neueste Version nach ACCESS Bytes Diskussion

## Detaillierte Änderungshistorie

### Version 1 → 2 (23.03. 08:36 → 24.03. 16:34)

**Zeitdelta:** 1 Tag, 8 Stunden

**Änderung:**

- FB3: Klarstellung dass alle Automatismen abgeschaltet werden müssen
- Begründung: "Tunnel Mode und automatisches Versenden schließen sich gegenseitig aus"

**Franke-Kommentar:**
> "Im FB3 werden alle Automatismen abgeschaltet damit der Tunnel Mode funktioniert, damit ist auch die funktionsweise
> der LED nicht sicher zu stellen!"

**Schlege-Zustimmung:**
> "OK, unter Tunnel-Mode war mein Verständnis, dass die Daten in beide Richtungen nur durchgereicht werden [...] Da im
> Grund der Funktionsablauf noch gewährleistet ist kann ich hier den Abstrich Zyklisch- und Einzel-Senden mitgehen"

---

### Version 2 → 3 (24.03. 16:34 → 25.03. 07:50)

**Zeitdelta:** 15 Stunden, 16 Minuten

**Änderung:**

- FB3: Ergänzung dass Telegramme zum Setzen der Baudrate abgefangen und verhindert werden müssen
- Baudrate muss fest auf 115200 bleiben

**Franke-Anforderung:**
Screenshot mit Markierung des fehlenden Punktes zur Baudrate-Sperre

---

### Version 3 → 4 (25.03. 07:50 → 25.03. 12:32)

**Zeitdelta:** 4 Stunden, 42 Minuten

**Änderung:**

- FB3 aus "LED grün beim Aktivieren" ausgenommen
- LED-Verhalten im FB3 nicht garantiert wegen abgeschalteter Automatismen

**Franke-Anforderung:**
> "und hier muss auch FB3 ausgenommen werden"

Screenshot mit Markierung des LED-Default Bereichs

---

### Version 4 → 5 (25.03. 12:32 → 26.03. 14:03)

**Zeitdelta:** 1 Tag, 1 Stunde, 31 Minuten

**Kontext:**

- Diskussion über ACCESS Bytes (0x08)
- Schlege erklärt: "vergleichbar mit Key A und Key B"
- Franke-Missverständnis: "Sie setzen jetzt ja auch den Key A und Key B nach dessen Eingabe zu einen Datenblock
  zusammen"

**Vermutliche Änderung:**

- Klarstellung/Korrektur zum ACCESS Bytes Punkt (0x08)
- Möglicherweise Entfernung oder Anpassung des Punktes nach Klärung

---

## Zeitstatistik

| Metrik                     | Wert                                |
|----------------------------|-------------------------------------|
| Gesamtzeitraum             | 23.03.2026 08:36 → 26.03.2026 14:03 |
| Dauer gesamt               | 3 Tage, 5 Stunden, 27 Minuten       |
| Anzahl Iterationen         | 5 PDF-Versionen                     |
| Durchschnitt pro Iteration | ~19 Stunden                         |
| Schnellste Iteration       | V3→V4: 4h 42min                     |
| Längste Iteration          | V4→V5: 25h 31min                    |

## Wichtige Hinweise

### ⚠️ Lokale Datei veraltet

Die lokale Datei `Issue\_57\Software_Spezifikation_RFID_to_MBS_V04-2.pdf` entspricht **NICHT** der neuesten Version!

**Neueste Version:** Version 5 (File-ID: 26274894) vom 26.03.2026 14:03 Uhr

### 📋 Änderungen zwischen den Versionen

Alle Änderungen wurden von Franke angefordert und beziehen sich hauptsächlich auf:

1. **FB3 Tunnel Mode Einschränkungen:**
    - Automatismen müssen abgeschaltet werden
    - Baudrate-Telegramme müssen blockiert werden
    - LED-Verhalten kann nicht garantiert werden

2. **ACCESS Bytes (0x08):**
    - Diskussion über Implementierung
    - Vergleich mit Key A/B Handling
    - Möglicherweise Klarstellung in V5

### 🎯 Verwendung für Angebot

Für das Angebot sollte die **neueste Version 5** als Referenz verwendet werden:

- Alle Korrekturen und Klarstellungen sind eingearbeitet
- FB3 Einschränkungen klar definiert
- ACCESS Bytes Punkt (0x08) möglicherweise korrigiert

## Issue-Link

**GitHub Issue #57:** https://github.com/FrankeEDF/IOLink/issues/57

**Titel:** LED Ansteuerung unvollständig
