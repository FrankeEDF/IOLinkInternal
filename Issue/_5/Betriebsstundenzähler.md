# Betriebsstundenzähler

- Author: Schlege
- Created: 2020-07-27T14:09:15Z
- State: CLOSED
- Labels: wontfix

---

Aktuell zeigt der Betriebsstundenzähler den Wert an 10000456320.0000, wenn wir in Sekunden rechnen dann ist dieser auch noch zu hoch. Wie setzt sich dieser zusammen, wir brauche auf der IO-Link Oberfläche eine Klartext anzeige in Stunden.

## Comments

### FrankeEDF (2020-07-27T18:41:00Z)

Wie in der Spezifikation festglegt ist die Auflösung des Wertes 1s. Ders Startwert ist 1.000.000.000 Sekunden. Dieser wird durch setzen des Zählers auf z.B 0 neu festgelegt. Dieses Funktion wird/ist in der PS implementiert

### Schlege (2020-07-28T05:08:11Z)

Nun vielleicht gibt es hier ein Verständnis Problem. Wenn ich er richtig verstanden habe dann steht dieser Wert 100004563200000 für 4563200000 Sekunden?

### FrankeEDF (2020-07-28T06:05:42Z)

Die Auflösung beträt 1S, es gibt keinen Offset, die SW Version 20 initailiert diesen Wert auf 1.000.000.000 dies etspricht 1.000.000.000 Sekunden. Sobald alles soweit ist, wird der Wert in der PS SW auf 0 gesetzt. 
Auslesen kann man diesen Wert bereits über die PS
Wie die IO Link CPU / Oberfläche diesen Wert ausliest und oder anzeigt weis ich nicht.

### Schlege (2020-07-28T06:13:00Z)

wenn ich Sie richtig verstanden habe dann zeigt die PS Software vom 28.6.20 den Betriebsstunden- Zähler an. Wenn Ja dann habe ich die falsche PS Software.

### FrankeEDF (2020-07-28T06:26:44Z)

Das einzige was fehlt ist eine Reset Funktion. Falsch angezeigt wird in der PS Software nichts. 
im Prinzip muss dieses Ticket aufgeteilt werden in

* PS: Reset Betriebsstundenzähler fehlt
* IOLink zeigt Betriebstundzähler falsch an
