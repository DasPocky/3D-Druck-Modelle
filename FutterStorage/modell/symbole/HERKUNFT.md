# Herkunft der Sortensymbole

Die acht Silhouetten stammen aus **OpenMoji** — dem freien Emoji-Satz der
Hochschule für Gestaltung Schwäbisch Gmünd.

- Projekt: <https://openmoji.org>
- Lizenz: **CC BY-SA 4.0** — <https://creativecommons.org/licenses/by-sa/4.0/>

| Datei | Emoji | Unicode |
|---|---|---|
| `huhn.svg` | 🐓 Rooster | U+1F413 |
| `rind.svg` | 🐄 Cow | U+1F404 |
| `fisch.svg` | 🐟 Fish | U+1F41F |
| `kaninchen.svg` | 🐇 Rabbit | U+1F407 |
| `ente.svg` | 🦆 Duck | U+1F986 |
| `truthahn.svg` | 🦃 Turkey | U+1F983 |
| `lamm.svg` | 🐑 Ewe | U+1F411 |
| `wild.svg` | 🦌 Deer | U+1F98C |

Verwendet wird jeweils die `color`-Gruppe, deren Flächen zu einer
geschlossenen Silhouette vereinigt werden — Strichzeichnungen wären als
0,6 mm tiefe Gravur nicht druckbar.

Zwei Abweichungen, beide aus der Sichtprüfung:

- Für **Huhn** wird 🐓 Rooster genommen, nicht 🐔 Chicken. Letzteres zeigt
  ein Küken von vorn; als Silhouette wird daraus eine Knolle, in der kein
  Tier mehr zu erkennen ist.
- Beim **Hirsch** kommt zusätzlich die `line`-Gruppe dazu, verdickt zu
  druckbaren Strichen. Das Geweih steckt dort und nicht in den Farbflächen
  — ohne es ist das Tier von Lamm und Rind nicht zu unterscheiden.

`werkzeuge/symbole-holen.py` wandelt die SVG in OpenSCAD-Polygone und
schreibt `modell/sortensymbole.scad`. Die SVG liegen mit im Repo, damit
der Bau ohne Internetzugang funktioniert und nachvollziehbar bleibt,
welche Fassung verwendet wurde.

**Weitergabe:** CC BY-SA verlangt Namensnennung und dieselbe Lizenz für
Bearbeitungen. Wer das Paket weitergibt, muss diesen Hinweis mitgeben.
