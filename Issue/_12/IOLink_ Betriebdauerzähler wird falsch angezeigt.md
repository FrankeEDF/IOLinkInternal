# IOLink: Betriebdauerzähler wird falsch angezeigt

- Author: FrankeEDF
- Created: 2020-07-28T06:28:22Z
- State: CLOSED
- Labels: bug

---

Das einzige was fehlt ist eine Reset Funktion. Falsch angezeigt wird in der PS Software nichts. 
im Prinzip muss dieses Ticket aufgeteilt werden in

* PS: Reset Betriebsstundenzähler fehlt
* IOLink zeigt Betriebstundzähler falsch an

_Originally posted by @FrankeEDF in https://github.com/FrankeEDF/IOLink/issues/5#issuecomment-664804304_

## Comments

### Schlege (2020-07-28T06:39:57Z)

Hinsichtlich des Betriebsstunden Zählers würde mich noch interessieren ob dieser Wert auch in der PS Software angezeigt wird.

### FrankeEDF (2020-07-28T06:47:02Z)

Ja, unter Diagnose das Feld Runtime
![grafik](https://user-images.githubusercontent.com/68696065/88628864-db476e80-d0ae-11ea-9d07-53d44618b7da.png)

### Schlege (2020-07-28T07:05:26Z)

Danke hab ich übersehen
Aktuell lese ich hier den Wert 1000565624 wenn der Startwert 1000000000 ist bleiben noch 565624 Sekunden was ca 157 Stunden betrifft. ok dann passt die Anzeige in der Mastersoftware nicht, Sie sind hier dann raus.

### Schlege (2020-07-28T08:23:37Z)

Hallo Herr Otterstätter, Aktuell wird der Wert der Betriebsstunden falsch im Aufbau angezeigt  haben Sie hier die Möglichkeit den Betriebsstunden Zähler in Stunden und ohne den Startwert anzuzeigen.

![grafik](https://user-images.githubusercontent.com/68856663/88638889-62e7aa00-d0bc-11ea-87e2-6fac9a9b8903.png)

### FrankeEDF (2020-07-28T08:56:45Z)

**Achtung** keinen Offset abziehen. ich werde den Reset der Betriebsdauer in die PS einbauen siehe #11

### FrankeEDF (2020-07-28T08:59:39Z)

bitte keinen neuen Labels erfinden bug ist ausreichen der Verantwotliche ist über das Assignees zuzuordnen:

![grafik](https://user-images.githubusercontent.com/68696065/88642881-5023a400-d0c1-11ea-995f-4fc59956feb2.png)

### Schlege (2020-07-28T09:16:34Z)

Sorry ist auch neu für mich

### aot-tmg (2020-07-28T09:23:32Z)

d.h. das einzige Problem hier ist doch die Darstelllung, welche jetzt noch in Sekunden ist und Sie hätten diese gerne in Stunden. Ist das so richtig?

### Schlege (2020-07-28T09:32:14Z)

fast, die erste Zahl sollte ausgeblendet werden und dann auf Stunden umgerechnetz werden.
**_1_**0005748...
![grafik](https://user-images.githubusercontent.com/68856663/88646809-b6aac100-d0c5-11ea-8088-345d2b610f97.png)

### FrankeEDF (2020-07-28T09:33:42Z)

Warum sollte man die 1 ausblenden???
sobald der Zähler bei 0 losläuft geht doch alles richtig

### FrankeEDF (2020-07-28T09:34:45Z)

https://github.com/FrankeEDF/IOLink/issues/12#issuecomment-664891218

### aot-tmg (2020-07-28T09:40:03Z)

Ich denke es ist klar. Stunden statt Sekunden aber nichts ausmaskieren. Pass ich in der IODD an.

### aot-tmg (2020-07-28T10:01:50Z)

Der bisherige Datentype in der IODD ist TimeSpanT dieser hat den Vorteil, das nach 24 Stunden umgebrochen wird auf Tage und es werden auch Minuten uns Sekunden separat angezeigt. Leider unterstützt unser Tool den Typ bisher nur unzureichend, sodass dieser nur als einfacher Zahlenwert angezeigt wird.
Nun stellt sich die Frage an Sie Herr Selig inwiefern Sie das einfache Stundenformat mit Nachkommastellen haben wollen oder das entspannter zu lesende TimeSpanT format. Dementsprechend würde ich dafür noch einen Bug bzgl. unseres Tools einreichen um die Anzeige hier etwas zu verschönern.

### Schlege (2020-07-28T10:11:32Z)

Nun Herr Otterstätter, wenn dieser Fehler nur an der TMG Mastersoftware liegt dann können wir die Zeitangabe im TimeSpanT Format lassen. Wir wollen ja nur den Device verkaufen, den Master wird sich unser Kunde auf dem freien Markt beziehen. Wenn das bei anderen Master Softwaren sauber funktioniert dann ist alles gut und wir brauchen hier **nicht** rein auf das Stundenformat gehen.

### Schlege (2020-08-03T06:26:02Z)

Hallo Herr Otterstätter,
die Seriennummer und die Hardware Version wird korrekt angezeigt
![Startbildschirm](https://user-images.githubusercontent.com/68856663/89152207-f1e43e80-d562-11ea-9dba-a7816d3413a4.png)

### Schlege (2020-08-03T06:28:33Z)

Hallo Herr Otterstätter
Sorry das Passt hier nicht dazu werde in dieser Sache für die Doku einen neuen Bag anlegen

### FrankeEDF (2020-09-11T11:46:39Z)

mit PS 1.2.1.6 gibt es den Reset Button. 
Die Firmware für die MPQ3326 LED Treiber startet den Counter bei 0

### Schlege (2020-09-14T14:00:45Z)

Hallo Herr Franke
bei der Neuen Software Version der PS wird der Betriebsstundenzähler immer noch mit 1.... beginnend angezeigt. wenn ich Ihre eMail richtig verstanden habe sollte dieser jetzt eine 0... am Anfang haben.
![grafik](https://user-images.githubusercontent.com/68856663/93095484-70281a80-f6a3-11ea-8ae3-82bd5e1fa297.png)

### Schlege (2020-09-14T14:03:36Z)

Könnten Sie mir auch noch das Password zum Betriebsstunden Zähler zurücksetzen  per eMail zusenden, dann kann ich diese Funktion auch noch testen.

### FrankeEDF (2020-09-14T17:25:21Z)

![grafik](https://user-images.githubusercontent.com/68696065/93118057-f9e5e100-f6bf-11ea-81ab-38925e20cd21.png)

das Password ist Abc123

### Schlege (2020-09-15T04:30:17Z)

Passt alle gewünschten Funktionen sind gegeben.

Ist es ein großer Aufwand hier das Password zu Ändern? darf ruhig im Quelltext bleiben.
