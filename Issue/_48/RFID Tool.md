# RFID Tool

- Author: Schlege
- Created: 2025-09-29T09:56:09Z
- State: CLOSED
- Labels: wontfix

---

Können Sie mich bitte bei der Inbetriebnahme des Modbus Tool unterstützen.
ein kurzer Rückruf würde völlig reichen.

## Comments

### FrankeEDF (2025-09-29T11:30:06Z)

Das GUI-Tool benötigt eine Modbus Verbindung zur IO Link Platine

- entweder über die Schnittstelle zum Deutschmann-IC( Deutschman im Reset halten)
- oder die USB Virtuelle Com Port Schnittstelle.

wird also ähnlich angeschlossen wie das Konfigurationstool für die Fertigung 

über den Debug Port gibt es **keine** Modbus-Funktionalität. Das Gui Tool und das Konfigurationstool funktionieren darüber **nicht**. Über den Debug Port kommen nur für die Entwicklung hilfreiche Klartext Ausgaben. 
Es kann sinnvoll sein auch diese mit anzuschließen. dafür benötigt man einen weiteren Serial - USB Adapter und ein Terminal um die Ausgaben auf den PC zu bekommen.

### Schlege (2025-09-29T13:14:03Z)

hab die Schnittstelle zum Deutschmann Modul verwendet, Passt aber immer noch nicht. Bin von der TX Leitung von der CPU auf den RX Pin an einem UART to USB Wandler gegangen und bei der RX Leitung auf die TX Leitung.

<img width="1202" height="932" alt="Image" src="https://github.com/user-attachments/assets/fb9ad7d1-f9ad-429f-a772-ce9959e3ef48" />

### Schlege (2025-09-29T13:15:18Z)

Ist bestimmt wieder eine Kleinigkeit die ich übersehen habe.

### FrankeEDF (2025-09-29T14:09:17Z)

es kommen keine RX Ausgaben. Wie geschrieben ist das Anschluss Schema das selbe wie für das PC Konfigurationstool, das in der Fertigung benutzt wird.

### Schlege (2025-09-29T14:50:22Z)

Ok hatte den falschen Port ausgewählt, war Irritierend da bei jedem Port das Programm grün "Connected" angezeigt hat.

### Schlege (2025-09-29T14:52:29Z)

Nun die Tags nach ISO 15693 liest er so nicht aus

<img width="1202" height="932" alt="Image" src="https://github.com/user-attachments/assets/f7632fd7-0ef6-460a-9f91-e88a645f126a" />

### Schlege (2025-09-29T15:20:48Z)

Hab den Fehler gefunden, lese jetzt den Kompletten Datensatz ein. 
Jedoch werden nicht alle Transponder erkannt. Sind die Test Transponder bereits bei Ihnen angekommen.

### FrankeEDF (2025-09-29T16:40:30Z)

Für eine neues Thema bitte ein neues Ticket anlegen. Das manche Transponder nicht funktionieren hat ja nichts mit dem der Überschrift "RFID Tool" zu tun ...

### Schlege (2026-01-30T09:02:05Z)

Hallo Herr Franke,
hab gerade Probleme mit dem Modbus Tool
FB1 funktioniert sauber FB3 bekomme ich folgende Fehlermeldung wenn ich den Code  "Send to RFID"

<img width="1202" height="932" alt="Image" src="https://github.com/user-attachments/assets/55b397d2-7e3e-4421-b6e9-5b0955adae10" />

Können Sie mir auch noch was zur Zusammenstellung der Codes in den TX und RX Feldern schreiben.

### Schlege (2026-01-30T09:41:26Z)

kann ich davon ausgehen dass der Anhang CRC dann die Checksumme berechnet

### Schlege (2026-01-30T10:50:26Z)

hab gerade über das "Manual Register Access" Reiter versucht die Register auszulesen und folgende Fehlermeldung bekommen.

<img width="1202" height="1032" alt="Image" src="https://github.com/user-attachments/assets/0ab8ee0f-8b9e-4087-9640-29c94653856c" />

Kann momentan keine Fehlbedienung erkennen,

### FrankeEDF (2026-02-06T00:02:04Z)

<img width="1176" height="724" alt="Image" src="https://github.com/user-attachments/assets/f8d80a0c-37c0-46e8-9bd6-d1a69886bdfb" />

Die Register 1000 bis 1008 sind als "Write only deklariert"
