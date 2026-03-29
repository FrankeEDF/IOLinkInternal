# ACCESS Bytes Implementierung - Optionen und Empfehlung

## Status
**OFFEN** - Wartet auf Antwort von Schlege zur genauen Spezifikation

## Problem-Analyse

### Aktuelles System

**Schreiben eines MIFARE Blocks (Register 1018-1025):**

1. Register 1010-1012: Key A setzen (wird intern gespeichert, kein RFID-Zugriff)
2. Register 1013-1015: Key B setzen (wird intern gespeichert, kein RFID-Zugriff)
3. Register 1016: Block-Nummer + Key-Auswahl (wird intern gespeichert)
4. **Register 1018-1025: 16 Bytes Daten → LÖST RFID-SCHREIBVORGANG AUS!**

**Quelle:** `C:\git\Schlegel\IOLink\documentation\Modbus\MultiIO_RFID_MIFARE_Block_Write.md`

### Trailer-Block Struktur

```
Trailer-Block (16 Bytes):
┌─────────────────────────────────────────────────┐
│ Byte 0-5   │ Byte 6-8     │ Byte 9  │ Byte 10-15│
│ Key A      │ ACCESS Bits  │ 0x00    │ Key B     │
│ (6 Bytes)  │ (3 Bytes)    │(unused) │ (6 Bytes) │
└─────────────────────────────────────────────────┘
```

**Problem:**
- Key A und Key B werden für **Authentifizierung** verwendet (in Register 1010-1015)
- Beim Schreiben eines **Trailer-Blocks** müssen sie auch als **Daten** verwendet werden
- ACCESS Bits sind **nur Daten** (nur im Trailer-Block)
- Aktuell: Kunde muss alle 16 Bytes manuell zusammenbauen und in 1018-1025 schreiben

### Was fordert die V04-Spezifikation?

**Seite 2, Funktionsbaustein 2:**

```
0x06  Key A wird übertragen
0x07  Key B wird übertragen
0x08  ACCESS Bytes werden übertragen
      Das ACCESS Byte wird nur im Transponder geändert, wenn sich die Daten im Register ändern.
      Default Werte: 00 00 00
```

**Interpretation:**
- Neue Register für ACCESS Bytes hinzufügen
- Beim Schreiben eines Trailer-Blocks sollen diese verwendet werden

---

## Implementierungs-Optionen

### Option A: Register 1018-1025 als Trigger (EMPFOHLEN)

**Neue Register:**
- **Register 1030-1031**: ACCESS Bytes (3 Bytes + 1 Padding)

**Ablauf für Kunde:**

```python
# Trailer von Sektor 1 (Block 7) schreiben:

# 1. Keys setzen (für Authentifizierung UND Daten)
modbus.write_registers(1010, [0xFFFF, 0xFFFF, 0xFFFF])  # Key A

# 2. ACCESS Bytes setzen (NEU!)
modbus.write_registers(1030, [0x7778, 0x0088])          # 78 77 88 00

# 3. Keys setzen (für Daten im Trailer)
modbus.write_registers(1013, [0xFFFF, 0xFFFF, 0xFFFF])  # Key B

# 4. Block-Nummer
modbus.write_registers(1016, [0x0007])                   # Block 7 (Trailer)

# 5. TRIGGER durch Schreiben auf 1018-1025
# Bei Trailer-Block: Inhalt wird IGNORIERT, Firmware baut automatisch zusammen
modbus.write_registers(1018, [0x0000, 0x0000, 0x0000, 0x0000,
                               0x0000, 0x0000, 0x0000, 0x0000])
```

**Firmware-Logik in `modbusSlave.cpp`:**

```c
case 1018: // Block-Daten schreiben (wie bisher)
    if (count == 8) {
        size_t block = rfidControl.GetBlockNumber();

        if (isTrailerBlock(block)) {
            // Trailer-Block: Automatisch aus Registern zusammenbauen
            uint8_t trailerData[16];
            rfidControl.ReadKeyA(&trailerData[0]);       // Reg 1010-1012
            rfidControl.ReadAccessBits(&trailerData[6]); // Reg 1030-1031 (NEU!)
            trailerData[9] = 0x00;                       // Unbenutzt
            rfidControl.ReadKeyB(&trailerData[10]);      // Reg 1013-1015

            result = rfidControl.WriteBlock(trailerData, block);
        } else {
            // Normaler Daten-Block: buffer direkt verwenden
            result = rfidControl.WriteBlock(buffer, block);
        }
        amount = 8;
    }
    break;

case 1030: // ACCESS Bytes setzen (NEU!)
    if (count == 2) {
        uint8_t accessBits[3];
        accessBits[0] = buffer[0];
        accessBits[1] = buffer[1];
        accessBits[2] = buffer[2];
        // buffer[3] ist Padding (0x00)

        result = rfidControl.SetAccessBits(accessBits);
        amount = 2;
    }
    break;
```

