# Modbus Kommunikation zwischen ATSAM und ATXMEGA Systemen

- Author: Schlege
- Created: 2023-01-31T09:28:20Z
- State: CLOSED

---

Da die Modbus Kommunikation zwischen den Modulen immer noch Identisch sein sollte zu der Modbus Kommunikation über den ATSAM sollte es möglich sein die alten und neuen Module kombienieren zu können.

Um Irritationen zu vermeiden hier die Zuordnung auf die Begriffe:
ALT ==>  steht für Controller ATXMEGE 128 mit entsprechender Software 
NEU ==> Steht für Controller ATSAM4S4A mit entsprechender Software

Ergebnis der Untersuchung Kommunikation System ALT mit System NEU
Basiseinheit NEU auf Erweiterungsmodule ALT ==> es konnte kein Fehler gefunden werden, werde hier aber noch weitere Tests durchführen

Basiseinheit ALT mit Erweiterungseinheiten NEU ==> es gab Kommunikations Probleme, werde diese aber noch nähers untersuchen und beschreiben.

## Comments

### Schlege (2023-01-31T14:36:49Z)

Ergänzung zu oben,
Bei der Kombination Master NEU, Device 1 ALT, Device 2 NEU war eine Funktion in beide Richtungen möglich. 
Bei der Kombination Master NEU, Device 1 ALT, Device 2 ALT war keine Funktion mit Device 2 möglich. 

Vermute aber dass der Fehler hier im Zusammenhang mit der Fehlermeldung Adressierfeler in Verbindung steht.

### Schlege (2023-02-03T06:09:04Z)

mit aktuellem Softwarestand komme ich nicht mehr weiter bei diesem Test.

### FrankeEDF (2023-02-03T07:45:09Z)

Bitte senden sie mir ein Entwicklungskit mit dem ich diesenFehler nachvollziehen kann.

### Schlege (2023-02-28T16:18:58Z)

Kann Aktuell das EW Kit aus der ATXMega128 Variante von Ihnen nicht finden, kann es sein dass dies noch bei Ihnen ist, Wenn nicht können Sie mir dann zusammenstellen welche Leitungen Sie zum Debugen benötigen dann würde ich diese bei meinem Aufbau ergänzen und Ihnen zuschicken.

### FrankeEDF (2023-02-28T21:08:51Z)

Leider ist meine ATSAM Basis Platine defekt. ich kann hier nichrt weiter testen

### Schlege (2023-03-01T06:01:50Z)

Kein Problem, dann schick ich Ihnen nur die Steckkarten. ist einfacher für mich.

### FrankeEDF (2023-03-01T13:03:55Z)

Bitte denken sie daran das ich die Karte auch mit dem JTAG Adapter verbinden muss. 
Diese Verdrahtunmg können sie ja viel einfacher als ich!

### Schlege (2023-03-02T06:41:09Z)

Ok, sorry gestern war viel los, hab Ihrer eMail erst heute gelesen. Die Teile sind bereits raus, schicken Sie einfach Ihr EW Bord mit den Platinen zurück dann überarbeiten wir dieses.

### FrankeEDF (2023-03-10T10:11:27Z)

Sollte in der Version 09 behoben sein

### Schlege (2023-04-03T10:26:43Z)

Hallo Herr Franke,
entschuldigen Sie bitte dass ich mich erst jetzt wieder melde, komm einfach nicht mehr dazu die Software abschließend zu testen.

### Schlege (2023-04-03T10:31:45Z)

Die Kommunikation zwischen den Alten Module mit ATXMEGA und neuen Modulen mit ATSAM funktioniert inzwischen reibungslos bei 3 Einheiten. Gleich welche Kombi, ob mit altem oder neuem Master. Sobald es aber Mehr wie 3 Module sind funktioniert hier ab dem driten Modul nichts mehr, Kann es sein dass Sie bei der Anzahl der Einzelnen Module was geändert haben bei der Neuen Software. Mein Aufbau hat 5 Module welche so auch Parametrisiert wurden.

### Schlege (2023-04-03T10:37:02Z)

PS: es ist mir auch aufgefallen dass ab dem 4ten Modul die Seriennummer, Firmware Version und Hardware Version nicht ausgelesen werden.

### FrankeEDF (2023-04-04T20:49:07Z)

Habe soeben die Version 10  eingespielt. damit sollten alle Kombinationen zwischen ATXMega und ATSAM Modulen funktionieren

### Schlege (2023-04-05T05:42:09Z)

Danke, werde diese gleich prüfen.

### Schlege (2023-04-05T15:21:31Z)

Hallo Herr Franke,
Die Kombination zwische ATXMEGA Systemen und ATSAM Systemen läuft soweit konne diese zwar erst mit 5 Modulen testen sollte aber kein Problem machen.

### FrankeEDF (2023-04-10T19:02:16Z)

hab die Version 11 eingespielt.
Das timing wurde nochmals nachgebessert.

### Schlege (2023-04-11T05:03:54Z)

werde diese gleich testen.

### FrankeEDF (2023-04-11T06:25:09Z)

