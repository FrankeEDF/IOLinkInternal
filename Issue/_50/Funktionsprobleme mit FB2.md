# Funktionsprobleme mit FB2

- Author: Schlege
- Created: 2025-11-10T17:01:12Z
- State: OPEN

---

Hallo Herr Franke,
hab den FB2 noch nicht zum Laufen bekommen. 
Zum Programmablauf im Unigate IC, die Daten für die entsprechenden Register werden im Unigate IC in einem Buffer abgelegt und dann über den Modbus FC16 in die Register in einem Aufwasch geschrieben. Hier sind die Ausgangsdaten zu den LED´s in der Taste wie auch die RFID Daten abgelegt, d.h. es kann sein dass der RFID Key A parallel zu den Status LED´s in der Taste übertragen werden.  Mein Interner Speicherbereich im Deutschmann Modul ist hier sehr begrenzt. Hier der Aktuelle Stand zur Software auf dem Unigate IC noch ohne FB3. 
„Compilation successful, 2238 bytes code generated. User RAM usage: 2744 bytes“  

Wenn ich ihre Beschreibung korrekt verstanden habe dann darf ich z. B. zum Ansteuern der Statusanzeige im Reader nur die Zwei Register 1027 und 1018 mit dem FC16 ansprechen und die Anzeige wird sofort geändert. Wenn weitere Register mit dabei sind dann funktioniert es so nicht.  
Aktuell macht mir dies Probleme da der Speicherbereich im Unigate IC hier schon sehr an der Gernze ist.

Hier ein Beispiel nur zum Ansteuern der Reader Status Anzeige in den Farbei Blau Grün Turkis und OFF
"Compilation successful, 2434 bytes code generated. User RAM usage: 2744 bytes" ergaben 196 Bytes

Kann mir aktuell nicht vorstellen so noch den FB3 im Unigate IC mit unterzubekommen. Bin hier aber auch Parallel mit Deutschmann im Gespräch

## Comments

### FrankeEDF (2025-11-14T09:36:12Z)

<img width="1023" height="217" alt="Image" src="https://github.com/user-attachments/assets/5ee27ea3-7ad9-4e1e-957b-f3606b3503ae" />

das Register 1026 ist ein Read Only Register daher geht das tatsächlich nicht die Register 1026 und 1027 in einenen größeren Block zu integrieren. Die Ansteuerung der LED's war aber auch nie gefordert. ich denke das einfachste wird sein , diese Funktionen wieder raus zu nehmen

<img width="1004" height="285" alt="Image" src="https://github.com/user-attachments/assets/6f6e257b-c13f-43b8-8063-052073af5b65" />

### Schlege (2026-01-19T07:04:18Z)

Guten Morgen Herr Franke,
verstehe Ihre Aussage nicht, dass die Ansteuerung der LED´s nie gefordert wurden. Die Steuercods 0x06 bis 0x09 waren von Anfang an in der Softwarespezifikation verankert.  

Nun Zur Situation: 
Da ich mir nicht sicher bin wo das Problem in der Modbus Kommunikation zwischen Ihrer Software und dem Unigate IC liegt habe ich mich auf die Ansteuerung der LED konzentriert. hier geht die Kommunikationsstrecke nur in eine Richtung. 
Wenn ich Ihre Beschreibung richtig verstanden habe dann reicht es aus im FB2 das Register 1027 und 1028 zu beschreiben über FC16 dann muss die entsprechende LED im Reader und Leuchtring leuchten. Der Inhalt von Register 1009 bleibt ja so lange bestehen bis dieser wieder überschrieben wird.

### Schlege (2026-01-20T13:46:22Z)

Hallo Herr Franke, 
inzwischen kann ich den Datentransfer zwischen Unigate und der CPU mitlesen, wenn auch nur exadezimal.
das Unigate sendet folgenden Code zur CPU
01 10 04 03 00 02 04 07 FF 00 04 B1 FD
die Rückantwort ist dann
01 10 04 03 00 02 B0 F8
Jedoch über den RFID Reader läuft keine Kommunikation und die Lampe am Reader schaltet auch nicht ein.
Mir ist auch aufgefallen, dass das Modbus Tool die Protokolle immer nur einzeln überträgt. In der Gesamtbetrachtung auf Grund der Abfrage der Eingänge muss ich hier im 100ms Tckt die Tasten abfragen.
Vermute wir haben hier ein Timing Problem.

