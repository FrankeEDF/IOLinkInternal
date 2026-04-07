# Pinbelegung / Schaltbild für Kontroller SAM4S2  - ???_DEBUG Signale

- Author: FrankeEDF
- Created: 2022-08-31T21:57:43Z
- State: CLOSED
- Labels: question

---

von G. Selig:
Kann ich davon ausgehen dass die ???_DEBUG Leitung nur zur Entwicklungsphase der Software benötigt werden?

## Comments

### FrankeEDF (2022-08-31T21:58:17Z)

Die Signale ???_Debug werden während und nach der Firmware Entwicklung zur Fehlersuche benutzt. Ganz so, wie vermutet.

### Schlege (2022-09-01T09:36:22Z)

Geht klar, dann werden wir Ihnen diese Zwei Pins auf der Entwicklungsumgebung mit zwei Litzen bereitstellen.

### FrankeEDF (2022-09-01T09:59:10Z)

Das mit den Litzen finde ich nicht so elegant!
Am liebsten wären mir eine einreihiger, 3 poliger Stecker. Rastermaß 2.54 oder 1.27 mit folgender Belegung:

| Pin | Signal   |
|-----|----------|
| 1   | RX_DEBUG |
| 2   | GND      |
| 3   | TX_DEBUG |


Dieser muss ja für die Serie nicht bestückt werden.

### Schlege (2022-09-01T13:57:06Z)

Kann ich Ihnen so noch nicht versprechen, die Platine wird am Montag einem redesign unterzogen, kann Ihnen am Dienstag mehr dazu sagen.

### FrankeEDF (2022-09-01T14:13:31Z)

Das schaffen sie bestimmt.
Die beiden Signale liegen am SAM4S direkt nebeneinander.
Viel Erfolg

| Pin | Signal   | Pin SAM4S
|-----|----------|-----|
| 1   | RX_DEBUG |5|
| 2   | GND      ||
| 3   | TX_DEBUG |6|
