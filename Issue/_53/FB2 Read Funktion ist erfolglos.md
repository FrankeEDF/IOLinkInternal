# FB2 Read Funktion ist erfolglos

- Author: Schlege
- Created: 2026-01-28T13:54:41Z
- State: CLOSED

---

Bei der Abfrage des Speicher Blocks im Transponder kommt nach dem Read Befehl keine Rückantwort von der CPU.
Die Register 1018 bis 1025 werden gelesen jedoch ohne Daten aus dem Transponder.
Die Read Funktion läuft über den FC03 ab wie bei allen anderen Read Abfragen. Bei den Tasten funktioniert es korrekt nur nicht beim lesen des Speicherblocks.
Bei Ihrem Modbus Tool funktioniert es korrekt, also vermute ich hier den Unterschied im Protokoll Aufbau. Wie sid bei ihnen der Steuercode aus welchen Sie zur  CPU schicken, meiner entspricht dem Standard Aufbau 01 03 03 FA

## Comments

### FrankeEDF (2026-01-28T14:05:59Z)

im Modbus Tool kann man die Kommunikation anschauen

<img width="1201" height="293" alt="Image" src="https://github.com/user-attachments/assets/07545d34-cd23-4b02-866e-3ddd2de7848b" />

### FrankeEDF (2026-01-28T14:24:47Z)

[rfid_modbus_sequence_read_block.pdf](https://github.com/user-attachments/files/24913005/rfid_modbus_sequence_read_block.pdf)

### Schlege (2026-01-29T13:10:22Z)

Hallo Herr Franke,
hab den Fehler gefunden, der Datensatz zum KeyA und KeyB muss geswapt werden hier hat mich das Unigate IC überlistet

### FrankeEDF (2026-01-29T14:25:08Z)

hat sich damit auch #52 erledigt?

### Schlege (2026-01-30T09:43:35Z)

Ja #52 können wir erledigen
