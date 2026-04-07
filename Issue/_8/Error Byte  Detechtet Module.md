# Error Byte  Detechtet Module

- Author: Schlege
- Created: 2020-07-27T14:40:40Z
- State: CLOSED
- Labels: bug

---

Hier wird keine Fehlermeldung ausgelöst wenn der eingestellte Wert mit dem erkannten Wert nicht übereinstimmt
Die Fehlermeldung "Änderung der Anzahl an Teilnehmer" oder die Meldung "Adressierfehler der Erweiterungsmodule" müsste hier kommne.

## Comments

### Schlege (2020-07-28T08:45:56Z)

Datenverkehr auf der TX Leitung der Schlegel CPU wenn ich eine Taste Drücke, Taste 2
01 03 14 00 FE 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 38 9A 
01 10 03 E7 00 0A F0 7D
Datenverkehr auf der TX Leitung der Schlegel CPU wenn ich den Externen Error auslöse und dabei gleichzeitig die Taste 1 dücke 
01 03 14 00 FF 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 46 67 
01 10 03 E7 00 0A F0 7D
hier müsste der externe Error doch erscheinen?

### FrankeEDF (2020-09-10T21:57:02Z)

Bitte mit der PS prüfen!

### Schlege (2020-09-14T07:40:20Z)

Hallo Herr Franke,
Dank Ihrer neuen Parametriersoftware PS konnte ich es direkt an der Schnittstelle prüfen, es wird sauber erkannt wenn ein Modul bei einem Neustart fehlt. Aktuell sieht es aus wie wenn es an der IO-Link Software liegt

### Schlege (2020-09-14T07:42:19Z)

Hallo Herr Otterstätter,

können Sie bitte prüfen ob das Auslesen des Error Bytes korrekt erfolgt.

### aot-tmg (2020-09-17T15:04:23Z)

Das lag daran, dass bisher der Parameter Configured Modules nur auf dem IO-Link µC abgespeichert wurde und nicht zur Schlegel CPU übertragen. Ist in der neuesten Firmware korrigiert und sollte meiner Meinung nach funktionieren.

### aot-tmg (2020-09-21T13:05:29Z)

Sorry da war ich zu schnell. Ist der Fehler behoben?

### Schlege (2020-09-21T13:33:33Z)

Zuordnung wurde geprüft passt soweit auch
