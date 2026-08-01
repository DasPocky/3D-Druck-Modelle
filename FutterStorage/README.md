# FutterStorage

Ein gedrucktes Regalsystem für 85-g-Nassfutterbeutel (Purina Gourmet, Felix
und Baugleiches). Waagerechte Kanäle über die volle Schranktiefe, eine
Konstantkraftfeder schiebt die Beutel nach vorne, entnommen wird immer der
vorderste. Die Ebenen stehen direkt aufeinander — kein toter Raum.

**Ausbau:** 5 Spalten × 3 Ebenen = 15 Sorten, 375 Beutel
**Passt in:** 540 × 500 × 520 mm nutzbaren Schrankraum
**Druckbett:** ab 180 × 180 mm (Bambu Lab A1 mini)

---

## Aufbau

| Ordner | Inhalt | Herkunft |
|---|---|---|
| `modell/` | Die OpenSCAD-Quelle — alle Maße als Variablen | von Hand |

Alles Weitere — Bauteile, Zeichnungen, Bilder, Anleitung — entsteht später
daraus. Geändert wird immer nur die Quelle.

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

---

## Wie der Verbund zusammenhält

Zwei Steckverbindungen, beide ohne Zusatzteile und ohne Stützmaterial:

- **Nach oben** laufen die Seitenwände als Zapfen weiter und stecken in Taschen
  im Boden der Ebene darüber.
- **Zur Seite** greift eine Nase am Bodenrand in die Tasche der Nachbarspalte.
  Beide liegen unterhalb des Innenraums und kosten keinen Beutelplatz.

---

## Was gekauft werden muss

Je Kanal eine **Konstantkraftfeder** (8–12 N, Auszug ≥ 500 mm, Band 16 mm,
Rolle ≤ 26 mm) und einen **3-mm-Rundstab** als Achse. Sonst nichts — keine
Schrauben, keine Muttern, kein Kleber.
