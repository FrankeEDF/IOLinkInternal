# Änderung V04-Spezifikation: ACCESS Bytes entfernen

## Zusammenfassung

Der Punkt "0x08 ACCESS Bytes werden übertragen" basiert auf einem Missverständnis und muss aus der Spezifikation entfernt werden.

## Grund

Das aktuelle System unterstützt bereits vollständig das Schreiben von Trailer-Blöcken inkl. ACCESS Bytes über die bestehenden Register 1018-1025.

Eine separate Behandlung von ACCESS Bytes ist **weder nötig noch sinnvoll**.

## Zu entfernender Text

**Datei:** `Software_Spezifikation_RFID_to_MBS_V04-2.pdf`
**Seite:** 2 von 5
**Abschnitt:** Funktionsbaustein 2 → Funktion: Schreib / Lese Parameter

### Aktueller Text (blau markiert):

```
Funktion: Schreib / Lese Parameter
Die Schreib Leseparameter werden in den Entsprechenden Register abgelegt und über die Steuercodes aus der SPS angestoßen.
0x06 Key A wird übertragen
0x07 Key B wird übertragen
0x08 ACCESS Bytes werden übertragen
     Das ACCESS Byte wird nur im Transponder geändert, wenn sich die Daten im Register ändern.
     Default Werte: 00 00 00
```

### Zu entfernen:

```diff
Funktion: Schreib / Lese Parameter
Die Schreib Leseparameter werden in den Entsprechenden Register abgelegt und über die Steuercodes aus der SPS angestoßen.
0x06 Key A wird übertragen
0x07 Key B wird übertragen
-0x08 ACCESS Bytes werden übertragen
-     Das ACCESS Byte wird nur im Transponder geändert, wenn sich die Daten im Register ändern.
-     Default Werte: 00 00 00
```

### Neuer Text:

```
Funktion: Schreib / Lese Parameter
Die Schreib Leseparameter werden in den Entsprechenden Register abgelegt und über die Steuercodes aus der SPS angestoßen.
0x06 Key A wird übertragen
0x07 Key B wird übertragen
```

**Hinweis:** 0x06 und 0x07 sind KEINE Steuercodes, sondern Beschreibungen der Register 1010-1015!

## Begründung

### Missverständnis

Die Spezifikation geht davon aus, dass die Firmware Key A und Key B zu einem Datenblock zusammenbaut.

**Das ist FALSCH!**

### Tatsächliche Implementierung

```cpp
// modbusSlave.cpp:796
case 1018: // 16 Byte, 8 register : Block Number + Block Data
   if (count == 8)
   {
      size_t block = rfidControl.GetBlockNumber();
      result = rfidControl.WriteBlock(buffer, block);  // ← buffer kommt direkt von Modbus!
      amount = 8;
   }
   break;
```

**Fakten:**

1. Register 1010-1012 (Key A) → nur für Authentifizierung
2. Register 1013-1015 (Key B) → nur für Authentifizierung
3. Register 1018-1025 (16 Bytes) → direkt zum Transponder (KEINE Modifikation!)

Die Firmware baut **KEINEN** Datenblock aus Key A/B zusammen!

### Warum ACCESS Bytes bereits funktionieren

Trailer Block schreiben funktioniert **JETZT SCHON** identisch zu allen anderen Blöcken:

```python
# 1. Auth Keys setzen
modbus.write_registers(1010, [0xFFFF, 0xFFFF, 0xFFFF])  # Key A
modbus.write_registers(1013, [0xFFFF, 0xFFFF, 0xFFFF])  # Key B

# 2. Block-Nummer
modbus.write_registers(1016, [0x0107])  # Block 7 (Trailer)

# 3. Kompletten Trailer Block über Modbus (16 Bytes)
trailer = [
    0xFFFF, 0xFFFF, 0xFFFF,  # Key A (Bytes 0-5)
    0x7F07, 0x8800,          # ACCESS Bits (6-8) + 0x00 (9)
    0xFFFF, 0xFFFF, 0xFFFF   # Key B (Bytes 10-15)
]
modbus.write_registers(1018, trailer)  # TRIGGER - schreibt sofort
```

**Das funktioniert bereits!** Siehe Dokumentation: `documentation/Modbus/MultiIO_RFID_MIFARE_Block_Write.md`

## Neue Version erstellen

**Vorschlag:**

- **Alte Version:** V04-2 (Datum: 25.3.2026)
- **Neue Version:** V04-3 (Datum: [heute])
- **Änderung:** "ACCESS Bytes Punkt entfernt (basierte auf Missverständnis)"

**Historie Eintrag:**

| Nr. | Datum | Änderungen/Seite | Bemerkungen | Doku |
|-----|-------|------------------|-------------|------|
| 6 | [heute] | Korrektur Seite 2 | ACCESS Bytes Punkt entfernt - bereits über Register 1018-1025 unterstützt | Software_Spezifikation_RFID_to_MBS_V04-3.doc |

## Optional: Ergänzung statt Entfernung

Falls Sie den Punkt nicht komplett entfernen wollen, könnten Sie ihn umformulieren:

```
Funktion: Schreib / Lese Parameter
Die Schreib Leseparameter werden in den Entsprechenden Register abgelegt und über die Steuercodes aus der SPS angestoßen.
0x06 Key A wird übertragen (Register 1010-1012, nur für Authentifizierung)
0x07 Key B wird übertragen (Register 1013-1015, nur für Authentifizierung)

Hinweis: ACCESS Bytes sind Teil des Trailer Blocks und werden wie alle anderen Block-Daten
über Register 1018-1025 übertragen. Eine separate Behandlung ist nicht erforderlich.
Siehe Datenblatt Seite 12-13 für Trailer Block Struktur.
```

## Empfehlung

**Einfach entfernen** ist besser als umformulieren:

- Klarer und eindeutiger
- Vermeidet weitere Verwirrung
- 0x06 und 0x07 sind ohnehin irreführend (es sind KEINE Steuercodes!)

## Aufwand

- PDF bearbeiten: **10-15 Minuten**
- Neue Version erstellen: **5 Minuten**
- **Gesamt: ~20 Minuten**
