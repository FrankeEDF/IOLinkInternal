# ACCESS Bytes - Finale Lösung (KORRIGIERT)

## Klarstellung: Keys haben KEINE doppelte Bedeutung!

### Aktuelles System (korrekt analysiert)

**Register 1010-1015 (Key A/B) werden NUR für Authentifizierung verwendet!**

```c
// In RfidControl::WriteBlock:
LoginAuthenticate(blockNr, useKeyB);  // Verwendet data_.keyA oder data_.keyB
WritePage(blockData, blockNr);        // Schreibt die übergebenen blockData (16 Bytes)
```

**Die 16 Bytes Block-Daten kommen immer vom Modbus (Register 1018-1025)!**

```c
// In modbusSlave.cpp:
case 1018:
    rfidControl.WriteBlock(buffer, block);  // buffer = die 16 Bytes aus Modbus
```

---

## Das bedeutet für Trailer-Blöcke

### Aktueller Zustand (funktioniert bereits!)

**Kunde KANN bereits Trailer-Blöcke schreiben:**

```python
# Schritt 1: Keys für Authentifizierung setzen
modbus.write_registers(1010, [0xFFFF, 0xFFFF, 0xFFFF])  # Auth Key A
modbus.write_registers(1013, [0xFFFF, 0xFFFF, 0xFFFF])  # Auth Key B

# Schritt 2: Block-Nummer
modbus.write_registers(1016, [0x0107])  # Block 7 mit Key B

# Schritt 3: Trailer-Daten MANUELL zusammenbauen
trailer_data = [
    0xFFFF, 0xFFFF, 0xFFFF,  # Neue Key A (6 Bytes) → Reg 1018-1020
    0x8877, 0x0078,          # ACCESS (3 Bytes) + 0x00 → Reg 1021-1022
    0xFFFF, 0xFFFF, 0xFFFF   # Neue Key B (6 Bytes) → Reg 1023-1025
]

# Schritt 4: Schreiben (mit alten Keys authentifizieren, neue Keys als Daten)
modbus.write_registers(1018, trailer_data)  # TRIGGER
```

**Das funktioniert perfekt!**
- Authentifizierung mit Register 1010-1015 (alte Keys)
- Daten aus Register 1018-1025 (neue Keys + ACCESS)

---

## Was will die V04-Spezifikation?

### Problem für den Kunden

**Kunde muss die 16 Bytes MANUELL zusammenbauen:**
- Bytes 0-5: Key A (welche? alte? neue?)
- Bytes 6-8: ACCESS Bits
- Byte 9: 0x00
- Bytes 10-15: Key B (welche? alte? neue?)

**Fehleranfällig und kompliziert!**

### Lösung: Komfort-Funktion

**Neue Register für Trailer-Block-DATEN:**
- 1040-1042: **Trailer Key A** (Keys die in den Trailer geschrieben werden)
- 1043-1045: **Trailer Key B** (Keys die in den Trailer geschrieben werden)
- 1030-1031: **ACCESS Bits**

**Wenn Trailer-Block geschrieben wird:**
Firmware baut die 16 Bytes automatisch zusammen!

---

## Implementierung

### Neue Register

```c
// In struct ControlData:
uint8_t authKeyA[6];      // Register 1010-1012: Für Authentifizierung
uint8_t authKeyB[6];      // Register 1013-1015: Für Authentifizierung
uint8_t trailerKeyA[6];   // Register 1040-1042: Für Trailer-Daten (NEU!)
uint8_t trailerKeyB[6];   // Register 1043-1045: Für Trailer-Daten (NEU!)
uint8_t accessBits[3];    // Register 1030-1031: Für Trailer-Daten (NEU!)
```

### Default-Werte bei Reset

```c
void Reset() {
    // Auth Keys (für Zugriff)
    const uint8_t defaultKey[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    memcpy(authKeyA, defaultKey, 6);
    memcpy(authKeyB, defaultKey, 6);

    // Trailer Keys (für Daten) = gleich wie Auth Keys
    memcpy(trailerKeyA, authKeyA, 6);
    memcpy(trailerKeyB, authKeyB, 6);

    // ACCESS Bits
    const uint8_t defaultAccess[] = {0x00, 0x00, 0x00};
    memcpy(accessBits, defaultAccess, 3);
}
```

### Modbus Handler

