#!/usr/bin/env python3
"""Misst jedes Sortensymbol nach: sitzt es mittig, ist es groß genug?

Warum das nötig ist: resize() im Schild skaliert die Silhouette auf ein
Quadrat, verschiebt sie aber nicht. Ein Symbol, dessen Schwerpunkt neben
dem Nullpunkt liegt, sitzt deshalb auch auf dem Schild daneben - genau das
war bei allen acht Tieren der Fall, und auf dem Rendering sah man es erst,
wenn man darauf hingewiesen wurde.

Geprüft wird:
  1. Mitte       - Bounding-Box-Mitte muss nahe (0,0) liegen
  2. Größe       - die Silhouette soll das Feld ausfüllen, nicht darin
                   schwimmen
  3. Verhältnis  - nicht breiter als hoch mal Faktor, sonst wird sie beim
                   Einpassen ins Quadrat sehr klein

Aufruf:  python3 werkzeuge/symbole-pruefen.py
"""
import os
import subprocess
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
MODELL = os.path.join(PROJ, "modell", "katzenfutter-regal.scad")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pruefen import lade

SYMBOLE = ["huhn", "rind", "fisch", "kaninchen", "ente", "truthahn",
           "lamm", "wild"]

MITTE_MAX = 0.6      # mm Abweichung vom Nullpunkt, die noch durchgeht
FELD_MIN = 15.0      # die größere Kante soll mindestens so groß sein
FELD_MAX = 21.0      # und höchstens so groß
SEITEN_MAX = 1.7     # breiter als hoch mal diesem Faktor wird zu klein


def grenzen(pfad):
    """Bounding Box in X und Y als (min, max)."""
    tri = lade(pfad)
    xs = [p[0] for t in tri for p in t]
    ys = [p[1] for t in tri for p in t]
    return (min(xs), max(xs)), (min(ys), max(ys))


def main():
    aus = os.path.join("/tmp", "symbolpruefung")
    os.makedirs(aus, exist_ok=True)
    print(f"{'Symbol':<12}{'Breite':>8}{'Höhe':>8}{'Mitte X':>9}{'Mitte Y':>9}"
          f"{'Seiten':>8}  Befund")
    print("-" * 68)

    schlecht = 0
    for name in SYMBOLE:
        ziel = os.path.join(aus, f"{name}.stl")
        e = subprocess.run(
            [SCAD, "-o", ziel, "-D", 'TEIL="symbol"',
             "-D", f'schild_symbol="{name}"', MODELL],
            capture_output=True, text=True)
        if not os.path.exists(ziel):
            print(f"  {name:<10} kein Ergebnis - {e.stderr.strip()[:40]}")
            schlecht += 1
            continue
        (x0, x1), (y0, y1) = grenzen(ziel)
        breit, hoch = x1 - x0, y1 - y0
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        verh = breit / hoch if hoch else 99

        befund = []
        if abs(mx) > MITTE_MAX or abs(my) > MITTE_MAX:
            befund.append("NICHT MITTIG")
        if max(breit, hoch) < FELD_MIN:
            befund.append("ZU KLEIN")
        if max(breit, hoch) > FELD_MAX:
            befund.append("ZU GROSS")
        if verh > SEITEN_MAX:
            befund.append("ZU BREIT")
        schlecht += bool(befund)

        print(f"  {name:<10}{breit:>8.1f}{hoch:>8.1f}{mx:>9.2f}{my:>9.2f}"
              f"{verh:>8.2f}  {' '.join(befund) if befund else 'ok'}")

    print()
    print(f"alle {len(SYMBOLE)} Symbole in Ordnung" if not schlecht
          else f"{schlecht} Symbole müssen nachgebessert werden")
    return 1 if schlecht else 0


if __name__ == "__main__":
    sys.exit(main())
