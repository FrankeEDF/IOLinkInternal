# GitHub Issues Uebersicht

*Stand: 2026-03-29*

| Version | Datun      |                                                           |
|---------|------------|-----------------------------------------------------------|
| V0.10   | 09.10.2025 | ISO 15693 Unterstützung                                   |
|         |            | Unterscheidung zwischen ISO 14443A (MIFARE) und ISO 15693 |
|         |            | ISO-Typ-Feld zu RFID Register Map hinzugefügt.            |
|         |            | Communication Error Handling                              | 
| V0.9    | 02.09.2025 | FB3 implenetiert - RFID Tunnel Mode )                     |
|         |            | LED-Steuerung über Modbus                                 |
| V0.8    | 02.09.2025 |                                                           |
| V0.7    | 01.09.2025 | FB2 implenetiert                                          |
| V0.6    | 20.02.2025 |                                                           |

---

## Issues 48-59

| #      | Thema                                        | Status      | Eroeffnet  | Geschlossen | Geschlossen von | Codeaenderung durch FrankeEDF efolgt                                                              |
|--------|----------------------------------------------|-------------|------------|-------------|-----------------|---------------------------------------------------------------------------------------------------|
| **59** | Frage Modbus Tool                            | Geschlossen | 05.02.2026 | 06.02.2026  | Schlege         | Nein - nur Rueckfrage zur CRC-Checksumme                                                          |
| **58** | Fehlerhafter FB1                             | Geschlossen | 02.02.2026 | 05.02.2026  | Schlege         | Nein - UID beim Uebergang FB0->FB1 wurde nicht uebertragen, Firmware-Fix durch FrankeEDF          |
| **57** | LED Ansteuerung unvollstaendig               | **OFFEN**   | 02.02.2026 | -           | -               | Ja (ausstehend) - LED Offline-Funktion (Code 0x14) noch nicht implementiert                       |
| **56** | Software Update FB3                          | Geschlossen | 30.01.2026 | 30.01.2026  | FrankeEDF       | Nein - kein Inhalt                                                                                |
| **55** | Software Update FB1                          | Geschlossen | 30.01.2026 | 30.01.2026  | FrankeEDF       | Nein - Dupilicat #57 - LED-Verhalten bei FB1-Wechsel implementiert (gruen, dann Reader-gesteuert) |
| **54** | Software Update FB2                          | Geschlossen | 30.01.2026 | 30.01.2026  | FrankeEDF       | Ja (ausstehend) - LED-Verhalten, Error-Code in Reg. 1026 und Neustart-Default FB1 umgesetzt       |
| **53** | FB2 Read Funktion erfolglos                  | Geschlossen | 28.01.2026 | 29.01.2026  | Schlege         | Nein - Protokoll-Missverstaendnis auf Kundenseite                                                 |
| **52** | Kommunikationsprobleme FB2                   | Geschlossen | 28.01.2026 | 02.02.2026  | Schlege         | Nein - Byte-Swap-Problem lag beim Kunden (Unigate)                                                |
| **51** | Timing Modbus Protokoll                      | Geschlossen | 19.01.2026 | 02.02.2026  | Schlege         | Nein - Timing-Problem auf Kundenseite (Deutschmann)                                               |
| **50** | Funktionsprobleme mit FB2                    | **OFFEN**   | 10.11.2025 | -           | -               | Offen - Speicherengpass im Unigate IC, Loesung noch ausstehend                                    |
| **49** | Kommunikationsprobleme mit Transponder-Typen | Geschlossen | 30.09.2025 | 05.02.2026  | FrankeEDF       | Ja - Kompatibilitaetsfehler mit diversen Transponder-Typen in der Firmware behoben                |
| **48** | RFID Tool                                    | Geschlossen | 29.09.2025 | 06.02.2026  | FrankeEDF       | Nein - wontfix, nur Support-Anfrage fuer Inbetriebnahme des Modbus-Tools                          |

## Alle Issues

