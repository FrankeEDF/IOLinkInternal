# MultiIO RFID: MIFARE Block über Modbus lesen

## Übersicht
Diese Anleitung beschreibt, wie im MultiIO-System ein MIFARE Classic Datenblock über die Modbus-Schnittstelle gelesen wird.

## Voraussetzungen
- MIFARE Classic Tag im Lesebereich
- Korrekte Keys (A und/oder B) für den Zielblock
- Modbus-Verbindung zum MultiIO-System mit RFID-Modul
- Funktionsbaustein 2 (FB2) muss aktiv sein

## Schritt-für-Schritt Anleitung

### Schritte 1-4: Vorbereitung
Die ersten vier Schritte sind **identisch** zum Schreiben eines Blocks.
Siehe [MultiIO RFID: MIFARE Block schreiben - Schritte 1-4](MultiIO_RFID_MIFARE_Block_Write.md#schritt-1-funktionsbaustein-aktivieren):

1. **Funktionsbaustein aktivieren** (Register 1009 = 2)
2. **Key A konfigurieren** (Register 1010-1012)
3. **Key B konfigurieren** (Register 1013-1015)
4. **Block-Nummer und Key-Auswahl setzen** (Register 1016)

**WICHTIG**: Alle Hinweise und Warnungen aus dem Write-Tutorial gelten auch hier!

### Schritt 5: Lesevorgang auslösen
**Register 1018-1025** lesen, um den MIFARE Block zu lesen

**WICHTIG**: Das LESEN der Register 1018-1025 löst eine Modbus Exception aus, wenn FB2 NICHT aktiv ist (Register 1009 ≠ 2)!

```
Modbus Read:
Start-Register: 1018
Anzahl: 8 Register

Rückgabe: 16 Bytes Blockdaten
```

**WICHTIG**: Erst beim LESEN dieser Register erfolgt die tatsächliche RFID-Kommunikation! Die Schritte 1-4 waren nur Vorbereitungen.

**Ablauf:**
1. Modbus Read Request auf Register 1018-1025 senden
2. RFID-Modul führt automatisch folgende Operationen aus:
   - Authentifizierung mit dem konfigurierten Key
   - Lesen des spezifizierten Blocks
3. Rückgabe der 16 Bytes Blockdaten ODER Modbus Exception bei Fehler

### Schritt 6: Gelesene Daten interpretieren
Die 16 Bytes werden in 8 Registern zurückgegeben:

```
Register 1018: Byte 1 (High) | Byte 0 (Low)
Register 1019: Byte 3 (High) | Byte 2 (Low)
Register 1020: Byte 5 (High) | Byte 4 (Low)
Register 1021: Byte 7 (High) | Byte 6 (Low)
Register 1022: Byte 9 (High) | Byte 8 (Low)
Register 1023: Byte 11 (High) | Byte 10 (Low)
Register 1024: Byte 13 (High) | Byte 12 (Low)
Register 1025: Byte 15 (High) | Byte 14 (Low)
```

### Schritt 7: Fehlercode prüfen
**Register 1026** (Read-Only) auslesen um den Status zu prüfen

```
Modbus Read:
Register: 1026
Rückgabe: [High Byte: Exception | Low Byte: Command]

Interpretation:
- 0x0000: Erfolg - Block wurde gelesen
- 0x1605: Authentication fehlgeschlagen
- 0x1705: Lesefehler
- 0x00xx: Interner Fehler
```

## Komplettes Beispiel: Block 4 lesen

```python
# Pseudo-Code Beispiel

# 1. FB2 aktivieren
modbus.write_register(1009, 0x0002)

# 2. Key A setzen (Transport-Key)
modbus.write_registers(1010, [0xFFFF, 0xFFFF, 0xFFFF])

# 3. Block 4 mit Key A auswählen
modbus.write_register(1016, 0x0004)

# 4. Block lesen (löst automatisch Lesevorgang aus)
data = modbus.read_registers(1018, 8)

# 5. Fehlercode prüfen
error = modbus.read_register(1026)
if error == 0x0000:
    print("Block erfolgreich gelesen")
    print(f"Daten: {data}")
else:
    print(f"Fehler: 0x{error:04X}")
```

## Unterschiede zum Schreibvorgang

| Aspekt | Block LESEN | Block SCHREIBEN |
|--------|-------------|-----------------|
| **Schritte 1-4** | Identisch | Identisch |
| **Schritt 5** | READ Register 1018-1025 | WRITE Register 1018-1025 |
| **Trigger** | Modbus Read löst RFID-Read aus | Modbus Write löst RFID-Write aus |
| **Datenfluss** | RFID → Register → Modbus Response | Modbus Request → Register → RFID |
| **Exception** | Bei Lesefehler | Bei Schreibfehler |

## Wichtige Hinweise

1. **FB2 muss aktiv sein**: Das LESEN der Register 1018-1025 löst eine Modbus Exception aus, wenn FB2 nicht aktiv ist
2. **Sektor-Trailer lesbar**: Blöcke 3, 7, 11, 15, ... enthalten Keys und Access Bits (Key B oft nicht lesbar)
3. **Block 0**: Enthält Hersteller-Daten, immer lesbar
4. **Authentifizierung**: Muss für jeden Sektor erfolgen (4 Blöcke = 1 Sektor)
5. **Tag-Präsenz**: Tag muss während des gesamten Vorgangs im Feld bleiben

## Fehlerbehandlung

### Modbus Exception Response
Bei RFID-Lesefehlern antwortet das Gerät mit einer Modbus Exception.
Nach Erhalt einer Exception sollte Register 1026 ausgelesen werden für Details zum spezifischen RFID-Fehler.

### Debugging bei Fehlern
1. **Modbus Exception erhalten?** → Register 1026 für RFID-spezifischen Fehlercode lesen
2. **Tag vorhanden?** → Register 2010 prüfen (UID-Länge muss > 0 sein)
3. **Keys korrekt?** → Standard-Keys oder individuelle Keys verifizieren
4. **Access-Rechte prüfen** → Sektor-Trailer analysieren (manche Blöcke sind schreibgeschützt aber lesbar)
5. **Alternativen versuchen** → Anderen Key (A/B) testen

## Spezielle Leseszenarien

### Sektor-Trailer lesen (z.B. Block 3, 7, 11, ...)
```
Achtung: Key B ist oft nicht lesbar (erscheint als 0x00)
Struktur: [Key A: 6 Bytes][Access Bits: 3 Bytes][GPB: 1 Byte][Key B: 6 Bytes]
```

### Manufacturer Block (Block 0) lesen
```
- Immer lesbar (keine Authentifizierung nötig)
- Enthält UID, BCC, SAK, ATQA und Manufacturer-Daten
- Niemals beschreibbar
```

## Byte-Reihenfolge (Endianness)

**WICHTIG**: Modbus verwendet Big-Endian für Register, aber die Byte-Reihenfolge innerhalb der Register kann variieren:

- Register-Wert 0x1234:
  - High Byte: 0x12
  - Low Byte: 0x34
- Bei MIFARE-Daten: Low Byte wird zuerst übertragen
  - Register 1018 = 0x0201 → MIFARE liefert: [0x01, 0x02]