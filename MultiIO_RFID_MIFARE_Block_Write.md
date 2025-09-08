# MultiIO RFID: MIFARE Block über Modbus schreiben

## Übersicht
Diese Anleitung beschreibt, wie im MultiIO-System ein MIFARE Classic Datenblock über die Modbus-Schnittstelle geschrieben wird.

## Voraussetzungen
- MIFARE Classic Tag im Lesebereich
- Korrekte Keys (A und/oder B) für den Zielblock
- Modbus-Verbindung zum MultiIO-System mit RFID-Modul
- Funktionsbaustein 2 (FB2) muss aktiv sein

## Schritt-für-Schritt Anleitung

### Schritt 1: Funktionsbaustein aktivieren
**Register 1009** auf Wert **2** setzen (FB2 - MIFARE Read/Write)

```
Modbus Write:
Register: 1009
Wert: 0x0002
```

### Schritt 2: Key A konfigurieren (falls benötigt)
**Register 1010-1012** mit Key A (6 Bytes) beschreiben

**HINWEIS**: Das Setzen der Keys löst noch KEINE Kommunikation mit dem RFID-Reader aus. Die Keys werden nur intern gespeichert.

**WICHTIG**: Das Schreiben auf Register 1010-1012 löst eine Modbus Exception aus, wenn FB2 NICHT aktiv ist (Register 1009 ≠ 2)!

```
Modbus Multi-Write:
Start-Register: 1010
Anzahl: 3 Register
Daten: [Key A - 6 Bytes]

Beispiel für Standard-Key (FF FF FF FF FF FF):
Register 1010: 0xFFFF
Register 1011: 0xFFFF  
Register 1012: 0xFFFF
```

### Schritt 3: Key B konfigurieren (falls benötigt)
**Register 1013-1015** mit Key B (6 Bytes) beschreiben

**HINWEIS**: Das Setzen der Keys löst noch KEINE Kommunikation mit dem RFID-Reader aus. Die Keys werden nur intern gespeichert.

**WICHTIG**: Das Schreiben auf Register 1013-1015 löst eine Modbus Exception aus, wenn FB2 NICHT aktiv ist (Register 1009 ≠ 2)!

```
Modbus Multi-Write:
Start-Register: 1013
Anzahl: 3 Register
Daten: [Key B - 6 Bytes]

Beispiel für Standard-Key:
Register 1013: 0xFFFF
Register 1014: 0xFFFF
Register 1015: 0xFFFF
```

### Schritt 4: Block-Nummer und Key-Auswahl setzen
**Register 1016** konfigurieren

**HINWEIS**: Auch das Setzen von Block-Nummer und Key-Auswahl löst noch KEINE RFID-Kommunikation aus. Dies sind nur Vorbereitungsschritte.

**WICHTIG**: Das Schreiben auf Register 1016 löst eine Modbus Exception aus, wenn FB2 NICHT aktiv ist (Register 1009 ≠ 2)!

```
Modbus Write:
Register: 1016
Wert: [High Byte: Key-Select | Low Byte: Block-Nummer]

Struktur:
- Low Byte: Block-Nummer (0-255)
- High Byte, Bit 0: Key-Select (0=Key A, 1=Key B)
- High Byte, Bit 1-7: Reserviert (0x00)

Beispiele:
- 0x0004: Block 4 mit Key A
- 0x0104: Block 4 mit Key B
- 0x003F: Block 63 mit Key A
- 0x013F: Block 63 mit Key B
```

### Schritt 5: Daten vorbereiten
**Register 1018-1025** mit den zu schreibenden Daten (16 Bytes) füllen

**WICHTIG**: Das Schreiben auf Register 1018-1025 löst eine Modbus Exception aus, wenn FB2 NICHT aktiv ist (Register 1009 ≠ 2)!

```
Modbus Multi-Write:
Start-Register: 1018
Anzahl: 8 Register
Daten: [16 Bytes Nutzdaten]

Beispiel:
Register 1018: 0x0201  (Byte 1=0x01, Byte 0=0x02)
Register 1019: 0x0403  (Byte 3=0x03, Byte 2=0x04)
Register 1020: 0x0605  (Byte 5=0x05, Byte 4=0x06)
Register 1021: 0x0807  (Byte 7=0x07, Byte 6=0x08)
Register 1022: 0x0A09  (Byte 9=0x09, Byte 8=0x0A)
Register 1023: 0x0C0B  (Byte 11=0x0B, Byte 10=0x0C)
Register 1024: 0x0E0D  (Byte 13=0x0D, Byte 12=0x0E)
Register 1025: 0x100F  (Byte 15=0x0F, Byte 14=0x10)
```