**Neue Funktionen in `RfidControl.h/cpp`:**

```c
// In struct ControlData:
uint8_t accessBits[3];  // NEU!

// Neue Funktionen:
bool SetAccessBits(const uint8_t *accessBits);
bool ReadAccessBits(uint8_t *accessBits) const;

// In Reset():
const uint8_t defaultAccessBits[] = {0x00, 0x00, 0x00};
memcpy(accessBits, defaultAccessBits, sizeof(accessBits));
```

**Helper-Funktion:**

```c
bool isTrailerBlock(uint8_t blockNr) {
    // Trailer-Blöcke bei MIFARE 1K: 3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63
    // Formel: (blockNr + 1) % 4 == 0
    return ((blockNr + 1) % 4) == 0;
}
```

**Vorteile:**
- ✅ Kein neues Trigger-Register nötig
- ✅ Konsistent mit bestehendem System
- ✅ Register 1018-1025 bleibt der Trigger
- ✅ Kunde kann weiterhin normale Blöcke wie gewohnt schreiben
- ✅ Bei Trailer-Blöcken automatisches Zusammenbauen

**Nachteile:**
- ⚠️ Register 1018-1025 haben doppelte Bedeutung (normal vs. Trailer)
- ⚠️ Bei Trailer-Blöcken wird der Inhalt von 1018-1025 ignoriert

---

### Option B: Schreiben der ACCESS Bytes als Trigger (ALTERNATIVE)

**Neue Register:**
- **Register 1030-1031**: ACCESS Bytes (3 Bytes + 1 Padding) + **TRIGGER!**

**Ablauf für Kunde:**

```python
# 1. Keys setzen
modbus.write_registers(1010, [0xFFFF, 0xFFFF, 0xFFFF])  # Key A
modbus.write_registers(1013, [0xFFFF, 0xFFFF, 0xFFFF])  # Key B

# 2. Block-Nummer
modbus.write_registers(1016, [0x0007])                   # Block 7

# 3. ACCESS Bytes setzen → LÖST SOFORT SCHREIBVORGANG AUS!
modbus.write_registers(1030, [0x7778, 0x0088])          # TRIGGER!
```

**Firmware-Logik in `modbusSlave.cpp`:**

```c
case 1030: // ACCESS Bytes setzen + Trailer schreiben
    if (count == 2) {
        uint8_t accessBits[3];
        accessBits[0] = buffer[0];
        accessBits[1] = buffer[1];
        accessBits[2] = buffer[2];

        // Speichern
        rfidControl.SetAccessBits(accessBits);

        // SOFORT Trailer-Block schreiben
        size_t block = rfidControl.GetBlockNumber();
        if (isTrailerBlock(block)) {
            uint8_t trailerData[16];
            rfidControl.ReadKeyA(&trailerData[0]);
            memcpy(&trailerData[6], accessBits, 3);
            trailerData[9] = 0x00;
            rfidControl.ReadKeyB(&trailerData[10]);

            result = rfidControl.WriteBlock(trailerData, block);
        }
        amount = 2;
    }
    break;
```

**Vorteile:**
- ✅ Klarer Trigger: "ACCESS Bytes setzen = Trailer schreiben"
- ✅ Konsistent mit LED-Control (Register 1027)
- ✅ Weniger Code-Änderungen in Register 1018-Handler
- ✅ Register 1018-1025 behalten ihre ursprüngliche Bedeutung

**Nachteile:**
- ⚠️ Schreibt SOFORT beim Setzen der ACCESS Bytes (keine Kontrolle über Timing)
- ⚠️ Kunde kann nicht mehr normal auf Trailer-Blöcke schreiben (nur über ACCESS-Register)
- ⚠️ Was passiert wenn ACCESS Bytes gesetzt werden, aber Block kein Trailer ist?