### FrankeEDF (2026-01-20T21:44:22Z)

um ihre Angaben prüfen zu können brauche ich mehr Informationen:
was soll mit dem Sende Telegramm bewirkt werden und welches verhalten ist erwartet. 
Ist das Antworttelegram inkorrekt?
oder was geht schief?
Haben sie den Test auch mit dem ModbusGui-Tool durchgeführt?

Außerdem scheint der letzte Text überhaupt nicht zum 1. Beschreibung unter dem Titel zu passen. in einem solchen Fall bitte ein neues Ticket eröffnen.

### Schlege (2026-01-21T06:40:11Z)

Unigate sendet folgenden Code zur Schlegel CPU:
01 10 04 03 00 02 04 07 FF 00 04 B1 FD          ==> die Schlegel CPU wird aufgefordert die blaue LED am Reader einzuschalten
die Rückantwort ist dann
01 10 04 03 00 02 B0 F8       ==> die Rückantwort von der Schlegel CPU an das Unigate

jedoch findet nach der und wärend der Übertragung keinerlei kommunikation zum RFID Reader statt. die LED am Reader leuchtet nicht.

### Schlege (2026-01-22T06:36:19Z)

Hallo Herr Franke,
haben Sie die Funktion "Zyklisch Sende" im Reader ausgeschaltet? Beim FB2 brauchen wir diese nicht da ist es sicherer im Manuellen Betrieb zu arbeiten.

### FrankeEDF (2026-01-22T19:47:20Z)

ja

### Schlege (2026-01-28T08:18:21Z)

Hi,
Bin wieder ein gutes Stück weitergekommen, LED´s lassen sich nun schalten. Beim auslesen des Speicherblocks gibt es aber Probleme. 
Versuche gerade den Block 8 mit Key A auszulesen bekomme aber keine korrekten Daten geliefert.
Beim auslesen des Registers 1026 bekomme ich folgende Rückmeldung 0xE022.  
Kann diese Meldung nicht zuordnen.

### Schlege (2026-01-28T08:29:50Z)

Sorry
Beim auslesen des Registers 1026 bekomme ich folgende Rückmeldung 0xE022 ==> ist ein Unigate Fehler muss diesen Swapen korrekterweise sollte es 0x22E0 heißen.

### FrankeEDF (2026-01-28T09:21:11Z)

Diese Ticket ist von ihnen geschlossen worden:

<img width="571" height="116" alt="Image" src="https://github.com/user-attachments/assets/c41dd1bc-957d-43e1-a257-b945bcdd8c86" />

### Schlege (2026-01-28T09:23:28Z)

Ok war mir so nicht bewusst, soll ich ein neues öffnen oder können Sie mir die jnfo auch über diesen Weg geben

### FrankeEDF (2026-01-28T10:14:26Z)

Bitte sehr feingliedrig Tickets anlegen. Jedes Thema ein Ticket. der Sinn ist das man jedes Ticket für sich bearbeiten kann. Keine Sammeltickets. Jedes Ticket mit einer aussagekräftigen Überschrift!

### Schlege (2026-01-28T10:52:00Z)

werden wir so machen

### Schlege (2026-02-12T10:23:08Z)

Hier die neue Software Spezifikation

[Software Spezifikation_RFID to MBS_V04.pdf](https://github.com/user-attachments/files/25258070/Software.Spezifikation_RFID.to.MBS_V04.pdf)

### FrankeEDF (2026-02-18T16:46:58Z)

es erscheint sinnvoller, den Befehl zum Ändern der Baudrate im FB3 zu **blockieren**. 
der Nutzer hat von einer Änderung der Baudrate nichts außer das danach der RFID Reader von der Firmware nicht mehr angesprochen werden kann.

### Schlege (2026-02-19T06:46:43Z)

Kann ich so mitgehen, dann plockiern wir den Befehl.
