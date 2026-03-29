# Kritisches Problem: Authentifizierungs-Keys vs. Daten-Keys

## Das Problem

**Szenario:** Kunde will die Keys im Transponder ÄNDERN (von alten zu neuen Keys)

### Aktuelles System

**Register 1010-1012 (Key A) und 1013-1015 (Key B) haben DOPPELTE Verwendung:**

1. **Als Authentifizierungs-Keys** (für Zugriff auf Blöcke)
2. **Als Daten** (beim Schreiben des Trailer-Blocks)

### Das funktioniert NICHT bei Key-Änderung!

**Beispiel:**

```python
# Transponder hat aktuell:
# - Key A: AA AA AA AA AA AA (alt)
# - Key B: BB BB BB BB BB BB (alt)

# Kunde will ändern zu:
# - Key A: FF FF FF FF FF FF (neu)
# - Key B: FF FF FF FF FF FF (neu)

# Versuch:
modbus.write_registers(1010, [0xFFFF, 0xFFFF, 0xFFFF])  # Neue Key A
modbus.write_registers(1013, [0xFFFF, 0xFFFF, 0xFFFF])  # Neue Key B
modbus.write_registers(1016, [0x0007])                   # Block 7 (Trailer)
modbus.write_registers(1018, [Trigger])

# Firmware versucht:
# 1. Authentifizierung mit Key B = FF FF FF FF FF FF
# 2. Transponder erwartet aber: BB BB BB BB BB BB
# 3. ❌ FEHLER: Authentifizierung fehlgeschlagen!
```

**Der Transponder kennt die NEUEN Keys noch nicht!**

---

## Die Lösung: Separate Auth-Keys und Daten-Keys

### Neue Register-Struktur

**Authentifizierung (für Zugriff):**
- Register 1010-1012: **Auth Key A** (aktueller Key im Transponder)
- Register 1013-1015: **Auth Key B** (aktueller Key im Transponder)

**Daten (für Trailer-Block-Inhalt):**
- Register 1040-1042: **New Key A** (wird in Trailer geschrieben)
- Register 1043-1045: **New Key B** (wird in Trailer geschrieben)
- Register 1030-1031: **ACCESS Bits** (wird in Trailer geschrieben)

### Korrekter Ablauf zum Ändern der Keys

```python
# Transponder hat aktuell:
# - Key A: AA AA AA AA AA AA
# - Key B: BB BB BB BB BB BB

# Schritt 1: ALTE Keys für Authentifizierung setzen
modbus.write_registers(1010, [0xAAAA, 0xAAAA, 0xAAAA])  # Auth Key A (alt!)
modbus.write_registers(1013, [0xBBBB, 0xBBBB, 0xBBBB])  # Auth Key B (alt!)

# Schritt 2: NEUE Keys für Trailer-Daten setzen
modbus.write_registers(1040, [0xFFFF, 0xFFFF, 0xFFFF])  # New Key A
modbus.write_registers(1043, [0xFFFF, 0xFFFF, 0xFFFF])  # New Key B

# Schritt 3: ACCESS Bits setzen
modbus.write_registers(1030, [0x7778, 0x0088])          # ACCESS

# Schritt 4: Block-Nummer
modbus.write_registers(1016, [0x0107])  # Block 7 mit Auth Key B

# Schritt 5: Trigger
modbus.write_registers(1018, [0x0000, ...])

# Firmware macht:
# 1. Authentifizierung mit Auth Key B = BB BB BB BB BB BB ✓
# 2. Schreibe Trailer mit:
#    - New Key A = FF FF FF FF FF FF
#    - ACCESS    = 78 77 88
#    - New Key B = FF FF FF FF FF FF
# 3. ✓ ERFOLG!

# Ab jetzt hat Transponder die NEUEN Keys!
```

---

## Implementierung

### Option 1: Separate Register (EMPFOHLEN)

**Auth-Keys (für Zugriff):**
- 1010-1012: Auth Key A
- 1013-1015: Auth Key B

**Trailer-Daten (für Schreiben):**
- 1040-1042: New Key A (für Trailer-Block)
- 1043-1045: New Key B (für Trailer-Block)
- 1030-1031: ACCESS Bits

**Firmware-Logik:**

```c
// In struct ControlData:
uint8_t authKeyA[6];    // Für Authentifizierung
uint8_t authKeyB[6];    // Für Authentifizierung
uint8_t newKeyA[6];     // Für Trailer-Daten (NEU!)
uint8_t newKeyB[6];     // Für Trailer-Daten (NEU!)
uint8_t accessBits[3];  // Für Trailer-Daten

// Bei WriteBlock:
bool RfidControl::WriteBlock(const uint8_t *blockData, size_t blockNr)
{
    bool useKeyB = (data_.blockNumber >> 8) & 0x01;

    // Authentifizierung mit AUTH-Keys (alt/aktuell im Transponder)
    bool authResult = LoginAuthenticate(blockNr, useKeyB);

    if (authResult) {
        if (isTrailerBlock(blockNr)) {
            // Trailer schreiben mit NEW-Keys (neu)
            uint8_t trailerData[16];
            memcpy(&trailerData[0], data_.newKeyA, 6);      // NEU!
            memcpy(&trailerData[6], data_.accessBits, 3);
            trailerData[9] = 0x00;
            memcpy(&trailerData[10], data_.newKeyB, 6);     // NEU!

            return WriteBlockToReader(blockNr, trailerData);
        } else {
            return WriteBlockToReader(blockNr, blockData);
        }
    }
    return false;
}

// In LoginAuthenticate:
bool RfidControl::LoginAuthenticate(size_t blockNr, bool useKeyB)
{
    // Verwendet AUTH-Keys (alt)
    const uint8_t *authKey = useKeyB ? data_.authKeyB : data_.authKeyA;
    // ... sende an Reader ...
}
```

