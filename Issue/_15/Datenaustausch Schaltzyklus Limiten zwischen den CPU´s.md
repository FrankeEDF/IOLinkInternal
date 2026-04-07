# Datenaustausch Schaltzyklus Limiten zwischen den CPU´s

- Author: Schlege
- Created: 2020-08-03T15:42:27Z
- State: CLOSED
- Labels: bug

---

Aktuell findet der Datenaustausch zwischen den über die Parametrier Software in der Schlegel CPU abgelegten Daten zur IO-Link CPU nicht statt. In die andere Richtung von der IO-Link CPU zur Schlegel CPU werden auch keine Daten zurückgeschrieben. Es müssen in beiden CPU´s die selben Werte stehen.

## Comments

### FrankeEDF (2020-09-09T08:40:39Z)

Bitte mit der PS prüfen!

### Schlege (2020-09-09T15:03:33Z)

Auch dieser Wehrt wird in der PS korrekt angezeigt

### aot-tmg (2020-09-17T13:41:50Z)

Hier scheint wohl etwas mit der Modbus Kommunikation nicht ganz zu funktionieren. Auf den Multiple-Write gibt es eine (falsch formatierte) Fehler Antwort:
![grafik](https://user-images.githubusercontent.com/68891435/93479140-43bb0b00-f8fc-11ea-991d-5d66f7fd9a7f.png)

### Schlege (2020-09-21T13:09:25Z)

Hallo die Herrn,
Aktuell konnte ich feststellen dass die Limiten über die IO-Link CPU veränert und auch an die Schlegel CPU Übertragen werden diese kann ich dann auch über die PS wieder auslesen. Wenn ich aber dann einen neuen Datesatz über die PS aufspiele dann werden diese Daten nicht von der Schlegel CPU an die IO-Link CPU übergeben.

![grafik](https://user-images.githubusercontent.com/68856663/93769975-e389d900-fc1b-11ea-9b3a-03756f2db759.png)

### Schlege (2020-09-21T13:10:38Z)

Hier habe ich die Daten auf die Schlegel CPU übertragen

![grafik](https://user-images.githubusercontent.com/68856663/93770488-880c1b00-fc1c-11ea-88f2-c24479f97fca.png)

### Schlege (2020-09-21T13:12:46Z)

Hier die Darstellung in der IO-Link Mastersoftware

![grafik](https://user-images.githubusercontent.com/68856663/93770712-d7524b80-fc1c-11ea-9c76-aede034f2851.png)

### aot-tmg (2020-09-21T13:15:26Z)

Das ist per definition/spezifikation so. Zumindest hatte ich es bisher so verstanden. Die Limits können schließlich/letztendlich nur eine Datenquelle haben. So wie ich es verstanden hatte wollten Sie dieses in IO-Link haben, falls ein Modul beim Kunden ausgetauscht werden muss.
Wenn Sie es anders haben wollen müssen wir über die Änderung und das wie Sie sich das genau vorstellen sprechen.

### Schlege (2020-09-21T13:56:26Z)

Hallo die Herrn,
im Grunde müssen die Schaltzyklus Limiten wir bei den "Modul detectet" Wert in beiden Systemen immer auf dem selben Stand sein. Wir haben folgende Vorgehensweisen.
Bei unseren Modul werden über die PS im Fertigungsprozess bei der Auslieferung die Limiten auf einen von Hause Schlegel festgelegten Wert gesetzt welche im IO-Link auch übernommen werden müssen, Wenn der Kunde hier dann Änderungen vornimmt werden diese neuene Daten auch an die Schlegel CPU übergeben so dass diese den Fehler Limiten Überschritten auswerten kann. Es ist zwingend notwendig dass beide die Schlegel CPU und die IO-Link CPU hier den gleichen Datensatz haben. Es wird auch nie der Fall sein dass diese Daten Zeitgleich geändert werden. 
Im Prinziep werden die Limiten im Hause Schlegel Voreingestellt und wenn der Kunde dann bei der Inbetriebnahme hier Änderungen vornimmt müssen diese dann dem Gesamtsystem wieder zur Verfügung stehen.

Herr Otterstätter,
eine Frage, wo werden die Limiten bzw generell die Parameter beim IO-Link überall abgelegt. Wie verhält sich dies wenn wir den IO-Link Device tauschen und der Kunde will auf die Alten Limiten zurückgreifen?

### aot-tmg (2020-09-21T14:07:08Z)

So geschickt der Issue-Tracker hier für die Fehlernachverfolgung ist so ungeschickt ist er für grundsätzliche Debatten und Spezifikationsänderungen.
Wir hatten das genau so besprochen:
Die voreingestellten Werte werden in der Schlegel CPU abgelegt.
Sollte der Kunde diese ändern wollen wir die Änderung nur in der IO-Link CPU abgespeichert aber nicht in der Schlegel CPU. Dennoch schreibt die IO-Link CPU diesen neuen Wert zur Schlegel-CPU damit diese überwachen kann. Desweiteren wird bei jedem Start das aktuell eingestellte Limit an die Schlegel-CPU von der IO-Link CPU übertragen.
Falls der Kunde wieder auf Werkseinstellungen zurückstellen möchte, werden diese aus der Schlegel-CPU ausgelesen.

Wenn Sie hier eine Spezifikationsänderung anstreben müssen wir das besprechen. Aber wie einleitend schon beschrieben nicht über diese Plattform.

### Schlege (2020-09-21T15:32:09Z)

Hallo Herr Otterstätter,
Die Spezifikation wurde Ihrerseite korrekt implementiert passt alles der Fehler lag daran, mir nicht mehr bewusst war, dass estmalige Übertragen der Limiten Daten nur einmal möglich ist. 
Es wurde nun getestet und wir können es so stehen lassen. die Spezifikation und Ihre Software  Passt so.

### Schlege (2020-09-21T15:34:14Z)

Kann abgeschlossen werden
