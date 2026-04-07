# Darstellung in der IO-Link Mastersoftware.

- Author: Schlege
- Created: 2020-08-03T06:30:59Z
- State: CLOSED
- Labels: bug

---

Hallo Herr Otterstätter,

den Punkt Seriennummer und HW-Version können wir nun Schließen, die Passt nun.

![Startbildschirm](https://user-images.githubusercontent.com/68856663/89152532-9bc3cb00-d563-11ea-8223-3c396a9641c3.png)

## Comments

### Schlege (2020-08-03T06:35:17Z)

Hallo Herr Otterstätter,

wie entsteht folgender Effekt, kann es sein dass dies mit der IODD Datei zusammen hängt.
Wenn ich die IO-Link Mastersoftware starte sieht der Bildschirm wie folgt aus 
![Startbildschirm](https://user-images.githubusercontent.com/68856663/89152701-ee9d8280-d563-11ea-902f-173ee64ba664.png)
Wenn ich dann die Zeilen im Feld Identifikation nacheinander anklicke werden die Daten aus der Schlegel CPU hochgeladen und verändern sich wie folgt.
![Startbildschirm_Aktualisiert](https://user-images.githubusercontent.com/68856663/89152910-2f959700-d564-11ea-8ea5-84179caa97dd.png)

### Schlege (2020-08-03T06:37:53Z)

besteht hier die Möglichkeit dass diese Daten gleich bei start der IO-Link Mastersoftware geladen werden, oder müssen wir dann hier die IODD Datei anpassen.

### aot-tmg (2020-09-01T10:44:34Z)

Die Daten die zuerst angezeigt werden sind die Defaults aus der IODD. Wenn diese konstant sind, kann ich diese auch in der IODD anpassen.

### Schlege (2020-09-01T13:25:09Z)

ok dann müssen wir die Daten auf den neusten einheitlichen Stand bringen.
Vendor Name        ==> ist Korrekt, kann so bleiben
Vendor Text           ==> ist Korrekt, kann so bleiben
Product Name        IO-Link IO-Modul
Product ID             IL_PB17115_03
Product Text           16x8 I/O Module 

Ändern Sie bitte auch gleich noch den Bezug auf das Bild für folgenden Namen   ==> deviceSymbol    
     "Schlegel - IO-Link - Bediensystem.png"

### aot-tmg (2020-09-01T13:40:15Z)

Wird angepasst. Nur warum wollen sie den Bezug auf das Bild ändern? Die Namen werden zum Teil von der IO-Link Spezifikation vorgegeben.

### Schlege (2020-09-01T13:47:02Z)

Ok, im Grunde will ich nur eine neutrale Bezeichnung un an dieser Stelle durch das tauschen des Bildes nicht auch noch die IODD Datei anzupassen. In welcher Form ist diese Bezeichnung durch die IO-Link Spezifikation vorgegeben.

### aot-tmg (2020-09-17T07:58:51Z)

Hab ich in neuester IODD angepasst. Geht Ihnen dann als Komplettsendung zu.
Bildername sind wie folgt spezifiziert:
![grafik](https://user-images.githubusercontent.com/68891435/93437518-5ddcf500-f8cc-11ea-9ca6-782e00cae206.png)

### Schlege (2020-09-17T08:19:27Z)

Wenn ich es nun richtig verstehe brauche ich nur im Ordner unter den entsprechenden Bezeichnungen wie z.B. **pic.png** ein Bild hinterlegen, was auf dem Bild abgebildet ist, ist nicht wichtig. Es muss nur das Format und die Datengröße passen.
Wenn dem so ist dann brauchen wir hier bezüglich der Bilder nichts anpassen.

### Schlege (2020-09-17T08:26:55Z)

Den IO-Link Workshop hinsichtlich IODD Datei habe ich genemigt bekommen somit können Wir diesen Part auch über diesen abwickeln. Im Prinzip geht es nur darum bei Kundenspezifischen Systemen die IODD Datei so einfach wie möglich selber abhandeln zu können.
Werde nächste Woche einen Gemeinsamen Termin suchen wann wir das Web-Meeting abhandeln können. Wir werden hier dann die zwei 1/2 Tage Variante bevorzugen. Diese zwei Tage sollten dann auch nicht soweit auseinander liegen, können Sie schon mal prüfen wie es bei Ihnen in KW 40 und 41 aussieht?

### aot-tmg (2020-09-17T08:52:05Z)

Bitte schauen Sie sich die Namensgebung der Bilder genau an dort steht:
`<vendor-name>-<picture-name>-pic.png`
demnach ist pic.png nicht zulässig. Selbstverständlich muss die Referenz auf das Bild in der IODD auch eingetragen werden.

### Schlege (2020-09-17T09:21:21Z)

Hallo Herr Otterstätter,
Ich vermute wir denken hier an einander vorbei,
Hier ein Bild zum Verzeichnis zur IODD Datei
![grafik](https://user-images.githubusercontent.com/68856663/93451287-45260c80-f8d7-11ea-9424-be83a52f9f73.png)

wenn ich hier das Bild unter der Bezeichnung Schlegel-PB-17115-03-pic gegen ein anderes mit der gleichen Bezeichnung austausche dann solte es doch die IODD Datei nicht interessieren. Wenn dem so ist würde mir reichen wenn wir hier für die Bezeichnung z.B. "Schlegel-PB-17115-03" einen Text wie "Schlegel-Applikation" verwenden könnten.

### Schlege (2020-09-17T09:58:23Z)

eigentlich geht es mir nur um die Bezeichnung "Schlegel-PB-17115-03" die Nummer 17115 wäre hier für uns im Hause Schlegel irreführend wenn Sie für die Bezeichnung **"Schlegel-PB-17115-03"** den Text  **"Schlegel-Applikation"** verwenden könnten dann hätten wir alles. Die Ergänzungen (z.B.--pic.png) im File Name bleiben dann immer noch IO-Link Conform und wird auch nicht angerührt.

### aot-tmg (2020-09-17T15:03:05Z)

Ich hab die IODD dahingehend angepasst. Obgleich ich mit Ihrer Vorgehensweise nicht wirklich einverstanden bin, ich würde die Bilder jeweils separat (so wie die IODD) nennen dann ist eine bessere Zuordnung möglich. Außerdem könnte es sein, dass Bilder im gleichen Ordner gehalten werden und dadurch sich die Bilder von verschiedenen IODDs überschreiben.

ProductName und ProductText werden aus der Schlegel-CPU ausgelesen, daher hab ich hier keinen Einfluss. In der IODD habe ich die Default-Werte allerdings angepasst.

### Schlege (2020-09-21T12:32:22Z)

Nun wenn wir mit der Schulung zur IODD Datei durch sind dann sehe ich großes Potential dass wir hier die Betrachtung mit der Bildzuordnung auch IO-Link Konform durchführen können. Sehe die Situation hier nicht in Stein gemeiselt.

### aot-tmg (2020-09-21T13:02:32Z)

Richtig.
