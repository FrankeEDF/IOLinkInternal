# Fehlerhafter FB1

- Author: Schlege
- Created: 2026-02-02T08:24:16Z
- State: CLOSED

---

Aktueller Ablauf der FB?

Neustart ==> FB1 aktiv          Korrekt
FB1  ==> to ==> FB2            Korrekt
FB2  ==> to ==> FB1            Korrekt
FB1  ==> to ==> FB0            Korrekt
**FB0  ==> to ==> FB1            Fehler UID wird nicht übertragen**
FB0  ==> to ==> FB2            Korrekt

Der Funktionsblock 1 kann nicht aus FB0 gestartet werden, ist nur möglich über FB2 oder Neustart

FB0  ==> to ==> FB1  muss funktional möglich sein

## Comments

### FrankeEDF (2026-02-02T22:23:24Z)

* Wenn sich der Reader per Commando im Standby Modus ist. braucht er dann ein spezielles Kommando um da wieder aufzuwachen?
* Haben sie die Schnittstellen zum RFID Reader mit aufgezeichnet?
* funktionert es mit dem GUI Tool ?
* leuchtet die LED am Reader wieder wenn von FB0 nach FB1 gewechselt wird?

Bitte alle Fragen beantworten !

Hinweis: Der Issue Titel besag das der ganze **FB1 fehlerhaft** ist. Das ist eine **unberechtigte** Mängelrüge die entsprechend in Rechnung stellen kann