---

### Option C: Separates Trigger-Register

**Neue Register:**
- **Register 1030-1031**: ACCESS Bytes (3 Bytes + 1 Padding, nur speichern)
- **Register 1032**: Trigger "Schreibe Trailer-Block"

**Ablauf für Kunde:**

```python
# 1. Keys und ACCESS Bytes vorbereiten
modbus.write_registers(1010, [0xFFFF, 0xFFFF, 0xFFFF])  # Key A
modbus.write_registers(1030, [0x7778, 0x0088])          # ACCESS
modbus.write_registers(1013, [0xFFFF, 0xFFFF, 0xFFFF])  # Key B

# 2. Block-Nummer
modbus.write_registers(1016, [0x0007])

# 3. Trigger
modbus.write_registers(1032, [0x0001])  # Schreibe Trailer-Block
```

**Vorteile:**
- ✅ Klare Trennung zwischen Daten und Normal-Blöcken
- ✅ Volle Kontrolle über Timing

**Nachteile:**
- ⚠️ Zusätzliches Register nötig
- ⚠️ Komplexeres API für den Kunden

---

## Empfehlung

### **Option A** ist am besten, ABER mit Verbesserung:

**Kombination aus Option A + Option B:**

1. **Register 1030-1031**: ACCESS Bytes setzen (speichern, kein Trigger)

2. **Zwei Wege zum Trigger:**

   **Weg 1: Für normale Blöcke (wie bisher)**
   ```python
   modbus.write_registers(1018, [Daten...])  # Normal-Block
   ```

   **Weg 2: Für Trailer-Blöcke (NEU)**
   ```python
   # Variante 2a: Über Register 1030 (ACCESS Bytes schreiben triggert)
   modbus.write_registers(1030, [0x7778, 0x0088])

   # ODER Variante 2b: Über Register 1018 (Auto-Zusammenbau)
   modbus.write_registers(1018, [0x0000, ...])  # Inhalt egal bei Trailer
   ```

**Firmware-Logik:**

```c
case 1030: // ACCESS Bytes
    if (count == 2) {
        uint8_t accessBits[3];
        accessBits[0] = buffer[0];
        accessBits[1] = buffer[1];
        accessBits[2] = buffer[2];

        rfidControl.SetAccessBits(accessBits);

        // OPTIONAL: Wenn Block-Nummer ein Trailer ist → SOFORT schreiben
        size_t block = rfidControl.GetBlockNumber();
        if (isTrailerBlock(block)) {
            // Auto-Trigger für Trailer-Blöcke
            uint8_t trailerData[16];
            // ... zusammenbauen ...
            result = rfidControl.WriteBlock(trailerData, block);
        }
        amount = 2;
    }
    break;

case 1018: // Block-Daten
    if (count == 8) {
        size_t block = rfidControl.GetBlockNumber();

        if (isTrailerBlock(block)) {
            // Trailer: Aus Registern zusammenbauen (Inhalt von 1018 ignoriert)
            uint8_t trailerData[16];
            // ... zusammenbauen aus 1010, 1030, 1013 ...
            result = rfidControl.WriteBlock(trailerData, block);
        } else {
            // Normal: buffer verwenden
            result = rfidControl.WriteBlock(buffer, block);
        }
        amount = 8;
    }
    break;
```

---

## Offene Fragen an Schlege

1. **Welcher Trigger soll verwendet werden?**
   - a) Register 1018-1025 (wie normale Blöcke)?
   - b) Register 1030-1031 (ACCESS Bytes schreiben)?
   - c) Beide Wege möglich?

2. **Was passiert bei normalem Block?**
   - Wenn ACCESS Bytes in Register 1030 gesetzt sind, aber Block-Nummer ist KEIN Trailer?
   - Sollen ACCESS Bytes ignoriert werden?

3. **Welche Register-Nummer für ACCESS Bytes?**
   - Vorschlag: 1030-1031 (nach Key B bei 1013-1015)

4. **Fehlerbehandlung:**
   - Modbus Exception wenn ACCESS Bytes gesetzt werden aber FB2 nicht aktiv?
   - Wie bei Key A/B (laut Dokumentation)?

