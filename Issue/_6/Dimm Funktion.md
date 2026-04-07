# Dimm Funktion

- Author: Schlege
- Created: 2020-07-27T14:32:20Z
- State: CLOSED
- Labels: enhancement

---

Die Dimm Funktion funktioniert soweit jedoch haben wir hier das Problem, dass hier der Default Wert in den Prozessdaten 0 ist und diese zur Folge hat dass die LED´s auf 0 gedimmt werden also OFF sind. Wenn jetzt Jemand die Dimmung über IO-Link nicht verwendet ist dieser gezwungen des Dimmwert immer auf 255 zu setzen, wird dies Übersehen dann wird im ersten Moment keine Status LED Leuchten.
Bittte prüfen Sie was Sie für eine Möglichkeit sehen hier bei der Inbetriebnahme über einen Default Wert zu arbeiten.

## Comments

### Schlege (2020-08-03T15:34:56Z)

Wir haben hausintern beschlossen dass die Thematik mit der Dimmung so bleibt, wir werden Diese über die Bedieungsanleitung  abhandeln

### FrankeEDF (2020-09-08T11:30:26Z)

Die Dimmung wurde mit dem neuen Treiber überarbeitet und ist nun wie bei den LIN Panels
