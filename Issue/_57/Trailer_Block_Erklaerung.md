# Trailer Block - Detaillierte Erklärung

## Ihre Frage ist absolut richtig!

**Key A und Key B werden NICHT gleichzeitig genutzt!**

Sie haben Recht - beim Zugriff (Lesen/Schreiben) verwendet man **entweder Key A ODER Key B** zur Authentifizierung.

## Trailer Block Struktur

Jeder Sektor bei MIFARE Classic hat 4 Blöcke. Der **4. Block ist der Trailer-Block**:

```
Sektor Beispiel:
  Block 0:  [16 Bytes Nutzdaten]
  Block 1:  [16 Bytes Nutzdaten]
  Block 2:  [16 Bytes Nutzdaten]
  Block 3:  [Trailer Block - 16 Bytes]
            ├─ Byte 0-5:   Key A (6 Bytes)
            ├─ Byte 6-8:   ACCESS Bits (3 Bytes)
            └─ Byte 9-15:  Key B (6 Bytes) + 1 Byte unbenutzt
```

## Wie funktionieren Key A und Key B?

### Konzept: Zwei verschiedene Schlüssel mit verschiedenen Rechten

Die ACCESS Bits bestimmen, was man mit jedem Schlüssel machen darf:

**Beispiel (aus Datenblatt Seite 14):**
```
ACCESS Bits: 78 77 88

Mit Key A kann man:
  - Blöcke 0, 1, 2 im Sektor LESEN
  - Block 3 (Trailer): nur ACCESS Bits lesen

Mit Key B kann man:
  - Blöcke 0, 1, 2 im Sektor LESEN und SCHREIBEN
  - Block 3 (Trailer): lesen und schreiben
```

**Anwendungsfall:**
- **Key A** = "Leseschlüssel" (nur lesen erlaubt)
- **Key B** = "Vollzugriffsschlüssel" (lesen + schreiben)

## Ablauf beim Zugriff auf einen Block

### 1. Authentifizierung (vor jedem Zugriff)

**Man muss sich ENTSCHEIDEN: Key A oder Key B?**

Aus dem RFID Datenblatt (Seite 12):

```
Lese-Kommando:
0x41                    = Speicherzelle auslesen
0xXX                    = Block Nummer
0xKeyA/KeyB             = Auswahl: ENTWEDER Key A ODER Key B
```

```
Schreib-Kommando:
0x81                    = Speicherzelle beschreiben
0xXX                    = Block Nummer
0xKeyA/KeyB             = Auswahl: ENTWEDER Key A ODER Key B
16 Bytes Daten
```

**Das bedeutet:**
- Beim Zugriff sendet man: "Ich möchte Block X mit Key A zugreifen"
- Der Reader authentifiziert sich mit Key A beim Transponder
- Danach wird geprüft: "Darf Key A das, was ich will?" (lesen/schreiben)
- Je nach ACCESS Bits wird der Zugriff erlaubt oder verweigert

### 2. Beispiel-Ablauf

#### Szenario 1: Lesen mit Key A

```
1. Kommando an Reader:
   "Lese Block 5 mit Key A"
   - Reader holt Key A aus seinem Speicher: FF FF FF FF FF FF
   - Reader authentifiziert sich beim Transponder mit Key A

2. Transponder prüft:
   - Ist der Key A korrekt? ✓
   - Sagen die ACCESS Bits, dass Key A Block 5 lesen darf? ✓
   - Zugriff erlaubt → Daten werden zurückgegeben
```

#### Szenario 2: Schreiben mit Key A (wenn nicht erlaubt)

```
1. Kommando an Reader:
   "Schreibe Block 5 mit Key A"
   - Reader authentifiziert sich mit Key A

2. Transponder prüft:
   - Ist Key A korrekt? ✓
   - Sagen die ACCESS Bits, dass Key A Block 5 schreiben darf? ✗
   - Zugriff VERWEIGERT → Fehler zurück
```

#### Szenario 3: Schreiben mit Key B

```
1. Kommando an Reader:
   "Schreibe Block 5 mit Key B"
   - Reader holt Key B aus seinem Speicher: FF FF FF FF FF FF
   - Reader authentifiziert sich mit Key B

2. Transponder prüft:
   - Ist Key B korrekt? ✓
   - Sagen die ACCESS Bits, dass Key B Block 5 schreiben darf? ✓
   - Zugriff erlaubt → Daten werden geschrieben
```

## Warum beide Keys im Trailer Block?

Der Trailer Block speichert **beide Schlüssel permanent im Transponder**:

```
Transponder-Speicher (Sektor 1, Block 7 - Trailer):
┌────────────────────────────────────────────────┐
│ Key A         │ ACCESS Bits │ Key B            │
│ FF FF FF FF FF│ 78 77 88    │ FF FF FF FF FF FF│
└────────────────────────────────────────────────┘
     ↑                              ↑
     Für Lese-                 Für Vollzugriff
     berechtigung
```

**Beide werden gespeichert, aber bei jedem Zugriff wird nur EINER verwendet!**

## Aus Ihrer Software-Sicht

