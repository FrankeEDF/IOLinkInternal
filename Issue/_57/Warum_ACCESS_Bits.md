# Warum braucht man ACCESS Bits?

## Ihre Situation JETZT

Ihre Firmware kann **jeden Block lesen und schreiben** - perfekt! Das funktioniert, weil:

1. Die Transponder ab Werk mit **Standard-Keys** kommen:
   - Key A: FF FF FF FF FF FF
   - Key B: FF FF FF FF FF FF

2. Die ACCESS Bits sind auf **"alles erlaubt"** gesetzt

3. Ihre Firmware kennt diese Standard-Keys und kann zugreifen

**Das funktioniert einwandfrei - ABER nur bei ungeschützten Transpondern!**

---

## Das Problem in der Praxis

### Szenario: Kunde will Transponder SICHERN

Stellen Sie sich vor:

**Ein Kunde nutzt RFID-Transponder für:**
- Zugangskontrolle zu Maschinen
- Speicherung von Benutzerrechten
- Protokollierung von Maschinenlaufzeiten

**Problem:**
Jeder mit einem Handy (NFC-App) kann:
- ❌ Die Daten auslesen (Benutzerrechte sehen)
- ❌ Die Daten ändern (sich Admin-Rechte geben)
- ❌ Den Transponder kopieren

**Das ist ein Sicherheitsproblem!**

---

## Lösung: Transponder SPERREN

Der Kunde will den Transponder **schützen**:

### Variante 1: Nur noch mit eigenem Key zugreifbar

```
Der Kunde schreibt in den Trailer-Block:
  Key A:     AB CD EF 12 34 56  (Geheimer Key, nur Kunde kennt ihn)
  Key B:     78 9A BC DE F0 11  (Geheimer Key, nur Kunde kennt ihn)
  ACCESS:    78 77 88            (Key A/B erforderlich)
```

**Resultat:**
- ✅ Nur wer die Keys kennt, kann auf den Transponder zugreifen
- ✅ Fremde können nichts lesen oder schreiben
- ❌ **ABER: Ihre Firmware kann jetzt auch NICHT mehr zugreifen!**

---

## Wo kommen die ACCESS Bits ins Spiel?

### Problem des Kunden:

Der Kunde hat den Transponder gesichert, aber will trotzdem:
1. **Bestimmte Daten öffentlich lesbar** (z.B. Serien-Nummer in Block 4)
2. **Andere Daten geschützt** (z.B. Benutzerrechte in Block 8)
3. **Konfigurationsdaten nur mit Admin-Key änderbar** (Trailer-Block)

### Lösung mit ACCESS Bits:

Die ACCESS Bits steuern **pro Block**, was erlaubt ist:

```
Sektor 1 Konfiguration:
  Block 4:  [Serien-Nummer]     → ACCESS: Mit Key A lesbar, mit Key B schreibbar
  Block 5:  [Benutzer-Level]    → ACCESS: Mit Key A lesbar, mit Key B schreibbar
  Block 6:  [Geheim-Daten]      → ACCESS: NUR mit Key B lesbar UND schreibbar
  Block 7:  [Trailer]           → ACCESS: NUR mit Key B änderbar
            Key A:    AB CD EF 12 34 56
            ACCESS:   78 77 88  ← Definiert die Rechte!
            Key B:    78 9A BC DE F0 11
```

**Mit diesen ACCESS Bits:**
- Jemand mit Key A kann Block 4-5 **lesen** (z.B. für Anzeige)
- Nur jemand mit Key B kann Block 4-6 **schreiben** (Admin)
- Block 6 ist komplett versteckt ohne Key B

---

## Praktisches Beispiel aus der Industrie

### Anwendungsfall: Maschinenbedienung

**Transponder enthält:**
```
Block 4:  Mitarbeiter-ID           (öffentlich lesbar)
Block 5:  Berechtigungs-Level      (öffentlich lesbar)
Block 8:  Maschinen-Freischaltung  (nur Admin änderbar)
Block 12: Arbeitszeit-Protokoll    (nur Maschine schreibbar)
```

**Drei verschiedene Zugriffsstufen:**

1. **Jeder mit NFC-Handy (kein Key):**
   - Kann **nichts** lesen oder schreiben (Transponder ist "unsichtbar")

2. **Mitarbeiter-Terminal (hat Key A):**
   - Kann Mitarbeiter-ID und Level **lesen** → Anzeige auf Display
   - Kann **nicht** ändern → keine Manipulation möglich

3. **Admin-System (hat Key B):**
   - Kann **alles** lesen und schreiben
   - Kann Berechtigungen ändern
   - Kann Arbeitszeit auswerten

**Das wird durch ACCESS Bits gesteuert!**

---

## Was bedeutet das für Ihre Firmware?

### Aktuell (ohne ACCESS Bits Funktion):

Ihre Firmware arbeitet mit **Standard-Keys (FF FF FF FF FF FF)**.

**Das funktioniert bei:**
- ✅ Neuen, ungeschützten Transpondern
- ✅ Unkritischen Anwendungen
- ❌ **NICHT bei vom Kunden gesicherten Transpondern!**

### Mit ACCESS Bits Funktion (neu in V04):

Der Kunde kann über Ihr System:

1. **Eigene Keys setzen:**
   ```
   Register Key A: AB CD EF 12 34 56
   Register Key B: 78 9A BC DE F0 11
   ```

2. **ACCESS Bits konfigurieren:**
   ```
   Register ACCESS: 78 77 88
   ```

3. **Trailer-Block schreiben:**
   - Ihre Firmware nimmt die Werte aus den Registern
   - Schreibt alle 16 Bytes in den Trailer
   - Transponder ist jetzt **gesichert**!

