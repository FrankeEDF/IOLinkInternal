# ACCESS Bytes - Detaillierte Erklärung

## Problem
Es ist unklar, wohin die ACCESS Bytes geschrieben werden und woher sie beim Lesen kommen.

## Antwort aus dem RFID Datenblatt (Seite 12)

### MIFARE Classic Speicherstruktur

Ein MIFARE Classic Transponder hat **Sektoren mit je 4 Blöcken**:

```
Sektor #0    Block #24  [384] [385] [386] ... [399]  (16 Bytes Daten)
             Block #25  [400] [401] [402] ... [415]  (16 Bytes Daten)
             Block #26  [416] [417] [418] ... [431]  (16 Bytes Daten)
             Block #27  [432] [433] [434] [435] [436] [437] [438] [439] [440] [441] [442] [443] [444] [445] [446] [447]
                         └─────────────┘ └────────┘ └─────────────┘
                            Key A       Access Bits      Key B
                           (6 Bytes)     (3 Bytes)      (7 Bytes)
```

### Der 4. Block (Trailer Block) ist speziell!

**Block #27** (bzw. der letzte Block in jedem Sektor) ist der **Trailer-Block** und enthält:
- **Byte 0-5**: Key A (6 Bytes)
- **Byte 6-8**: Access Bits (3 Bytes) ← **HIER!**
- **Byte 9-15**: Key B (7 Bytes, wobei Byte 9 unbenutzt ist)

## Konkrete Anwendung in Ihrer Software

### Beim SCHREIBEN eines Sektors

Wenn Sie einen **kompletten Sektor** (oder den Trailer-Block) beschreiben:

**Kommando: 0x81 - Speicherzelle im Transponder beschreiben**

Beispiel: Schreiben von Block 27 (Trailer-Block):

```
Daten-String "WRITE"
0x81                          = Speicherzelle beschreiben
0x1B                          = Block Nummer 27 (hex: 1B)
0xKeyA/KeyB                   = Auswahl Key A oder Key B für Authentifizierung
16 Byte´s Daten:
  [0-5]:   FF FF FF FF FF FF  = Key A (aus Register)
  [6-8]:   78 77 88           = ACCESS Bytes (aus Register 0x08)
  [9-15]:  FF FF FF FF FF FF FF = Key B (aus Register)
```

### Beim LESEN eines Sektors

Wenn Sie einen **Sektor auslesen**:

**Kommando: 0x41 - Speicherzelle im Transponder auslesen**

Beispiel: Lesen von Block 27 (Trailer-Block):

```
Daten-String "READ"
0x41                          = Speicherzelle auslesen
0x1B                          = Block Nummer 27 (hex: 1B)
0xKeyA/KeyB                   = Auswahl Key A oder Key B

Rückantwort:
0x41                          = Bestätigung
0x1B                          = Block Nummer 27
16 Byte´s Daten:
  [0-5]:   00 00 00 00 00 00  = Key A (oft 00, da nicht auslesbar!)
  [6-8]:   78 77 88           = ACCESS Bytes ← **HIER auslesen!**
  [9-15]:  FF FF FF FF FF FF FF = Key B
```

**WICHTIG**: Key A und Key B sind oft **nicht auslesbar** aus Sicherheitsgründen (abhängig von ACCESS Bits). Die ACCESS Bits selbst sind aber **lesbar**!

## Was muss Ihre Software tun?

### Register-Zuordnung (Beispiel)

Sie brauchen Modbus-Register für den **Trailer-Block**:

```
Register X+0/X+1/X+2:  Key A (6 Bytes)
Register X+3:          ACCESS Bytes (3 Bytes) ← NEU!
Register X+4/X+5/X+6:  Key B (7 Bytes)
```

### Beim Schreiben (Steuercode 0x81)

1. **Alle 16 Bytes des Trailer-Blocks zusammensetzen**:
   - Bytes 0-5: Aus Key A Registern
   - **Bytes 6-8: Aus ACCESS Bytes Register (0x08)**
   - Bytes 9-15: Aus Key B Registern

