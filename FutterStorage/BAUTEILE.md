# Was gekauft werden muss

Alles andere wird gedruckt. Für einen Kanal braucht es genau zwei Zukaufteile:
eine Konstantkraftfeder und einen Rundstab als Achse.

Stand der Recherche: 1. August 2026. Preise und Verfügbarkeit im Shop prüfen.

---

## Wie die Federkraft zustande kommt

Die Feder muss zwei Grenzen einhalten — deshalb steht die Rechnung hier
und nicht nur das Ergebnis.

**Nach unten** begrenzt die Reibung des vollen Stapels:

| | |
|---|---|
| 25 Beutel × 85 g | 2,125 kg = 20,9 N Gewichtskraft |
| Reibbeiwert Folie auf PLA | 0,3 bis 0,4 (am Teil zu messen) |
| **nötige Schubkraft** | **6,3 bis 8,3 N** |

**Nach oben** begrenzt der Beutel selbst. Die volle Federkraft liegt
*immer* auf dem vordersten — egal ob fünf oder fünfundzwanzig dahinter
stehen. Zu viel Kraft drückt ihn flach, er weicht seitlich aus und klemmt:
Im 92-mm-Kanal hat ein 88-mm-Beutel nur 4 mm Spiel. Platzen droht nicht
(8,8 N verteilen sich auf 81 cm² Anlagefläche, das sind rund 1000 Pa —
ein Daumendruck ist hundertmal höher), aber die Verformung reicht zum
Verklemmen. Praktische Obergrenze: **rund 12 N**.

Gewählt ist deshalb eine Feder in der Mitte dieses Fensters.

---

## 1 · Konstantkraftfeder

**Gewählt: CF025-0198** — 8,8 N · Auszug 557 mm · Band 12,7 mm · Rolle Ø 15,5 mm

| Kennwert | Wert | Bedarf |
|---|---|---|
| Zugkraft | 8,8 N | 8,3 N nötig, 12 N Obergrenze |
| Auszug Lmax | 557 mm | 470 mm gebraucht |
| Bandbreite | 12,70 mm | bestimmt Bandnut und Trommel |
| Rolle Ø außen | 15,5 mm | |
| Trommel Ø | 14,5 mm | **wird mitgedruckt**, siehe unten |
| Werkstoff | Federbandstahl 1.4310, rostfrei | |
| Lebensdauer | 4.000 Hübe | |
| Preis | ~16,20 € | Kleinmengen-Listenpreis |

