# ACCESS Bytes - KORREKTUR meiner Erklärung

## Sie haben VOLLKOMMEN RECHT!

Ich habe einen fundamentalen Fehler gemacht in meiner Erklärung!

## Die Fakten aus dem Datenblatt

### 1. Key A und Key B gibt es NUR EINMAL (global für alle Operationen)

**Aus der Spezifikation V04:**
```
0x06  Key A wird übertragen
0x07  Key B wird übertragen
```

Das sind **GLOBALE** Register in Ihrer Firmware, die für **ALLE** Lese-/Schreiboperationen verwendet werden!

### 2. ACCESS Bytes gibt es in JEDEM Sektor im Trailer-Block

**Aus dem RFID Datenblatt (Seite 12):**

```
MIFARE 1K: 16 Sektoren

Sektor 0:  Block 3  (Trailer) → enthält ACCESS Bytes für Sektor 0
Sektor 1:  Block 7  (Trailer) → enthält ACCESS Bytes für Sektor 1
Sektor 2:  Block 11 (Trailer) → enthält ACCESS Bytes für Sektor 2
...
Sektor 15: Block 63 (Trailer) → enthält ACCESS Bytes für Sektor 15
```

**Jeder Sektor hat seinen eigenen Trailer-Block mit eigenen ACCESS Bytes!**

### 3. ACCESS Bytes sind TEIL DES BLOCKS, nicht Teil des Telegramms!

Sie haben völlig recht:
- ❌ ACCESS Bytes werden NICHT im Telegramm übertragen
- ✅ ACCESS Bytes sind DATEN IM BLOCK selbst

---

## Was bedeutet Steuercode 0x08 ACCESS Bytes?

Schauen wir nochmal in die Spezifikation V04 Seite 2:

```
Funktion: Schreib / Lese Parameter

0x06  Key A wird übertragen
0x07  Key B wird übertragen
0x08  ACCESS Bytes werden übertragen
      Das ACCESS Byte wird nur im Transponder geändert, wenn sich die Daten im Register ändern.
      Default Werte: 00 00 00
```

### INTERPRETATION (korrigiert):

Der Steuercode 0x08 bedeutet **NICHT** "sende ACCESS Bytes im Telegramm"!

Er bedeutet: **"Wenn du einen Trailer-Block schreibst, nimm die ACCESS Bytes aus diesem Register!"**

---

## Wie funktioniert es WIRKLICH?

### Szenario: Kunde will Trailer-Block von Sektor 5 beschreiben

**Schritt 1: Parameter in Register setzen**

```
Modbus-Register setzen:
- Register für Key A:      FF FF FF FF FF FF  (Steuercode 0x06)
- Register für Key B:      FF FF FF FF FF FF  (Steuercode 0x07)
- Register für ACCESS:     78 77 88           (Steuercode 0x08)
```

**Schritt 2: Trailer-Block schreiben (Steuercode 0x81)**

```
Kunde sendet:
- Steuercode: 0x81 (Schreibe Block)
- Block-Nummer: 23 (Trailer von Sektor 5)
- 16 Bytes Daten für Block 23
```

**Schritt 3: Ihre Firmware bereitet Daten vor**

```c
// Wenn Block-Nummer ein Trailer-Block ist (3, 7, 11, 15, ...)
if (isTrailerBlock(blockNr)) {
    // 16 Bytes aus den Registern zusammenbauen:
    trailerData[0..5]   = keyA_Register;     // 0x06
    trailerData[6..8]   = access_Register;   // 0x08 ← HIER!
    trailerData[9]      = 0x00;              // unbenutzt
    trailerData[10..15] = keyB_Register;     // 0x07
}
```

**Schritt 4: An RFID Reader senden**

```
RFID Telegram (Beispiel):
50 00 11 18 17 FF 64 FF FF FF FF FF 78 77 88 00 FF FF FF FF FF FF xx CRC
│  │  │  │  │  └─────────────────────────────────────────┘
│  │  │  │  │              16 Bytes Block-Daten
│  │  │  │  └─ Block 23
│  │  │  └─ Command 0x18 (Write)
│  │  └─ Länge
│  └─ 00
└─ 50 (Header)

Die 16 Bytes ENTHALTEN die ACCESS Bytes als Teil der Blockdaten!
```

---

## Der Unterschied zu Key A/B

### Key A und Key B (0x06, 0x07)

**Zwei Verwendungen:**

**1. Als Parameter für Authentifizierung (bei JEDEM Zugriff):**
```
Beim Lesen von Block 5:
- Firmware nimmt Key B aus Register (0x07)
- Sendet ans RFID-Telegramm zur Authentifizierung
- Reader authentifiziert sich beim Transponder
- Block 5 wird gelesen
```

**2. Als Daten beim Schreiben des Trailer-Blocks:**
```
Beim Schreiben von Block 7 (Trailer):
- Firmware nimmt Key A aus Register (0x06)
- Firmware nimmt Key B aus Register (0x07)
- Baut 16-Byte Block zusammen (inkl. Keys)
- Sendet als Blockdaten
```

### ACCESS Bytes (0x08)

**Nur EINE Verwendung:**

**Nur als Daten beim Schreiben des Trailer-Blocks:**
```
Beim Schreiben von Block 7 (Trailer):
- Firmware nimmt ACCESS aus Register (0x08)
- Baut 16-Byte Block zusammen (inkl. ACCESS)
- Sendet als Blockdaten
```

