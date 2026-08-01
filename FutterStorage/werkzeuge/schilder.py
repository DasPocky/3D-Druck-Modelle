#!/usr/bin/env python3
"""Baut für jede Sorte ein Schild - als STL zum Drucken und als PNG für die
Dokumentation.

Die Sortenliste deckt ab, was Purina Gourmet und Felix in der 85-g-Tüte
führen. Wer eine andere Sorte braucht, trägt sie hier ein: Name, Symbol.
Verfügbare Symbole stehen im Modell unter schild_sym().

Aufruf:  python3 werkzeuge/schilder.py [stl|png|beide]
"""
import os
import subprocess
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
MODELL = os.path.join(PROJ, "modell", "katzenfutter-regal.scad")
if not os.path.exists(MODELL):
    MODELL = os.path.join(PROJ, "katzenfutter-regal.scad")

# (Aufdruck, Symbol) - der Aufdruck darf bis zu zwölf Zeichen haben,
# das Modell setzt längere Namen automatisch schmaler.
SORTEN = [
    ("HUHN",       "huhn"),
    ("RIND",       "rind"),
    ("LACHS",      "lachs"),
    ("KANINCHEN",  "kaninchen"),
    ("TRUTHAHN",   "truthahn"),
    ("ENTE",       "ente"),
    ("THUNFISCH",  "thunfisch"),
    ("LAMM",       "lamm"),
    ("WILD",       "wild"),
    ("FORELLE",    "forelle"),
    ("GEFLUEGEL",  "gefluegel"),
    ("SEELACHS",   "fisch"),
]


def bauen(was):
    stl = os.path.join(PROJ, "stl", "schilder")
    png = os.path.join(PROJ, "bilder", "schilder")
    os.makedirs(stl, exist_ok=True)
    os.makedirs(png, exist_ok=True)

    for i, (text, symbol) in enumerate(SORTEN, 1):
        datei = f"{i:02d}-{symbol}"
        # TEIL steht als erstes und wird je Aufruf gesetzt. Frueher haengte
        # der zweite Aufruf sein TEIL vor die gemeinsame Liste - das dahinter
        # folgende TEIL="schild" ueberschrieb es, und die "-text"-Datei war in
        # Wirklichkeit noch einmal die Platte.
        def ruf(ziel, teil, extra=()):
            return subprocess.run(
                [SCAD, "-o", ziel, "-D", f'TEIL="{teil}"',
                 "-D", f'schild_text="{text}"',
                 "-D", f'schild_symbol="{symbol}"', *extra, MODELL],
                capture_output=True)

        if was in ("stl", "beide"):
            ruf(os.path.join(stl, datei + ".stl"), "schild")
            # Der erhabene Schriftkoerper fuer den Zweifarbdruck - und fuer
            # die Renderings, damit dort jede Spalte ihre Sorte zeigt.
            ruf(os.path.join(stl, datei + "-text.stl"), "schild_text")
        if was in ("png", "beide"):
            ruf(os.path.join(png, datei + ".png"), "schild",
                ("--render", "--viewall", "--autocenter",
                 "--camera=0,0,0,0,0,0,0", "--imgsize=960,400",
                 "--colorscheme=Tomorrow Night"))
        print(f"  {text:<12} {symbol}")
    print(f"{len(SORTEN)} Schilder in {was}")


if __name__ == "__main__":
    bauen(sys.argv[1] if len(sys.argv) > 1 else "beide")
