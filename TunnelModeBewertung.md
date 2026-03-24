# Technische Bewertung und Festlegung
## Tunnel-Mode mit eigenständigem zyklischem Senden

---

## 1. Zweck

Dieses Dokument beschreibt die technische Bewertung des Betriebsmodus, in dem ein Gerät gleichzeitig:

- im **Tunnel-Mode** betrieben wird und
- **eigenständig zyklische oder ereignisbasierte Telegramme** erzeugt.

Ziel ist die normative Einordnung der Zulässigkeit dieses Betriebs unter den gegebenen Randbedingungen.

---

## 2. Randbedingungen

Für den Tunnel-Mode gilt folgende zwingende Anforderung:

> Das Gerät darf **keine Annahmen über Requests oder deren Kontext** treffen.

Daraus ergeben sich folgende Eigenschaften:

- kein Kontextwissen über Kommunikationsbeziehungen
- keine Zuordnung von Request/Response
- keine Interpretation von Telegramminhalten
- keine zustandsbehaftete Protokollverarbeitung

---

## 3. Definition Tunnel-Mode

Im Sinne dieser Spezifikation ist ein Tunnel-Mode definiert als:

- **frame-transparente Weiterleitung** von Telegrammen
- **zustandslose Verarbeitung** auf Protokollebene
- **keine semantische Interpretation** der übertragenen Daten

Das Gerät agiert ausschließlich als Weiterleitungselement.

---

## 4. Analyse des geforderten Betriebs

Der geforderte Betriebsmodus kombiniert:

1. transparente Weiterleitung (Tunnel-Funktion)
2. aktive Teilnahme durch eigengenerierte Telegramme

Diese Kombination führt zu einer Überlagerung von:

- **Transit-Traffic** (weitergeleitete Telegramme)
- **Eigen-Traffic** (lokal erzeugte Telegramme)

---

## 5. Technischer Widerspruch

Die Einspeisung eigener Telegramme führt dazu, dass das Gerät:

- eine **eigene Kommunikationssemantik** einführt und
- als **aktiver Teilnehmer** im Kommunikationssystem auftritt.

Dies steht im direkten Widerspruch zur Anforderung:

> keine Annahmen über Requests oder deren Kontext zu treffen.

Ein aktiver Teilnehmer impliziert notwendigerweise:

- implizite oder explizite Kontextbildung
- Unterscheidung von Telegrammursprüngen
- Einfluss auf Kommunikationsabläufe

Diese Eigenschaften sind im Tunnel-Mode explizit ausgeschlossen.

---

## 6. Nicht auflösbare Ambiguität

Ohne Kontextinformation ist folgende Unterscheidung prinzipiell nicht möglich:

Ein empfangenes Telegramm ist entweder:

- eine Response auf einen Request eines externen Teilnehmers
- oder ein lokal erzeugtes Telegramm des Geräts

Da beide Telegrammarten über denselben Kommunikationskanal übertragen werden und keine Kennzeichnung erfolgt, entsteht eine **nicht auflösbare Ambiguität**.

---

## 7. Auswirkungen auf das Systemverhalten

### 7.1 Verlust der Eindeutigkeit

- keine eindeutige Zuordnung von Responses zu Requests
- fehlende Korrelation von Kommunikationsvorgängen

---

### 7.2 Verletzung der Deterministik

- zeitliche Überlagerung von Telegrammen (Race Conditions)
- nicht reproduzierbares Verhalten

---

### 7.3 Fehlinterpretation durch Kommunikationspartner

- zyklische Telegramme können als Responses interpretiert werden
- Responses können verworfen oder falsch zugeordnet werden
- inkorrekte Timeout- und Fehlerbehandlung

---

## 8. Bewertung möglicher Gegenmaßnahmen

Zur Auflösung der Ambiguität wären erforderlich:

- Einführung von **Telegrammkennzeichnungen** (z. B. Source-ID, Message-Type)
- Nutzung von **Korrelationsmechanismen** (z. B. Request-ID)
- **Trennung von Kommunikationskanälen**

Diese Maßnahmen setzen jedoch voraus:

- Interpretation von Telegrammen oder
- Erweiterung der Protokollsemantik

Beides widerspricht der definierten Randbedingung:

> keine Annahmen über Requests zu treffen.

---

## 9. Schlussfolgerung

Der kombinierte Betrieb aus:

- Tunnel-Mode (transparent, zustandslos, ohne Kontext)
- und eigenständigem zyklischem oder ereignisbasiertem Senden

ist unter den gegebenen Randbedingungen **technisch nicht zulässig**.

Begründung:

- fehlende Möglichkeit zur eindeutigen Unterscheidung von Telegrammquellen
- notwendige Kontextbildung widerspricht der Tunnel-Definition
- deterministisches und korrekt interpretierbares Verhalten ist nicht gewährleistet

Die zur Realisierung erforderlichen Voraussetzungen sind **prinzipbedingt nicht erfüllbar**.

---

## 10. Normative Festlegung

Der folgende Sachverhalt wird verbindlich festgelegt:

> Ein Gerät im Tunnel-Mode darf keine eigenständig erzeugten zyklischen oder spontanen Telegramme auf demselben Kommunikationskanal senden.

Der beschriebene kombinierte Betriebsmodus gilt als:

- **nicht spezifikationskonform**
- **nicht implementierbar unter den gegebenen Randbedingungen**
- **technisch unzulässig**