| #      | Thema                                            | Status      | Eroeffnet  | Geschlossen | Geschlossen von |
|--------|--------------------------------------------------|-------------|------------|-------------|-----------------|
| **59** | Frage Modbus Tool                                | Geschlossen | 05.02.2026 | 06.02.2026  | Schlege         |
| **58** | Fehlerhafter FB1                                 | Geschlossen | 02.02.2026 | 05.02.2026  | Schlege         |
| **57** | LED Ansteuerung unvollstaendig                   | OFFEN       | 02.02.2026 | -           | -               |
| **56** | Software Update FB3                              | Geschlossen | 30.01.2026 | 30.01.2026  | FrankeEDF       |
| **55** | Software Update FB1                              | Geschlossen | 30.01.2026 | 30.01.2026  | FrankeEDF       |
| **54** | Software Update FB2                              | Geschlossen | 30.01.2026 | 30.01.2026  | FrankeEDF       |
| **53** | FB2 Read Funktion erfolglos                      | Geschlossen | 28.01.2026 | 29.01.2026  | Schlege         |
| **52** | Kommunikationsprobleme FB2                       | Geschlossen | 28.01.2026 | 02.02.2026  | Schlege         |
| **51** | Timing Modbus Protokoll                          | Geschlossen | 19.01.2026 | 02.02.2026  | Schlege         |
| **50** | Funktionsprobleme mit FB2                        | OFFEN       | 10.11.2025 | -           | -               |
| **49** | Kommunikationsprobleme mit Transponder-Typen     | Geschlossen | 30.09.2025 | 05.02.2026  | FrankeEDF       |
| **48** | RFID Tool                                        | Geschlossen | 29.09.2025 | 06.02.2026  | FrankeEDF       |
| **47** | Probleme V02 Platine                             | Geschlossen | 13.02.2024 | 06.05.2024  | FrankeEDF       |
| **46** | Hintergrundinfo                                  | Geschlossen | 11.07.2023 | 11.07.2023  | Schlege         |
| **45** | Fehlercode Parametriersoftware                   | Geschlossen | 26.04.2023 | 30.01.2024  | FrankeEDF       |
| **44** | Versionierung der Software                       | Geschlossen | 11.04.2023 | 11.04.2023  | FrankeEDF       |
| **43** | Schaltzykluszaehler                              | Geschlossen | 05.04.2023 | 11.04.2023  | FrankeEDF       |
| **42** | Fehlerbetrachtung LED Fehler                     | Geschlossen | 03.02.2023 | 03.02.2023  | Schlege         |
| **41** | Modbus ATSAM/ATXMEGA Kommunikation               | Geschlossen | 31.01.2023 | 11.04.2023  | FrankeEDF       |
| **40** | Fehlermeldung Adressierfehler Erweiterungsmodule | Geschlossen | 31.01.2023 | 11.04.2023  | FrankeEDF       |
| **39** | Software Stand                                   | Geschlossen | 30.01.2023 | 31.01.2023  | FrankeEDF       |
| **38** | Connect Parametriersoftware                      | Geschlossen | 30.01.2023 | 30.01.2023  | Schlege         |
| **37** | Parametrierung                                   | Geschlossen | 30.01.2023 | 13.04.2023  | Schlege         |
| **36** | SAM4S Poti Eingang zeigt 100                     | Geschlossen | 26.01.2023 | 26.01.2023  | FrankeEDF       |
| **35** | Software Testreihe                               | Geschlossen | 14.12.2022 | 26.01.2023  | FrankeEDF       |
| **34** | Erweiterungsmodul: Pin 5 nicht mit GND           | Geschlossen | 11.11.2022 | 30.01.2023  | Schlege         |
| **33** | Treiber MPQ3324 / MP3326                         | Geschlossen | 31.08.2022 | 01.09.2022  | FrankeEDF       |
| **32** | Pinbelegung DEBUG-Signale                        | Geschlossen | 31.08.2022 | 03.02.2023  | Schlege         |
| **31** | Pinbelegung Modbus SAM4S2                        | Geschlossen | 31.08.2022 | 03.02.2023  | Schlege         |
| **30** | Baudraten-Fehler Berechnung                      | Geschlossen | 09.06.2021 | 21.10.2021  | FrankeEDF       |
| **29** | Parametrier Software 1.4.1.8                     | Geschlossen | 08.04.2021 | 31.08.2022  | FrankeEDF       |
| **28** | Anfrage Mitlesen LIN Bus                         | Geschlossen | 01.04.2021 | 01.04.2021  | FrankeEDF       |
| **27** | Kommunikationsproblem Modbus-Schnittstelle       | Geschlossen | 01.04.2021 | 06.04.2021  | FrankeEDF       |
| **26** | Darstellung HW-/SW-Version                       | Geschlossen | 22.09.2020 | 22.09.2020  | Schlege         |
| **25** | Modbus Multiple-Write Fehlerantwort              | Geschlossen | 21.09.2020 | 21.09.2020  | FrankeEDF       |
| **24** | Parametriersoftware: Darstellung Strings         | Geschlossen | 15.09.2020 | 15.09.2020  | FrankeEDF       |
| **23** | Parametriersoftware: Baugruppen-Wechsel          | Geschlossen | 09.09.2020 | 11.09.2020  | FrankeEDF       |
| **22** | Status-LED Kommunikation                         | Geschlossen | 09.09.2020 | 09.09.2020  | FrankeEDF       |
| **21** | Parametriersoftware: Upload Fehlermeldung        | Geschlossen | 08.09.2020 | 09.09.2020  | FrankeEDF       |
| **20** | Error Byte                                       | Geschlossen | 07.09.2020 | 21.09.2020  | aot-tmg         |
| **19** | Anzeige LED-Ausfall                              | Geschlossen | 07.09.2020 | 21.09.2020  | aot-tmg         |
| **18** | Modbus Master Kommunikations-LED                 | Geschlossen | 07.09.2020 | 14.09.2020  | FrankeEDF       |
| **17** | Analog Wert                                      | Geschlossen | 03.08.2020 | 21.09.2020  | aot-tmg         |
| **16** | Device ID                                        | Geschlossen | 03.08.2020 | 21.09.2020  | aot-tmg         |
| **15** | Datenaustausch Schaltzyklus-Limiten              | Geschlossen | 03.08.2020 | 21.09.2020  | Schlege         |
| **14** | Darstellung IO-Link Mastersoftware               | Geschlossen | 03.08.2020 | 21.09.2020  | aot-tmg         |
| **13** | Neuer LED-Treiber                                | Geschlossen | 28.07.2020 | 08.09.2020  | FrankeEDF       |
| **12** | IOLink Betriebsdauerzaehler falsch               | Geschlossen | 28.07.2020 | 11.09.2020  | FrankeEDF       |
| **11** | PS: Reset Betriebsdauerzaehler fehlt             | Geschlossen | 28.07.2020 | 08.09.2020  | FrankeEDF       |
| **10** | Produkt ID                                       | Geschlossen | 27.07.2020 | 14.09.2020  | FrankeEDF       |
| **9**  | Seriennummer automatisch hochzaehlen             | Geschlossen | 27.07.2020 | 11.09.2020  | FrankeEDF       |
| **8**  | Error Byte Detected Module                       | Geschlossen | 27.07.2020 | 21.09.2020  | Schlege         |
| **7**  | Error Byte Schaltzyklen ueberschritten           | Geschlossen | 27.07.2020 | 17.09.2020  | aot-tmg         |
| **6**  | Dimm Funktion                                    | Geschlossen | 27.07.2020 | 08.09.2020  | FrankeEDF       |
| **5**  | Betriebsstundenzaehler                           | Geschlossen | 27.07.2020 | 28.07.2020  | FrankeEDF       |
| **4**  | Schaltzyklus Limiten                             | Geschlossen | 27.07.2020 | 28.07.2020  | aot-tmg         |
| **3**  | Detected Modul                                   | Geschlossen | 27.07.2020 | 21.09.2020  | FrankeEDF       |
| **2**  | Device ID                                        | Geschlossen | 27.07.2020 | 28.07.2020  | FrankeEDF       |
| **1**  | System Seriennummer                              | Geschlossen | 27.07.2020 | 28.07.2020  | aot-tmg         |

---

## Zusammenfassung

- **2 Issues noch offen:** #57 (LED Offline-Funktion) und #50 (FB2 Speicherproblem Unigate)
- **ca. 38 Issues** erforderten eine Codeaenderung durch FrankeEDF
- **ca. 19 Issues** waren Kundenfragen, Hardware-Probleme, wontfix oder kundenseitige Probleme
