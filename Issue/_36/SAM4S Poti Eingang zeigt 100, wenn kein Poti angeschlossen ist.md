# SAM4S Poti Eingang zeigt 100, wenn kein Poti angeschlossen ist

- Author: FrankeEDF
- Created: 2023-01-26T14:44:15Z
- State: CLOSED

---

kann jetzt mit der Parametrier Software auf die Module zugreifen, dieser Part passt, werde morgen weiter testen.
mir ist noch aufgefallen dass der Poti Eingang den Wert 100 anzeigt wenn kein Poti gesteckt ist bzw. wenn der Eingang Bim_Wert offen ist. Auf der Leitung stehen dann 0,64V an konnte noch nicht herausfinden woher diese kommen. 
Mit gestecktem Poti passt alles.

_Originally posted by @Schlege in https://github.com/FrankeEDF/IOLink/issues/35#issuecomment-1359696448_

## Comments

### FrankeEDF (2023-01-26T15:27:26Z)

Laut Datenblatt fließen aus einem Eingang bis zu **1 uA**, damit fallen an dem angeschlossen 1 MOhm Widerstand bis zu 1V ab. Das ist die Spannung die der ADC dann auch ermittelt. 

Ich haber versucht den internen PullDown Widerstand mit zu aktivieren. Die Pullup / PullDown werden aber abgeschaltet sobald der an dem Pin der Analog Eingang für den ADC aktiviert wird.

![image](https://user-images.githubusercontent.com/68696065/214875527-9fe35665-1b1f-42c3-aaa1-8de433706632.png)