```c
// Bestehende Register (unverändert)
case 1010: // Auth Key A
    if (count == 3) {
        result = rfidControl.SetKeyA(buffer);
        // Auto-Copy zu Trailer Key A (Default-Verhalten)
        rfidControl.SetTrailerKeyA(buffer);
        amount = 3;
    }
    break;

case 1013: // Auth Key B
    if (count == 3) {
        result = rfidControl.SetKeyB(buffer);
        // Auto-Copy zu Trailer Key B (Default-Verhalten)
        rfidControl.SetTrailerKeyB(buffer);
        amount = 3;
    }
    break;

// Neue Register
case 1030: // ACCESS Bits (NEU!)
    if (count == 2) {
        uint8_t accessBits[3];
        accessBits[0] = buffer[0];
        accessBits[1] = buffer[1];
        accessBits[2] = buffer[2];
        result = rfidControl.SetAccessBits(accessBits);
        amount = 2;
    }
    break;

case 1040: // Trailer Key A (NEU!)
    if (count == 3) {
        result = rfidControl.SetTrailerKeyA(buffer);
        amount = 3;
    }
    break;

case 1043: // Trailer Key B (NEU!)
    if (count == 3) {
        result = rfidControl.SetTrailerKeyB(buffer);
        amount = 3;
    }
    break;

// Erweiterung für Register 1018
case 1018: // Block-Daten schreiben
    if (count == 8) {
        size_t block = rfidControl.GetBlockNumber();

        // Prüfen ob Trailer-Block
        if (isTrailerBlock(block)) {
            // AUTO-ASSEMBLY: 16 Bytes aus Registern zusammenbauen
            uint8_t trailerData[16];
            rfidControl.ReadTrailerKeyA(&trailerData[0]);
            rfidControl.ReadAccessBits(&trailerData[6]);
            trailerData[9] = 0x00;
            rfidControl.ReadTrailerKeyB(&trailerData[10]);

            // Schreiben (authentifiziert mit authKeyA/B)
            result = rfidControl.WriteBlock(trailerData, block);
        } else {
            // Normaler Block: buffer direkt verwenden
            result = rfidControl.WriteBlock(buffer, block);
        }
        amount = 8;
    }
    break;
```

### Helper-Funktion

```c
static bool isTrailerBlock(uint8_t blockNr) {
    // Trailer bei MIFARE 1K: 3, 7, 11, 15, ..., 63
    // Formel: (blockNr + 1) modulo 4 == 0
    return ((blockNr + 1) % 4) == 0;
}
```

---

## Verwendungs-Szenarien

### Szenario 1: Nur ACCESS Bits ändern (Keys bleiben gleich)

```python
# Auth Keys setzen
modbus.write_registers(1010, [0xFFFF, 0xFFFF, 0xFFFF])  # Auth = FF FF FF
modbus.write_registers(1013, [0xFFFF, 0xFFFF, 0xFFFF])

# Trailer Keys werden AUTO kopiert (sind jetzt auch FF FF FF)

# Nur ACCESS ändern
modbus.write_registers(1030, [0x7778, 0x0088])  # ACCESS = 78 77 88

# Schreiben
modbus.write_registers(1016, [0x0107])  # Block 7
modbus.write_registers(1018, [0x0000, ...])  # TRIGGER (Inhalt egal)

# Firmware schreibt in Trailer:
# - Key A:   FF FF FF FF FF FF (aus Trailer Reg 1040)
# - ACCESS:  78 77 88          (aus Reg 1030)
# - Key B:   FF FF FF FF FF FF (aus Trailer Reg 1043)
```

### Szenario 2: Keys UND ACCESS ändern

```python
# Alte Keys für Authentifizierung
modbus.write_registers(1010, [0xAAAA, 0xAAAA, 0xAAAA])  # Auth Key A = AA AA AA
modbus.write_registers(1013, [0xBBBB, 0xBBBB, 0xBBBB])  # Auth Key B = BB BB BB

# Neue Keys für Trailer-Daten
modbus.write_registers(1040, [0x1122, 0x3344, 0x5566])  # Trailer Key A = 11 22 33 44 55 66
modbus.write_registers(1043, [0x7788, 0x99AA, 0xBBCC])  # Trailer Key B = 77 88 99 AA BB CC

# ACCESS Bits
modbus.write_registers(1030, [0x7778, 0x0088])

# Schreiben
modbus.write_registers(1016, [0x0107])  # Block 7 mit Auth Key B
modbus.write_registers(1018, [0x0000, ...])  # TRIGGER

# Firmware macht:
# 1. Authentifizierung mit BB BB BB BB BB BB (aus Reg 1013)
# 2. Schreibt in Trailer:
#    - Key A:   11 22 33 44 55 66 (aus Reg 1040)
#    - ACCESS:  78 77 88          (aus Reg 1030)
#    - Key B:   77 88 99 AA BB CC (aus Reg 1043)
```

