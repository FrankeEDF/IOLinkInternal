# Pinbelegung / Schaltbild für Kontroller SAM4S2  - Modbus

- Author: FrankeEDF
- Created: 2022-08-31T21:55:00Z
- State: CLOSED

---

von G. Selig:

bin mir aktuell nicht sicher ob ich Ihr File „Belegung SAM4S2-48.xls“ korrekt verstanden habe. Anbei das von mir ergänzte File im Anhang, meine Ergänzungen beruhen auf den
Schaltungsunterlagen welche wir Ihnen bereitgestellt haben. Aktuell sind wir nochmals an einem Redesign der Schaltung dran und könnten diverse Änderungswünsche Ihrerseits
einfließen lassen.

Hier eine Darstellung was möglich wäre

| Port-Name  | Wunsch | IST | Umsetzbar  |
|------------|--------|-------|------------|
| NSPL_LIN   | PA7    | PA0      |  Nein/ Ungern          |
| RXD_LIN    | PA5    | PB2      |  ja          |
| TXD_LIN    | PA6    | PB3      |  ja          |
| RXD_DEBUG  | PB2    | PA9      |  ja          |
| TXD_DEBUG  | PB3    | PA10      |  ja          |

## Comments

### FrankeEDF (2022-08-31T21:55:29Z)

Das Signal NSLP_LIN dient zur Steuerung der Richtung des Modbus Bausteins und muss an PA7 angeschlossen sein.
Dort und nur dort ist das Signal RTS0 verfügbar (Siehe Tabelle Spalte O „Used Function).  

Die Modbus Signale liegen damit alle auf „Usart0“. Nur dann funktioniert ein Modbus Treiber korrekt.
![grafik](https://user-images.githubusercontent.com/68696065/187792161-58408424-5b3c-4b0f-8ccb-7dcca80be4ba.png)

### Schlege (2022-09-01T08:39:13Z)

Hallo Herr Franke,
hab mich in dieser Thematik noch nicht so tief in den ATSAM eingearbeitet, wir werden den Pin NSPL_LIN auf den Port PA7 legen. wird nicht einfach aber es sollte gehen. Dann können wir das Pinning nach dem File  "Belegung SAM4S2-48" einfrieren.
