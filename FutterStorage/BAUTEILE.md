# Was gekauft werden muss

Alles andere wird gedruckt. Für einen Kanal braucht es genau zwei Zukaufteile:
eine Konstantkraftfeder und einen Rundstab als Achse.

Stand der Recherche: 1. August 2026. Preise und Verfügbarkeit im Shop prüfen.

---

## 1 · Konstantkraftfeder

**Gewählt: CF030-0237** — 10,5 N · Auszug 610 mm · Band 15,0 mm · Rolle Ø 22 mm

| Kennwert | Wert |
|---|---|
| Zugkraft | 10,5 N (über den ganzen Weg gleich) |
| Auszug Lmax | 610 mm — der Schieber legt 480 mm zurück |
| Bandbreite | 14,99 mm |
| Rolle Ø außen | 22,0 mm |
| Trommel Ø empfohlen | 20,7 mm — **wird mitgedruckt**, siehe unten |
| Montageloch | 4,7 mm |
| Werkstoff | Federbandstahl 1.4310 / Typ 301, rostfrei |
| Lebensdauer | 4.000 Hübe |
| Preis | ~16,40 € |

**Bezug:** [sodemann-federn.de](https://www.sodemann-federn.de/cf030-0237) ·
alternativ [Febrotec, Halver/NRW](https://www.febrotec.de/de-DE/konstantkraftfedern-rollfedern)
als `0CF030-0237` — deutscher Hersteller, kürzere Lieferstrecke, Sonderfertigung möglich.

### Warum nicht 16 mm Band?

Die erste Auslegung ging von 16 mm aus. **Das gibt es bei 8–12 N nicht ab Lager.**
Die Kraft einer Rollfeder wächst mit Bandbreite × Banddicke²: bei 15,87 mm Band
liegt die Standardfeder schon bei 14,7 N — zu stark. Im Zielbereich 8–12 N sind
die Bänder 12,7 bis 15,0 mm breit. 15,0 mm ist das nächstliegende Maß, das Modell
ist darauf ausgelegt.

### Alternativen

| Artikel | Kraft | Auszug | Band | Rolle Ø | Preis |
|---|---|---|---|---|---|
| CF030-0263 | 11,7 N | 663 mm | 12,70 mm | 20,5 mm | 16,22 € |
| CF025-0198 | 8,8 N | 557 mm | 12,70 mm | 15,5 mm | 16,22 € |

Zwei parallel geführte Federn addieren ihre Kräfte. Falls sich 10,5 N am echten
Teil als zu schwach erweisen, ist das der Weg — nicht eine breitere Feder.

---

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

Deshalb liegt `stl/trommel.stl` bei: Ø 20,7 mm Wickelfläche, 17 mm breit, mit
Bordscheiben gegen seitliches Ablaufen, Bohrung 3,5 mm — sie läuft frei auf der
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
| Konstantkraftfeder CF030-0237 | 1 | ~16,40 € |
| Edelstahl-Rundstab 3 × 500 mm | 1 | 1,05 € |
| **Material je Kanal** | | **~17,45 €** |
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
