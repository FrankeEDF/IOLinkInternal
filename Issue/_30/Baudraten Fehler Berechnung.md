# Baudraten Fehler Berechnung

- Author: Schlege
- Created: 2021-06-09T09:29:53Z
- State: CLOSED

---

Hallo Herr Franke,

Im Hausinternen Freigabeprozess sind wir bei der Fehlerbetrachtung bei der Baudrate auf einen Fehler von -4,2% bei 115200Bd gestoßen. Denke sie haben hier Intern über die CPU den Fehler korrigiert. Können Sie mir bitte diesen Korrekturfaktor nennen dass wir diesen bei unserer Fehlerbetrachtung mit einrechnen können.

## Comments

### FrankeEDF (2021-06-10T12:19:32Z)

Die Abweichung der Baudrate ist nicht relevant da Master und Slaves mit der selben Abweichung arbeiten.
Keine Ahnung wie  sie auf so eine Fehlerrate kommen.

### Schlege (2021-06-10T13:39:21Z)

Hallo Herr Franke,
das ist soweit korrekt, die Kommunikation vom Basismodul zu den Erweiterungsmodulen sehe ich auch nicht für Kritisch da bin ich bei Ihnen. Wie sieht es dann mit der Kommunikationsstrecke Schlegel CPU zur IO-Link CPU aus hier arbeiten wir bei der IO-Link CPU mit 14,7456MHZ. Würde sich hier nicht dann der Fehler bemerkbar machen, oder liege ich hier Falsch.

### FrankeEDF (2021-06-10T14:17:10Z)

da sind es keine 115200 bd. Immer noch die Frage wie sie auf so eine Abweichung kommen ...

### Schlege (2021-06-11T10:59:29Z)

Hallo Herr Franke,
ist soweit korrekt, bei 57600Bd sieht es schon besser aus. bei enem Standard Betriebsmodus sind wir hier dennoch bei 2,1% was aus meiner Sicht etwas hoch ist. Wenn Sie mir den Betribsmodus vom Baudraten Generator in der CPU sagen könnten dann würde das völlig reichen. Bei doppelter Geschwindigleit sind wir hier schon bei -0,8 % was schon ein guter Wert ist.

### FrankeEDF (2021-06-11T11:28:50Z)

Wie kommen sie auf diese Werte ????

### Schlege (2021-06-15T06:51:50Z)

Hallo Herr Franke, 
hab diesen Fehler über diverse Formeln über die Quarz Tolleranz hochgerechnet Alternativ geht es natürlich auch über diese Tabelle bei der Grundfrequenz von 16MHz
![beispiel4-baudrate-atmega8](https://user-images.githubusercontent.com/68856663/122006184-d4a11300-cdb6-11eb-8efb-3d714296f9b1.jpg)

### FrankeEDF (2021-06-15T07:42:48Z)

Können sie mir noch sagen aus welchem Dokument sie die Tabelle haben?

### Schlege (2021-06-16T05:30:11Z)

Die Relation zwischen CPU-Frequenz und Baudrate ist.
16 * (UBRR+1) * BAUDRATE = CPU_FREQ

UBRR = (CPU_Frerq / Baudrate / 16) -1 
UBRR = 16MHz / 57600 /16 -1 = 16,361111 Da aber UBRR nur ein Ganzzahliger Wert sein kann muss hier gerundet werden, in dem Fall auf 16. Dies hat zur Folge die Baudrate bei UBRR 16 liegt bei 58823,52 Bd was zur Zentralen Baudrate 57600 um 2,1% daneben liegt. Der relative Fehler bei der Baudrate sollte 2% nicht übersteigen ist eine Aussage aus diversen Foren welche ich nun nicht matematisch belegen kann.
Unterm Strich funktioniert alles sehe stabiel wir haben also kein Problem, meine Aufgabe ist es hier die Praktische Umsetzung auch noch Theoretisch nachzuweisen.

### FrankeEDF (2021-06-16T07:18:23Z)

Können sie mir noch sagen aus welchem Dokument sie die Formel haben?

### Schlege (2021-06-16T09:02:32Z)

Hallo Herr Franke,
Wenn Sie unter Goggle "baudrate fehler berechnen" eingeben dann finden Sie dieses Dokumente an verschiedenen Stellen
Die Formen konnte ich im AVR Datenblatt finden.

### FrankeEDF (2021-06-16T13:45:38Z)

Ich möchte dennoch genau wissen welche Dokumente **Sie** verwendet haben. Aus meiner Sicht passt das nicht zum verwendeten Kontroller.

https://www.dolman-wim.nl/xmega/tools/baudratecalculator/index.php

### Schlege (2021-06-16T15:34:08Z)

Hallo Herr Franke
Diese Formeln stammen aus einem ATtiny 2313 Datenblatt. Dass der ATXMega hier mehr Möglichkeiten bietet kann ich mir gut vortellen, desshalb habe ich ja in meiner ersten Anfrage hier bei Ihnen nachgefragt welchen Korrekturfaktor Sie hier verwenden um den Fehler auszugleichen. Dass dieser Fehler nicht zwingend für den ATXMega zufrifft zeigt ja schon die Situation dass  ja alles Funktioniert. Meine Aufgabe ist nur im Versuchsberich zu der Baugruppe in der Theorie zu bestätigen dass es hier keinen Fehler ansteht. Der Link ist sehr interessant, dennoch wäre es für mich wichtig zu wissen wie sich Ihre Fehler Werte ergeben.
Was das Datenblatt zum ATXMega betrifft ist hier auch nichts brauchbares zu finden. In den 222 Seiten wird kaum auf die Interne Architektur eingegangen. Beim ATMega 8 z.B. ist hier einfach noch mehr hinterlegt. 

Eigentlich reicht mir ein Zweizeiler wie sich der Baudraten Fehler bei 16MHz von 0,1% in Ihrem Fall zusammensetzt

### FrankeEDF (2021-06-16T15:54:07Z)

Was für eine abstruses Vorgehen ihreseits: wenn das richtige Datenblatt nicht nach ihrem Geschmak ist, einfach ein völlig falsches Datenblatt nehmen. Und zusätzliche Leistungen bei SW Entwickler abrufen.
Wenn ich sie verstanden habe ist es doch Ihre Aufgabe das Nachzuweisen. Warum in aller Welt sollte ich hier tätig werden?
![grafik](https://user-images.githubusercontent.com/68696065/122252654-d27ca880-cecb-11eb-810a-d152aeb2065c.png)
