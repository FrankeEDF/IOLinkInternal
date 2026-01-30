# 🐞 Git Issue – Anleitung & Bug Report (Firmware)

## Wie schreibe ich ein gutes Git Issue?

Ein gutes Issue hilft anderen (und dir selbst), ein Problem **schnell zu verstehen, nachzustellen und zu beheben**.
Gerade bei Firmware-Problemen sind **klare Struktur und technische Details** entscheidend.

### 1. Titel
Der Titel sollte kurz und präzise beschreiben, **was nicht funktioniert**.

**Gute Beispiele:**
- UART RX hängt nach Wakeup aus Sleep
- I2C Timeout bei hoher Buslast

**Schlechte Beispiele:**
- Bug
- Problem
- Firmware kaputt
- Kommunikationsproblem

---

### 2. Inhalt & Struktur
Nutze klar getrennte Abschnitte:
- Was ist kaputt?
- Was wäre korrektes Verhalten?
- Wie kann man es reproduzieren?
- In welcher Umgebung tritt es auf?

Je leichter ein anderer Entwickler das Problem **nachstellen** kann, desto schneller wird es gelöst.

---

### 3. Stil & Ton
- Sachlich und technisch schreiben
- Keine Schuldzuweisungen oder Bewertungen
- **Keine persönlichen Ansprachen** (z. B. „@Max kannst du mal…", „Lieber Entwickler…")
  → Issues sind technische Dokumentation, keine Direktnachrichten
- Annahmen klar als solche kennzeichnen
- Lieber zu viele Informationen als zu wenige

---

### 4. Ein Ticket = Ein Thema
- **Jedes Issue sollte nur ein einzelnes Problem behandeln**
- Keine Sammlung verschiedener Themen in einem Ticket
- Bei mehreren unabhängigen Problemen → mehrere separate Issues erstellen
- Vorteile:
  - Klarere Nachverfolgbarkeit
  - Einfacheres Schließen einzelner Probleme
  - Bessere Übersicht im Issue-Tracker
  - Gezieltere Diskussionen und Lösungen

---

## Bug Report – Firmware

## Titel
Der Titel sollte kurz und präzise beschreiben, **was nicht funktioniert**.

### Beschreibung
Kurze und klare Beschreibung des Problems.

> Beispiel:
> Nach dem Aufwachen aus dem Sleep-Modus empfängt die Firmware keine UART-Daten mehr.

---

### Erwartetes Verhalten
Beschreibe, was die Firmware stattdessen tun sollte.

> Beispiel:
> UART RX sollte nach dem Wakeup wieder normal funktionieren.

---

### Tatsächliches Verhalten
Was passiert aktuell stattdessen?

> Beispiel:
> RX-Interrupt wird nicht mehr ausgelöst, FIFO bleibt leer.

---

### Schritte zur Reproduktion
So kann das Problem reproduziert werden:

1. Firmware flashen
2. Gerät in Sleep-Modus versetzen
3. Wakeup über GPIO auslösen
4. UART-Daten senden

---

### Umgebung
Bitte so detailliert wie möglich ausfüllen:

- MCU:
- Board / HW-Revision:
- Firmware-Version / Commit:
- Toolchain / Compiler:
- RTOS (falls vorhanden):
- Peripherie-Konfiguration (z. B. UART, I2C, SPI):
- Takt / Power-Modus (falls relevant):

### Zusätzliche Informationen
Alles, was beim Debuggen helfen könnte:

- Log-Ausgaben
- Register-Dumps
- Messungen (Scope / Logic Analyzer)
- Vermutete Ursache oder erste Analyse
