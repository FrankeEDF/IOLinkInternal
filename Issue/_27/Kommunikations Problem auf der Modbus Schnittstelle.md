# Kommunikations Problem auf der Modbus Schnittstelle

- Author: Schlege
- Created: 2021-04-01T12:16:40Z
- State: CLOSED

---

Hallo Herr Franke,
hier das Neue Tiket zu dem Kommunikations Problem auf der Modbus Schnittstelle.
Hinsichtlich Timing konnte ich in der Modbus Spec. bis auf die Baudrate nichts finden.

Hier die Fehlerbeschreibung von Herrn Otterstätter

Damit funktioniert bei mir nun das Schreiben und Lesen der Limits.
Allerdings (siehe vorherige eMail) konnte ich dies nur mit der aktuell geflashten Schlegel-Firmware testen. Die
Anpassung ist aus meiner Sicht allerdings nur ein Workaround für Fehler in der Schlegel-Firmware. Denn diese antwortet
nicht immer direkt auf eine Lesesaufforderung über Modbus. Und gibt auch keinen sinnvollen Fehlercode (0x10 laut Modbus
nicht spezifiziert) zurück. In diesem Fall hab ich die Software nun mit einer Schleife versucht zu retten, indem so oft
versucht wird zu lesen bis ordentliche Daten kommen. Bei mir hat das bisher auch immer geklappt. Braucht aber unter
Umständen ziemlich lange (500 ms beim Startup). Ebenso gab es beim Schreiben auf die Limits Probleme. Hier wurde nicht
nur ein ungültiger Fehlercode zurückgeliefert sondern ein ungültiges Modbus-Frame. Auch hier habe ich eine Schleife
eingebaut um dies abzufangen in der Hoffnung, dass Ihre Firmware es irgendwann gebacken bekommt. Und so war es bei
meinen Tests bisher auch immer. Allerdings benötigt auch dieser Schreibzugriff sehr lange ich habe bis zu 1 Sekunde
gemessen (ohne Anspruch auf Vollständigkeit). Dabei habe ich nur ein Limit geändert. Bitte bedenken Sie, dass bei
IO-Link für ISDUs ein Timeout von 5 Sekunden einzuhalten ist. Daher können hier nicht alle Limits geschrieben werden,
wenn dies immer so lange braucht.

Leider musste ich somit feststellen, dass die Fehler nicht auf unsere Kappe gehen, das ist aus meiner Sicht sehr
unerfreulich. Daher muss ich Ihnen leider mitteilen, das damit der normale Fehlerbehebungs-/Supportaufwand erschöpft ist
und wir Ihnen weiteren Support bezüglich dieses Projekts zu unserem Support-Tagessatz von 1800 € in Rechnung stellen
müssen.
Ich kann verstehen, dass Sie hier etwas zwischen den Stühlen sind, aus meiner Sicht kommen Sie aber nicht umhin sich
zumindest die Modbus-Kommunikation zu Gemüte zu führen, da diese die Schnittstelle zwischen den beiden µC darstellt und
somit sich auch leicht feststellen lässt wer sich "falsch" verhält.

## Comments

### FrankeEDF (2021-04-01T17:36:26Z)

Gibt es weitere Informationen zu diesem Verhalten. Es wird ein "vorherige Mail" erwähnt.
Gibt es vielleicht Oszillogramme.
Unter welchen Umständen tritt denn ein Fehlverhalten auf?

### Schlege (2021-04-06T04:40:44Z)

Hallo Herr Franke,
in der davor liegenden eMails ging es nur darum ob er bei der Sotware Version in der Schlegel CPU auf den Laufenden war.
Da er bei sich auch die Version 02 hatte war dies so bestätigt.

### Schlege (2021-04-06T04:47:20Z)

Hallo Herr Otterstätter,
Könnten Sie hier bitte für Herrn Franke noch weitere Infos für die Fehlerbehebung bereitstellen, wir müssen hier einfach
die Startup Zeit noch verringern um gegebenen Falls auch bei 127 Befehlsstellen mit Linits bedienen zu können und dabei
nicht die Timeout Zeit von 5 Sekunden überschreiten.

### FrankeEDF (2021-04-06T06:55:05Z)

seit 7 Monaten ist die Version V0.3 aktuell. Dort wurde der Fehler #25 behoben

### Schlege (2021-04-06T07:37:39Z)

Hallo Herr Franke,
meine letzte Version war die V05 vom 15.9.20

### FrankeEDF (2021-04-06T08:10:59Z)

![grafik](https://user-images.githubusercontent.com/68696065/113679692-56423980-96c0-11eb-97b6-2dd34d5facf0.png)

### Schlege (2021-04-06T16:12:14Z)

Hallo Herr Franke,
hab inzwischen die V03 aus dem Datensatz gefunden. Werde diese nun mit der neuen IO-Link Software testen. denke dann
haben wir es.
