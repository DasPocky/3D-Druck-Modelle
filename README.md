# 3D-Druck-Modelle

Meine selbst konstruierten Modelle für den 3D-Druck. Jedes Projekt liegt in
einem eigenen Ordner und ist für sich abgeschlossen — Quelldateien, fertige
STLs, Zeichnungen und Anleitung gehören zusammen.

---

## Projekte

Noch keine — der Ordner ist gerade erst eingerichtet.

---

## Aufbau eines Projekts

Die Ordner folgen überall demselben Schema:

| Ordner | Inhalt |
|---|---|
| `modell/` | Die Quelle — meist OpenSCAD, alle Maße als Variablen |
| `werkzeuge/` | Skripte, die alles Weitere daraus erzeugen |
| `stl/` | Druckfertige Bauteile |
| `zeichnungen/` | Bemaßte SVG-Blätter |
| `bilder/` | Renderings |
| `paket/` | Die fertige Dokumentation zum Weitergeben |

Geändert wird nur in `modell/` und `werkzeuge/`. Alles andere entsteht daraus
neu — die jeweilige Projekt-README sagt, mit welchem Befehl.

Fertige `.zip`-Pakete liegen bewusst nicht im Repo. Sie werden beim Bauen
erzeugt und wären hier nur eine Kopie von allem anderen.

---

## Drucken

Wer nur drucken will, braucht nichts zu installieren: Die STLs liegen fertig
im Repo. Ordner öffnen, `stl/*.stl` herunterladen, in den Slicer ziehen. Die
Projekt-README nennt Material, Schichthöhe und was sonst noch gebraucht wird.

---

## Lizenz

Privates Projekt, keine Garantie auf irgendwas. Nachdrucken und anpassen
ausdrücklich erwünscht.
