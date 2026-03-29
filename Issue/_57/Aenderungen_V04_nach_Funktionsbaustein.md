# Änderungswünsche V04 nach Funktionsbaustein

Alle blau markierten Änderungen aus der Software Spezifikation V04 (Datum 25.3.2026)

---

## Funktionsbaustein 0 (FB0)

### Default Einstellung
- **Die Statusanzeige ist OFF** (keine LED im Reader und Leuchtring braucht zu leuchten)

**Beschreibung:**
Der RFID Reader geht in den Offline Zustand. Im Gegensatz zu den anderen Funktionsbausteinen sind hier die LEDs komplett ausgeschaltet.

---

## Funktionsbaustein 1 (FB1)

### Steuer Code: 0x01
Abfrage der UID mit "Zyklisch senden"

### Default Einstellungen
1. **Die Statusanzeige wird über den Reader gesteuert und muss beim Aktivieren des Funktionsbaustein 1 grün leuchten**

**Beschreibung:**
- Beim Start/Aktivierung von FB1: LED grün
- LED-Steuerung erfolgt automatisch über den Reader (internes Reader-Management)
- FB1 ist der aktive Funktionsbaustein beim Systemneustart

---

## Funktionsbaustein 2 (FB2)

### Steuer Code: 0x02
Anwendung "Mifare Classic"

### Default Einstellungen

1. **Die Statusanzeige wird über den Reader gesteuert und muss beim Aktivieren des Funktionsbaustein 2 grün leuchten**

2. **Key A und Key B in den Registern sollen beim Einschalten immer FF FF FF FF FF FF haben**, da diese meistens im Transponder beim Auslieferungszustand so hinterlegt ist.

3. **ACCESS Bytes (neu hinzugefügt):**
   - **Steuercode: 0x08**
   - **Funktion: ACCESS Bytes werden übertragen**
   - Das ACCESS Byte wird nur im Transponder geändert, wenn sich die Daten im Register ändern
   - **Default Werte: 00 00 00**
   - Bytes 54-56 oder 118-120 im Speicherblock
   - Steuerung von Lese-/Schreibrechten auf Speicherblöcke
   - Vergleichbar mit Key A/Key B Handhabung

### Statusanzeige (Seite 3)

**Hinweis zur LED Offline-Funktion (Code 0x14):**
- **Der Offline-Betrieb ist aktiv wenn der Reader im Einzelsenden "ohne externer LED Ansteuerung" ist.**
- Im Offline-Betrieb (0x14) übernimmt der Reader die eigenständige Steuerung der LED-Farbgebung und Status-LED

**Zuordnung der Codes:**
- Farbe Offline: 0x14 - Die Farbgebung des LED Ringes und der Status LED wird über den Reader eigenständig angehandelt
- Farbe Blau: 0x16
- Farbe Grün: 0x17
- Farbe Türkis: 0x18
- Farbe OFF: 0x19 - Die Ausleuchtung der LED ist OFF

---

## Funktionsbaustein 3 (FB3)

### Steuer Code: 0x03
Tunnel Mode - Direkter Zugriff auf RFID Reader Kommandos

### Default Einstellungen

1. **Die Baudrate am Reader sollte immer in der Software beim Neustart auf 115200Baud eingestellt sein.**
   - **Das Verändern der Bausrate soll gesperrt werden so dass hier generell keine Änderung möglich ist.**
   - Grund: Sicherstellung der Kommunikation nach Neustart, falls Anwender die Baudrate über FB3 ändert

2. **Key A und Key B in den Registern sollen beim Einschalten immer FF FF FF FF FF FF haben**, da diese meistens im Transponder beim Auslieferungszustand so hinterlegt ist.

### Besonderheiten FB3