### Schritt 6: Schreibvorgang auslösen
Der Schreibvorgang wird automatisch ausgelöst, sobald die Daten in Register 1018-1025 geschrieben werden.

**WICHTIG**: Erst JETZT erfolgt die tatsächliche RFID-Kommunikation! Die Schritte 2-4 waren nur Vorbereitungen.

**WICHTIG**: Wenn der MIFARE-Schreibvorgang fehlschlägt, antwortet das Modbus-Gerät mit einer **Modbus Exception Response**.
Die genaue Fehlerursache kann dann über Register 1026 ausgelesen werden

### Schritt 7: Fehlercode prüfen
**Register 1026** (Read-Only) auslesen um den Status zu prüfen

```
Modbus Read:
Register: 1026
Rückgabe: [High Byte: Exception | Low Byte: Command]

Interpretation:
- 0x0000: Erfolg - Block wurde geschrieben
- 0x1605: Authentication fehlgeschlagen
- 0x1805: Schreibfehler
- 0x00xx: Interner Fehler
```

## Komplettes Beispiel: Block 4 mit Daten beschreiben

```python
# Pseudo-Code Beispiel

# 1. FB2 aktivieren
modbus.write_register(1009, 0x0002)

# 2. Key A setzen (Transport-Key)
modbus.write_registers(1010, [0xFFFF, 0xFFFF, 0xFFFF])

# 3. Block 4 mit Key A auswählen
modbus.write_register(1016, 0x0004)

# 4. Daten schreiben (löst automatisch Schreibvorgang aus)
data = [0x1122, 0x3344, 0x5566, 0x7788, 
        0x99AA, 0xBBCC, 0xDDEE, 0xFF00]
modbus.write_registers(1018, data)

# 5. Fehlercode prüfen
error = modbus.read_register(1026)
if error == 0x0000:
    print("Block erfolgreich geschrieben")
else:
    print(f"Fehler: 0x{error:04X}")
```

## Wichtige Hinweise

1. **FB2 muss aktiv sein**: ALLE MIFARE-spezifischen Register (1010-1025) lösen eine Modbus Exception aus, wenn FB2 nicht aktiv ist
2. **Sektor-Trailer nicht überschreiben**: Blöcke 3, 7, 11, 15, ... enthalten Keys und Access Bits
3. **Block 0**: Enthält Hersteller-Daten, meist schreibgeschützt
4. **Authentifizierung**: Muss für jeden Sektor erfolgen (4 Blöcke = 1 Sektor)
5. **Timing**: Nach dem Schreiben der Daten kurz warten bevor Fehlercode gelesen wird
6. **Tag-Präsenz**: Tag muss während des gesamten Vorgangs im Feld bleiben

## Fehlerbehandlung

### Modbus Exception Response
Bei RFID-Operationsfehlern antwortet das Gerät mit einer Modbus Exception.
Nach Erhalt einer Exception sollte Register 1026 ausgelesen werden für Details zum spezifischen RFID-Fehler

### Debugging bei Fehlern
1. **Modbus Exception erhalten?** → Register 1026 für RFID-spezifischen Fehlercode lesen
2. **Tag vorhanden?** → Register 2010 prüfen (UID-Länge muss > 0 sein)
3. **Keys korrekt?** → Standard-Keys oder individuelle Keys verifizieren
4. **Access-Rechte prüfen** → Sektor-Trailer analysieren
5. **Alternativen versuchen** → Anderen Key (A/B) oder anderen Block testen

## Byte-Reihenfolge (Endianness)

**WICHTIG**: Modbus verwendet Big-Endian für Register, aber die Byte-Reihenfolge innerhalb der Register kann variieren:

- Register-Wert 0x1234:
  - High Byte: 0x12
  - Low Byte: 0x34
- Bei MIFARE-Daten: Low Byte wird zuerst übertragen
  - Register 1018 = 0x0201 → MIFARE erhält: [0x01, 0x02]