❌ ACCESS Bytes werden NIEMALS zur Authentifizierung verwendet!
❌ ACCESS Bytes sind KEIN Parameter im Telegramm!
✅ ACCESS Bytes sind nur DATEN im Trailer-Block!

---

## Ihre Fragen beantwortet

### "Im Datenblatt sind die ACCESS Bytes nur als Inhalt eines Blocks beschrieben"

✅ **RICHTIG!** Sie sind Teil der 16 Bytes Blockdaten im Trailer.

### "In keinem Telegramm brauch ich die Information zusätzlich"

✅ **RICHTIG!** ACCESS Bytes sind kein separater Parameter, sondern Teil der Nutzdaten.

### "Außerdem gibt's die ACCESS Bytes öfter / Key A und B nur einmal"

✅ **RICHTIG!**
- ACCESS Bytes: Pro Sektor unterschiedlich (16x bei MIFARE 1K)
- Key A/B: Global in Firmware-Registern (1x)

---

## Was muss Ihre Firmware WIRKLICH tun?

### Option 1: NUR beim Schreiben von Trailer-Blöcken

```c
void writeBlock(uint8_t blockNr, uint8_t* data, uint8_t len) {

    if (isTrailerBlock(blockNr)) {
        // Trailer-Block: Daten aus Registern zusammenbauen
        uint8_t trailerData[16];
        memcpy(&trailerData[0], keyA_Register, 6);      // 0x06
        memcpy(&trailerData[6], access_Register, 3);    // 0x08
        trailerData[9] = 0x00;
        memcpy(&trailerData[10], keyB_Register, 6);     // 0x07

        sendToRfid(blockNr, trailerData, 16);
    } else {
        // Normaler Datenblock: Daten direkt senden
        sendToRfid(blockNr, data, len);
    }
}
```

### Option 2: Kunde gibt ALLE 16 Bytes vor (einfacher!)

**Alternative Interpretation:**

Vielleicht will der Kunde **gar nicht** die Daten aus Registern zusammenbauen lassen?

**Vielleicht bedeutet es:**

```
Steuercode 0x06: "Key A im Trailer ist ab jetzt FF FF FF FF FF FF"
Steuercode 0x07: "Key B im Trailer ist ab jetzt FF FF FF FF FF FF"
Steuercode 0x08: "ACCESS im Trailer ist ab jetzt 78 77 88"
```

Dann beim Schreiben des Trailer (0x81):
- Firmware baut die 16 Bytes automatisch zusammen
- Kunde muss nicht die kompletten 16 Bytes senden

**ODER:**

Kunde sendet einfach alle 16 Bytes direkt beim Schreiben?

---

## Die eigentliche Frage an den Kunden (Schlege)

Aus Issue #57 fehlen wichtige Details:

### Was soll beim Lesen eines Trailer-Blocks passieren?

**Variante A: Aufspalten**
```
Firmware liest Block 7 (16 Bytes):
FF FF FF FF FF FF 78 77 88 00 FF FF FF FF FF FF

Firmware schreibt in Register:
- Register Key A:     FF FF FF FF FF FF
- Register ACCESS:    78 77 88
- Register Key B:     FF FF FF FF FF FF
```

**Variante B: Als Block durchreichen**
```
Firmware liest Block 7 (16 Bytes):
FF FF FF FF FF FF 78 77 88 00 FF FF FF FF FF FF

Firmware schreibt in Modbus-Register:
- Register 2010-2017: Alle 16 Bytes
```

### Was soll beim Schreiben eines Trailer-Blocks passieren?

**Variante A: Aus Einzelregistern zusammenbauen**
```
Kunde setzt:
- Register Key A (0x06)
- Register ACCESS (0x08)
- Register Key B (0x07)

Firmware baut automatisch 16 Bytes zusammen.
```

**Variante B: Kunde sendet 16 Bytes direkt**
```
Kunde setzt:
- Register 1000-1007: Alle 16 Bytes

Firmware schreibt direkt.
```

---

## Meine Vermutung (korrigiert)

Basierend auf der Spezifikation:

```
0x06  Key A wird übertragen
0x07  Key B wird übertragen
0x08  ACCESS Bytes werden übertragen
```

**Vermutung:**

Diese Steuercodes bedeuten **NICHT** separate Operationen!

Sie sind **PARAMETER-REGISTER**, die beim Schreiben/Lesen von Trailer-Blöcken verwendet werden:

```
Ablauf:
1. Kunde setzt Register für Key A, Key B, ACCESS
2. Kunde sendet Steuercode 0x81 + Block-Nummer (Trailer)
3. Firmware erkennt: "Ah, das ist ein Trailer!"
4. Firmware baut 16 Bytes zusammen aus den Registern
5. Firmware sendet an RFID Reader
```

---

## Was Sie jetzt prüfen sollten

### Im vorhandenen Code schauen:

1. **Wie werden Key A und Key B (0x06, 0x07) aktuell behandelt?**
   - Gibt es schon Register dafür?
   - Werden sie beim Trailer-Schreiben verwendet?

2. **Kann man bereits Trailer-Blöcke schreiben?**
   - Wenn ja: Wie werden die 16 Bytes zusammengebaut?
   - Wenn nein: Das wäre dann die neue Funktion!

3. **Gibt es bereits eine Block-Schreib-Funktion (0x81)?**
   - Wie sehen die Daten aus, die der Kunde sendet?

Soll ich im Code nachschauen, wie Key A/B aktuell implementiert sind?
