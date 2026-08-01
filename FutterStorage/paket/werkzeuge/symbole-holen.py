#!/usr/bin/env python3
"""Wandelt die OpenMoji-SVG in OpenSCAD-Polygone.

Warum nicht selbst gezeichnet: Ein erster Versuch mit von Hand gesetzten
Kreisen und Polygonen ergab Tiere, die man raten musste - das Wild sah aus
wie ein Lama. OpenMoji ist ein durchgezeichneter Satz aus einer Hand, damit
sehen alle acht Sorten wie aus derselben Familie aus.

Verwendet wird die `color`-Gruppe jeder Datei: ihre Flaechen ergeben
vereinigt die Silhouette. Die `line`-Gruppe waere eine Strichzeichnung und
als 0,6 mm tiefe Gravur nicht druckbar.

OpenSCAD kann kein SVG lesen. Die Pfade werden deshalb hier abgetastet -
Geraden direkt, kubische Beziers in Stuecken - und als polygon() geschrieben.
Arcs kommen in diesen Dateien nicht vor.

Aufruf:  python3 werkzeuge/symbole-holen.py
"""
import math
import os
import re
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(PROJ, "modell", "symbole")
ZIEL = os.path.join(PROJ, "modell", "sortensymbole.scad")

# Name -> ob zusaetzlich die line-Gruppe verdickt mitgenommen wird.
# Nur beim Hirsch noetig: sein Geweih steckt dort und nicht in den
# Farbflaechen. Ohne es ist er von Lamm und Rind nicht zu unterscheiden.
SORTEN = {
    "huhn": False, "rind": False, "fisch": False, "kaninchen": False,
    "ente": False, "truthahn": False, "lamm": False, "wild": True,
}

FELD = 20.0        # Kantenlaenge des Zielfeldes, zentriert um (0,0)
BOGEN = 8          # Stuetzpunkte je Bezier - mehr macht die STL nur groesser
MINDEST = 1.2      # Flaechen kleiner als das entfallen (Augen, Glanzpunkte)
STRICH = 2.6       # Strichstaerke fuer line-Pfade, in SVG-Einheiten

_ZAHL = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def _zahlen(text):
    return [float(x) for x in _ZAHL.findall(text)]


