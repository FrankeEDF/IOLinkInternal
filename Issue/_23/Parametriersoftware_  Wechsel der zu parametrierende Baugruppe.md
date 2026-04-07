# Parametriersoftware:  Wechsel der zu parametrierende Baugruppe

- Author: Schlege
- Created: 2020-09-09T04:33:35Z
- State: CLOSED
- Labels: enhancement

---

Beim Wechseln der Baugruppe von z.B. 1.Erw aus 2.Erw wird die Kommunikation unterbrochen und muss erneut connectet werden.
dies geschieht auch wenn die Einheit getauscht wird. Da diese Software in der Fertigung verwendet wird sollten wir hier beim Wechsel der Baugruppe wie auch beim Wechsel der Zuordnung wie z.B. von Basis auf 1.Erw nicht erneut connecten müssen.
Das ist eine zu große Fehlerquelle für das Bedinpersonal und zu Zeitaufwändig.

PS: in dieser Zeit ist der USB to UART Adapter immer über die USB Schnittstelle mit spannung versorgt.

## Comments

### Schlege (2020-09-09T04:47:00Z)

Sollte es beim Wechsel der Baugruppe nicht möglich sein dann bitte einen gut sichtbaren bzw, nicht zu übersehenden Butten zum neu connecten vorsehen. 

![grafik](https://user-images.githubusercontent.com/68856663/92555122-4025e500-f267-11ea-89d9-74ad5d1ba1dc.png)

In der Fertigung werden später die Einzelnen Baugruppen in Cargen gefertigt und dabei auch Parametriert, hier müssen wir sehr Zeitoptimiert arbeiten da Jeder Klick uns Zeit kostet.

### FrankeEDF (2020-09-11T11:48:48Z)

Mit der PS 1.2.1.6 wird bei Wechsel nicht mehr nur durch den Wechsel der Baugruppe getrennt

### Schlege (2020-09-14T14:22:53Z)

Diese Funktion läuft inzwischen sauber der Wechsel zwischen den Modulen ist möglich auch ohne einem erneuten Connechten.

Aktuell haben wir nur noch das Problem wenn wir die Einzelmodule einzeln parametriesieren dass bei jedem Wechsel der Baugruppe nach ca. 5 Sekunden ein Timeout Fehler ansteht. Besteht hier die Möglichkeit dass entweder die Zeit auf 15 Skunden verlängert wird oder am Besten dieser Fehler nicht mehr ansteht.

Welcher Zustand besteht wenn das Modul gewechselt wird:
1.) die Baugruppe wird komplett von der Spannung genommen 
2.) der USB to UART Adappter wird weiterhin über die USB Schnittstelle versorgt.

![grafik](https://user-images.githubusercontent.com/68856663/93096585-de211180-f6a4-11ea-95a1-473b0fe68951.png)

### FrankeEDF (2020-09-14T17:58:16Z)

der Timeout tritt nur auf, wenn man auf der Diagnose Seite ist. Dort findet eine Zyklische Kommunikation statt.
Auf der Konfigurationsseite findet keine zyklische Kommunikation statt. Daher gibt es dort erst ein Timeout wenn man eine Aktion auslöst. Ein Verlängerung der Zeit hätte nur zur Folge das die Meldung entsprechend später angezeigt wird.

### Schlege (2020-09-15T04:16:58Z)

OK Herr Franke, damit kann ich leben.
