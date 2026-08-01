#!/usr/bin/env python3
"""Erzeugt alle druckbaren Bauteile aus der einen OpenSCAD-Quelle.

Jeder Aufruf setzt per -D andere Variablen und bekommt damit ein anderes
Bauteil aus derselben Datei - deshalb kann kein Teil zu einem anderen
Stand gehören.

Aufruf:  python3 werkzeuge/stl-bauen.py
"""
import os
import subprocess
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
MODELL = os.path.join(PROJ, "modell", "katzenfutter-regal.scad")
STL = os.path.join(PROJ, "stl")

# Ein Segment sitzt an drei Stellen zugleich: in der Tiefe, in der Hoehe
# und in der Breite. Jede Achse hat eigene Randfaelle, deshalb wird die
# volle Matrix erzeugt - im 5x3-Ausbau kommt jede der 27 Kombinationen
# tatsaechlich vor.
TIEFE  = ["front", "mitte", "end"]      # segment_typ
EBENE  = ["unten", "mitte", "oben"]     # ebene_typ
SPALTE = ["links", "mitte", "rechts"]   # spalte_typ

SEGMENTE = [
    (f"segmente/{t}-{e}-{s}.stl",
     {"TEIL": "segment", "segment_typ": t, "ebene_typ": e, "spalte_typ": s})
    for t in TIEFE for e in EBENE for s in SPALTE
]

# (Zieldatei, Variablen)
TEILE = SEGMENTE + [
    ("schieber.stl",      {"TEIL": "schieber"}),
    ("schild.stl",        {"TEIL": "schild"}),
    ("schild-text.stl",   {"TEIL": "schild_text"}),
    ("verbinder.stl",     {"TEIL": "verbinder"}),
    # Wickeltrommel fuer die Konstantkraftfeder. Liegend drucken.
    ("trommel.stl",       {"TEIL": "trommel"}),
    ("probe.stl",         {"TEIL": "probe"}),
]


def stueckliste(spalten=5, ebenen=3, segmente=3):
    """Welche Variante wie oft gebraucht wird. Aus derselben Matrix wie die
    STL-Namen gerechnet, damit Druckliste und Dateien nicht auseinanderlaufen."""
    def rand(i, n, namen):
        return namen[0] if i == 0 else (namen[2] if i == n - 1 else namen[1])

    zaehler = {}
    for sp in range(spalten):
        for eb in range(ebenen):
            for sg in range(segmente):
                name = (TIEFE[0] if sg == 0 else
                        (TIEFE[2] if sg == segmente - 1 else TIEFE[1]))
                schluessel = (name, rand(eb, ebenen, EBENE),
                              rand(sp, spalten, SPALTE))
                zaehler[schluessel] = zaehler.get(schluessel, 0) + 1
    return zaehler

# Diese Prüfungen müssen leer bleiben: Ebenen und Spalten dürfen sich
# nicht durchdringen.
KOLLISION = [("test", "Ebene darüber"),
             ("test_seite", "Spalte daneben"),
             ("test_diagonal", "Nachbar schräg darüber")]


def scad(ziel, werte):
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    befehl = [SCAD, "-o", ziel]
    for k, v in werte.items():
        # true/false sind Wahrheitswerte, keine Zeichenketten
        befehl += ["-D", f"{k}={v}" if v in ("true", "false")
                   else "-D".join(["", f'{k}="{v}"'])[2:]]
    befehl.append(MODELL)
    e = subprocess.run(befehl, capture_output=True, text=True)
    fehler = [z for z in e.stderr.splitlines() if "ERROR" in z]
    return fehler


def main():
    os.makedirs(STL, exist_ok=True)
    if not os.path.exists(MODELL):
        print("Modell nicht gefunden:", MODELL)
        return 1

    schlecht = 0
    for name, werte in TEILE:
        fehler = scad(os.path.join(STL, name), werte)
        gr = os.path.getsize(os.path.join(STL, name)) / 1024
        print(f"  {name:<30}{gr:>8.0f} kB" + ("  FEHLER" if fehler else ""))
        for f in fehler:
            print("     ", f)
        schlecht += len(fehler)

    # Was der Vollausbau an Segmenten braucht - aus derselben Matrix
    liste = stueckliste()
    print(f"\n  Stueckliste fuer {5} Spalten x {3} Ebenen "
          f"({sum(liste.values())} Segmente):")
    for (t, e, s), n in sorted(liste.items()):
        print(f"    {n:>2} x  segmente/{t}-{e}-{s}.stl")

    print()
    for teil, was in KOLLISION:
        ziel = os.path.join("/tmp", f"kollision-{teil}.stl")
        scad(ziel, {"TEIL": teil})
        # Eine leere oder volumenlose Datei bedeutet: keine Durchdringung.
        gr = os.path.getsize(ziel) if os.path.exists(ziel) else 0
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from pruefen import lade, volumen
        v = volumen(lade(ziel)) if gr > 200 else 0.0
        print(f"  Kollision {was:<24}{v:8.3f} mm3" + ("  PROBLEM" if v > 0.01 else ""))
        if v > 0.01:
            schlecht += 1

    print()
    print("alle Bauteile erzeugt" if not schlecht
          else f"{schlecht} Probleme - nicht drucken")
    return 1 if schlecht else 0


if __name__ == "__main__":
    sys.exit(main())
