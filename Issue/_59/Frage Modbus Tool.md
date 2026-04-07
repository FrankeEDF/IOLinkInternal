# Frage Modbus Tool

- Author: Schlege
- Created: 2026-02-05T14:53:52Z
- State: CLOSED

---

muss ich beim Modbus Test GUT die Checksumme im FB3 mit angeben oder reicht für die Checksumme der Code CRC in der Zeile aus?


<img width="394" height="275" alt="Image" src="https://github.com/user-attachments/assets/bbd9391f-6efc-4e24-8849-dac529aeae8d" />

## Comments

### FrankeEDF (2026-02-05T22:58:52Z)

das Tool berechnet die CRC **nicht** selber, das ist absichtlich so !!! es ist ja ein transparent Mode: alle Daten werden ohne Prüfung oder Ergänzung an den RFID Reader weitergegeben !

### FrankeEDF (2026-02-05T22:59:43Z)

Bitte im Titel **wesentlich** konkreter werden
