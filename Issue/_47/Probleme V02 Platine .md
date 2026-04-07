# Probleme V02 Platine 

- Author: Schlege
- Created: 2024-02-13T14:45:13Z
- State: CLOSED

---

Hallo Herr Franke,
wie sollen wir zu diesem Problem in kontakt treten, ist Ihnen dieser Weg lieber wir per eMail.

## Comments

### FrankeEDF (2024-02-14T11:31:20Z)

Via Email:

Hallo Herr Franke,

bei der IOLinkMaster Software gibt es gerade auch Probleme mit der Neuen Platine welche im Schaltungsaufbau weitgehend der ersten Ausführung entspricht, wir kommen nicht weiter.
Die Software funktioniert mit dem ersten Schaltungsaufbau korrekt, somit würde ich an erster Stelle sagen dass es nicht an der Software liegen kann. Wir haben alles kontrolliert kommen aber nun doch zu dem Entschluss dass die Software bei dem Fehlerbild mit im Boot ist.

Aktuell ist das Problem wie folgt reproduzierbar.
Bei einem Dimmwert von 0 werden die Ausgangs LED´s eingeschaltet und leuchten auf, nach kurzer Zeit resetet sich das System von selber obwohl auf der Reset Leitung wie auch auf den Spannung führenden Leitungen sich nichts ändert im Sekunden Takt (ca. 1,5 sec) sobald ich der Dimmwert auf 255 eingestellt habe läuft alles stabil, bei einem Dimmwert von 245. 
Die Unterbrechungen sind nur auf der LED_EN Leitung ersichtlich und auf der RFS/FLT Leitung, beides sind Eingänge auf dem LED Controller.

Können Sie bitte prüfen mit welchen Watchdog Zeiten Sie in der Software arbeiten, es muss hier in irgend einer Form ein Reset intern ausgelöst werden welcher nicht auf die Reset Leitung kommt. Das Zeitfenster von ca. 1.5sec konnte ich auf der Clock Frequens am Quarz nachmessen, denn sogar dieser schaltet sich kurz ab.

Aktuell wissen wir uns keinen Rat, wir messen seit zwei Tage am System und kommen nicht dahinter woran es liegen könnte. Können Sie uns hier unterstützen. Wenn es für Sie hilfreich wäre können Sie mich auch gerne Zurückrufen dann gehen wir die Punkte am Telefon durch.

### FrankeEDF (2024-02-14T11:33:02Z)

Kommt den auf dem Pin DEBUG_TX eine Ausgabe? können sie ein Log File mit den Debug Ausgaben anhängen?

Welcher Firmware Version wird verwendet?

### Schlege (2024-02-14T13:35:53Z)

Log File werden wir Ihnen erstellen,
Firmware Version IOLinkMaster.elf vom 25.04.2022. 
Falls es untergegangen ist, das Problem entsteht bei dem Aufbau mit ATXMega128 nicht beim ATSAM Aufbau.

### Schlege (2024-02-20T11:20:16Z)

Hallo Herr Franke,
wir können den issue schließen, die Brown Out Spannung war zu knap eingestellt wir haben nun an der Hardware optimiert und hier in den Fusese bei der Brown Out Spannung 2,8V eingestellt. jetzt läuft das System wieder stabiel.

Konnten Sie in der Thematik Master Software LIN bereits weiter kommen.
