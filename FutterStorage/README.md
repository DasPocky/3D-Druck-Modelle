# FutterStorage

Ein gedrucktes Regalsystem für 85-g-Nassfutterbeutel (Purina Gourmet, Felix
und Baugleiches). Waagerechte Kanäle über die volle Schranktiefe, eine
Konstantkraftfeder schiebt die Beutel nach vorne, entnommen wird immer der
vorderste. Die Ebenen stehen direkt aufeinander — kein toter Raum.

**Ausbau:** 5 Spalten × 3 Ebenen = 15 Sorten, 375 Beutel
**Passt in:** 540 × 500 × 520 mm nutzbaren Schrankraum
**Druckbett:** ab 180 × 180 mm (Bambu Lab A1 mini)

---

## Schnellstart

```bash
python3 werkzeuge/stl-bauen.py     # Bauteile erzeugen
python3 werkzeuge/pruefen.py       # prüfen, bevor gedruckt wird
```

Dann `stl/*.stl` in den Slicer. Die vollständige Anleitung liegt in
`paket/index.html` — dort steht auch, was gekauft werden muss.

---

## Aufbau

| Ordner | Inhalt | Herkunft |
|---|---|---|
| `modell/` | Die OpenSCAD-Quelle — alle Maße als Variablen | von Hand |
| `werkzeuge/` | Skripte, die alles Weitere erzeugen | von Hand |
| `stl/` | Druckfertige Bauteile, dazu ein Schild je Sorte | erzeugt |
| `zeichnungen/` | Sieben bemaßte SVG-Blätter | erzeugt |
| `bilder/` | Renderings in voller Auflösung | erzeugt |
| `paket/` | Die fertige Dokumentation zum Weitergeben | erzeugt |

Geändert wird ausschließlich in `modell/` und `werkzeuge/`. Alles andere
entsteht daraus neu.

### Die Skripte

| Datei | Was sie tut |
|---|---|
| `stl-bauen.py` | Ruft OpenSCAD je Bauteil auf, prüft Stapel und Spalten auf Kollision |
| `pruefen.py` | Wasserdicht, Volumen, Überhänge, Bauraum, Passung — bricht bei Fehlern ab |
| `zeichnungen.py` | Bemaßte SVG-Blätter, prüft sich selbst auf Überdeckungen |
| `rendern.py` | Blender-Szenen mit automatischer Kamerarahmung |
| `schilder.py` | Ein Schild je Futtersorte, als STL und als Bild |
| `seiten.py` | Baut die HTML-Dokumentation und das ZIP |

### Alles neu bauen

```bash
python3 werkzeuge/stl-bauen.py
python3 werkzeuge/pruefen.py
python3 werkzeuge/schilder.py beide
python3 werkzeuge/zeichnungen.py
for s in front mitte end schieber schild kanal explosion gefuellt ebene gesamt; do
    blender -b -P werkzeuge/rendern.py -- $s bilder/b_$s.png
done
python3 werkzeuge/seiten.py
```

---

## Anpassen

Alle Maße stehen oben in `modell/katzenfutter-regal.scad`. Die wichtigsten:

| Variable | Standard | Wirkung |
|---|---|---|
| `beutel_breit` | 88 | bestimmt die Spaltenbreite und damit, wie viele Spalten passen |
| `beutel_hoch` | 136 | bestimmt die Ebenenhöhe |
| `beutel_dicke` | 19 | bestimmt die Kapazität je Kanal |
| `segment_laenge` | 160 | muss auf das Druckbett passen |
| `passung` | 0,2 | Spiel je Flanke — bei strammem Sitz erhöhen |
| `schild_text` | HUHN | Aufdruck des Schilds |
| `schild_symbol` | huhn | Tiersymbol daneben |

Nach jeder Änderung `stl-bauen.py` und `pruefen.py` laufen lassen. Zeichnungen
und Renderings lesen die Maße selbst aus dem Modell und passen sich an.

---

## Wie der Verbund zusammenhält

Zwei Steckverbindungen, beide ohne Zusatzteile und ohne Stützmaterial:

- **Nach oben** laufen die Seitenwände als Zapfen weiter und stecken in Taschen
  im Boden der Ebene darüber.
- **Zur Seite** greift eine Nase am Bodenrand in die Tasche der Nachbarspalte.
  Beide liegen unterhalb des Innenraums und kosten keinen Beutelplatz.

`stl-bauen.py` prüft nach jedem Lauf, dass sich weder gestapelte Ebenen noch
benachbarte Spalten durchdringen.

---

## Was gekauft werden muss

Je Kanal eine **Konstantkraftfeder** (8–12 N, Auszug ≥ 500 mm, Band 16 mm,
Rolle ≤ 26 mm) und einen **3-mm-Rundstab** als Achse. Sonst nichts — keine
Schrauben, keine Muttern, kein Kleber.

---

## Vor dem Serienstart

`stl/probe.stl` drucken (34 g, gut eine halbe Stunde) und einen echten Beutel
hineinstellen. Passt er mit zwei Millimetern Luft, stimmen alle weiteren Maße.
