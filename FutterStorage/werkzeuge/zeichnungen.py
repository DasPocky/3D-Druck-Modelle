#!/usr/bin/env python3
"""Bemasste technische Zeichnungen. Jede Masslinie sagt, was sie misst;
Positionsnummern verweisen auf eine Legende."""
import os
import re

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PROJ, "zeichnungen")
os.makedirs(OUT, exist_ok=True)

def _modellwerte():
    """Liest die Parameter aus der OpenSCAD-Quelle. So kann eine Zeichnung
    nicht von dem abweichen, was tatsächlich gedruckt wird."""
    quelle = os.path.join(PROJ, "modell", "katzenfutter-regal.scad")
    if not os.path.exists(quelle):
        quelle = os.path.join(PROJ, "katzenfutter-regal.scad")
    v = {}
    with open(quelle, encoding="utf-8") as f:
        for zeile in f:
            teil = zeile.split("//")[0].strip().rstrip(";")
            if teil.count("=") == 1:
                k, _, w = teil.partition("=")
                try:
                    v[k.strip()] = float(w.strip())
                except ValueError:
                    pass
    innen_x = v["beutel_breit"] + v["spiel"]
    innen_z = v["beutel_hoch"] + v["luft_oben"]
    boden_d = v["boden"] + v["bandnut_tiefe"] + 0.8
    return dict(
        innen_x=innen_x, innen_z=innen_z,
        aussen_x=innen_x + 2 * v["wand"], aussen_z=boden_d + innen_z,
        boden=boden_d, wand=v["wand"], anschlag=v["anschlag_hoehe"],
        mulde_b=v["mulde_breite"], mulde_bis=v["mulde_bis"],
        nut_b=v["bandnut_breite"], nut_t=v["bandnut_tiefe"],
        segL=v["segment_laenge"],
        ay_front=v["segment_laenge"] + 3.0,
        ay_mitte=v["segment_laenge"],
        ay_end=v["segment_laenge"] + v["wand"],
        zunge_l=9, zunge_h=1.2,
        schild_b=v["schild_breite"], schild_h=v["schild_hoehe"],
        schild_d=v["schild_dicke"],
        feder_d=v["feder_rolle_d"], feder_b=v["feder_band_b"],
        achse=v["feder_achse_d"],
        zapfen_h=v["zapfen_h"], zapfen_l=v["zapfen_l"], zapfen_rand=v["zapfen_rand"],
        nase_t=v["nase_t"], nase_l=v["nase_l"], nase_h=v["nase_h"],
        passung=v["passung"],
        beutel_b=v["beutel_breit"], beutel_h=v["beutel_hoch"],
        beutel_d=v["beutel_dicke"])


M = _modellwerte()

LINIE, MASSL, HILF, GRAU, PAPIER = "#1a1a1e", "#bd4d0a", "#a8a29a", "#6e6a65", "#f7f5f2"
FLAECHE = "#e9e5de"
FS, FS_L, FS_T = 10, 8.8, 14


def _schneidet(x1, y1, x2, y2, rx1, ry1, rx2, ry2):
    """Kreuzt die Strecke das Rechteck? Liang-Barsky, auf das Noetige gekuerzt."""
    if rx2 <= rx1 or ry2 <= ry1:
        return False
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - rx1), (dx, rx2 - x1),
                 (-dy, y1 - ry1), (dy, ry2 - y1)):
        if p == 0:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return False
                t0 = max(t0, r)
            else:
                if r < t0:
                    return False
                t1 = min(t1, r)
    return t0 < t1


def _breite(s, size, mono):
    """Textbreite schaetzen. Entities zaehlen als ein Zeichen."""
    n = len(re.sub(r"&[a-z]+;", "x", s))
    return n * size * (0.60 if mono else 0.53)


