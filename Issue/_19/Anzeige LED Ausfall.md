# Anzeige LED Ausfall

- Author: Schlege
- Created: 2020-09-07T13:06:12Z
- State: CLOSED
- Labels: bug

---

Hallo die Herrn,

aktuell wird der Fehler beim Ausfall einer LED nicht korrekt angezeigt, Die LED7 ist bei allen Modulen immer Failure, wenn ich dann an der LED7 einen Fehler stimuliere wird der bei der LED6 angezeigt. Vermute stark dass einmal von 0 bis 7 gezählt wird und einmal von 1 bis 8.

## Comments

### FrankeEDF (2020-09-07T13:10:04Z)

Wo wird denn was falsch angezeigt? 
Bzw haben sie ds mit der Parametrier SW überprüft?

### Schlege (2020-09-07T13:14:17Z)

Aktuell arbeite ich mit der IO-Link Mastersoftware
![grafik](https://user-images.githubusercontent.com/68856663/92391206-83277180-f11c-11ea-8512-29cbfa6f50e3.png)

hier werden mir die LED Fehler angezeigt, Die Parametrier Software hab ich noch nicht zum Laufen bekommen,

### Schlege (2020-09-07T13:16:18Z)

PS: die Dimmung und das Nachtdesigne funktionieren sehr gut der Wechsel des LED Treibers hat sich gelohnt.

### FrankeEDF (2020-09-09T08:36:47Z)

Bitte mit der ParametrierSW prüfen!

### Schlege (2020-09-09T15:52:59Z)

in der Parametrier Software wird der Fehler nicht angezeigt, vermute auch dass es bei der Übergabe in den Modbus Registern klemmt.

### aot-tmg (2020-09-17T08:49:42Z)

Was ist jetzt mit dem Fehler?

### Schlege (2020-09-17T09:49:49Z)

die Schlegel CPU wertet die Fehler korrekt aus wird jedoch nicht an IO-Link angezeigt.
Aktuell wird die LED 7 mit Failure angezeigt obwohl kein Fehler anliegt. gilt auch für das Error Bit External Error.
![grafik](https://user-images.githubusercontent.com/68856663/93454833-ced7d900-f8db-11ea-888b-5fedeac66084.png)

Parallel sollte dann dieser Fehler auch noch im Error Byte in den Prozessdaten angezeigt werden. 
Aktuell  wird hier beim Error Byte wie auch beim Analog Wert nichts angezeigt.

### aot-tmg (2020-09-17T14:30:49Z)

Das war noch ein Fehler bei der Byte-Zuordnung ist in der neuesten Firmware gefixt. Bitte testen.

### Schlege (2020-09-21T12:26:23Z)

Die Zuordnung der LED Fehlererkennung passt soweit die Fehler werden korrekt angezeigt.
