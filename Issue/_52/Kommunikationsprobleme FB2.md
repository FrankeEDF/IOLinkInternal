# Kommunikationsprobleme FB2

- Author: Schlege
- Created: 2026-01-28T09:28:29Z
- State: CLOSED

---

Hi,
Bin wieder ein gutes Stück weitergekommen, LED´s lassen sich nun schalten. Beim auslesen des Speicherblocks gibt es aber Probleme.
Versuche gerade den Block 8 mit Key A auszulesen bekomme aber keine korrekten Daten geliefert.
Beim auslesen des Registers 1026 bekomme ich folgende Rückmeldung 0xE022.
Kann diese Meldung nicht zuordnen.
Beim auslesen des Registers 1026 bekomme ich folgende Rückmeldung 0xE022 ==> ist ein Unigate Fehler muss diesen Swapen korrekterweise sollte es 0x22E0 heißen.

## Comments

### Schlege (2026-01-28T13:28:01Z)

Gibt es zu den Fehlermeldungen welche generiert werden eine Zusammenfassung. Bzw. kann diesen Fehler in Ihren Unterlagen nicht finden.

### FrankeEDF (2026-01-28T13:38:42Z)

Wo haben sie den den Fehler gesucht ?

### FrankeEDF (2026-01-28T13:40:06Z)

und was hat das mit **Kommunikationsprobleme FB2** zu tun? an welcher stelle gibt es ein Problem ?
Sie müssen aussagekräftige Überschriften für das Ticket benutzten. 
Sonst haben wir 30 Tickets. die alle  **"Kommunikationsprobleme"** in der Überschrift haben

### Schlege (2026-01-28T14:13:36Z)

Nach dem Auslesen der Read Register 1018 bis 1025 lese ich zur Kontrolle nochmals das Register 1026 aus um hier diverse Fehlermeldungen zu erörtern.
Jetzt kommt beim auslesen des Registers 1026 die folgende Rückmeldung 0xE022.
Kann diese Meldung nicht zuordnen.

### FrankeEDF (2026-01-28T14:27:47Z)

die Meldung ist dokumentiert

### FrankeEDF (2026-01-28T14:30:29Z)

<img width="1261" height="616" alt="Image" src="https://github.com/user-attachments/assets/bd9fff62-7172-4bfa-b579-333db74cd3e7" />


Der **High Byte "Exception Code"** stammt vom RFID Reader. 
also Command = 0x22 -> RFID Login
Code = 0xE0 -> 


<img width="1204" height="263" alt="Image" src="https://github.com/user-attachments/assets/fd97a7b3-b474-4caa-a502-8cd946f14672" />

<img width="923" height="394" alt="Image" src="https://github.com/user-attachments/assets/935b8b28-06fe-49e1-a1c7-5113d1f28a9a" />

### FrankeEDF (2026-01-30T14:46:39Z)

nachdem #53 geschlossen ist schliese ich das hier auch
