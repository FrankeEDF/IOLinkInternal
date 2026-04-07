# Timing Modbus Protokoll

- Author: Schlege
- Created: 2026-01-19T07:11:53Z
- State: CLOSED

---

Hallo Herr Franke,
in der Deutschmann Umgebung ist mir aufgefallen wenn ich zwei Modbusprotokolle in dem Fall zwei mal FC16 hintereinander übertrage dass diese nur korrekt interpretiert werden wenn ich zwischen die zwei Protokolle ein Delay von 1 Sekunde gesetzt ist. Können Sie prüfen mit welchem Timing die Modbus Kommunikation in Ihrer Software arbeitet.

## Comments

### Schlege (2026-01-19T08:05:08Z)

Hallo Herr Franke,
die Baudrate zum RFID Reader haben Sie von 115200 Baud 8/1/none nicht angepasst. Vermute nicht wollte aber zur Sicherheit mal nachfragen.

### FrankeEDF (2026-01-20T21:30:12Z)

um ihre Angaben prüfen zu können sind mehr Informationen nötig

### FrankeEDF (2026-01-20T22:03:16Z)

Nein, die Baudrate zum RFID-Reader wird in der Firmware nicht verändert.
Hier sind die Details dazu:
• Feste Einstellung: Die Baudrate ist im Quellcode fest auf 115200 Baud (Parity: None) vordefiniert.

### Schlege (2026-01-21T06:27:53Z)

Passt, konnte inzwischen die Kommunikation am Reader mitlesen, das passt soweit.

### FrankeEDF (2026-01-21T22:07:47Z)

Messen ist eine gute Idee um auch ihr beschriebenes Verhalten mit 1 sec min abstand zu prüfen. 
in der Atmel - Firmware gibt es keine Einschränkungen in Bezug auf Wartezeit zwischen zwei Modbus Requests. Es muss nur auf das Response gewartet werde bevor der nächste Request geschickt wird. 
im Gui Tool kann man die UID pollen. da kann mal messen:

<img width="1026" height="451" alt="Image" src="https://github.com/user-attachments/assets/5608605d-99df-421f-afb6-6b43318ea1e2" />

### FrankeEDF (2026-01-21T22:08:58Z)

ich selber kann nicht messen, ich habe das Projekt bereits vor zwei Monaten zur Seite gestellt.

### FrankeEDF (2026-01-21T22:31:50Z)

Im **ModbusConfig Tool** werden die Diagnose-Daten mit einer Rate von **500 ms** (plus der Dauer der Modbus-Kommunikation) abgefragt.

*   **Bedingung:** Die zyklische Abfrage ist nur aktiv, wenn im Programm der Reiter **"Module Diagnostic"** (`TabModuleDiagnostic`) ausgewählt ist.
*   **Ablauf:** 
    1. Der Timer wird gestoppt.
    2. Die Daten werden über Modbus gelesen/geschrieben (u.a. `ProcessDataWrite`, `ProcessDataRead`, `OperatingData` und `ModuleDataRead`).
    3. Der Timer wird erneut mit 500 ms gestartet.

Die effektive Taktrate liegt also bei ca. **2 Hz**, wobei sich die Zeit pro Zyklus leicht um die Dauer der Modbus-Antwortzeiten verlängert.
