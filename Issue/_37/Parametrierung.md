# Parametrierung

- Author: Schlege
- Created: 2023-01-30T11:29:18Z
- State: CLOSED

---

nach einem Neustart gehen die Parameterdaten zum Teil verloren.
Parametrierte Daten
![grafik](https://user-images.githubusercontent.com/68856663/215465076-a35ecb55-9083-431a-b536-a0d3a7ad9f93.png)

Nach Neustart
![grafik](https://user-images.githubusercontent.com/68856663/215464913-b5bd0677-cdd8-4bca-a134-2ec927e36a96.png)

## Comments

### Schlege (2023-01-30T11:31:48Z)

Sorry hier noch mit der Basis
![grafik](https://user-images.githubusercontent.com/68856663/215465550-dc59a33b-7238-4c7c-9971-b7a9175aeaea.png)

### Schlege (2023-01-30T11:39:33Z)

die Firmware wurde heute heruntergelagen
![grafik](https://user-images.githubusercontent.com/68856663/215467035-255655ba-e827-4297-b150-aa2698973d50.png)

### Schlege (2023-01-31T11:40:33Z)

Eine weitere Untersuchung ergab hinsichtlich des verlierens der Parameterdaten folgendes Ergebnis:
die Daten werden nur in diesem Ablauf unkontroliert verändert.
![grafik](https://user-images.githubusercontent.com/68856663/215750382-29f70be1-3427-4c36-b358-abca9eac2040.png)

System ist in Betrieb, der IO-Link ist nicht angeschlossen ==> Parametrierung wird gestartet Daten sind korrekt abgelegt ==> Verbindung zum Parametrieren wird getrennt ==> Spannungsversorgung zum System wird unterbrochen für ca. 3 bis 4 Sec und anschließend wieder gestartet  ==> Verbindung zur Parametrierung wird hergestellt ==> Daten werden Ausgelesen. 

![grafik](https://user-images.githubusercontent.com/68856663/215750308-5cbeb470-fe02-4420-b1e2-cce76feb6234.png)

### Schlege (2023-01-31T11:42:18Z)

PS: muss oben folgende Aussage korrigieren "Ablauf unkontroliert verändert." in
"Die Daten werden immer konstant geändert."

### FrankeEDF (2023-02-03T07:52:22Z)

Sollte mit Version 07 behoben sein:

### FrankeEDF (2023-02-03T10:08:32Z)

**Achtung** mit der Version 07 muss die Parametrierung neu durchgeführt werden.

### Schlege (2023-02-03T10:15:36Z)

Erste Veruche haben Ihre Aussage bestätigt, die Parametrierung geht nicht mehr über die Parametriersoftware verlohren. Aktuell muss hier noch die IO-Link Schiene geprüft werden.

### FrankeEDF (2023-02-23T12:18:55Z)

Gibt es neue Erkenntnisse?

### Schlege (2023-02-28T16:19:47Z)

Werde hier mit der Version V08 weitertesten

### FrankeEDF (2023-04-11T20:01:37Z)

Gibt es neue Erkenntnisse?

### Schlege (2023-04-13T12:41:44Z)

Hallo Herr Franke,
es gibt ab und zu Probleme mit dem Connekten vermute aber dass es sich hier um ein Windows Problem handelt. Aktuell passt di Parametriesierung über das Tool. wir können diese Aufgabe hier auch schließen.