### Szenario 3: Keys ändern (vereinfacht mit Auto-Copy)

```python
# Neue Keys setzen
modbus.write_registers(1010, [0x1122, 0x3344, 0x5566])  # Auth + AUTO zu Trailer
modbus.write_registers(1013, [0x7788, 0x99AA, 0xBBCC])  # Auth + AUTO zu Trailer

# Trailer Keys sind jetzt automatisch gleich!

# ACCESS
modbus.write_registers(1030, [0x7778, 0x0088])

# Schreiben
modbus.write_registers(1016, [0x0107])
modbus.write_registers(1018, [0x0000, ...])

# Problem: Authentifizierung schlägt fehl!
# Transponder hat noch alte Keys (z.B. FF FF FF)
# Lösung: Erst mit alten Keys authentifizieren, dann neue setzen (siehe Szenario 2)
```

---

## Vorteile der Lösung

### ✅ Für Standard-Fall (Keys nicht ändern)

Kunde muss nur:
```python
modbus.write_registers(1030, [ACCESS])  # ACCESS setzen
modbus.write_registers(1016, [BLOCK])
modbus.write_registers(1018, [TRIGGER])
```

Keine manuelle 16-Byte-Zusammenstellung!

### ✅ Für komplexen Fall (Keys ändern)

Volle Kontrolle:
- Auth Keys ≠ Trailer Keys möglich
- Jeder Key einzeln setzbar

### ✅ Rückwärtskompatibel

Kunde kann weiterhin manuell 16 Bytes in 1018-1025 schreiben!

**Firmware erkennt:**
- Wenn Block-Nr = Trailer → Auto-Assembly
- Sonst → Daten aus Register verwenden

**ODER: Flag einführen?**

```c
// Option: Control-Byte in Register 1016 erweitern
// Bit 0: Use Key B
// Bit 1: Auto-Assemble Trailer (NEU!)

if ((data_.blockNumber >> 8) & 0x02) {
    // Auto-Assembly aktiv
    if (isTrailerBlock(block)) {
        // Zusammenbauen aus Registern
    }
} else {
    // Manuell: Daten aus 1018-1025
}
```

---

## Offene Fragen

1. **Auto-Copy bei Register 1010/1013?**
   - Soll das Setzen von Auth Keys automatisch Trailer Keys setzen?
   - Oder immer explizit über Register 1040/1043?

2. **Trigger-Mechanismus:**
   - Nur über Register 1018 (wie bisher)?
   - Oder auch über Register 1030 (ACCESS setzen)?

3. **Register-Nummern:**
   - 1030-1031: ACCESS Bits ✓
   - 1040-1042: Trailer Key A ✓
   - 1043-1045: Trailer Key B ✓
   - OK so?

4. **Beim Lesen eines Trailers:**
   - Sollen gelesene Werte in Register geschrieben werden?
   - Register 1030, 1040, 1043?
   - Oder nur in Read-Registern 2010-2017?

5. **Fehlerbehandlung:**
   - Modbus Exception wenn Trailer-Register beschrieben aber FB2 nicht aktiv?

---

## Implementierungs-Aufwand

### Code-Änderungen

**RfidControl.h:**
- 3 neue Member-Variablen
- 6 neue Funktionen (Set/Read für Trailer Keys und ACCESS)

**RfidControl.cpp:**
- 6 neue Funktionen implementieren
- Reset() erweitern

**modbusSlave.cpp:**
- 3 neue Case-Blöcke (1030, 1040, 1043)
- Case 1018 erweitern (if-isTrailerBlock)
- Helper-Funktion isTrailerBlock()

**Geschätzter Aufwand:** ~2-3 Stunden

### Test-Aufwand

- Test mit MIFARE Classic Transponder
- Test verschiedener Szenarien
- Dokumentation schreiben

**Geschätzter Aufwand:** ~2-3 Stunden

---

## Empfehlung

**Diese Lösung ist optimal weil:**

1. ✅ **Einfach für Standard-Fall** (nur ACCESS ändern)
2. ✅ **Mächtig für Komplexfall** (Keys ändern)
3. ✅ **Keine doppelte Bedeutung** von Registern
4. ✅ **Rückwärtskompatibel** (alte Methode funktioniert weiter)
5. ✅ **Klare Trennung** Auth vs. Daten
6. ✅ **Auto-Copy als Komfort** (optional)

**Wartet auf finale Bestätigung von Schlege:**
- Register-Nummern OK?
- Auto-Copy gewünscht?
- Trigger über 1018 oder 1030?
