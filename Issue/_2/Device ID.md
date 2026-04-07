# Device ID

- Author: Schlege
- Created: 2020-07-27T13:58:32Z
- State: CLOSED
- Labels: wontfix

---

Device ID, hier gebe ich über die Parametriersoftware die Nummer 1234 ein über den Modbus kommt aber 3412 vermute es passt nicht mit der Zuordnung High Byte Low Byte.

## Comments

### FrankeEDF (2020-07-27T18:50:07Z)

Mit welcher Modbus SW lesen sie die Werte zurück? gibt es dazu einen Trace?

### Schlege (2020-07-28T05:12:52Z)

Diesen Wert "3412" habe ich über eine Sonderfunktion in der Mastersoftware zurückgelesen.

### FrankeEDF (2020-07-28T06:09:00Z)

-> dann haben sie das Tool falsch benutzt oder den Wert falsch interpretriert

### Schlege (2020-07-28T10:03:08Z)

Nun habe die Device ID geändert in 7654 und über die PS Software aufgespielt wenn ich mit dem Index 68 über die IO-Link Mastersoftware diese Auslese bekomme ich dies.
![grafik](https://user-images.githubusercontent.com/68856663/88651737-49e5f580-d0ca-11ea-862a-944087dc0d9c.png)

### FrankeEDF (2020-07-28T10:06:26Z)

Sieht gut aus
