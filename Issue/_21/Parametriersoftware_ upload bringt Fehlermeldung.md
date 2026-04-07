# Parametriersoftware: upload bringt Fehlermeldung

- Author: Schlege
- Created: 2020-09-08T14:55:54Z
- State: CLOSED
- Labels: bug

---

Hallo Herr Franke, 
wenn ich einen Datensatz auf die Schlegel CPU laden will kommt folgende Fehlermeldung
![grafik](https://user-images.githubusercontent.com/68856663/92492488-ad982e00-f1f3-11ea-99f9-ce741ea24b33.png)

Das Eingabe Fenster der IO-Link Device ID ist rot umrandet obwol diese nur 4 Stellen hat, Hat dies was zu bedeuten oder hängt dies mit dieser Fehlermeldung zusammen.

## Comments

### Schlege (2020-09-08T14:56:48Z)

hier noch ein Bild von der Oberfläche
![grafik](https://user-images.githubusercontent.com/68856663/92492969-462eae00-f1f4-11ea-8c36-72d9654e9a80.png)

### FrankeEDF (2020-09-09T08:35:39Z)

Laut spezifiaktion ist die Device ID 3 Byte; es müssen also 6 Stellige Werte eingegben werden

### Schlege (2020-09-09T15:58:56Z)

ok muss ich mit Herrn Otterstätter noch klären, aktuell hat die Device ID 4 Stellen es soll aber auch eine mit 24Bit Variante geben welche dann 3 Byte benötigt. 
Vorerst werden wir die Zwei zusätzlichen Stellen mit 00 füllen. Das würde dann auch die Fehlermeldung aus der PS erklären.