2. **Kompletten Block an RFID Reader senden**

### Beim Lesen (Steuercode 0x41)

1. **16 Bytes vom RFID Reader empfangen**

2. **Aufteilen in Register**:
   - Bytes 0-5 → Key A Register
   - **Bytes 6-8 → ACCESS Bytes Register** ← Hier ablegen!
   - Bytes 9-15 → Key B Register

## Welche Blöcke haben ACCESS Bytes?

**Nur der Trailer-Block** (letzter Block in jedem Sektor):

- Sektor 0: Block 3 (nur UID, nicht beschreibbar)
- Sektor 1-15: Jeweils Block 3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63

Für einen **1K Transponder (ESRT1_X)**:
- 16 Sektoren × 4 Blöcke = 64 Blöcke
- Trailer-Blöcke: 3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63

## Standard-Werte

Laut Spezifikation V04:
- **Default: 00 00 00** (beim Start)
- **Standard auf neuen Karten: oft FF 07 80** oder **78 77 88**

## Zusammenfassung für die Implementierung

### Neuer Steuercode 0x08

**Funktion**: ACCESS Bytes für den Trailer-Block setzen

**Was tun beim Schreiben eines Trailer-Blocks**:
```
Trailer-Block (16 Bytes) = [Key A (6)] + [ACCESS Bytes (3)] + [Key B (7)]
                            └─ Reg 0x06  └─ Reg 0x08           └─ Reg 0x07
```

**Was tun beim Lesen eines Trailer-Blocks**:
```
Empfangene 16 Bytes aufteilen:
- Bytes 0-5   → Key A Register
- Bytes 6-8   → ACCESS Bytes Register (0x08)
- Bytes 9-15  → Key B Register
```

**Wichtig**: ACCESS Bytes werden **nur zusammen mit dem kompletten Trailer-Block** gelesen/geschrieben, nicht einzeln!

## Beispiel-Ablauf

### Szenario: Schreibe Sektor 1, Block 7 (Trailer)

1. **Anwender setzt in Modbus-Registern**:
   - Key A: FF FF FF FF FF FF
   - **ACCESS Bytes: 78 77 88** ← Zugriffsrechte konfigurieren
   - Key B: FF FF FF FF FF FF

2. **Ihre Software (bei Steuercode 0x81)**:
   - Liest alle Register aus
   - Baut 16-Byte Block zusammen:
     `FF FF FF FF FF FF 78 77 88 00 FF FF FF FF FF FF FF`
   - Sendet an RFID Reader zum Schreiben in Block 7

3. **RFID Reader**:
   - Schreibt alle 16 Bytes in Block 7
   - ACCESS Bits sind jetzt im Transponder gespeichert
   - Diese steuern nun die Zugriffsrechte auf Sektor 1!

### Szenario: Lese Sektor 1, Block 7 (Trailer)

1. **Ihre Software (bei Steuercode 0x41)**:
   - Sendet Lesekommando für Block 7 an RFID Reader

2. **RFID Reader antwortet**:
   - 16 Bytes: `00 00 00 00 00 00 78 77 88 00 FF FF FF FF FF FF FF`
     (Key A oft 00, da nicht lesbar)

3. **Ihre Software**:
   - Bytes 0-5 → Key A Register (00 00 00 00 00 00)
   - **Bytes 6-8 → ACCESS Bytes Register (78 77 88)** ← Hier ablegen!
   - Bytes 9-15 → Key B Register

4. **Anwender kann über Modbus**:
   - ACCESS Bytes auslesen und sieht: 78 77 88
   - Weiß jetzt, welche Zugriffsrechte konfiguriert sind

## Fazit

**Wohin beim Schreiben?**
→ In den **Trailer-Block** (letzter Block eines Sektors), Bytes 6-8

**Woher beim Lesen?**
→ Aus dem **Trailer-Block**, Bytes 6-8 extrahieren und in Register ablegen

Die ACCESS Bytes sind also **Teil des Trailer-Blocks** und werden zusammen mit Key A und Key B behandelt.
