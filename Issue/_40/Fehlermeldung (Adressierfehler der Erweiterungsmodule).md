# Fehlermeldung (Adressierfehler der Erweiterungsmodule)

- Author: Schlege
- Created: 2023-01-31T06:26:01Z
- State: CLOSED

---

Aktuell wird über den IO-Link das ERROR Byte mit folgenden Fehlermeldungen beaufschlagt, 
==> Adressierfehler der Erweiterungsmodule
==> Änderung der Anzahl an Teilnehmern
Jedoch kommen alle Signale von den 3 Modulen korrekt an, ob Output oder Input an,
Diese Fehler werden auch auf auf der Testoberfläche dargestellt.

![grafik](https://user-images.githubusercontent.com/68856663/215682815-f26d1cb0-8277-452c-8ce2-cf238f428690.png)

## Comments

### FrankeEDF (2023-01-31T11:27:11Z)

Wieviel Module wurden den konfiguriert?

### Schlege (2023-01-31T12:21:20Z)

Aktuell arbeite ich mit den Entwicklungskitt, 1 x Master 2 X Erweiterung

### Schlege (2023-01-31T12:32:02Z)

Eventuell könnte Ihnen diese Info noch weiterhelfen:
wenn ich das System auf 2 Module in der Software auslege und aber 3 Module angeschlossen habe dann besteht keine Fehlermeldung,
![grafik](https://user-images.githubusercontent.com/68856663/215760598-39991788-6923-406d-b51c-75732f01f152.png)

### Schlege (2023-01-31T12:35:30Z)

zur Ergänzung,
bei 2 Module in der Parametrierung und 2 Module im System ist der Fehler wieder da.
![grafik](https://user-images.githubusercontent.com/68856663/215761392-5ae40cc1-1cdd-4a1e-82b1-7814cdb85ab9.png)

### FrankeEDF (2023-02-03T07:53:00Z)

Sollte mit Version 07 behoben sein

### FrankeEDF (2023-02-03T10:06:36Z)

**Achtung** mit der Version 07 muss die Parametrieung neu erfolgen

### Schlege (2023-02-03T10:07:59Z)

Erstet Test bestätigen Ihre Aussage, komme jedoch gerade nicht mehr auf den IO-Link, bzw. die Kommunikation zwischen Schlegel CPU und IO-Link CPU macht Probleme. Werde diese noch genauer untersuchen und dann gegebenen falls eine neue issus erstellen.
Zu Ihrem Hinweis Parametrieren, "ist bekannt"

### Schlege (2023-02-03T10:09:30Z)

wir haben bereits neu parametriert aktuell funktioniert alles über die Parametriersoftware.

### Schlege (2023-02-03T11:47:47Z)

Kurze Rückmeldung, System funktioniert wieder werde am Montag die Testreihe fortsetzen

### FrankeEDF (2023-02-23T12:18:22Z)

Gibt es neue Erkenntnisse?

### Schlege (2023-04-05T15:24:52Z)

Hallo Herr Franke,
Passt so noch nicht,
Habe hier 5 Module Parametriert
![grafik](https://user-images.githubusercontent.com/68856663/230127797-aa5bec39-119e-4c86-953a-2f6f7cb019a8.png)
es werden aber nur 2 Module erkannt
![grafik](https://user-images.githubusercontent.com/68856663/230127918-6283437a-d1e4-4cf1-8d00-0ad632c47bc9.png)
dennoch werden die Daten alle 5 Module korrekt über den IO-Link in beide Richtungen abgehandelt

### Schlege (2023-04-05T15:36:32Z)

Weiterer Hinweis, 
Wenn ich die Anzahl der Module dann auf 2 Korrigiere und dies auch über den IO-Link Master dem System mitteile ist die Fehlermeldung weg. Als ich dann wieder die 5 Modulen aufgeschaltet hatte wurden auf einmal 3 Module erkannt. Der Aufbau entspricht genau dem gleichen wir zuvor als er 2 Module detectiert hat.

### Schlege (2023-04-05T15:37:17Z)

Wenn ich Ihnen noch weitere gezielte Tests machen soll geben Sie einfach Bescheid

### FrankeEDF (2023-04-05T21:59:36Z)

Bitte beschreiben Sie genau die Reihenfolge der einzelnen Module ATSAM bzw ATXMega

### Schlege (2023-04-06T07:27:10Z)

Kein Problem,
die Basis ist ein Master mit ATSAM ==> Erweiterung mit ATSAM ==> Erweiterung mit ATXMega ==> Erweiterung mit ATXMega ==> Erweiterung mit ATSAM.
Folgendes ist mir auch noch aufgefallen:
- bei dem oben Beschriebenen Aufbau erkennt er bei einem Kompetten Neustart mit Neustart der Parametriersoftware 5 Module kurz darauf ändert dann die Anteige im Parametriertool von 5 auf 2 Module
- wenn ich ohne die Erweiterungs Module mit dem ATXMega arbeite erkennt er die Anzahl der 3Module korrekt.

### Schlege (2023-04-06T07:28:46Z)

werde als nächstest mit 5  Erweiterungen mit ATSAM testen.

### Schlege (2023-04-06T10:31:49Z)

Wir haben inzwischen den Aufbau mit 6 Modulen mit ATSAM getestet, die Module werden korrekt erkannt, sobald ich ein Modul mit ATXMega dazwischen habe läuft die Adressierung der Module nicht korrekt. 
Kann hier inzwischen noch besser eingrenzen, die Adressierung macht nur Probleme wenn die Module mit ATXMega zwischen den Modulen mit ATSAM plaziert werden. Am Ende des Strings werden die ATXMega Module auf einmal wieder sauber erkannt.

### Schlege (2023-04-06T10:35:32Z)

noch ein Hinweis, der Aufbau mit den ATXMega Erweiterungen am Ende des Strings läuft auch mit der Basisplatine mit ATXMega sauber an.

### Schlege (2023-04-06T11:52:18Z)

Wenn ich das Mastermodul verwende mit ATXMega dann werden die Module korrekt erkannt bei allen Kombinationen.
Beim Mastermodul mit ATSAM und dem selben String wie beim Mastermodul mit ATXMega werden die Module nach dem ersten Erweiterungsmodul mit ATXMega nicht mehr erkannt.

### Schlege (2023-04-11T15:10:10Z)

hat sich erledigt
