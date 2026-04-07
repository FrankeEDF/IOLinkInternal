# Detectet Modul

- Author: Schlege
- Created: 2020-07-27T14:00:18Z
- State: CLOSED
- Labels: bug

---

Detected Module, der angezeigte Wert stimmt mit der tatsächlichen Anzahl an Modulen nicht überein, aktuell wird ein Modul Zuviel angezeigt (-> bei einem Basis Modul und zwei Erweiterungsmodulen müsste 3 angezeigt werden). <del>_Was mich hier noch Irritiert, ist dass dann wenn wir den Wert ungleich über den IO-Link einstelle es keine Fehlermeldung über das Error Byte gibt. Dann ist mir auch aufgefallen, dass bei 3 Modulen und zwei erkannten Modulen die entsprechende LED im Modul 1 leuchtet auch die entsprechende LED im Modul 3._

## Comments

### FrankeEDF (2020-07-27T14:07:00Z)

hier sind mehrer Probleme zusammengefasst. bitte aufteilen

### Schlege (2020-07-27T14:34:57Z)

Ok, wir reduzieren diesen Fall auf die Detektierung.
Hier stimmt die Anzahl nicht mit den tazächlich vorhandenen Teilen nicht überein.

### FrankeEDF (2020-07-27T15:19:32Z)

Wieviel Module waren angeschlossen und vieviele wurden erkannt?

### Schlege (2020-07-27T15:38:46Z)

3 Module waren angeschlossen und auf der IO-Link Oberfläche wurden nur 2 erkannt.

### Schlege (2020-07-27T15:41:33Z)

PS: hab dann die Einheit von der Spannung genommen und neu hochgefahren dann hat er 4 angezeigt.

### FrankeEDF (2020-07-27T16:13:49Z)

Bitte mit der PS Software prüfen

### Schlege (2020-07-28T05:02:18Z)

Mit der PS Software kann ich einen Wert unter "Module Count" einstellen und ablegen, dieser Wert wird auch in der Schlegel CPU  übernommen. Dieser Wert muss aber nicht mit den tatsächlich vorhndenen Modulen übereinstimmen. bei Read wird hier auch nicht die tatsächliche Anzahl sondern nur der über die PS Software hinterlegte Wert angezeigt.
Wenn ich hier 3 eingegeben habe und gespeichert habe dann wird in der Mastersoftware 2 angezeigt, nach einem Reset der IO-Link CPU wird 4 angezeigt, nach einem Reset des Gesamtsystems wird immer noch 4 angezeigt.

### FrankeEDF (2020-09-10T21:57:58Z)

Bitte mit der PS prüfen

### Schlege (2020-09-14T07:44:18Z)

Wird in der PS sauber erkannt, muss an der IO-Link Software liegen

### aot-tmg (2020-09-17T07:50:23Z)

Wüsste nicht, was hier an der IO-Link Software liegen sollte? Ich gebe lediglich die Daten von Modbus weiter. Werden die daten für das PS auch über Modbus abgefragt? Die gleichen Routinen wie bei IO-Link?

### Schlege (2020-09-17T08:13:33Z)

Die PS Software greift auf die gleiche Schnittstelle zurück wie die IO-Link CPU. Beim Parametrieren wird die IO_link CPU mittels Reset abgeschaltet dass es beim Übertragen keine Überschneidungen gibt. Beide Systeme arbeite auf dem Modbus.

### aot-tmg (2020-09-17T12:13:36Z)

Bitte kontrollieren ich kann das hier nicht nachvollziehen. Es wird ordentlich angezeigt 3 Module detected und dann stell ich auf 3 Module Configured und es werden alle korrekt angesprochen. Vielleicht verstehe ich den Fehler auch nicht. Am bisherigen Code hab ich nichts geändert.

### aot-tmg (2020-09-17T14:29:00Z)

Ich hab noch ein Problem beim Starten ohne Debugger gefunden. Hier wird das Modules-Detected nicht oft genug ausgelesen (also nicht so lange bis ein korrekter Wert zurückgemeldet wurde). Ist in neuester Firmware gefixt.

### Schlege (2020-09-21T11:44:38Z)

Detectet Modul passt soweit die Werte werden jetzt sauber übertragen.

### Schlege (2020-09-21T11:57:37Z)

Das abändern der Detectet Modul mit Übergabe auf die Schlegel CPU wurde auch getestet, funktioniert soweit gut
