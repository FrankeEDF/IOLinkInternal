# Modbus: Multiple-Write kommt eine (falsch formatierte) Fehler Antwort

- Author: FrankeEDF
- Created: 2020-09-21T20:42:07Z
- State: CLOSED

---

Hier scheint wohl etwas mit der Modbus Kommunikation nicht ganz zu funktionieren. Auf den Multiple-Write gibt es eine (falsch formatierte) Fehler Antwort:
![grafik](https://user-images.githubusercontent.com/68891435/93479140-43bb0b00-f8fc-11ea-991d-5d66f7fd9a7f.png)

_Originally posted by @aot-tmg in https://github.com/FrankeEDF/IOLink/issues/15#issuecomment-694243375_

## Comments

### FrankeEDF (2020-09-21T20:51:56Z)

Die Fehler Antwort kommt, wenn das Erweiterungsmodul nicht erreicht wird oder bei Starten nicht erkannt wurde.
Die Antwort ist tatsächlich falsch formatiert. Es fehlt die vorangestellte Modbus ID.
