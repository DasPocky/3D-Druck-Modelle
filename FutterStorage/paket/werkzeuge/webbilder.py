#!/usr/bin/env python3
"""Erzeugt aus den vollen Renderings die kleinen Fassungen für die Seiten.

Die Dokumentationsseiten laden nicht die 2,5-MB-PNG, sondern verkleinerte
JPEG aus bilder/web/. Bisher entstanden die von Hand — was zweierlei
bedeutete: Beim Nachbauen fehlte der Schritt, und nach einer Änderung am
Modell zeigten die Seiten wochenalte Bilder, während die PNG daneben schon
neu waren. Genau die Art von Auseinanderdriften, die abgleich.py sonst
überall abfängt.

Verkleinert wird mit sips, das auf jedem Mac vorhanden ist — keine
Fremdbibliothek nötig.

Aufruf:  python3 werkzeuge/webbilder.py
"""
import os
import subprocess
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BILDER = os.path.join(PROJ, "bilder")
WEB = os.path.join(BILDER, "web")

BREITE = 1600          # so breit werden die Seiten sie höchstens zeigen
QUALITAET = "78"       # sichtbar verlustfrei, spart gegenüber PNG ~95 %


def main():
    if not os.path.isdir(BILDER):
        print("keine Bilder gefunden:", BILDER)
        return 1
    os.makedirs(WEB, exist_ok=True)

    quellen = sorted(f for f in os.listdir(BILDER)
                     if f.endswith(".png") and f.startswith("b_"))
    if not quellen:
        print("keine Renderings in", BILDER)
        return 1

    gesamt_png = gesamt_jpg = 0
    for name in quellen:
        quelle = os.path.join(BILDER, name)
        ziel = os.path.join(WEB, name[:-4] + ".jpg")
        e = subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", QUALITAET,
             "-Z", str(BREITE), quelle, "--out", ziel],
            capture_output=True, text=True)
        if e.returncode != 0 or not os.path.exists(ziel):
            print(f"  {name}: FEHLER {e.stderr.strip()[:60]}")
            return 1
        a, b = os.path.getsize(quelle), os.path.getsize(ziel)
        gesamt_png += a
        gesamt_jpg += b
        print(f"  {name[:-4] + '.jpg':<22}{b / 1024:>7.0f} kB   "
              f"aus {a / 1048576:.1f} MB")

    # Verwaiste Dateien melden - sie stammen von Szenen, die es nicht mehr gibt
    erwartet = {n[:-4] + ".jpg" for n in quellen}
    for f in sorted(os.listdir(WEB)):
        if f.endswith(".jpg") and f not in erwartet:
            print(f"  ueberzaehlig: web/{f} - kein Rendering dazu")

    print(f"\n{len(quellen)} Bilder, {gesamt_jpg / 1048576:.1f} MB statt "
          f"{gesamt_png / 1048576:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