class Blatt:
    def __init__(self, w=0, h=0):
        self.el, self.kaesten, self.bb = [], [], None
        self.leader = []
        self.name = "?"

    def _(self, s): self.el.append(s)

    def _bb(self, x1, y1, x2, y2):
        """Inhaltsgrenzen mitfuehren, damit das Blatt eng zugeschnitten wird."""
        if self.bb is None:
            self.bb = [x1, y1, x2, y2]
        else:
            self.bb = [min(self.bb[0], x1), min(self.bb[1], y1),
                       max(self.bb[2], x2), max(self.bb[3], y2)]

    def rect(self, x, y, w, h, fill="none", stroke=LINIE, sw=1.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self._(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
        self._bb(x, y, x + w, y + h)

    def line(self, x1, y1, x2, y2, stroke=LINIE, sw=1.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self._(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
               f'stroke="{stroke}" stroke-width="{sw}"{d}/>')
        self._bb(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

    def poly(self, pts, fill="none", stroke=LINIE, sw=1.2):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self._(f'<polyline points="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        self._bb(min(p[0] for p in pts), min(p[1] for p in pts),
                 max(p[0] for p in pts), max(p[1] for p in pts))

    def kreis(self, cx, cy, r, fill="none", stroke=LINIE, sw=1.2):
        self._(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
               f'stroke="{stroke}" stroke-width="{sw}"/>')
        self._bb(cx - r, cy - r, cx + r, cy + r)

    def txt(self, x, y, s, size=FS, anchor="middle", fill=LINIE, weight="400", mono=False,
            pruefen=True):
        fam = ("ui-monospace, SFMono-Regular, Menlo, monospace" if mono
               else "ui-sans-serif, system-ui, sans-serif")
        self._(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
               f'fill="{fill}" font-weight="{weight}" font-family="{fam}">{s}</text>')
        br = _breite(s, size, mono)
        x0 = x if anchor == "start" else (x - br if anchor == "end" else x - br / 2)
        kasten = (x0, y - size * 0.78, x0 + br, y + size * 0.24)
        self._bb(*kasten)
        if pruefen and s.strip():
            self.kaesten.append((kasten, s))

    # ---- Bemassung ----------------------------------------------------
    # Die Masshilfslinien laufen von der Objektkante (von=) bis zur Masslinie,
    # damit immer sichtbar ist, welche Kanten ein Mass verbindet.
    def mh(self, x1, x2, y, zahl, was="", von=None, oben=False):
        """von: y der Objektkante. oben=True: Kette liegt ueber dem Objekt."""
        if von is not None:
            ueber = 6 if von > y else -6
            for x in (x1, x2):
                self.line(x, von, x, y + ueber, HILF, 0.7)
        else:
            for x in (x1, x2):
                self.line(x, y - 4 if oben else y - 9, x, y + 9 if oben else y + 4, HILF, 0.7)
        b = _breite(zahl, FS, True) + 8
        eng = (x2 - x1) < b + 10
        self.line(x1, y, x2, y, MASSL, 1.0)
        for x, s in ((x1, 1), (x2, -1)):
            v = -s if eng else s          # bei engem Mass zeigen die Pfeile von aussen herein
            self._(f'<path d="M{x:.1f},{y:.1f} l{v*6:.1f},-2.6 l0,5.2 z" fill="{MASSL}"/>')
        if eng:
            # Zahl seitlich versetzt, kurze Fahne zur Masslinie
            zx = x2 + 12 + b / 2
            self.line(x2 + 6, y, zx - b / 2, y, MASSL, 1.0)
            self.txt(zx, y + 3.6, zahl, FS, "middle", MASSL, "600", True)
            if was:
                self.txt(zx + b / 2 + 4, y + 3.6, was, FS_L, "start", GRAU)
            return
        self._(f'<rect x="{(x1+x2)/2-b/2:.1f}" y="{y-7.5:.1f}" width="{b:.1f}" '
               f'height="11" fill="{PAPIER}"/>')
        self.txt((x1 + x2) / 2, y + 3.6, zahl, FS, "middle", MASSL, "600", True)
        if was:
            self.txt((x1 + x2) / 2, y - 13 if oben else y + 17, was, FS_L, "middle", GRAU)

    def mv(self, y1, y2, x, zahl, was="", von=None):
        """von: x der Objektkante."""
        if von is not None:
            ueber = 6 if von > x else -6
            for y in (y1, y2):
                self.line(von, y, x + ueber, y, HILF, 0.7)
        else:
            for y in (y1, y2):
                self.line(x - 9, y, x + 4, y, HILF, 0.7)
        ym, b = (y1 + y2) / 2, _breite(zahl, FS, True) + 8
        eng = (y2 - y1) < b + 10
        self.line(x, y1, x, y2, MASSL, 1.0)
        for y, s in ((y1, 1), (y2, -1)):
            v = -s if eng else s
            self._(f'<path d="M{x:.1f},{y:.1f} l-2.6,{v*6:.1f} l5.2,0 z" fill="{MASSL}"/>')
        if eng:
            zy = y2 + 12 + b / 2
            self.line(x, y2 + 6, x, zy - b / 2, MASSL, 1.0)
            self._(f'<g transform="translate({x:.1f},{zy:.1f}) rotate(-90)">'
                   f'<text x="0" y="3.6" font-size="{FS}" text-anchor="middle" fill="{MASSL}" '
                   f'font-weight="600" font-family="ui-monospace, Menlo, monospace">{zahl}'
                   f'</text></g>')
            self.kaesten.append(((x - 7, zy - b / 2, x + 5, zy + b / 2), zahl))
            self._bb(x - 7, zy - b / 2, x + 5, zy + b / 2)
            if was:
                bw = _breite(was, FS_L, False)
                self._(f'<g transform="translate({x:.1f},{zy+b/2+6:.1f}) rotate(-90)">'
                       f'<text x="0" y="3.2" font-size="{FS_L}" text-anchor="end" fill="{GRAU}" '
                       f'font-family="ui-sans-serif, system-ui, sans-serif">{was}</text></g>')
                self.kaesten.append(((x - 7, zy + b / 2 + 6, x + 5, zy + b / 2 + 6 + bw), was))
                self._bb(x - 7, zy + b / 2 + 6, x + 5, zy + b / 2 + 6 + bw)
            return
        self._(f'<g transform="translate({x:.1f},{ym:.1f}) rotate(-90)">'
               f'<rect x="{-b/2:.1f}" y="-7.5" width="{b:.1f}" height="11" fill="{PAPIER}"/>'
               f'<text x="0" y="3.6" font-size="{FS}" text-anchor="middle" fill="{MASSL}" '
               f'font-weight="600" font-family="ui-monospace, Menlo, monospace">{zahl}'
               f'</text></g>')
        self.kaesten.append(((x - 7, ym - b / 2, x + 5, ym + b / 2), zahl))
        self._bb(x - 7, ym - b / 2, x + 5, ym + b / 2)
        if was:
            self._(f'<g transform="translate({x-16:.1f},{ym:.1f}) rotate(-90)">'
                   f'<text x="0" y="0" font-size="{FS_L}" text-anchor="middle" fill="{GRAU}" '
                   f'font-family="ui-sans-serif, system-ui, sans-serif">{was}</text></g>')
            bw = _breite(was, FS_L, False)
            self.kaesten.append(((x - 22, ym - bw / 2, x - 13, ym + bw / 2), was))
            self._bb(x - 22, ym - bw / 2, x - 13, ym + bw / 2)

    def pos(self, nr, von_x, von_y, nach_x, nach_y):
        self.line(von_x, von_y, nach_x, nach_y, HILF, 0.8)
        self.leader.append(((von_x, von_y, nach_x, nach_y), f"Pos {nr}"))
        self.kreis(nach_x, nach_y, 10, PAPIER, LINIE, 1.1)
        self.txt(nach_x, nach_y + 3.6, str(nr), 10, "middle", LINIE, "700", True)

    def ansicht(self, x, y, t):
        """Ansichtstitel mit Unterstrich, steht immer oberhalb aller Massketten."""
        br = _breite(t, 10.5, False) + 8
        self.txt(x, y, t, 10.5, "start", LINIE, "700", pruefen=False)
        self.line(x, y + 5, x + br, y + 5, MASSL, 1.4)
        self.kaesten.append(((x, y - 9, x + br, y + 7), t))   # Text und Unterstrich zusammen

    def legende(self, x, y, eintraege, spalten=2):
        self.txt(x, y, "POSITIONEN", 9.5, "start", GRAU, "700")
        pro = (len(eintraege) + spalten - 1) // spalten
        for i, (nr, was, mass) in enumerate(eintraege):
            sp, zi = i // pro, i % pro
            xx, yy = x + sp * 400, y + 22 + zi * 19
            self.kreis(xx + 8, yy - 3.5, 8, "none", LINIE, 1.0)
            self.txt(xx + 8, yy, str(nr), 9, "middle", LINIE, "700", True)
            self.txt(xx + 24, yy, was, 10, "start")
            if mass:
                self.txt(xx + 366, yy, mass, 10, "end", MASSL, "600", True)

    def titel(self, name, unter, nr):
        self._titel = (name, unter, nr)

    def _kollisionen(self):
        """Zwei Pruefungen: Beschriftungen duerfen sich nicht ueberdecken,
        und keine Hinweislinie darf durch eine Beschriftung laufen."""
        tr, fund = 1.5, []
        for i in range(len(self.kaesten)):
            (ax1, ay1, ax2, ay2), a = self.kaesten[i]
            for j in range(i + 1, len(self.kaesten)):
                (bx1, by1, bx2, by2), bt = self.kaesten[j]
                ux = min(ax2, bx2) - max(ax1, bx1)
                uy = min(ay2, by2) - max(ay1, by1)
                if ux > tr and uy > tr:
                    fund.append(f'{self.name}: "{a[:38]}" ueberdeckt "{bt[:38]}" '
                                f'({ux:.0f}x{uy:.0f} px)')
        for (lx1, ly1, lx2, ly2), wer in self.leader:
            for (kx1, ky1, kx2, ky2), was in self.kaesten:
                if was == wer.split()[-1]:      # die eigene Ziffer am Ende
                    continue
                if _schneidet(lx1, ly1, lx2, ly2,
                              kx1 + 1, ky1 + 1, kx2 - 1, ky2 - 1):
                    fund.append(f'{self.name}: Linie {wer} laeuft durch '
                                f'"{was[:38]}"')
        return fund

    def save(self, datei):
        self.name = datei
        RAND, TB = 26, 66
        x0, y0, x1, y1 = self.bb
        dx, dy = RAND - x0, RAND - y0
        w = round(x1 - x0 + 2 * RAND)
        h = round(y1 - y0 + 2 * RAND)
        teile = [f'<g transform="translate({dx:.1f},{dy:.1f})">', "".join(self.el), "</g>"]

        name, unter, nr = getattr(self, "_titel", ("", "", ""))
        ty = h + 2
        teile.append(
            f'<line x1="{RAND}" y1="{ty}" x2="{w-RAND}" y2="{ty}" stroke="{LINIE}" '
            f'stroke-width="1.6"/>'
            f'<text x="{RAND}" y="{ty+22}" font-size="{FS_T}" fill="{LINIE}" font-weight="700" '
            f'font-family="ui-sans-serif, system-ui, sans-serif">{name}</text>'
            f'<text x="{RAND}" y="{ty+39}" font-size="10" fill="{GRAU}" '
            f'font-family="ui-sans-serif, system-ui, sans-serif">{unter}</text>'
            f'<text x="{w-RAND}" y="{ty+22}" font-size="11.5" fill="{MASSL}" font-weight="700" '
            f'text-anchor="end" font-family="ui-monospace, Menlo, monospace">{nr}</text>'
            f'<text x="{w-RAND}" y="{ty+39}" font-size="10" fill="{GRAU}" text-anchor="end" '
            f'font-family="ui-sans-serif, system-ui, sans-serif">Alle Ma&#223;e in mm</text>')

        H = h + TB
        with open(os.path.join(OUT, datei), "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>'
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" '
                    f'viewBox="0 0 {w} {H}">'
                    f'<rect width="{w}" height="{H}" fill="{PAPIER}"/>'
                    + "".join(teile) + "</svg>")
        return datei, self._kollisionen()