5. **Beim Lesen eines Trailer-Blocks:**
   - Sollen ACCESS Bits automatisch in Register 1030-1031 geschrieben werden?
   - Oder bleiben sie Teil der 16 Bytes in Register 2010-2017 (Read-Register)?

---

## Benötigte Code-Änderungen

### 1. `RfidControl.h`

```c
// In struct ControlData hinzufügen:
uint8_t accessBits[3];  // NEU! Default: 00 00 00

// In Reset():
const uint8_t defaultAccessBits[] = {0x00, 0x00, 0x00};
memcpy(accessBits, defaultAccessBits, sizeof(accessBits));

// Neue Funktionen deklarieren:
bool SetAccessBits(const uint8_t *accessBits);
bool ReadAccessBits(uint8_t *accessBits) const;
```

### 2. `RfidControl.cpp`

```c
bool RfidControl::SetAccessBits(const uint8_t *accessBits)
{
    ON_DEBUG(printf("SetAccessBits\n"));
    if (!accessBits)
        return false;

    EnterCritical();
    memcpy(data_.accessBits, accessBits, sizeof(data_.accessBits));
    ExitCritical();

    return true;
}

bool RfidControl::ReadAccessBits(uint8_t *accessBits) const
{
    ON_DEBUG(printf("ReadAccessBits\n"));
    if (!accessBits)
        return false;

    EnterCritical();
    memcpy(accessBits, data_.accessBits, sizeof(data_.accessBits));
    ExitCritical();

    return true;
}

// Helper-Funktion
static bool isTrailerBlock(uint8_t blockNr)
{
    // Trailer bei MIFARE 1K: Blöcke 3, 7, 11, 15, ..., 63
    return ((blockNr + 1) % 4) == 0;
}
```

### 3. `modbusSlave.cpp`

```c
// Neuer Case für ACCESS Bytes
case 1030: // 3 Bytes, 2 Register: ACCESS Bits
    if (count == 2)
    {
        uint8_t accessBits[3];
        accessBits[0] = buffer[0];
        accessBits[1] = buffer[1];
        accessBits[2] = buffer[2];

        result = rfidControl.SetAccessBits(accessBits);

        // OPTIONAL: Auto-Trigger für Trailer-Blöcke
        // (je nach Antwort von Schlege)

        amount = 2;
    }
    break;

// Erweitern von Case 1018
case 1018: // Block-Daten
    if (count == 8)
    {
        size_t block = rfidControl.GetBlockNumber();

        if (isTrailerBlock(block)) {
            // Trailer-Block: Aus Registern zusammenbauen
            uint8_t trailerData[16];
            uint8_t keyA[6], keyB[6], accessBits[3];

            rfidControl.ReadKeyA(keyA);
            rfidControl.ReadAccessBits(accessBits);
            rfidControl.ReadKeyB(keyB);

            memcpy(&trailerData[0], keyA, 6);
            memcpy(&trailerData[6], accessBits, 3);
            trailerData[9] = 0x00;
            memcpy(&trailerData[10], keyB, 6);

            result = rfidControl.WriteBlock(trailerData, block);
        } else {
            // Normaler Block
            result = rfidControl.WriteBlock(buffer, block);
        }
        amount = 8;
    }
    break;
```

### 4. Dokumentation erstellen

- `MultiIO_RFID_MIFARE_Trailer_Write.md` (analog zu existing Block_Write.md)
- Update zu `ModbusSpecRFID_Add.md` mit Register 1030-1031

---

## Nächste Schritte

1. ⏳ **Antwort von Schlege abwarten** zu den offenen Fragen
2. ⏳ Entscheidung über Trigger-Mechanismus
3. ⏳ Register-Nummer für ACCESS Bytes bestätigen
4. 🔲 Code implementieren
5. 🔲 Testen mit MIFARE Classic Transponder
6. 🔲 Dokumentation schreiben

---

## Zusammenfassung

**Empfohlene Lösung:**
- Neue Register 1030-1031 für ACCESS Bytes
- Beim Schreiben von Trailer-Blöcken (über Reg 1018 oder 1030) automatisch aus Registern zusammenbauen
- Helper-Funktion `isTrailerBlock()` zur Erkennung
- Default-Werte: 00 00 00

**Status:** Wartet auf Spezifikation von Schlege
