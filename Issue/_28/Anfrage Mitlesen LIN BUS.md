# Anfrage Mitlesen LIN BUS

- Author: Schlege
- Created: 2021-04-01T12:26:33Z
- State: CLOSED

---

Hallo Herr Franke,
wir haben bei einem Großkunden ein Problem mit unserer Vorgänger Version mit LIN Bus.
Könnte es sein dass Sie sich damals ein Testprogramm erstellt hatten um die Komunikation auf dem LIN Bus mitzulesen?
Wir können aktuell nicht nachvollziehen warum sporadisch hier an der selben Stelle das LIN System abstürzt

Wenn Sie hier was hätten auch wenn es keinen Proessionelen Oberfläche hat würde mich interessiern. Die LIN Signale habe ich inzwischen auf der USB Schnittstelle am PC, kann nur diese Hex Zahlen nicht zuordnen.

## Comments

### Schlege (2021-04-01T13:20:07Z)

Hallo Herr Franke,

wissen Sie noch mit welcher Baudrate Sie hier auf dem LIN Bus arbeiten, und welches Start Byte verwenden Sie hier.

### Schlege (2021-04-01T14:50:39Z)

Sorry Herr Otterstätter,
Sie sind hier eigentlich falsch, das Projekt war vor Ihrer Zeit.

### Schlege (2021-04-01T14:52:06Z)

Hallo Herr Franke,
können Sie sich kurz melden bin mir nicht sicher ob dieses Tiket bei Ihnen angekommen ist?

### FrankeEDF (2021-04-01T17:42:42Z)

LIN mit dem PC zu dekodieren geht nur mit einem zusätzlichen Adapter.
Moderne Oszilloskope haben so genannte Protokoll Analyser damit kann man LIN prima mitlesen. Oder auch ein Logikanalysator zum Beispiel von Salea.

### Schlege (2021-04-06T05:30:43Z)

Die Hardware von LIN über UART zu USB auf den PC habe ich bereits, hier kommen auch Daten an, das Problem ist nur diese auszuwerten oder wenigstens die Start Sequenz des Strings zu erkennen. 

![grafik](https://user-images.githubusercontent.com/68856663/113663120-c42f3680-96a9-11eb-8454-de0a00ad5620.png)

### Schlege (2021-04-06T06:27:28Z)

Bei der Baudrate von 19200 kann ich zwar das Break 0x00 und Sync 0x55 Byte erkennen aber bei der Gesamtkomunikation tue ich mir schwer. Kann aktuell auch noch nicht nachvollziehen mit welcher Baudrate Sie auf dem LIN arbeiten. bin bisher von 57600 bd ausgegangen.

![grafik](https://user-images.githubusercontent.com/68856663/113667824-9f3ec180-96b1-11eb-9a1b-5c8609af6ec9.png)

### FrankeEDF (2021-04-06T06:52:56Z)

LIN mit dem PC zu dekodieren geht nur mit einem zusätzlichen Adapter.
Moderne Oszilloskope haben so genannte Protokoll Analyser damit kann man LIN prima mitlesen. Oder auch ein Logikanalysator zum Beispiel von Salea. Die Baudrate ist 19200

### Schlege (2021-04-06T07:07:55Z)

Den Adapter für den PC haben wir uns über einen LIN Baustein aufgebaut, die UART Seite des LIN Bausteins ist dann auf einen UART to USB und dann auf den PC weitergegeben worden. So sollten im PC die gleichen Daten ankommen wir am UART der Controllers. Da wir nur der LIN-Bus über die read Leitung mitlesen bleibt die TX Leitung außeracht. Wir können jetzt nur nicht unterscheiden welche Daten vom Master und welche vom Slave kommen. Unser Oszilloskop hat keine Protokoll analyse und einen Logikanalyser haben wir auch keinen

### FrankeEDF (2021-04-06T08:06:03Z)

LIN mit dem PC zu dekodieren geht nur mit einem zusätzlichen Adapter der das auch beherscht!

### Schlege (2021-04-06T08:22:22Z)

Geht klar, wenn ich solch einen Adapter habe wie sieht dann das Protokoll aus, nach meinem Wissensstand beginnt die Kommunikation mit einem Break und einem Sync Byte welches der Hex Folge 0x00 und 0x55 entspricht. Wenn ich dies mit meinem Standard Oszilloskop messe passt das auch, es wird dann danach ein Byte  oder mehrere Bytes übertragen.  Hier sollte ich nur noch die Zuordnung wissen.

### FrankeEDF (2021-04-06T09:05:24Z)

Mehr hab ich auch nicht:
[Lin Messung.pdf](https://github.com/FrankeEDF/IOLink/files/6263428/Lin.Messung.pdf)

### Schlege (2021-04-06T11:32:26Z)

Nun das kann ich auch messen, gut dann muss ich versuchen wie wir hier noch mehr rausholen können.
