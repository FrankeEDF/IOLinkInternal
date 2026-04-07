# Device ID

- Author: Schlege
- Created: 2020-08-03T15:50:45Z
- State: CLOSED
- Labels: bug

---

Die Device ID wird aus der Schlegel CPU nicht übernommen über den Befehl Index 68 bekomme ich die Rückmeldung 0x5476 in der Schlegel CPU ist jedoch 0x7654 ale Device ID hinterlegt.

## Comments

### Schlege (2020-09-17T07:31:38Z)

Die Device ID wurde inzwischen in der Schlegel CPU auf 3 Byte erweitert, aktuell wird hier immer noch die 0x000010 angezeigt.
Wenn ich diese dann über den Index 68 auslese kommt diese wie folgt an. 
![grafik](https://user-images.githubusercontent.com/68856663/93434339-4e5bad00-f8c8-11ea-8d93-40bceff72722.png)

### Schlege (2020-09-17T07:32:29Z)

Sorry
es wurde die Device ID 123456 in der Schlegel CPU hinterlegt.

### aot-tmg (2020-09-17T08:47:50Z)

Okay, dann werd ich es entsprechend drehen.

### aot-tmg (2020-09-17T12:11:57Z)

Könnten Sie das nochmal testen ich hab hier kein PS und kann somit keine DeviceID eintragen.

### Schlege (2020-09-21T06:25:57Z)

Können Sie mir ein Bild zu der Basiseinheit zusenden, wenn Sie die Adaptierung der Debug Schnittstelle drauf haben dann spricht nichts dagegen dass sie mit der PS Software auch arbeiten können.

### Schlege (2020-09-21T10:06:26Z)

Hab die neuen Softwares aufgespielt, die Diviche ID wird jetzt richtig erkannt.

![grafik](https://user-images.githubusercontent.com/68856663/93754673-630aae80-fc02-11ea-8df4-2ad0db3fb33f.png)

Wenn Sie mir zeigen können wo ich diese in der IODD Datei ändern kann dann müsste es laufen oder welche Device ID haben Sie in der IODD Datei verwendet dann lege ich diese in der Schlegel CPU ab.

### aot-tmg (2020-09-21T10:16:17Z)

Die bisher genutzte DeviceID ist 0x000010 (also 16 Dezimal). In der IODD gibt es das Attribut deviceId im DeviceIdentity Tag. Allerdings müssen Sie die IODD neu stampen, bevor Sie diese mit der geänderten DeviceID nutzen können. Prinzipiell reicht der von Ihnen eingebundene Screenshot ja auch schon als Nachweis.

### Schlege (2020-09-21T10:16:37Z)

Hab inzwischen die Device ID 0x000010 auf der Schlegel CPU abgelegt,  jetzt komme ich weiter

### Schlege (2020-09-21T10:19:30Z)

Was verstehen Sie unter "neu stampen" ?