def bezier(p0, p1, p2, p3, n=BOGEN):
    """Kubische Bezierkurve abtasten, Startpunkt ausgelassen."""
    aus = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        aus.append((u**3 * p0[0] + 3 * u * u * t * p1[0]
                    + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1]
                    + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return aus


def pfad_zu_ringen(d):
    """Ein SVG-d-Attribut in geschlossene Punktzuege zerlegen."""
    ringe, punkte = [], []
    pos = (0.0, 0.0)
    start = (0.0, 0.0)
    letzte_c2 = None
    befehl = None
    i = 0
    stuecke = re.findall(r"([A-Za-z])|([-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?)", d)
    werte = []
    folge = []
    for buchstabe, zahl in stuecke:
        if buchstabe:
            folge.append((buchstabe, werte := []))
        elif folge:
            folge[-1][1].append(float(zahl))

    for befehl, args in folge:
        gross = befehl.isupper()
        b = befehl.upper()

        if b == "M":
            for k in range(0, len(args) - 1, 2):
                p = (args[k], args[k + 1]) if gross else \
                    (pos[0] + args[k], pos[1] + args[k + 1])
                if k == 0:
                    if len(punkte) > 2:
                        ringe.append(punkte)
                    punkte = [p]
                    start = p
                else:
                    punkte.append(p)
                pos = p
            letzte_c2 = None
        elif b == "L":
            for k in range(0, len(args) - 1, 2):
                p = (args[k], args[k + 1]) if gross else \
                    (pos[0] + args[k], pos[1] + args[k + 1])
                punkte.append(p)
                pos = p
            letzte_c2 = None
        elif b == "H":
            for a in args:
                p = (a, pos[1]) if gross else (pos[0] + a, pos[1])
                punkte.append(p)
                pos = p
            letzte_c2 = None
        elif b == "V":
            for a in args:
                p = (pos[0], a) if gross else (pos[0], pos[1] + a)
                punkte.append(p)
                pos = p
            letzte_c2 = None
        elif b == "C":
            for k in range(0, len(args) - 5, 6):
                if gross:
                    c1 = (args[k], args[k + 1])
                    c2 = (args[k + 2], args[k + 3])
                    p = (args[k + 4], args[k + 5])
                else:
                    c1 = (pos[0] + args[k], pos[1] + args[k + 1])
                    c2 = (pos[0] + args[k + 2], pos[1] + args[k + 3])
                    p = (pos[0] + args[k + 4], pos[1] + args[k + 5])
                punkte += bezier(pos, c1, c2, p)
                pos, letzte_c2 = p, c2
        elif b == "S":
            for k in range(0, len(args) - 3, 4):
                if gross:
                    c2 = (args[k], args[k + 1])
                    p = (args[k + 2], args[k + 3])
                else:
                    c2 = (pos[0] + args[k], pos[1] + args[k + 1])
                    p = (pos[0] + args[k + 2], pos[1] + args[k + 3])
                # Erster Kontrollpunkt ist die Spiegelung des letzten
                c1 = pos if letzte_c2 is None else \
                    (2 * pos[0] - letzte_c2[0], 2 * pos[1] - letzte_c2[1])
                punkte += bezier(pos, c1, c2, p)
                pos, letzte_c2 = p, c2
        elif b == "Q":
            for k in range(0, len(args) - 3, 4):
                if gross:
                    q = (args[k], args[k + 1])
                    p = (args[k + 2], args[k + 3])
                else:
                    q = (pos[0] + args[k], pos[1] + args[k + 1])
                    p = (pos[0] + args[k + 2], pos[1] + args[k + 3])
                # quadratisch als kubisch ausdruecken
                c1 = (pos[0] + 2 / 3 * (q[0] - pos[0]),
                      pos[1] + 2 / 3 * (q[1] - pos[1]))
                c2 = (p[0] + 2 / 3 * (q[0] - p[0]),
                      p[1] + 2 / 3 * (q[1] - p[1]))
                punkte += bezier(pos, c1, c2, p)
                pos = p
            letzte_c2 = None
        elif b == "Z":
            if len(punkte) > 2:
                ringe.append(punkte)
            punkte = []
            pos = start
            letzte_c2 = None

    if len(punkte) > 2:
        ringe.append(punkte)
    return ringe


def kreis_zu_ring(cx, cy, rx, ry, n=28):
    return [(cx + rx * math.cos(2 * math.pi * i / n),
             cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def flaeche(ring):
    s = 0.0
    for i in range(len(ring)):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % len(ring)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def striche_aus_svg(pfad):
    """Offene Linienzuege der line-Gruppe. Sie werden spaeter zu Baendern
    verdickt - als Haarlinie waeren sie nicht druckbar."""
    roh = open(pfad, encoding="utf-8").read()
    m = re.search(r'<g[^>]*id="line"[^>]*>(.*?)</g>\s*</svg>', roh, re.S)
    if not m:
        m = re.search(r'<g[^>]*id="line"[^>]*>(.*)', roh, re.S)
    teil = m.group(1) if m else ""
    zuege = []
    for d in re.findall(r'\bd="([^"]+)"', teil):
        zuege += pfad_zu_ringen(d)
    for tag in re.findall(r"<(?:polyline|polygon)[^>]*>", teil):
        w = dict(re.findall(r'(\w+)="([^"]+)"', tag))
        if "points" in w:
            z = _zahlen(w["points"])
            zuege.append([(z[i], z[i + 1]) for i in range(0, len(z) - 1, 2)])
    return [z for z in zuege if len(z) >= 2]


def ringe_aus_svg(pfad):
    """Alle Formen der color-Gruppe als Punktzuege."""
    roh = open(pfad, encoding="utf-8").read()
    m = re.search(r'<g[^>]*id="color"[^>]*>(.*?)</g>', roh, re.S)
    teil = m.group(1) if m else roh

    ringe = []
    for d in re.findall(r'\bd="([^"]+)"', teil):
        ringe += pfad_zu_ringen(d)
    for tag in re.findall(r"<circle[^>]*>", teil):
        w = dict(re.findall(r'(\w+)="([^"]+)"', tag))
        if {"cx", "cy", "r"} <= w.keys():
            ringe.append(kreis_zu_ring(float(w["cx"]), float(w["cy"]),
                                       float(w["r"]), float(w["r"])))
    for tag in re.findall(r"<ellipse[^>]*>", teil):
        w = dict(re.findall(r'(\w+)="([^"]+)"', tag))
        if {"cx", "cy", "rx", "ry"} <= w.keys():
            ringe.append(kreis_zu_ring(float(w["cx"]), float(w["cy"]),
                                       float(w["rx"]), float(w["ry"])))
    for tag in re.findall(r"<(?:polygon|polyline)[^>]*>", teil):
        w = dict(re.findall(r'(\w+)="([^"]+)"', tag))
        if "points" in w:
            z = _zahlen(w["points"])
            ringe.append([(z[i], z[i + 1]) for i in range(0, len(z) - 1, 2)])
    for tag in re.findall(r"<rect[^>]*>", teil):
        w = dict(re.findall(r'(\w+)="([^"]+)"', tag))
        if {"x", "y", "width", "height"} <= w.keys():
            x, y = float(w["x"]), float(w["y"])
            b, h = float(w["width"]), float(w["height"])
            ringe.append([(x, y), (x + b, y), (x + b, y + h), (x, y + h)])
    return [r for r in ringe if flaeche(r) >= MINDEST]


def einpassen(ringe, striche=()):
    """SVG-Koordinaten (y nach unten) in ein Feld um (0,0) bringen.
    Flaechen und Striche werden gemeinsam eingepasst, sonst passten sie
    hinterher nicht mehr zueinander."""
    alle = list(ringe) + list(striche)
    xs = [p[0] for r in alle for p in r]
    ys = [p[1] for r in alle for p in r]
    breit, hoch = max(xs) - min(xs), max(ys) - min(ys)
    k = FELD / max(breit, hoch)
    mx, my = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    # y spiegeln: SVG zaehlt nach unten, OpenSCAD nach oben
    um = lambda r: [((x - mx) * k, -(y - my) * k) for x, y in r]
    return [um(r) for r in ringe], [um(r) for r in striche], k


def main():
    if not os.path.isdir(SVG):
        print("keine Symbol-SVG gefunden:", SVG)
        return 1

    teile = ['''// =====================================================================
//  Sortensymbole - ERZEUGT, nicht von Hand aendern
//
//  Quelle:  modell/symbole/*.svg  (OpenMoji, CC BY-SA 4.0)
//  Erzeugt: werkzeuge/symbole-holen.py
//
//  Jede Silhouette ist die vereinigte color-Gruppe der OpenMoji-Datei,
//  auf ein Feld von 20 x 20 um den Nullpunkt gebracht. Dass sie mittig
//  liegt, prueft werkzeuge/symbole-pruefen.py nach.
//
//  Namensnennung gehoert bei Weitergabe dazu - siehe
//  modell/symbole/HERKUNFT.md
// =====================================================================
''']

    for name, mit_linien in SORTEN.items():
        pfad = os.path.join(SVG, name + ".svg")
        if not os.path.exists(pfad):
            print(f"  {name}: SVG fehlt")
            return 1
        roh_ringe = ringe_aus_svg(pfad)
        roh_striche = striche_aus_svg(pfad) if mit_linien else []
        ringe, striche, k = einpassen(roh_ringe, roh_striche)
        r_strich = STRICH * k / 2          # Halbe Strichstaerke im Zielmass

        gesamt = sum(len(r) for r in ringe)
        anm = f", {len(striche)} Striche" if striche else ""
        teile.append(f"\n// {name} - {len(ringe)} Flaechen, {gesamt} Punkte{anm}\n"
                     f"module sym_{name}() {{\n    union() {{")
        for r in ringe:
            punkte = ", ".join(f"[{x:.2f},{y:.2f}]" for x, y in r)
            teile.append(f"        polygon([{punkte}]);")
        # Striche als Kette von Kapseln - so bleibt das Geweih druckbar
        for z in striche:
            for a, b in zip(z, z[1:]):
                if (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 < 1e-6:
                    continue
                teile.append(
                    f"        hull() {{ translate([{a[0]:.2f},{a[1]:.2f}]) "
                    f"circle(r={r_strich:.2f}, $fn=10); "
                    f"translate([{b[0]:.2f},{b[1]:.2f}]) "
                    f"circle(r={r_strich:.2f}, $fn=10); }}")
        teile.append("    }\n}")
        print(f"  {name:<12}{len(ringe):>3} Flaechen{gesamt:>6} Punkte{anm}")

    # Das Fischauge bleibt als Aussparung erhalten
    teile.append('''
// Aussparung im Fisch - ohne sie verschwaende das Auge in der Silhouette
module sym_fisch_auge() {
    translate([3.4, 2.2]) circle(r = 1.5);
}
''')
    with open(ZIEL, "w", encoding="utf-8") as f:
        f.write("\n".join(teile) + "\n")
    print(f"\n{ZIEL} geschrieben ({os.path.getsize(ZIEL) / 1024:.0f} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
