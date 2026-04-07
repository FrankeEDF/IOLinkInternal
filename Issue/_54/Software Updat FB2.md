# Software Updat FB2

- Author: Schlege
- Created: 2026-01-30T11:41:44Z
- State: CLOSED

---

Hallo Herr Franke,
den FB2 können wir nun abschließen mit folgenden Anpassungen in der Firmware.
1.)  die LED am Reader soll bei (nach) der Auswahl von FB2 grün leuchten und über den Reader angesteuert werden. Erst wenn ein LED Kommando über den Modbus kommt welches die LED Farbe verändert dann soll die Default 
2.) Einstellung zu den LED Farben verlassen werden. 
-	Beim Neustart soll der Funktionsblock FB1 als Default Einstellung hinterlegt sein
-	LED Darstellung zwischen den Funktionsblöcken.
       o	FB0		LED Off 
       o	FB1		LED grün, Reader steuert eigenständig die LED´s an 
       o	FB2		LED grün, Reader steuert eigenständig die LED´s an bis 
                                erstes Modbus-Kommando kommt.
       o	FB3		LED grün, Reader steuert eigenständig die LED´s an bis 
                                erstes Modbus-Kommando kommt.

3. Beim Auslesen und beim Beschreiben eines Speicherblocks soll eine Error Code im Register 1026 erzeugt werden über welchen erkannt wird:
     o	Kein Transponder vorhanden
     o	Kein Mifare Classic Transponder
     o	Alles Korrekt 

Wenn Fragen zu diesen Punkten aufkommen können wir diese auch gemeinsam durchgehen

## Comments

### FrankeEDF (2026-01-30T14:45:44Z)

bitte keine Sammel-Tickets
