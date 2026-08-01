#!/usr/bin/env python3
"""Prüft die erzeugten STL-Dateien, bevor gedruckt wird.

Zwei Prüfungen, beide ohne Fremdbibliothek:

  1. Wasserdicht   - jede Kante gehört zu genau zwei Dreiecken
  2. Volumen       - über den Divergenzsatz, ergibt das Druckgewicht

Aufruf:  python3 werkzeuge/pruefen.py
"""
import math
import os
import struct
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(PROJ, "stl")

DICHTE = 1.24e-3              # PLA in g/mm^3


def lade(pfad):
    """Liest eine STL und gibt die Dreiecke als Punktetripel zurück.
    OpenSCAD schreibt je nach Version ASCII oder binär, deshalb beides."""
    with open(pfad, "rb") as f:
        roh = f.read()
    if roh[:5] == b"solid" and b"facet normal" in roh[:2048]:
        dreiecke, ecken = [], []
        for zeile in roh.decode("utf-8", "replace").splitlines():
            t = zeile.split()
            if t and t[0] == "vertex":
                ecken.append(tuple(float(x) for x in t[1:4]))
                if len(ecken) == 3:
                    dreiecke.append(tuple(ecken))
                    ecken = []
        return dreiecke
    (n,) = struct.unpack_from("<I", roh, 80)
    return [tuple(struct.unpack_from("<12f", roh, 84 + i * 50)[j:j + 3]
                  for j in (3, 6, 9)) for i in range(n)]


def wasserdicht(dreiecke):
    """Zählt Kanten. Bei einem geschlossenen Körper kommt jede genau zweimal
    vor - einmal je angrenzendem Dreieck."""
    kanten = {}
    for tri in dreiecke:
        for a, b in ((0, 1), (1, 2), (2, 0)):
            k = tuple(sorted((_r(tri[a]), _r(tri[b]))))
            kanten[k] = kanten.get(k, 0) + 1
    offen = sum(1 for v in kanten.values() if v != 2)
    return offen, len(kanten)


def _r(p, k=4):
    return (round(p[0], k), round(p[1], k), round(p[2], k))


def volumen(dreiecke):
    """Divergenzsatz: das Volumen ist die Summe der Spatprodukte durch sechs."""
    v = 0.0
    for a, b, c in dreiecke:
        v += (a[0] * (b[1] * c[2] - b[2] * c[1])
              - a[1] * (b[0] * c[2] - b[2] * c[0])
              + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return abs(v) / 6.0


def main():
    dateien = sorted(f for f in os.listdir(STL) if f.endswith(".stl"))
    if not dateien:
        print("keine STL-Dateien in", STL)
        return 1

    print(f"{'Datei':<20}{'Gramm':>8}{'Kanten':>9}{'offen':>7}")
    print("-" * 44)
    schlecht = 0
    for name in dateien:
        tris = lade(os.path.join(STL, name))
        offen, nk = wasserdicht(tris)
        g = volumen(tris) * DICHTE
        marke = ""
        if offen:
            marke += " NICHT DICHT"
            schlecht += 1
        print(f"{name:<20}{g:>8.1f}{nk:>9}{offen:>7}{marke}")

    print()
    print("alles in Ordnung" if not schlecht else f"{schlecht} Probleme gefunden")
    return 1 if schlecht else 0
if __name__ == "__main__":
    sys.exit(main())
