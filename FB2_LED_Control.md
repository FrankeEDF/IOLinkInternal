# LED-Steuerung in FB2

  Voraussetzung: Register 1009 = 2 (FB2 aktivieren)

  LED-Befehl senden: Multi-Register Write (FC16) auf Register 1027-1028:
  - Register 1027:
    - Low Byte: Leuchtdauer (0xFF = Dauerlicht)
    - High Byte: 0x07 (LED-Freigabe)
  - Register 1028:
    - Low Byte: LED-Auswahl (0x01=Gr�n, 0x04=Blau, 0x05=Cyan, 0x00=Aus)
    - High Byte: 0x00 (unbenutzt)

  Beispiele:
  - Grün dauerhaft: Schreibe [0xFF, 0x07, 0x01, 0x00] auf Register 1027-1028
  - Blau dauerhaft: Schreibe [0xFF, 0x07, 0x04, 0x00] auf Register 1027-1028
  - LEDs aus: Schreibe [0xFF, 0x07, 0x00, 0x00] auf Register 1027-1028

## Beispiel als 16-Bit Modbus Register-Werte (LED = Blau):
  - Register 1027: 0x07FF (High Byte: 0x07, Low Byte: 0xFF)
  - Register 1028: 0x0004 (High Byte: 0x00, Low Byte: 0x04)

  Modbus Write Multiple Registers (FC16):
  - Start-Adresse: 1027
  - Anzahl Register: 2
  - Register-Werte: [0x07FF, 0x0004]
  - Resultierende Bytes im Buffer: [0xFF, 0x07, 0x04, 0x00]
  - RFID-Kommando: 0x50 0x00 0x03 0x03 0xFF 0x07 0x04 0xAC

  Wichtig: Es muss ein Multi-Register Write sein - einzelne Register-Writes funktionieren nicht!