**Bezug:** [sodemann-federn.de](https://www.sodemann-federn.de/produkte/konstantkraftfedern/konstantkraftfedern) ·
alternativ [Febrotec, Halver/NRW](https://www.febrotec.de/de-DE/konstantkraftfedern-rollfedern)
— deutscher Hersteller, Preise auf Anfrage.

### Warum nicht die stärkere Feder?

Die erste Auslegung nahm die CF030-0237 mit 10,5 N — die stärkste, die ins
Raster passte. Das ist die 1,26-fache Reserve über dem Bedarf und bringt
nichts außer mehr Druck auf den vordersten Beutel. Ihr 15-mm-Band verlangte
zudem eine breitere Nut im Boden und eine größere Trommel.

### Andere Feder einsetzen

Passend ist alles, was **8 bis 12 N** liefert und mindestens **480 mm**
auszieht. Im Modell sind dafür vier Zeilen zu ändern:

```openscad
feder_kraft   = 8.8;   // N
feder_band_b  = 12.7;  // Bandbreite
feder_auszug  = 557;   // Lmax
feder_rolle_d = 15.5;  // Rolle außen
```

Bandnut, Federkammer und Trommel rechnen sich daraus.
`pruefen.py` schlägt an, wenn die Feder zu schwach, zu stark oder zu kurz ist.

### Preis drücken

Der Listenpreis von ~16 € gilt für Einzelabnahme und ist bei allen Größen
etwa gleich — er ist ein Mindestpreis, kein Materialpreis. Wer 15 Kanäle
baut, sollte **beim Hersteller nach Staffelpreisen fragen**. Auch
Direktimport (AliExpress, Alibaba) führt dieselben Federn deutlich
günstiger, bei entsprechender Lieferzeit und ohne geprüftes Datenblatt.

## 2 · Achse Ø 3 mm

**Gewählt: Edelstahl-Rundstab V2A, 3 mm × 500 mm — 1,05 €**

[stahl-shop24.de](https://www.stahl-shop24.de/Edelstahl-Rundstab-3mm-500mm) ·
Werkstoff 1.4301, blank gezogen, Toleranz h9.

Ein 500-mm-Stab reicht für fünf Achsen à 90 mm. Ablängen mit Trennscheibe oder
Seitenschneider und Feile.

| Alternative | Werkstoff | Länge | Preis | Anmerkung |
|---|---|---|---|---|
| Silberstahl 1.2210 | geschliffen, poliert | 500 mm | 8,33 € | präziser, achtfacher Preis — nur bei hoher Zyklenzahl sinnvoll |
| Messing-Rundstab | hartgezogen | 1000 mm | 3,80 € | weicher, korrosionsfrei |

### Filament taugt hier nicht

Naheliegend, aber falsch: Standard-Filament ist 1,75 oder 2,85 mm, nicht 3,0.
Ein 2,85er hätte 0,15 mm Spiel in der Bohrung, und PLA kriecht unter der
Dauerlast der Federrolle. Für einen Wegwerf-Prototyp genügt es, für den
Dauerbetrieb nicht.

---

## 3 · Die Trommel wird gedruckt

**Die Feder darf nicht auf der 3-mm-Achse aufwickeln.** Ihr natürlicher
Innendurchmesser liegt bei 11–17 mm; der Hersteller verlangt eine Trommel
10–20 % über diesem Maß. Ein zu enger Wickel erhöht die Biegespannung im Band
und verkürzt die Lebensdauer.

Deshalb liegt `stl/trommel.stl` bei: Ø 14,5 mm Wickelfläche, 14,7 mm breit,
mit Bordscheiben gegen seitliches Ablaufen, Bohrung 3,5 mm — sie läuft frei auf der
Achse. Liegend drucken, dann ist die Bohrung rund und es braucht keine Stützen.

---

## 4 · Regeln für den Umgang mit der Feder

- **Mindestens 1½ Windungen** müssen bei vollem Auszug auf der Trommel bleiben.
- Band **geradlinig** herausführen, keine seitliche Ablenkung — dafür ist die
  Bodennut da.
- Band **niemals knicken, falten oder über scharfe Kanten** laufen lassen. Nicht
  kürzen, bohren oder erwärmen.
- **Die Bandkanten sind scharf.** Bei der Montage Handschuhe und Schutzbrille
  tragen, die Rolle kontrolliert halten — sie wickelt sich beim Loslassen
  schlagartig zurück.

---

## 5 · Kosten

| Position | Menge | Preis |
|---|---|---|
| Konstantkraftfeder CF025-0198 | 1 | ~16,20 € |
| Edelstahl-Rundstab 3 × 500 mm | 1 | 1,05 € |
| **Material je Kanal** | | **~17,25 €** |
| Versand (zwei Shops) | | ~10–14 € |

Der Versand macht fast die Hälfte aus. Für den Vollausbau mit 15 Kanälen
lohnt eine Sammelbestellung; bei Mehrfachabnahme sinkt der Stückpreis der
Federn deutlich.

---

## Quellen

- Sodemann-Federn, Konstantkraftfedern — <https://www.sodemann-federn.de/produkte/konstantkraftfedern/konstantkraftfedern>
- Febrotec GmbH, Rollfedern — <https://www.febrotec.de/de-DE/konstantkraftfedern-rollfedern>
- Lesjöfors, Rollfedern (Sonderfertigung) — <https://www.lesjofors.com/de/produkte/flachfedern/rollfedern/>
- Stahl-Shop24, Edelstahl-Rundstahl — <https://www.stahl-shop24.de/Edelstahl/Edelstahl-rund/>
