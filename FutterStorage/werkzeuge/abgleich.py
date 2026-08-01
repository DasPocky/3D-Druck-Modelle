#!/usr/bin/env python3
"""Vergleicht Modell, STL, Zeichnungen und Bilder gegeneinander.

Die Maße stehen an einer Stelle — in der OpenSCAD-Quelle. Alles andere wird
daraus erzeugt. Dieses Skript prüft, ob das auch stimmt:

  1. Sind die STL neuer als das Modell?
  2. Stimmen die STL-Abmessungen mit den gerechneten Maßen überein?
  3. Sind Zeichnungen und Bilder neuer als die STL?
  4. Steht in den Zeichnungen dieselbe Zahl wie im Modell?

Aufruf:  python3 werkzeuge/abgleich.py
"""
import os
import re
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pruefen import lade, kasten

MODELL = os.path.join(PROJ, "modell", "katzenfutter-regal.scad")


def werte():
    v = {}
    with open(MODELL, encoding="utf-8") as f:
        for zeile in f:
            t = zeile.split("//")[0].strip().rstrip(";")
            if t.count("=") == 1:
                k, _, w = t.partition("=")
                try:
                    v[k.strip()] = float(w.strip())
                except ValueError:
                    pass
    v["innen_x"] = v["beutel_breit"] + v["spiel"]
    v["innen_z"] = v["beutel_hoch"] + v["luft_oben"]
    v["aussen_x"] = v["innen_x"] + 2 * v["wand"]
    v["boden_dick"] = v["boden"] + v["bandnut_tiefe"] + 0.8
    v["aussen_z"] = v["boden_dick"] + v["innen_z"]
    return v