**Vorteile:**
- ✅ Klare Trennung: Auth-Keys vs. Daten-Keys
- ✅ Key-Änderung funktioniert korrekt
- ✅ Beide Keys können gleichzeitig geändert werden

**Nachteile:**
- ⚠️ Mehr Register nötig (6 zusätzlich)
- ⚠️ API wird komplexer für den Kunden

---

### Option 2: "Use Current Keys" Flag (ALTERNATIVE)

**Register:**
- 1010-1012: Key A
- 1013-1015: Key B
- 1030-1031: ACCESS Bits
- **1046**: Flag "Use current keys for trailer data" (0=use reg 1010/1013, 1=keep current in transponder)

**Ablauf:**

```python
# Fall 1: Keys NICHT ändern (Standard-Fall)
modbus.write_registers(1046, [0x0001])  # Use current keys
modbus.write_registers(1030, [0x7778, 0x0088])  # Nur ACCESS ändern
modbus.write_registers(1016, [0x0007])
modbus.write_registers(1018, [Trigger])

# Fall 2: Keys ÄNDERN
modbus.write_registers(1046, [0x0000])  # Use new keys from registers
modbus.write_registers(1010, [0xFFFF, 0xFFFF, 0xFFFF])  # Neue Keys
modbus.write_registers(1013, [0xFFFF, 0xFFFF, 0xFFFF])
modbus.write_registers(1030, [0x7778, 0x0088])
modbus.write_registers(1016, [0x0007])
modbus.write_registers(1018, [Trigger])
```

**Firmware-Logik:**

```c
if (isTrailerBlock(blockNr)) {
    uint8_t trailerData[16];

    if (data_.useCurrentKeysFlag) {
        // Keys NICHT ändern: Lese vom Transponder
        // Problem: Wie bekomme ich die aktuellen Keys?
        // → NICHT MÖGLICH! Keys sind meist nicht lesbar!
    } else {
        // Keys ändern: Aus Registern
        memcpy(&trailerData[0], data_.authKeyA, 6);
        memcpy(&trailerData[6], data_.accessBits, 3);
        memcpy(&trailerData[10], data_.authKeyB, 6);
    }
}
```

**Problem:**
- ❌ Keys aus Transponder lesen oft nicht möglich (schreibgeschützt)
- ❌ Komplizierte Logik
- ⚠️ Kunde muss unterscheiden zwischen "Keys ändern" und "nur ACCESS ändern"

---

### Option 3: Default-Verhalten + Override

**Standard-Verhalten:**
- Register 1010-1015 werden für BEIDE Zwecke verwendet (Auth + Daten)
- Funktioniert nur wenn Keys GLEICH bleiben (Standard-Fall)

**Override für Key-Änderung:**
- Register 1040-1045: Wenn gesetzt, werden diese für Trailer-Daten verwendet
- Wenn leer/0: Verwende Register 1010-1015

**Firmware-Logik:**

```c
// In Reset():
memset(newKeyA, 0, sizeof(newKeyA));  // Leer = nicht gesetzt
memset(newKeyB, 0, sizeof(newKeyB));

// Bei WriteBlock Trailer:
bool useNewKeys = !isKeyEmpty(data_.newKeyA) || !isKeyEmpty(data_.newKeyB);

if (useNewKeys) {
    // Keys ändern: Verwende newKeyA/B für Daten
    memcpy(&trailerData[0], data_.newKeyA, 6);
    memcpy(&trailerData[10], data_.newKeyB, 6);
} else {
    // Keys gleich: Verwende authKeyA/B für Daten
    memcpy(&trailerData[0], data_.authKeyA, 6);
    memcpy(&trailerData[10], data_.authKeyB, 6);
}

// Für Authentifizierung IMMER authKeyA/B
```

**Vorteile:**
- ✅ Rückwärtskompatibel
- ✅ Einfach für Standard-Fall (nur ACCESS ändern)
- ✅ Möglich für komplexen Fall (Keys ändern)

**Nachteile:**
- ⚠️ Implizites Verhalten (Magic: 0x00 = nicht gesetzt)
- ⚠️ Was wenn Key wirklich 00 00 00 00 00 00 sein soll?

---

## Weitere Überlegungen

### Was ist mit Key A = Key B?

