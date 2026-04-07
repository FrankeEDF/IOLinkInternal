# Parametriersoftware:  Darstellung Hardware- und Software Version

- Author: Schlege
- Created: 2020-09-22T05:53:29Z
- State: CLOSED
- Labels: enhancement

---

Hallo Herr Franke,

ist eigentlich nur ein Schönheitsfehler,  bei den Factory Settings ist die Anzahl der Zeichen in der Software Version und Hardware Version auf Zwei Zeichen begrenzt eigentlich waren 16 Byte gewünscht, Wenn es in einem akzeptalen Rahmen möglich wäre würde ich hier gerne die Versionsverwaltung wie folgt darstellen: 
Software Version     ==>     SW Vxx [Datum]       Braucht nicht über die Parametrier Software geändert werden können reicht im Quelltext.
Hardware Version   ==>     HW Vxx [Datum]  

Diese Anzahl an Zeichen würden für unsere Versionsverwaltung völlig ausreichen. Jedoch sollte es in der Speicherverwaltung probleme verursachen könnte ich es auch als Schönheitsfehler akzeptieren.

## Comments

### FrankeEDF (2020-09-22T07:28:44Z)

Die Software und Hardware Versionsummern wurden auf jeweils 2 Byte ASCII festgelegt.

Hier die Mail aus demr Festlegung vom 22.01.2020:


Hallo Herr Selig, Herr Schwarz und Herr Franke,

vielen Dank für das konstruktive Treffen.

Hier die Auflistung wie wir sie zusammengestellt haben:


Prozessdaten IO-Link

Inputs:
Tasterstellung Modul 16 - 1
Basismodul Eingänge:
- 1 Byte Input - Analogwert (Poti)
- 1 Byte Input  - Fehler Sammlung (Oder aller Modul Error Bytes)

Outputs:
LED Zustand Modul 16 bis 1
Ausgänge Basismodul:
- 1 Byte Output - Dimmung (Helligkeit der LEDs)
- 1 Byte Output - Nachtdesign


[Modbus]

max 15 Module + Basismodul

[Prozessdaten]
Basismodul:
- 1 Byte Input - Analogwert (Poti) 0 - 255
- 1 Byte Output - Dimmung (Helligkeit der LEDs) 0 - 255
- 1 Byte Output - Nachtdesign 0 - 255
- 1 Byte Input  - Fehler Sammlung (Oder aller Modul Error Bytes)
- 1 Byte Output - Zustand IO-Link

pro Modul:
- 1 Byte Input - Tasterstellung
- 1 Byte Output - LED-Schalten
- 1 Byte Input - Error Byte (siehe Spezifikation)

Parameter:
pro Modul:
- 4 Byte Read/Write - Laufzeitzähler (zurücksetzen bei schreiben) -
Sekunden
- 12 Byte ReadOnly - Seriennummer
- 1 Byte Input - LED-Fehler
- 8x 4 Byte Read/Write - Schaltspielzähler (zurücksetzen bei schreiben)
- 8x 4 Byte Read/Write - Schaltspielgrenzwert
- 2 Byte ReadOnly - Firmware Revision - ASCII
- 2 Byte ReadOnly - Hardware Revision - ASCII


nur Basismodul:
- 1 Byte ReadOnly - Anzahl erkannter Module
- 1 Byte Read/Write - Anzahl konfigurierter Module
- 1 Byte Read/Write - Verhalten im Fehlerfall


Grüße,
Armin Otterstätter

### Schlege (2020-09-22T11:50:43Z)

Hallo Herr Ottenstätter,

wenn wir die Versionierung der Hardware und Software 
2 Byte ReadOnly - Firmware Revision - ASCII
2 Byte ReadOnly - Hardware Revision - ASCII
auf 16 Byte erhöhen müssen wir dann die IODD Datei sowie die Software der IO_link CPU mit anpassen oder ist Ihr Fenster bereits auf 16 Byte ausgelegt.

### aot-tmg (2020-09-22T13:44:04Z)

hmm kann mir nicht ganz vorstellen wie wir da ein Fenster größer auslegen könnten? Schließlich werden bei Modbus beim Lesezugriff angegeben wieviele Register gelesen werden. Da steht momentan 1 (Also 2 Bytes) drin. Von daher müsste ich selbstverständlich die IO-Link Firmware anpassen und die IODD sowieso.

Wäre aus meiner Sicht aber nicht das Ding, wenn es das dann war. Klar muss sein, dass ich nicht jede Woche eine ein klein wenig geänderte Firmware und IODD zur Verfügung stellen möchte.

### FrankeEDF (2020-09-22T13:48:18Z)

> Wäre aus meiner Sicht aber nicht das Ding, wenn es das dann war. Klar muss sein, dass ich nicht jede Woche eine ein klein wenig geänderte Firmware und IODD zur Verfügung stellen möchte.

das seh ich genau so

auf meiner Seite ist die Änderung auch nicht so gering, da diese Modbus Register mittendrin liegen und es dort keinen Platz mehr gibt, um sie zu erweitern. Das bedeutet diese müssen dann verschoben werden oder das ganze Register Mapping muss angepasst werden.
Dann muss noch die PS SW entsprechend angepasst werden und die Spezifikation nachgebessert.
Kleine Änderungen bedeuten selten nur kleiner Aufwand

### Schlege (2020-09-22T15:38:19Z)

Ok, dann lassen wir es so stehen, der Aufwand ist die Sache nicht Wert.