4. **Zukünftiger Zugriff:**
   - Ihre Firmware muss die **gleichen Keys verwenden**
   - Sonst funktioniert nichts mehr!

---

## Konkrete Anforderung aus Issue #57

Aus den Kommentaren (Schlege):

> "über diese Bytes kann man diverse Funktionen beim Lesen und Schreiben auf den Speicherblock auslösen. eine Funktion hier ist z.B. dass der Speicherblock im Transponder **nicht sichtbar ist** und nur über Key A oder Key B sichtbar gemacht werden kann. **Aktuell kann man die Blockdaten mit jedem NFC tauglichen Handy auslesen.**"

**Das Problem:**
- Kundendaten sind ungeschützt
- Jeder kann mit Handy auslesen
- Kunde will Sicherheit!

**Die Lösung:**
- Kunde kann über Ihre Firmware ACCESS Bits setzen
- Transponder wird geschützt
- Nur autorisierte Systeme (mit Keys) können zugreifen

---

## Technische Umsetzung in Ihrer Firmware

### Was muss implementiert werden?

**Neuer Steuercode 0x08: ACCESS Bytes übertragen**

**Beim Schreiben des Trailer-Blocks:**

```c
// Register auslesen
uint8_t keyA[6];      // Register für Key A
uint8_t access[3];    // Register für ACCESS Bits (NEU!)
uint8_t keyB[6];      // Register für Key B

// 16-Byte Trailer-Block zusammenbauen
uint8_t trailerBlock[16];
memcpy(&trailerBlock[0], keyA, 6);      // Bytes 0-5
memcpy(&trailerBlock[6], access, 3);    // Bytes 6-8 (NEU!)
trailerBlock[9] = 0x00;                 // Byte 9 unbenutzt
memcpy(&trailerBlock[10], keyB, 6);     // Bytes 10-15

// An RFID Reader senden zum Schreiben in Trailer
sendToRfidReader(blockNr, trailerBlock, 16);
```

**Beim Lesen des Trailer-Blocks:**

```c
// 16 Bytes vom RFID Reader empfangen
uint8_t trailerBlock[16];
receiveFromRfidReader(blockNr, trailerBlock, 16);

// In Register aufteilen
memcpy(keyA, &trailerBlock[0], 6);      // Bytes 0-5
memcpy(access, &trailerBlock[6], 3);    // Bytes 6-8 (NEU!)
memcpy(keyB, &trailerBlock[10], 6);     // Bytes 10-15

// In Modbus-Register schreiben für Unigate IC
```

---

## Zusammenfassung

### Warum braucht man ACCESS Bits?

**Ohne ACCESS Bits:**
- Transponder ist ungeschützt
- Jeder kann Daten auslesen/ändern
- Keine Sicherheit

**Mit ACCESS Bits:**
- Transponder kann gesichert werden
- Verschiedene Zugriffsstufen möglich
- Nur autorisierte Systeme haben Zugriff

### Was ändert sich in Ihrer Firmware?

**Vorher:**
- Key A und Key B in Registern ✓
- Trailer-Block schreiben: 6 Bytes Key A + ?? + 6 Bytes Key B ❌
- ACCESS Bits waren undefiniert / 0x00 0x00 0x00

**Nachher (V04):**
- Key A und Key B in Registern ✓
- **ACCESS Bits in Register (NEU!)** ✓
- Trailer-Block schreiben: 6 Bytes Key A + **3 Bytes ACCESS** + 6 Bytes Key B ✓
- Kunde kann Transponder sichern ✓

---

## Praktischer Ablauf

### Schritt 1: Kunde will Transponder sichern

```
Modbus-Befehle an Ihre Firmware:
1. Schreibe Register Key A:    AB CD EF 12 34 56
2. Schreibe Register Key B:    78 9A BC DE F0 11
3. Schreibe Register ACCESS:   78 77 88  ← NEU!
4. Steuercode 0x81: Schreibe Trailer-Block
```

### Schritt 2: Ihre Firmware schreibt Trailer

```
Ihre Firmware:
- Liest alle 3 Register aus
- Baut 16-Byte Block zusammen
- Sendet an RFID Reader
- Transponder ist jetzt GESICHERT!
```

### Schritt 3: Zukünftiger Zugriff

```
Beim nächsten Lesen/Schreiben:
- Firmware MUSS die neuen Keys verwenden (AB CD... und 78 9A...)
- Sonst: RFID Reader meldet Fehler "Authentifizierung fehlgeschlagen"
```

---

## Die wichtige Erkenntnis

**Sie brauchen ACCESS Bits nicht für die Grundfunktion** (Lesen/Schreiben funktioniert ja schon).

**Sie brauchen ACCESS Bits, damit Ihr KUNDE den Transponder sichern kann!**

Es ist eine **Security-Funktion für den Endkunden**, nicht für Ihre Firmware.

Ohne diese Funktion kann Ihr Kunde **keine gesicherten RFID-Anwendungen** bauen.

---

## Offene Fragen für die Implementierung

1. **Wo werden die ACCESS Bits Register abgelegt?**
   - Neue Modbus-Register-Nummer?

2. **Was passiert mit den Keys in der Firmware?**
   - Werden die geänderten Keys persistent gespeichert?
   - Oder muss der Kunde sie bei jedem Zugriff neu setzen?

3. **Default-Werte beim Start?**
   - Key A: FF FF FF FF FF FF ✓
   - Key B: FF FF FF FF FF FF ✓
   - ACCESS: 00 00 00 (oder besser FF 07 80?)

Diese Punkte sollten mit dem Kunden (Schlege) geklärt werden!