### Register-Layout (Beispiel)

```
Register für Trailer-Block:
  1025: Key A Byte 0-1
  1026: Key A Byte 2-3
  1027: Key A Byte 4-5
  1028: ACCESS Bytes (3 Bytes)
  1029: Key B Byte 0-1
  1030: Key B Byte 2-3
  1031: Key B Byte 4-5
```

### Beim Schreiben des Trailer-Blocks (0x81)

**Die Software schreibt BEIDE Keys gleichzeitig in den Trailer:**

```
Zusammenbauen der 16 Bytes:
┌─────────────────────────────────────────────────┐
│ FF FF FF FF FF FF │ 78 77 88 │ 00 FF FF FF FF FF FF│
│    Key A          │ ACCESS   │    Key B            │
│  (aus Reg 1025-27)│(Reg 1028)│  (aus Reg 1029-31)  │
└─────────────────────────────────────────────────┘

Diese 16 Bytes werden in einem Rutsch in den Trailer geschrieben.
```

**ABER:** Um den Trailer-Block zu schreiben, muss man sich **vorher** mit einem der Keys authentifizieren!

```
Kommando an Reader:
0x81                           = Schreibe Block
0x07                           = Block 7 (Trailer von Sektor 1)
0x61                           = Authentifizierung mit Key B
FF FF FF FF FF FF 78 77 88 ... = 16 Bytes Daten (inkl. beide Keys!)
```

### Beim Lesen des Trailer-Blocks (0x41)

**Authentifizierung mit einem Key:**

```
Kommando an Reader:
0x41                    = Lese Block
0x07                    = Block 7 (Trailer)
0x60 oder 0x61          = Mit Key A (0x60) oder Key B (0x61)
```

**Rückantwort vom Reader:**

```
┌─────────────────────────────────────────────────┐
│ 00 00 00 00 00 00 │ 78 77 88 │ FF FF FF FF FF FF │
│    Key A          │ ACCESS   │    Key B          │
│  (oft nicht lesbar)│(lesbar!) │  (oft lesbar)     │
└─────────────────────────────────────────────────┘
```

**WICHTIG:** Key A ist aus Sicherheitsgründen oft **nicht auslesbar** (abhängig von ACCESS Bits)!

## Was bedeutet der Parameter in Ihrer Spezifikation?

Aus dem Datenblatt (Seite 12):

```
0xKeyA/KeyB    = Auswahl Key A oder Key B
```

**Das ist ein PARAMETER, kein Wert!**

In der Praxis könnte das sein:
- `0x60` = verwende Key A
- `0x61` = verwende Key B

### In Ihrer Software-Spezifikation (V04, Seite 3):

```
Daten-String "READ"
0x41              Speicherzelle im Transponder auslesen
0xXX              Block Nummer 1 bis 255
0xKeyA/KeyB       Auswahl Key A oder Key B
```

**Das bedeutet:**
Die Software muss beim Lesen/Schreiben entscheiden:
- Soll mit Key A authentifiziert werden? → Parameter = 0x60
- Oder mit Key B? → Parameter = 0x61

## Typische Verwendung in der Praxis

### Standard-Konfiguration

```
Key A:     FF FF FF FF FF FF  (Werkszustand)
Key B:     FF FF FF FF FF FF  (Werkszustand)
ACCESS:    FF 07 80            (Standard: Key A = Read, Key B = Write)
```

### Gesicherte Konfiguration

```
Key A:     AB CD EF 12 34 56  (Geheimer Leseschlüssel)
Key B:     78 9A BC DE F0 11  (Geheimer Schreibschlüssel)
ACCESS:    78 77 88            (Key A = Read only, Key B = Full access)
```

**Anwendung:**
- Anwender mit Key A können Daten **nur lesen**
- Nur Administratoren mit Key B können Daten **ändern**

## Zusammenfassung

1. **Beide Keys werden im Trailer gespeichert** (gleichzeitig im Transponder)

2. **Beim Zugriff wird nur EINER verwendet** (entweder Key A oder Key B)

3. **Die ACCESS Bits bestimmen**, was jeder Key darf:
   - Key A: z.B. nur Lesen
   - Key B: z.B. Lesen + Schreiben

4. **Ihre Software muss:**
   - Beide Keys in Registern vorhalten
   - Beide gleichzeitig in den Trailer schreiben
   - Beim Lesen/Schreiben von Datenblöcken entscheiden: Key A oder Key B verwenden

5. **Default-Werte laut V04:**
   - Key A: FF FF FF FF FF FF
   - Key B: FF FF FF FF FF FF
   - ACCESS: 00 00 00 (oder besser: FF 07 80 / 78 77 88)

## Offene Frage für die Implementierung

**Welcher Key soll beim Lesen/Schreiben von Datenblöcken verwendet werden?**

Das sollte in der Spezifikation geklärt werden:
- Immer Key B (Vollzugriff)?
- Konfigurierbar über Register?
- Automatisch je nach Operation (Lesen = Key A, Schreiben = Key B)?

Diese Entscheidung fehlt aktuell in der V04-Spezifikation!
