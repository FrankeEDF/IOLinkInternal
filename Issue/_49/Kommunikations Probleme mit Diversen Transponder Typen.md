# Kommunikations Probleme mit Diversen Transponder Typen

- Author: Schlege
- Created: 2025-09-30T05:13:50Z
- State: CLOSED
- Labels: bug, waiting for reply

---

## Comments

### Schlege (2025-09-30T05:14:40Z)

Jedoch werden nicht alle Transponder erkannt. Sind die Test Transponder bereits bei Ihnen angekommen.

### FrankeEDF (2025-09-30T09:46:37Z)

Bitte präzise bestimmen, welche Transponder nicht erkannt werden.
Transponder sind bei mir noch nicht angekommen. die vorhandenen sind alle von Type Mifar. Und worauf beziehen sich "Kommunikation Probleme"
bitte **generell** bei Beschreibung und Überschrift **präziser** sein.

### Schlege (2025-09-30T10:10:59Z)

Nun aktuell können die Transponder nach ISO 15693 nicht eingelesen werden, Transponder dieses Typs sind an Sie unterwegs.

### FrankeEDF (2025-09-30T11:12:01Z)

im Dokument das sie Datenblatt nennen hab ich gesehen das das Antwort Telegramm vom RFID Reader für diese ISO 15693-Tags einen anderen Aufbau haben. Andere als dieser ISO 15693 Typ und die Mifare Typen sind nicht beschrieben und können nicht unterstützt werden. durch den anderen Aufbau der Rückantwort und aus Mangel an Tags ist wohl tatsächlich ein Fehler in der Firmware

### Schlege (2025-09-30T12:29:08Z)

Habe gerade die Liefersituation der Transponder geprüft:
Diese Sollten heute oder Morgen bei Ihnen eingehen, so haben Sie mal eine Testumgebung.

Zum Protokoll nach ISO 15693:

<img width="738" height="377" alt="Image" src="https://github.com/user-attachments/assets/6a92c08f-3ba6-40db-b000-c0ef22652018" />
Stimmt das Antwort Protokoll sieht hier in der Tat anderst aus als bei den 14443... Typen, hatte bisher vermehrt mit den Mifare Tag´s gearbeitet. Sehen Sie hir eine Möglichkeit diese Type noch mit aufzunehmen.

### FrankeEDF (2025-09-30T12:43:50Z)

Fehler kann ich schon beheben. würde damit aber warten bis sie alle ihre Tests abgeschlossen haben

### FrankeEDF (2025-09-30T12:46:08Z)

und bitte daran denken für **jedes** Thema ein **eigenes** Ticket mit einer möglichst **aussagekräftigen** Überschrift und Beschreibung anzulegen

### FrankeEDF (2025-10-01T21:09:54Z)

Die Tags sind angekommen. reicht es bei einem ISO 15693 SAK und ACK im Modebus Register auf 0 zu setzen um die UID von einem ISO 14443A UID zu unterscheiden:

<img width="580" height="337" alt="Image" src="https://github.com/user-attachments/assets/83eb0f94-f887-4ed4-b5cd-85d1883711d7" />

oder brauchen wird dem vom Reader gelieferten Typ in den Modbus Registern abgebildet (Wert = z.B. 0x05):

<img width="1083" height="536" alt="Image" src="https://github.com/user-attachments/assets/7141fcbb-b472-4532-96ac-d46ab64f014f" />

### Schlege (2025-10-02T05:52:28Z)

Hallo Herr Franke,
wenn Sie die Tag Type hier im Register ATQA ablegen und das SAK Register auf 0 Setzen würde passen. So kann der Anwender wenigstens die Type mit auswerten.

### FrankeEDF (2025-10-02T11:42:50Z)

Vom MB-Register 2017 in dem der SAK Wert liegt, werden ja nur 8 Bits verwendet. 
Ich würde dann den ISO Type dort immer in das High Byte legen ->

<img width="1785" height="378" alt="Image" src="https://github.com/user-attachments/assets/63099bba-5b5d-49da-bc8f-699ddf276365" />

### Schlege (2025-10-02T12:05:46Z)

Passt machen wir so

### FrankeEDF (2026-02-05T23:03:04Z)

Alle Transponder funktionieren
