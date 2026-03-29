## Aussage von Ihnen

> "Sie setzen jetzt ja auch den Key A und Key B nach dessen Eingabe zu einen Datenblock zusammen."

## Das ist NICHT korrekt!

### Aktuelle Implementierung

**Firmware macht NICHT das Zusammenbauen von Keys zu einem Block!**

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

**Was passiert wirklich:**

1. **Register 1010-1012 (Key A)** → gespeichert in `rfidControl.data_.keyA[]`
2. **Register 1013-1015 (Key B)** → gespeichert in `rfidControl.data_.keyB[]`
3. **Register 1018-1025 (16 Bytes)** → direkt als `buffer` an `WriteBlock()` übergeben

**KEINE Zusammenführung!**

Die Keys bleiben separat und werden nur für die Authentifizierung benutzt:

```cpp
// RfidControl.cpp:556
bool RfidControl::LoginAuthenticate(uint8_t block, uint8_t keyFlag)
{
   // ...
   if (keyFlag & 0x01)
      blockData = data_.keyA;  // ← Keys werden NUR hier benutzt
   else
      blockData = data_.keyB;

   return sendRfidTelegram(RfidTelegram::PICCAUTHKEY, ...);
}
```

### Was Sie vorschlagen

Sie denken, die Firmware würde:

1. Key A aus Register 1010-1012 nehmen
2. Key B aus Register 1013-1015 nehmen
3. Daraus einen 16-Byte Datenblock bauen
4. Diesen Block zum RFID Reader schicken

**Das ist FALSCH! Die Firmware macht das NICHT!**

### Der Unterschied

| Was Sie denken               | Was wirklich passiert                          |
|------------------------------|------------------------------------------------|
| Keys → werden zu Datenblock  | Keys → nur für Auth                            |
| Firmware baut Block zusammen | Block kommt komplett über Modbus via 1018-1025 |
| Keys haben doppelte Funktion | Keys haben EINE Funktion: Auth                 |

## Was das für ACCESS Bytes bedeutet

**Ihr Vorschlag:**
> "2 weitere Modbus Register mit in Summe 4 Byte vergleichbar mit Key A"

Das würde bedeuten:

- Register 1030-1031 für ACCESS Bytes (4 Bytes)
- Firmware würde dann automatisch einen Trailer Block bauen:
    - Byte 0-5: Key A aus Register 104x
    - Byte 6-8: ACCESS aus Register 1030-1031
    - Byte 9: 0x00
    - Byte 10-15: Key B aus Register 104x

**Problem: Das macht die Firmware JETZT NICHT!**

Die Firmware nimmt die 16 Bytes DIREKT von Register 1018-1025 und schreibt sie 1:1 zum Transponder.

## Korrektur meiner vorherigen Analyse

Ich lag falsch mit:
> "Keine Firmware-Änderung nötig"

**Jetzt verstehe ich:**

Sie WOLLEN tatsächlich eine neue Funktionalität:

- Ähnlich wie bei Key A/B separate Register
- Firmware soll ACCESS Bytes + Keys zu einem Trailer Block zusammenbauen
- Das wäre eine NEUE Komfort-Funktion

**ABER:** Sie haben die falsche Vorstellung, dass die Firmware das mit Key A/B bereits macht!

## Die richtige Frage

**Was soll implementiert werden?**

Option A: **Wie Key A/B** (aber Keys werden NICHT zu Block zusammengebaut!)

- Register 1030-1031 für ACCESS Bytes
- Register 1040-1042 für Trailer Key A (neue!)
- Register 1043-1045 für Trailer Key B (neue!)
- Firmware baut daraus einen 16-Byte Trailer Block
- **Das ist NEUE Funktionalität!**

Option B: **Dokumentation**

- Modbus-Master baut Trailer Block manuell
- Nutzt Register 1018-1025 wie bisher
- Keine Firmware-Änderung

## Meine Empfehlung

**Zuerst Sie korrigieren:**

"Die Firmware setzt Key A und Key B **NICHT** zu einem Datenblock zusammen.

Key A/B in Registern 1010-1015 werden **nur für die Authentifizierung** benutzt.

Der 16-Byte Block kommt **komplett über Modbus** via Register 1018-1025.

Wenn Sie eine Komfort-Funktion wie bei Key A/B wollen, dann müssten wir:

1. Neue Register für ACCESS Bytes (1030-1031)
2. Neue Register für Trailer Keys (1040-1045)
3. Neue Logik zum automatischen Zusammenbauen eines Trailer Blocks
4. Neuen Trigger-Mechanismus

**Das ist komplett NEUE Funktionalität!**

Alternativ: Modbus-Master baut Trailer Block manuell und nutzt bestehende Register 1018-1025."
