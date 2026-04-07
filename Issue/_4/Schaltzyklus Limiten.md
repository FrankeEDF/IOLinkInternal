# Schaltzyklus Limiten

- Author: Schlege
- Created: 2020-07-27T14:06:01Z
- State: CLOSED
- Labels: bug

---

Hier findet kein Austausch zwischen den CPU´s statt, die Werte welche über die Parametrier Software hinterlegt werden kommen nicht beim IO-Link an und die Daten welche im IO-Link hinterlegt werden kommen nicht bei der Schlegel CPU an. Vermute dass hier die Kommunikation nicht sauber läuft. 
Die Werte von Schaltzyklus Zähler kommen jedoch korrekt an. Auch hier wird kein Error ausgelöst wenn dieser Wert überschritten ist . Auch wenn ich über die Parametriersoftware die Key Limit einstelle und diesen Wert über schreite kommt keine Error Meldung auf den Prozessdaten.
Zusätzlich ist mir auch aufgefallen, wenn ich die Schaltzyklus Limit über die Parametrier Software (PS) eingestellt habe und dann wieder mit der PS auslese dann passen die Werte. Gehe ich dann mit der IO-Link Mastersoftware auf die Device Einstellung und schreibe die Schaltzyklus Limit in die IO-Link CPU. Lesen wir dann die Daten über die PS aus dann kommen hier wirre Werte zurück.

## Comments

### FrankeEDF (2020-07-27T18:48:04Z)

Da das schreiben / lesen der Werte über die PS richtig sind. muss wohl die IO Link CPU die "wirren Werte" ablegen

### aot-tmg (2020-07-28T09:34:42Z)

So wie ich das sehe geht es hier hauptsächlich um die Limits, welche ja nicht funktionieren alles andere scheint wohl zu klappen. Hier gab es noch einen Dreher in der IO-Link Firmware. Ist in der nächsten Software dann behoben.
