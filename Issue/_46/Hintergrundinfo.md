# Hintergrundinfo

- Author: Schlege
- Created: 2023-07-11T06:43:14Z
- State: CLOSED

---

Hallo Herr Franke,
wie sind nun in der Serieneinführung mit der IO-Link Baugruppe im ATSAM Aufbau.
Wir haben das Layout unter REVA Gesichtspunkte geringfügig angepasst und dabei noch den Bestücker gewechselt.
Seit dem läuft das System nicht mehr korrekt, um hier in der Fehlersuche weiterzukommen sollte ich vom Software Ablauf wissen was Sie signalisieren wenn die Status LED langsam Blinkt, auf welche Info wartet Ihre Software dass diese sich nicht im System inizialisiert.

Sie können mich auch gerne Zurückrufen wenn es für Sie einfacher ist.

## Comments

### Schlege (2023-07-11T13:09:21Z)

Hallo Herr Franke,
Fehler hat sich erübrigt bzw. wir haben den Fehler gefunden. Der Quarz wurde mit einem falschen Wert bestückt, anstatt 16MHz wurden 14,7MHz bestückt.
