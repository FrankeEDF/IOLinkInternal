# GitHub Issues Übersicht

*Stand: 2026-03-29*

| # | Titel | Status | Geschlossen von | Codeänderung nötig |
|---|-------|--------|-----------------|-------------------|
| **59** | Frage Modbus Tool | Geschlossen | Schlege | Nein — nur Frage zur CRC-Checksumme im Modbus-Tool |
| **58** | Fehlerhafter FB1 | Geschlossen | Schlege | Ja — UID wurde beim Übergang FB0→FB1 nicht übertragen |
| **57** | LED Ansteuerung unvollständig | **OFFEN** | — | Ja — LED Offline-Funktion (Code 0x14) fehlt noch |
| **56** | Software Update FB3 | Geschlossen | FrankeEDF | Ja (klein) — Schönheitsfehler nach FB3-Abschluss |
| **55** | Software Update FB1 | Geschlossen | FrankeEDF | Ja — LED soll bei FB1-Wechsel grün leuchten, danach Reader-gesteuert |
| **54** | Software Update FB2 | Geschlossen | FrankeEDF | Ja — LED-Verhalten, Error-Code in Reg. 1026, Neustart-Default FB1 |
| **53** | FB2 Read Funktion erfolglos | Geschlossen | Schlege | Nein — Protokoll-Missverständnis auf Kundenseite |
| **52** | Kommunikationsprobleme FB2 | Geschlossen | Schlege | Nein — Byte-Swap-Problem lag beim Kunden (Unigate) |
| **51** | Timing Modbus Protokoll | Geschlossen | Schlege | Unklar — Timing-Untersuchung, wahrscheinlich Kundenproblem |
| **50** | Funktionsprobleme mit FB2 | **OFFEN** | — | Offen — Speicherengpass im Unigate IC für FB2-Implementierung |
| **49** | Kommunikationsprobleme mit Transponder-Typen | Geschlossen | FrankeEDF | Ja — Bug mit diversen Transponder-Typen behoben |
| **48** | RFID Tool | Geschlossen | FrankeEDF | Nein (wontfix) — Support-Anfrage für Inbetriebnahme |
| **47** | Probleme V02 Platine | Geschlossen | FrankeEDF | Unklar — Kontaktaufnahme wegen V02-Platinen-Problemen |
| **46** | Hintergrundinfo | Geschlossen | Schlege | Nein — Info-Anfrage zur langsam blinkenden Status-LED |
| **45** | Fehlercode Parametriersoftware | Geschlossen | FrankeEDF | Nein — Fehlercode 63 bei Installation auf neuem Rechner (Konfiguration) |
| **44** | Versionierung der Software | Geschlossen | FrankeEDF | Ja (klein) — Version 05 in Firmware-Dateien eingetragen |
| **43** | Schaltzykluszähler | Geschlossen | FrankeEDF | Ja — Fehlerauswertung via Error Bit funktionierte nur bis Modul 2 |
| **42** | Fehlerbetrachtung LED Fehler | Geschlossen | Schlege | Ja — Nachtdesign-Aktivierung löste fälschlich LED-Fehler aus |
| **41** | Modbus ATSAM <-> ATXMEGA Kommunikation | Geschlossen | FrankeEDF | Ja (Untersuchung) — Basiseinheit ALT + Module NEU hatte Kommunikationsprobleme |
| **40** | Fehlermeldung Adressierfehler Erweiterungsmodule | Geschlossen | FrankeEDF | Ja — Error Byte schlug trotz korrekter Signalübertragung an |
| **39** | Software Stand | Geschlossen | FrankeEDF | Nein — Info-Frage zum aktuellen Software-Stand |
| **38** | Connect Parametriersoftware | Geschlossen | Schlege | Ja — Reconnect nach Neustart ohne CPU-Neustart nicht möglich |
| **37** | Parametrierung | Geschlossen | Schlege | Ja — Parameterdaten gingen nach Neustart teilweise verloren |
| **36** | SAM4S Poti Eingang zeigt 100 | Geschlossen | FrankeEDF | Nein — Hardware-Ursache (0,64V bei offenem Eingang) |
| **35** | Software Testreihe | Geschlossen | FrankeEDF | Ja — Parameterdaten-Verlust + Modbus-Kommunikationsprobleme |
| **34** | Erweiterungsmodul: Pin 5 nicht mit GND | Geschlossen | Schlege | Nein — Hardware-Schaltbildfehler (GND mit Signal N1 verbunden) |
| **33** | Treiber MPQ3324 / MP3326 | Geschlossen | FrankeEDF | Ja — Treibererkennung per I2C oder Hardware-Pin abzustimmen |
| **32** | Pinbelegung DEBUG-Signale | Geschlossen | Schlege | Nein — Frage ob DEBUG-Leitungen nur in Entwicklung benoetigt |
| **31** | Pinbelegung Modbus SAM4S2 | Geschlossen | Schlege | Nein — Pin-Abstimmung mit Kunde fuer Hardware-Redesign |
| **30** | Baudraten-Fehler Berechnung | Geschlossen | FrankeEDF | Nein — Info-Anfrage zum Korrekturfaktor fuer 115200Bd |
| **29** | Parametrier Software 1.4.1.8 | Geschlossen | FrankeEDF | Ja — System-Seriennummer wurde faelschlich auch bei Erweiterungsmodulen hochgezaehlt |
| **28** | Anfrage Mitlesen LIN Bus | Geschlossen | FrankeEDF | Nein — Anfrage nach vorhandenem LIN-Bus-Tool |
| **27** | Kommunikationsproblem Modbus-Schnittstelle | Geschlossen | FrankeEDF | Ja — Modbus antwortete mit ungueltigem Fehlercode 0x10, langsame Reaktionszeit |
| **26** | Darstellung HW-/SW-Version | Geschlossen | Schlege | Ja — Versionstring war auf 2 Zeichen begrenzt statt 16 Byte |
| **25** | Modbus Multiple-Write Fehlerantwort | Geschlossen | FrankeEDF | Ja — Multiple-Write lieferte falsch formatierte Fehlerantwort |
| **24** | Parametriersoftware: Darstellung Strings | Geschlossen | FrankeEDF | Ja — Unterstriche in Bezeichnungen wurden nicht korrekt gespeichert |
| **23** | Parametriersoftware: Baugruppen-Wechsel | Geschlossen | FrankeEDF | Ja — Reconnect beim Baugruppen-Wechsel in der Fertigung erforderlich |
| **22** | Status-LED Kommunikation | Geschlossen | FrankeEDF | Ja — Status-LED blinkte nicht mehr bei aktiver Kommunikation |
| **21** | Parametriersoftware: Upload Fehlermeldung | Geschlossen | FrankeEDF | Ja — Upload eines Datensatzes auf CPU schlug fehl |
| **20** | Error Byte | Geschlossen | aot-tmg | Ja — Parameterdaten-Fehler wurden nicht im Error Byte angezeigt |
| **19** | Anzeige LED-Ausfall | Geschlossen | aot-tmg | Ja — Off-by-one Fehler bei LED-Nummerierung (0-7 vs. 1-8) |
| **18** | Modbus Master Kommunikations-LED | Geschlossen | FrankeEDF | Ja — Gruene Kommunikations-LED blinkte nicht mehr |
| **17** | Analog Wert | Geschlossen | aot-tmg | Ja — Analog-Wert in Prozessdaten nach Software-Update verschwunden |
| **16** | Device ID | Geschlossen | aot-tmg | Ja — Device ID wurde mit vertauschten High/Low Bytes uebertragen |
| **15** | Datenaustausch Schaltzyklus-Limiten | Geschlossen | Schlege | Ja — Kein Datenaustausch zwischen Parametriersoftware-CPU und IO-Link-CPU |
| **14** | Darstellung IO-Link Mastersoftware | Geschlossen | aot-tmg | Ja — Seriennummer und HW-Version in falschen IO-Link-Feldern angezeigt |
| **13** | Neuer LED-Treiber | Geschlossen | FrankeEDF | Ja — Software-Anpassung fuer neuen LED-Treiber MPQ3326 |
| **12** | IOLink Betriebsdauerzaehler falsch | Geschlossen | FrankeEDF | Ja — Betriebsdauerzaehler wurde falsch in IO-Link-Mastersoftware angezeigt |
| **11** | PS: Reset Betriebsdauerzaehler fehlt | Geschlossen | FrankeEDF | Ja — Reset-Funktion fuer Betriebsstundenzaehler in Parametriersoftware fehlte |
| **10** | Produkt ID | Geschlossen | FrankeEDF | Ja — IO-Link-Produkt-ID-Parameter ueber Parametriersoftware hinzufuegen |
| **9** | Seriennummer automatisch hochzaehlen | Geschlossen | FrankeEDF | Ja — Automatisches Hochzaehlen der Seriennummer funktionierte nicht |
| **8** | Error Byte Detected Module | Geschlossen | Schlege | Ja — Keine Fehlermeldung bei falscher Modulanzahl |
| **7** | Error Byte Schaltzyklen ueberschritten | Geschlossen | aot-tmg | Ja — Fehlermeldung bei Ueberschreitung der Schaltzyklus-Limiten fehlte |
| **6** | Dimm Funktion | Geschlossen | FrankeEDF | Ja — Default-Wert 0 liess alle LEDs ausgeschaltet |
| **5** | Betriebsstundenzaehler | Geschlossen | FrankeEDF | Nein (wontfix) — unrealistisch hoher Zaehlerwert |
| **4** | Schaltzyklus Limiten | Geschlossen | aot-tmg | Ja — Kein CPU-Datenaustausch, keine Fehlermeldungen bei Limituberschreitung |
| **3** | Detected Modul | Geschlossen | FrankeEDF | Ja — Angezeigte Modulanzahl um eins zu hoch (Off-by-one) |
| **2** | Device ID | Geschlossen | FrankeEDF | Nein (wontfix) — Byte-Reihenfolge der Device ID |
| **1** | System Seriennummer | Geschlossen | aot-tmg | Ja — Seriennummer und HW-Version in falschen IO-Link-Feldern |

---

## Zusammenfassung

- **2 Issues noch offen:** #57 (LED Offline-Funktion) und #50 (FB2 Speicherproblem Unigate)
- **~40 Issues** erforderten eine Codeaenderung
- **~17 Issues** waren Fragen, Hardware-Probleme oder wontfix ohne Quelltextaenderung
