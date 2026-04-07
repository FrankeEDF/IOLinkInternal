# System Seriennummer

- Author: Schlege
- Created: 2020-07-27T13:57:22Z
- State: CLOSED
- Labels: bug

---

System Seriennummer, hier lesen wir die Hardware Version welche wir über die Parametriersoftware gespeichert hatten. Bei der Hardware Version bekommen wir dann die Seriennummer mit Personalnummer. (Personal Nummer 0815).
Die Ausgabe der Seriennummer soll im Feld Seriennummer erfolgen ohne die Personal Nummer, diese ist beim IO-Link nicht relevant.

## Comments

### FrankeEDF (2020-07-27T18:51:33Z)

durch was wird gelesen?

### Schlege (2020-07-28T05:20:05Z)

diese Werte habe ich aus der Mastersoftware. 
Hätte Ihnen ein Bild angehängt wenn ich wüsste wie.

### Schlege (2020-07-28T05:22:05Z)

PS: der Zahlen Wert stimmt mit dem welchen ich zuvor über die PS Software abgelegt habe überein jedoch am Schluss ist noch die Personal Nummer angehängt.

### FrankeEDF (2020-07-28T06:36:16Z)

Sicher hätte man das auch über Google gefunden: 

Am 2020-07-28 07:20, schrieb Schlege: 

> diese Werte habe ich aus der Mastersoftware.
> Hätte Ihnen ein Bild angehängt wenn ich wüsste wie. 
> 
> --
> You are receiving this because you commented.
> Reply to this email directly, view it on GitHub [1], or unsubscribe [2].

  

Links:
------
https://github.com/FrankeEDF/IOLink/issues/1#issuecomment-664783107
https://github.com/notifications/unsubscribe-auth/AQMDQAOQPOLGUEBSIUVMRB3R5ZNZDANCNFSM4PIZLN2Q

### Schlege (2020-07-28T09:12:12Z)

hab Google gefragt,

Nun folgender Datensatz konnte auf der TX Leitung der Schlegel CPU gelesen werden.
01 03 10 31 32 33 34 35 36 37 38 39 30 31 32 30 38 31 35 45 7D hier wird die Personal Nummer 0815 mit überragen

dieser Datensatz würde zu der Abfrage der System Seriennummer auf der TX Leitung der IO-Link CPU passen
01 03 **27 46** 00 08 AF 6D     

==> Sorry kann aktuell noch nicht beide TX Leitungen gleichzeitig abfragen, bin aber dran.
Bitte beachten, die Seriennummer der Module wird korrekt angezeigt und somit sicherlich auch korrekt übertragen.

### aot-tmg (2020-07-28T13:42:38Z)

0x2746 ist aber nicht die Seriennumer sondern die Hardware Version welche auch mit 16 Bytes spezifiziert ist. Wird bei der Seriennummer zuviel gelesen? Hier sind in der Spezifikation 12 Bytes vorgesehen.

### Schlege (2020-07-28T15:36:05Z)

Nach meinem Verständniss ist 
10044 ==> Hex 273C   Device ID              3  Byte
10054 ==> Hex 2746   Seriennummer      12 Byte
10062 ==> Hex 274E   HW Version           16 Byte
Die Seriennummer ist 12 Byte lang, nach dem angezeigten Wert lesen Sie die Personal Nummer (hier 0815) auch noch mit aus.     
Somit lesen sie die nachfolgenden 4 Speicherstelle auch noch mit aus.

### aot-tmg (2020-07-28T15:42:47Z)

Das lag an einer alten Version der ModbusSpec.pdf in der neuen ist es wie Sie schreiben. @FrankeEDF: Nach Mögichkeit bitte nächstes Mal kenntlichmachen wenn sich etwas bereits spezifiziertes ändert. Ich werde die Adressen in der nächsten Firmware anpassen.