**Häufiger Fall:**
```
Beide Keys identisch:
- Key A: FF FF FF FF FF FF
- Key B: FF FF FF FF FF FF
```

**Problem bei Option 1:**
Kunde muss beide separat setzen:
```python
modbus.write_registers(1040, [0xFFFF, 0xFFFF, 0xFFFF])  # New Key A
modbus.write_registers(1043, [0xFFFF, 0xFFFF, 0xFFFF])  # New Key B (gleich!)
```

**Lösung:** "Copy Key A to Key B" Flag?

---

### Lesen eines Trailer-Blocks

**Problem:**
Wenn Trailer gelesen wird, welche Keys werden zurückgegeben?

```python
# Trailer lesen
modbus.read_registers(2010, 8)  # 16 Bytes

# Antwort:
# - Byte 0-5:   Key A (oft 00 00 00 00 00 00, da nicht lesbar!)
# - Byte 6-8:   ACCESS Bits (lesbar!)
# - Byte 9:     0x00
# - Byte 10-15: Key B (manchmal lesbar)
```

**Sollen die gelesenen Keys automatisch in Register geschrieben werden?**
- In Auth-Keys (1010-1015)?
- In New-Keys (1040-1045)?
- Gar nicht?

---

## Empfehlung

### **Option 1 mit Vereinfachung**

**Register-Layout:**

**Für Authentifizierung:**
- 1010-1012: Auth Key A (für Zugriff)
- 1013-1015: Auth Key B (für Zugriff)

**Für Trailer-Block-Daten (NUR bei Trailer-Schreiben):**
- 1040-1042: Trailer Key A (Default: gleich wie Auth Key A)
- 1043-1045: Trailer Key B (Default: gleich wie Auth Key B)
- 1030-1031: ACCESS Bits (Default: 00 00 00)

**Vereinfachung:**
Beim Reset: `Trailer Keys = Auth Keys` (kopiert)

```c
void Reset() {
    // Auth Keys auf Standard
    const uint8_t defaultKey[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    memcpy(authKeyA, defaultKey, 6);
    memcpy(authKeyB, defaultKey, 6);

    // Trailer Keys = Auth Keys (initial)
    memcpy(newKeyA, authKeyA, 6);
    memcpy(newKeyB, authKeyB, 6);

    // ACCESS Bits
    const uint8_t defaultAccess[] = {0x00, 0x00, 0x00};
    memcpy(accessBits, defaultAccess, 3);
}
```

**Neue Modbus-Handler:**

```c
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
```

**Standard-Fall (Keys NICHT ändern):**
```python
# Kunde muss nur ACCESS ändern:
modbus.write_registers(1030, [0x7778, 0x0088])
modbus.write_registers(1016, [0x0007])
modbus.write_registers(1018, [Trigger])

# Firmware verwendet:
# - Auth Keys (1010-1015) für Zugriff
# - Trailer Keys (1040-1045) für Daten
# - Da Trailer Keys = Auth Keys (Default): Alles bleibt gleich!
```

**Komplexer Fall (Keys ÄNDERN):**
```python
# Alte Keys für Auth setzen
modbus.write_registers(1010, [0xAAAA, 0xAAAA, 0xAAAA])  # Auth Key A (alt)
modbus.write_registers(1013, [0xBBBB, 0xBBBB, 0xBBBB])  # Auth Key B (alt)

# Neue Keys für Trailer setzen
modbus.write_registers(1040, [0xFFFF, 0xFFFF, 0xFFFF])  # Trailer Key A (neu)
modbus.write_registers(1043, [0xFFFF, 0xFFFF, 0xFFFF])  # Trailer Key B (neu)

# ACCESS + Trigger
modbus.write_registers(1030, [0x7778, 0x0088])
modbus.write_registers(1016, [0x0107])  # Key B für Auth
modbus.write_registers(1018, [Trigger])

# Ergebnis: Transponder hat neue Keys FF FF FF!
```

---

## Offene Fragen an Schlege

1. **Ist Key-Änderung eine Anforderung?**
   - Müssen Keys im Transponder geändert werden können?
   - Oder bleiben sie immer FF FF FF FF FF FF?

2. **Wenn ja: Separate Register für Auth vs. Trailer?**
   - Register 1040-1045 für neue Keys?
   - Oder einfacherer Mechanismus?

3. **Standard-Fall: Nur ACCESS ändern?**
   - Keys bleiben gleich, nur ACCESS Bits werden geändert?
   - Dann reichen Register 1010-1015 für beides?

4. **Beim Lesen eines Trailers:**
   - Sollen gelesene Keys in Register geschrieben werden?
   - Oder nur als Teil der 16 Bytes in Read-Registern?

---

## Zusammenfassung

**Kritisches Problem identifiziert:**
- ✅ Auth-Keys ≠ Daten-Keys bei Key-Änderung

**Lösung:**
- Separate Register für Auth (1010-1015) und Trailer-Daten (1040-1045)
- Default: Trailer = Auth (für einfache Fälle)
- Override möglich (für Key-Änderung)

**Wartet auf Klärung mit Schlege!**
