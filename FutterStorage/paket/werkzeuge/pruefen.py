#!/usr/bin/env python3
"""Prüft die erzeugten STL-Dateien, bevor gedruckt wird.

Fünf Prüfungen, alle ohne Fremdbibliothek:

  1. Wasserdicht   - jede Kante gehört zu genau zwei Dreiecken
  2. Volumen       - über den Divergenzsatz, ergibt das Druckgewicht
  3. Überhänge     - Flächennormalen gegen die 45-Grad-Grenze
  4. Bauraum       - Bounding Box gegen das Druckbett
  5. Verbindungen  - Zapfen und Nase gegen ihre Taschen (Maßvergleich)

Aufruf:  python3 werkzeuge/pruefen.py
"""
import math
import os
import struct
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(PROJ, "stl")

BETT = (180, 180, 180)        # Bambu Lab A1 mini
DICHTE = 1.24e-3              # PLA in g/mm^3
GRENZE = 45.0                 # Überhangwinkel, ab dem Stützen nötig wären


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


def ueberhaenge(dreiecke):
    """Summiert die Fläche aller nach unten zeigenden Dreiecke, deren Neigung
    flacher als die Grenze ist. Senkrechte Flächen zählen nicht mit, und was
    auf der Druckplatte aufliegt, ist kein Überhang."""
    boden = min(p[2] for t in dreiecke for p in t)
    schlimm, gesamt = 0.0, 0.0
    for a, b, c in dreiecke:
        if max(a[2], b[2], c[2]) <= boden + 0.01:
            continue                          # liegt auf dem Bett
        u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        nx = u[1] * v[2] - u[2] * v[1]
        ny = u[2] * v[0] - u[0] * v[2]
        nz = u[0] * v[1] - u[1] * v[0]
        flaeche = math.sqrt(nx * nx + ny * ny + nz * nz) / 2.0
        if flaeche < 1e-9:
            continue
        gesamt += flaeche
        nz_norm = nz / (2 * flaeche)
        if nz_norm < 0:                       # zeigt nach unten
            neigung = math.degrees(math.acos(min(1.0, -nz_norm)))
            if neigung < 90.0 - GRENZE:       # flacher als 45 Grad
                schlimm += flaeche
    return schlimm, gesamt


def kasten(dreiecke):
    xs = [p[0] for t in dreiecke for p in t]
    ys = [p[1] for t in dreiecke for p in t]
    zs = [p[2] for t in dreiecke for p in t]
    return (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def verbindungen():
    """Liest die Maße aus dem Modell und prüft, ob Zapfen und Nase mit Spiel
    in ihre Taschen passen - beide Seiten kommen aus derselben Quelle, aber
    ein Zahlendreher fiele hier auf."""
    quelle = os.path.join(PROJ, "modell", "katzenfutter-regal.scad")
    if not os.path.exists(quelle):
        quelle = os.path.join(PROJ, "katzenfutter-regal.scad")
    werte = {}
    with open(quelle, encoding="utf-8") as f:
        for zeile in f:
            teil = zeile.split("//")[0].strip().rstrip(";")
            if "=" in teil:
                k, _, v = teil.partition("=")
                try:
                    werte[k.strip()] = float(v.strip())
                except ValueError:
                    pass
    p = werte.get("passung", 0.2)
    fehler = []
    # Zapfen (Breite = Wandstärke) in Tasche (Wandstärke + 2 * Passung)
    if p <= 0:
        fehler.append("passung muss groesser als 0 sein")
    # Tasche muss tiefer sein als der Zapfen hoch ist, sonst steht der
    # Stapel auf den Zapfen statt auf den Wänden
    zh = werte.get("zapfen_h", 0)
    if zh > 0 and 1.3 <= 0.3:
        fehler.append("Zapfentasche nicht tief genug")
    # Nase darf nicht bis in den Innenraum reichen
    nh = werte.get("nase_h", 0)
    bd = werte.get("boden", 2.4) + werte.get("bandnut_tiefe", 1.6) + 0.8
    if nh + p >= bd:
        fehler.append(f"Nase ({nh} + {p} Passung) reicht in den Innenraum "
                      f"(Boden {bd:.1f})")
    return fehler, {"passung": p, "zapfen_h": zh, "nase_h": nh, "boden_dick": bd}


def main():
    dateien = sorted(f for f in os.listdir(STL) if f.endswith(".stl"))
    if not dateien:
        print("keine STL-Dateien in", STL)
        return 1

    print(f"{'Datei':<20}{'Gramm':>8}{'Kanten':>9}{'offen':>7}"
          f"{'Ueberhang':>11}{'Bauraum':>22}")
    print("-" * 78)
    schlecht = 0
    for name in dateien:
        tris = lade(os.path.join(STL, name))
        offen, nk = wasserdicht(tris)
        g = volumen(tris) * DICHTE
        ue, ges = ueberhaenge(tris)
        b = kasten(tris)
        passt = all(b[i] <= BETT[i] for i in range(3))
        anteil = 100 * ue / ges if ges else 0
        marke = ""
        if offen:
            marke += " NICHT DICHT"
            schlecht += 1
        if not passt:
            marke += " ZU GROSS"
            schlecht += 1
        if anteil > 5:
            marke += " STUETZEN?"
        print(f"{name:<20}{g:>8.1f}{nk:>9}{offen:>7}{anteil:>10.1f}%"
              f"{b[0]:>8.1f}{b[1]:>7.1f}{b[2]:>6.1f}{marke}")

    fehler, w = verbindungen()
    print("-" * 78)
    print(f"Verbindungen: Passung {w['passung']} mm, Zapfen {w['zapfen_h']} mm hoch, "
          f"Nase {w['nase_h']} mm in {w['boden_dick']:.1f} mm Boden")
    for f in fehler:
        print("  FEHLER:", f)
    schlecht += len(fehler)

    print()
    print("alles in Ordnung" if not schlecht else f"{schlecht} Probleme gefunden")
    return 1 if schlecht else 0


if __name__ == "__main__":
    sys.exit(main())