def main():
    v = werte()
    fehler, hinweise = [], []
    t_modell = os.path.getmtime(MODELL)

    # ---- 1. Reihenfolge der Erzeugung -------------------------------
    def juenger(pfad, was, referenz, ref_name):
        if not os.path.exists(pfad):
            fehler.append(f"{was} fehlt: {pfad}")
            return
        if os.path.getmtime(pfad) < referenz:
            fehler.append(f"{was} ist aelter als {ref_name} "
                          f"- neu erzeugen: {os.path.relpath(pfad, PROJ)}")

    stl_zeiten = []
    # Stellvertretend die Mittellage je Tiefe - sie enthaelt alle Merkmale.
    # Die uebrigen 24 Varianten entstehen im selben Lauf.
    for f in ("segmente/front-mitte-mitte.stl", "segmente/mitte-mitte-mitte.stl",
              "segmente/end-mitte-mitte.stl", "schieber.stl", "schild.stl",
              "schild-text.stl", "trommel.stl", "probe.stl"):
        p = os.path.join(PROJ, "stl", f)
        juenger(p, "STL", t_modell, "das Modell")
        if os.path.exists(p):
            stl_zeiten.append(os.path.getmtime(p))
    t_stl = max(stl_zeiten) if stl_zeiten else t_modell

    for f in sorted(os.listdir(os.path.join(PROJ, "zeichnungen"))):
        if f.endswith(".svg"):
            juenger(os.path.join(PROJ, "zeichnungen", f), "Zeichnung",
                    t_modell, "das Modell")
    for f in sorted(os.listdir(os.path.join(PROJ, "bilder"))):
        if f.endswith(".png"):
            juenger(os.path.join(PROJ, "bilder", f), "Bild", t_stl, "die STL")

    # ---- 2. STL gegen die gerechneten Masse -------------------------
    soll = {
        # Die seitliche Verbindung steht nicht mehr vor - die Aussenkante
        # ist buendig, deshalb genau aussen_x.
        "segmente/front-mitte-mitte.stl":
            (v["aussen_x"],
             v["segment_laenge"] + 3.0 + 9 + v["schild_dicke"] + 0.4,
             v["aussen_z"] + v["zapfen_h"]),
        "segmente/mitte-mitte-mitte.stl":
            (v["aussen_x"], v["segment_laenge"] + 9,
             v["aussen_z"] + v["zapfen_h"]),
        # Oberste Lage: ohne Zapfen genau die Ebenenhoehe
        "segmente/mitte-oben-mitte.stl":
            (v["aussen_x"], v["segment_laenge"] + 9, v["aussen_z"]),
        "schild.stl": (v["schild_breite"], v["schild_hoehe"], v["schild_dicke"]),
        # Trommel liegend: X und Y sind der Bordscheiben-Durchmesser,
        # Z die Wickelbreite mit beiden Scheiben
        "trommel.stl": (v["trommel_d"] + 3.0, v["trommel_d"] + 3.0,
                        v["trommel_b"] + 2 * 1.2),
    }
    for datei, (sx, sy, sz) in soll.items():
        p = os.path.join(PROJ, "stl", datei)
        if not os.path.exists(p):
            continue
        b = kasten(lade(p))
        for i, (ist, s, achse) in enumerate(zip(b, (sx, sy, sz), "XYZ")):
            if abs(ist - s) > 1.2:
                fehler.append(f"{datei}: {achse} ist {ist:.1f} mm, "
                              f"erwartet {s:.1f} mm")

    # ---- 3. Zahlen in den Zeichnungen -------------------------------
    # Jede Zeichnung traegt die Masse als Text. Wenn dort eine Zahl steht,
    # die es im Modell nicht mehr gibt, ist das Blatt veraltet.
    erwartet = {
        "01-frontsegment.svg": [f'{v["aussen_x"]:.1f}'.replace(".", ","),
                                f'{v["aussen_z"]:.1f}'.replace(".", ","),
                                f'{v["innen_x"]:.0f}'],
        "05-beutel-passung.svg": [f'{v["beutel_breit"]:.0f}',
                                  f'{v["beutel_hoch"]:.0f}',
                                  f'{v["beutel_dicke"]:.0f}'],
        "06-verbindungen.svg": [f'{v["zapfen_h"]:.1f}'.replace(".", ","),
                                f'{v["nase_t"]:.1f}'.replace(".", ",")],
        # Der Greifraum ist das Mass, an dem die Entnahme haengt - er muss
        # auf dem Zugriffsblatt stehen.
        "07-zugriff.svg": [f'{v["luft_oben"]:.0f}',
                           f'{v["anschlag_hoehe"]:.0f}'],
        # Federkammer und Trommel gehoeren aufs Schieberblatt
        "03-schieber-schild.svg": [
            f'{v["trommel_d"]:.1f}'.replace(".", ","),
            f'{v["schild_breite"]:.0f}'],
    }
    for datei, zahlen in erwartet.items():
        p = os.path.join(PROJ, "zeichnungen", datei)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            txt = f.read()
        sicht = " ".join(re.findall(r">([^<]+)<", txt))
        for z in zahlen:
            if z not in sicht:
                fehler.append(f"{datei}: Mass {z} fehlt im Blatt")

    # ---- 4. Schilder vollzaehlig ------------------------------------
    ordner = os.path.join(PROJ, "stl", "schilder")
    if os.path.isdir(ordner):
        platten = [f for f in os.listdir(ordner)
                   if f.endswith(".stl") and not f.endswith("-text.stl")]
        for pl in platten:
            if not os.path.exists(os.path.join(ordner, pl[:-4] + "-text.stl")):
                fehler.append(f"Schild ohne Schriftkoerper: {pl}")
            p = os.path.join(ordner, pl)
            b = kasten(lade(p))
            if abs(b[0] - v["schild_breite"]) > 0.6 or \
               abs(b[1] - v["schild_hoehe"]) > 0.6:
                fehler.append(f"schilder/{pl}: {b[0]:.0f}x{b[1]:.0f} mm, "
                              f"Modell sagt {v['schild_breite']:.0f}x"
                              f"{v['schild_hoehe']:.0f}")
        bilder = os.path.join(PROJ, "bilder", "schilder")
        if os.path.isdir(bilder):
            n_bild = len([f for f in os.listdir(bilder) if f.endswith(".png")])
            if n_bild != len(platten):
                hinweise.append(f"{len(platten)} Schilder, aber {n_bild} Bilder")

    # ---- Ergebnis ---------------------------------------------------
    print(f"Modell:   Schild {v['schild_breite']:.0f} x {v['schild_hoehe']:.0f} mm, "
          f"Greifraum {v['luft_oben']:.0f} mm ueber dem Beutel")
    print(f"          Segment {v['aussen_x']:.1f} x {v['aussen_z']:.1f} mm, "
          f"Zapfen {v['zapfen_h']:.1f} mm, Nase {v['nase_t']:.1f} mm")
    print(f"          Feder {v['feder_band_b']:.0f} mm Band auf Trommel "
          f"{v['trommel_d']:.1f} mm")
    print()
    for h in hinweise:
        print("  Hinweis:", h)
    for f in fehler:
        print("  FEHLER:", f)
    print()
    print("Modell, Bauteile, Zeichnungen und Bilder passen zusammen"
          if not fehler else f"{len(fehler)} Abweichungen gefunden")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
