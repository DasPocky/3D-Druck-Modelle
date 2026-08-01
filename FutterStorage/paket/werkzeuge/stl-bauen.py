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

# (Zieldatei, Variablen)
TEILE = [
    ("segment-front.stl", {"TEIL": "segment", "segment_typ": "front"}),
    ("segment-mitte.stl", {"TEIL": "segment", "segment_typ": "mitte"}),
    ("segment-end.stl",   {"TEIL": "segment", "segment_typ": "end"}),
    ("schieber.stl",      {"TEIL": "schieber"}),
    ("schild.stl",        {"TEIL": "schild"}),
    ("schild-text.stl",   {"TEIL": "schild_text"}),
    ("verbinder.stl",     {"TEIL": "verbinder"}),
    # Fuer die oberste Lage: dieselben Segmente ohne die Stapelzapfen,
    # damit oben nichts uebersteht. Nur noetig, wenn es buendig sein soll.
    ("oben/segment-front.stl", {"TEIL": "segment", "segment_typ": "front",
                                "stapel_zapfen": "false"}),
    ("oben/segment-mitte.stl", {"TEIL": "segment", "segment_typ": "mitte",
                                "stapel_zapfen": "false"}),
    ("oben/segment-end.stl",   {"TEIL": "segment", "segment_typ": "end",
                                "stapel_zapfen": "false"}),
    ("probe.stl",         {"TEIL": "probe"}),
]

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
        print(f"  {name:<22}{gr:>8.0f} kB" + ("  FEHLER" if fehler else ""))
        for f in fehler:
            print("     ", f)
        schlecht += len(fehler)

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
