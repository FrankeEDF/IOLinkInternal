# Software Testreige

- Author: Schlege
- Created: 2022-12-14T08:04:37Z
- State: CLOSED

---

Aktuell scheint es so wie wenn die Parameter Daten nach einem Neustart verloren gehen. Habe auch keine kontinuierliche Kommunikation über den Modbus zu den Erweiterungsmodulen. Siehe Bild Diagnostic
![grafik](https://user-images.githubusercontent.com/68856663/207539149-32c25695-d453-4bd9-b068-38f85516bc43.png)

![grafik](https://user-images.githubusercontent.com/68856663/207539791-cba90786-74dc-4daf-a162-bf19206543ea.png)

## Comments

### Schlege (2022-12-19T13:30:41Z)

Auf das Zweite Erweiterungsmodul habe ich Aktuell über die Parametrier-Software keinen Zugriff.  Das Erste Erweiterungsmodul auch nur bedingt, Mal geht es mal geht es nicht, hier die Fehlermeldung zum Ereigniss.
![grafik](https://user-images.githubusercontent.com/68856663/208436925-231b6868-f986-48b2-a5a8-5afdb8bfd16f.png)

### FrankeEDF (2022-12-19T21:36:14Z)

Mit der Version 0.5 sollte der Fehler mit den Erweiterungsmodulen behoben sein

### Schlege (2022-12-20T16:38:50Z)

kann jetzt mit der Parametrier Software auf die Module zugreifen, dieser Part passt, werde morgen weiter testen.
mir ist noch aufgefallen dass der Poti Eingang den Wert 100 anzeigt wenn kein Poti gesteckt ist bzw. wenn der Eingang Bim_Wert offen ist. Auf der Leitung stehen dann 0,64V an konnte noch nicht herausfinden woher diese kommen. 
Mit gestecktem Poti passt alles.

### Schlege (2022-12-21T08:34:10Z)

Hallo Herr Franke,
können Sie bitte prüfen ob Controllerseitig hier über die Beschaltung des Analog Inputs der Pin mit einer Spannung beaufschlagt wird. in der Hardware konnten wir nichts finden.

### FrankeEDF (2023-01-26T15:28:42Z)

Bitte für jedes neue Thema ein neuen Issue anlegen!