Mit der Version 11 habe ich momentan ein Testaufbau mit einem programmierbaren Netzteil. Damit starte ich diesen Aufbau alle 3 Sekunden neu und Lesse kurz vor dem Abschalten die Anzahl der erkannten Module aus. Bis jetzt wurde knapp 14'000 mal neu gestartet und dabei immer die korrekte Anzahl Module erkannt.
Mein Aufbau besteht aus 5 Modulen: ATSAM als Master und 2 x Erweiterung danach noch 2 x ATXmega

### Schlege (2023-04-11T06:29:28Z)

Hallo Herr Franke,
dieser Aufbau hat bei mir auch funktioniert, bitte stellen Sie Ihren Aufbau wie folgt um,
Master mit ATSAM          ==> 1 x Erweiterung mit ATSAM                 ==> 2 x Erweiterung mit ATXMega             ==> 1 x Erweiterung mit ATSAM, bei diesem Aufbau gab es Probleme.
Werde um 10:00 Uhr mit den Tests mit der Software V11  beginnen.

Mit freundlichen Grüßen / Best Regards

Georg Selig
Elektro-Engineering (EE)

Von: Daniel Franke ***@***.***>
Gesendet: Dienstag, 11. April 2023 08:25
An: FrankeEDF/IOLink ***@***.***>
Cc: Georg Selig ***@***.***>; Assign ***@***.***>
Betreff: Re: [FrankeEDF/IOLink] Modbus Kommunikation zwischen ATSAM und ATXMEGA Systemen (Issue #41)


Mit der Version 11 habe ich momentan ein Testaufbau mit einem programmierbaren Netzteil. Damit starte ich diesen Aufbau alle 3 Sekunden neu und Lesse kurz vor dem Abschalten die Anzahl der erkannten Module aus. Bis jetzt wurde knapp 14'000 mal neu gestartet und dabei immer die korrekte Anzahl Module erkannt.
Mein Aufbau besteht aus 5 Modulen: ATSAM als Master und 2 x Erweiterung danach noch 2 x ATXmega

—
Reply to this email directly, view it on GitHub<https://github.com/FrankeEDF/IOLink/issues/41#issuecomment-1502749926>, or unsubscribe<https://github.com/notifications/unsubscribe-auth/AQNKWVZVCLSDRIOKXH466VLXAT2NBANCNFSM6AAAAAAUMF6AMQ>.
You are receiving this because you were assigned.Message ID: ***@***.******@***.***>>

[Georg Schlegel GmbH & Co. KG]<http://www.schlegel.biz/>

Georg Schlegel GmbH & Co. KG
Kapellenweg 4
D-88525 Dürmentingen
www.schlegel.biz<https://www.schlegel.biz/>

[https://www.schlegel.biz/web/we-bilder/email_signatur/linkedin_button.jpg]<https://de.linkedin.com/company/georg-schlegel-gmbh-co-kg>
        Tel.: +49 7371 / 502-240
Fax:  +49 7371 / 502-49
***@***.******@***.***> <https://www.schlegel.biz/>





[https://www.schlegel.biz/web/we-bilder/email_signatur/2022_lea_sozial_engagiert.png]


Geschäftsführer: Eberhard Schlegel, Christoph Schlegel, Wolfgang Weber
Rechtsform KG Sitz Dürmentingen HRA Ulm 650202 Komplementärin: Elektrokontakt GmbH
Sitz Dürmentingen HRB Ulm 650048 USt-IdNr.: DE 146 544 521
Alle Informationen zur Ihren gespeicherten Daten nach Artikel 13 und 14 EU DSGVO finden Sie unter folgendem Link: https://www.schlegel.biz/web/de/datenschutz.php

Diese Nachricht kann vertrauliche Informationen enthalten. Sollten Sie nicht der vorgesehene Empfänger sein, so bitten wir um eine kurze Nachricht.
Jede unbefugte Weiterleitung oder Fertigung einer Kopie ist unzulässig. Da wir die Echtheit oder Vollständigkeit der in dieser Nachricht
enthaltenen Informationen nicht garantieren können, schließen wir die rechtliche Verbindlichkeit der vorstehenden Erklärungen und Äußerungen aus.

This message may contain confidential information. If you are not the intended recipient please inform us.
Any unauthorised dissemination, distribution or copying hereof is prohibited. As we cannot guarantee the genuineness or completeness
of the information contained in this message, the statements set forth above are not legally binding.

### FrankeEDF (2023-04-11T06:48:02Z)

Okay, hab den Test neu gestartet mit dem Aufbau wie von ihnen beschrieben.

### Schlege (2023-04-11T09:37:05Z)

Kurze Rückmeldung;
Hardware funktioniert in der besagten Kombination, werde meine Testreihe zur Software Freigabe weiterführen.

### Schlege (2023-04-11T15:14:50Z)

Hallo Herr Franke,
Aktuell kann ich bestätigen, dass die Software soweit stabil läuft es stehen noch die Versuche aus mit 16 Modulen in Voller System Bestückung. Kann mir aber nicht vorstellen, dass hier noch was Unerwartetes auftreten kann.
Aus meiner Sicht können Sie die Rechnung stellen, sollte dennoch noch was Auftreten werde ich mich wieder melden.