**Automatismen müssen abgeschaltet werden:**
- **Die Funktionen Zyklisch- und Einzel-Senden müssen hierzu abgeschaltet werden, da dieser Automatismus zwischen MBS-CPU (ATSAM) und dem Reader über die Datenstrecke bis zum Anwender nicht abbildbar ist.**
- **Der Automatismus in der Funktion Zyklisch- und Einzel-Senden am RFID-Reader kann hier abgeschaltet werden.**

**Grund:**
Im Tunnel Mode wird der komplette Datenstring vom Anwender zusammengestellt und durchgereicht. Die MBS-CPU weiß nicht, welche Telegramme ausgetauscht werden und in welchem Zustand sich der Reader befindet. Daher können keine automatischen Sendevorgänge parallel laufen.

---

## Allgemeine Default-Werte (übergreifend)

### Systemneustart Default-Werte:

Bei Systemneustart ist der Reader wie auch die Ansteuerung der LED's auf folgenden Default Werten:

- **Baudrate: 115200 kBd**
- **Zyklisch Senden: ON**
- **LED Statusanzeige: Erfolgt automatisch über den Reader**
- **Funktionsbaustein: FB1 ist aktiv**

### LED-Verhalten beim Funktionsbausteinwechsel:

**1.) Bei der Aktivierung bzw beim Wechsel zwischen den Funktionsblöcken soll beim Start die LED grün leuchten und die Farbgebung der LED´s soll über den Reader intern laufen, ausgenommen FB0 und FB3.**

**Bedeutung:**
- **FB1 und FB2:** LED grün beim Start, dann interne Reader-Steuerung (solange kein LED-Steuercode 0x14-0x19 gesendet wird)
- **FB0:** LED OFF (keine LED-Anzeige)
- **FB3:** Keine automatische LED-Steuerung (da alle Automatismen abgeschaltet)

---

## Zusammenfassung der Implementierungsanforderungen

### FB0 (Offline)
- [ ] LED Status auf OFF setzen

### FB1 (UID Abfrage)
- [ ] LED beim Start grün
- [ ] LED-Steuerung über Reader aktivieren
- [ ] FB1 als Default beim Systemneustart

### FB2 (Mifare Classic)
- [ ] LED beim Start grün
- [ ] LED-Steuerung über Reader aktivieren
- [ ] Key A/B Default: FF FF FF FF FF FF
- [ ] **ACCESS Bytes Funktion (0x08) implementieren**
- [ ] **ACCESS Bytes Default: 00 00 00**
- [ ] **LED Offline Funktion (0x14) implementieren** - Reader im Einzelsenden "ohne externe LED Ansteuerung"

### FB3 (Tunnel Mode)
- [ ] Baudrate fest auf 115200 Baud, Änderung sperren
- [ ] Key A/B Default: FF FF FF FF FF FF
- [ ] Zyklisch-Senden abschalten
- [ ] Einzel-Senden abschalten
- [ ] Keine automatische LED-Steuerung

### Systemneustart
- [ ] Baudrate: 115200 kBd
- [ ] Zyklisch Senden: ON
- [ ] LED über Reader
- [ ] FB1 aktivieren

---

## Hinweise zur LED Offline-Funktion (0x14)

**Technische Umsetzung:**

Laut Issue #57 Diskussion sollte über Kommandocode 0x23 (Einzelsenden) mit Byte 9 der Offline-Betrieb gesteuert werden:

- **Einzelsenden mit Reader-LED-Steuerung (Offline):**
  `50 00 05 23 FF 01 00 01 03 CRC`
  (Byte 9 = 0x03 aktiviert interne Reader-LED-Steuerung)

- **Einzelsenden ohne Reader-LED-Steuerung:**
  `50 00 05 23 FF 64 00 01 00 CRC`
  (Byte 9 = 0x00 deaktiviert interne Reader-LED-Steuerung)

**Unterschied:**
- **LED OFF (0x19):** Schaltet LEDs komplett aus
- **LED Offline (0x14):** Übergibt LED-Steuerung an den Reader (internes Management)
