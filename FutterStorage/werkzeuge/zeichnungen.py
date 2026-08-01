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


# =====================================================================
def blatt1():
    K = 1.7
    b = Blatt(1300, 940)
    ax, az, ay = M["aussen_x"] * K, M["aussen_z"] * K, M["ay_front"] * K
    W, BO = M["wand"] * K, M["boden"] * K

    # ---------- Vorderansicht ----------
    ox, oy = 118, 96
    b.ansicht(ox, oy - 78, "VORDERANSICHT")
    b.rect(ox, oy, ax, az, FLAECHE)
    # Innenraum
    b.rect(ox + W, oy + BO, M["innen_x"] * K, M["innen_z"] * K, PAPIER, HILF, 0.9, "5 3")
    # Frontwand: alles unterhalb dieser Linie ist Wand
    wy = oy + az - (M["anschlag"] + M["boden"]) * K
    b.rect(ox, wy, ax, (M["anschlag"] + M["boden"]) * K, FLAECHE, LINIE, 1.2)
    # Griffmulde
    mb, fa = M["mulde_b"] * K, 11 * K
    mx = ox + ax / 2 - mb / 2
    my = oy + az - (M["mulde_bis"] + M["boden"]) * K
    b.poly([(mx, wy), (mx, my - fa), (mx + fa, my), (mx + mb - fa, my),
            (mx + mb, my - fa), (mx + mb, wy)], PAPIER, LINIE, 1.2)
    # Schildtasche
    sb, sh = M["schild_b"] * K, (M["schild_h"] + 4) * K
    sx, sy = ox + ax / 2 - sb / 2, oy + az - (6 + M["schild_h"] + 4) * K
    b.rect(sx - 1.6 * K, sy, sb + 3.2 * K, sh, "none", MASSL, 1.4)

    b.pos(1, ox + ax - 14, wy + 8, ox + ax + 66, wy - 16)
    b.pos(2, mx + mb / 2, my - fa / 2, ox + ax + 66, my - 30)
    b.pos(3, sx + sb - 10, sy + sh / 2, ox + ax + 66, sy + sh / 2)

    b.mh(ox + W, ox + ax - W, oy + az + 40, f'{M["innen_x"]:.0f}', "Innenbreite für den Beutel",
         von=oy + az)
    b.mh(ox, ox + ax, oy + az + 74, f'{M["aussen_x"]:.1f}'.replace(".", ","), "Außenbreite = Spaltenmaß", von=oy + az)
    b.mv(oy, oy + az, ox - 34, f'{M["aussen_z"]:.1f}'.replace(".", ","), "Außenhöhe = Ebenenmaß", von=ox)
    b.mv(wy, oy + az, ox - 78, f'{M["anschlag"]:.0f}', "Frontwand", von=ox)
    b.mh(mx, mx + mb, oy - 34, "52", "Griffmulde", von=my - fa, oben=True)

    # ---------- Seitenansicht ----------
    ox2 = ox + ax + 210
    b.ansicht(ox2, oy - 78, "SEITENANSICHT")
    b.rect(ox2, oy, ay, az, FLAECHE)
    b.rect(ox2, oy + az - BO, ay, BO, "#d8d3cb", LINIE, 1.0)          # Boden
    b.rect(ox2, wy - oy + oy, 3 * K, (M["anschlag"] + M["boden"]) * K, "#3d3d43")  # Frontwand
    fh = (M["innen_z"] - 26) * K
    b.rect(ox2 + 17 * K, oy + az - (M["boden"] + 14) * K - fh,
           (M["segL"] - 28) * K, fh, PAPIER, HILF, 1.0, "5 3")       # Fenster
    b.rect(ox2 + ay, oy + az - BO, M["zunge_l"] * K, M["zunge_h"] * K, MASSL, MASSL, 1.0)

    b.pos(4, ox2 + 17 * K + 40, oy + az - (M["boden"] + 14) * K - fh + 20,
          ox2 - 44, oy + 30)
    b.pos(5, ox2 + ay + 4, oy + az - BO + 2, ox2 + ay + 60, oy + az - 44)
    b.pos(6, ox2 + ay - 26, oy + az - BO / 2, ox2 + ay + 58, oy + az + 14)

    b.mh(ox2, ox2 + ay, oy + az + 40, "163", "Bauteillänge", von=oy + az)
    b.mh(ox2 + ay, ox2 + ay + M["zunge_l"] * K, oy + az + 74, "9", "Zungenüberstand",
         von=oy + az)
    b.mv(oy, oy + az, ox2 + ay + 96, f'{M["aussen_z"]:.1f}'.replace(".", ","), "Außenhöhe", von=ox2 + ay)

    # ---------- Draufsicht ----------
    oy3 = oy + az + 212
    b.ansicht(ox, oy3 - 78, "DRAUFSICHT")
    b.rect(ox, oy3, ax, ay, FLAECHE)
    b.rect(ox + W, oy3 + 3 * K, M["innen_x"] * K, (M["ay_front"] - 3) * K,
           PAPIER, HILF, 0.9, "5 3")
    nb = M["nut_b"] * K
    b.rect(ox + ax / 2 - nb / 2, oy3, nb, ay, "#f0d9c8", MASSL, 1.3)
    b.pos(7, ox + ax / 2 + nb / 2, oy3 + ay * 0.4, ox + ax + 66, oy3 + ay * 0.4)
    b.mh(ox + ax / 2 - nb / 2, ox + ax / 2 + nb / 2, oy3 - 34, "18", "Bandnut",
         von=oy3, oben=True)
    b.mv(oy3, oy3 + ay, ox - 34, "163", "Bauteillänge", von=ox)

    b.legende(ox2, oy3 + 30, [
        (1, "Frontwand, hält den Beutel", "92 hoch"),
        (2, "Griffmulde zum Anfassen", "52 breit"),
        (3, "Tasche für das Schild", "74 x 18"),
        (4, "Fenster in der Seitenwand", "132 x 114"),
        (5, "Bodenzunge zum Nachbarsegment", "9 lang"),
        (6, "Bodenstärke mit Nut", "4,8"),
        (7, "Bandnut für die Feder", "18 x 1,6"),
    ], spalten=1)

    b.titel("Frontsegment", "Vorderstes Kanalstück mit Frontwand, Griffmulde, "
            "Schildtasche und Bandhaken", "TEIL 01")
    return b.save("01-frontsegment.svg")


# =====================================================================
def blatt2():
    K = 1.6
    b = Blatt(1340, 860)
    ax, az = M["aussen_x"] * K, M["aussen_z"] * K
    W, BO = M["wand"] * K, M["boden"] * K

    for i, (typ, ayv, nr) in enumerate([("MITTELSEGMENT", M["ay_mitte"], 1),
                                        ("ENDSEGMENT", M["ay_end"], 4)]):
        ox, oy = 118 + i * 640, 96
        ay = ayv * K
        b.ansicht(ox, oy - 78, typ + " — SEITENANSICHT")
        b.rect(ox, oy, ay, az, FLAECHE)
        b.rect(ox, oy + az - BO, ay, BO, "#d8d3cb", LINIE, 1.0)
        fh = (M["innen_z"] - 26) * K
        b.rect(ox + 14 * K, oy + az - (M["boden"] + 14) * K - fh,
               (M["segL"] - 28) * K, fh, PAPIER, HILF, 1.0, "5 3")
        if i == 0:
            b.rect(ox + ay, oy + az - BO, M["zunge_l"] * K, M["zunge_h"] * K, MASSL, MASSL)
            b.rect(ox - M["zunge_l"] * K, oy + az - BO, M["zunge_l"] * K,
                   M["zunge_h"] * K, "none", MASSL, 1.0, "3 2")
            b.pos(1, ox + ay + 4, oy + az - BO, ox + ay + 56, oy + az - 50)
            b.pos(2, ox - 4, oy + az - BO, ox - 56, oy + az - 50)
            b.pos(3, ox + 14 * K + 30, oy + az - (M["boden"] + 14) * K - fh + 18,
                  ox + 30, oy - 40)
        else:
            b.rect(ox + ay - W, oy, W, az, "#3d3d43")
            sw, shh = (M["innen_x"] - 24) * K, (M["innen_z"] - 34) * K
            b.rect(ox + ay - W - 6, oy + az - (M["boden"] + 16) * K - shh, 6, shh,
                   PAPIER, HILF, 1.0, "5 3")
            b.pos(4, ox + ay - W, oy + 40, ox + ay + 56, oy + 20)
            b.pos(5, ox + ay - W - 6, oy + az - 130, ox + ay + 56, oy + az - 150)
        b.mh(ox, ox + ay, oy + az + 40, f'{ayv:.1f}'.replace(".", ","), "Bauteillänge",
             von=oy + az)
        b.mv(oy, oy + az, ox - 34, f'{M["aussen_z"]:.1f}'.replace(".", ","), "Außenhöhe", von=ox)

    # Querschnitt gemeinsam
    ox, oy2 = 118, 96 + az + 176
    b.ansicht(ox, oy2 - 78, "QUERSCHNITT — gilt für alle Segmente")
    b.rect(ox, oy2, ax, az, FLAECHE)
    b.rect(ox + W, oy2 + BO, M["innen_x"] * K, M["innen_z"] * K, PAPIER, HILF, 0.9, "5 3")
    nb = M["nut_b"] * K
    b.rect(ox + ax / 2 - nb / 2, oy2 + az - BO, nb, M["nut_t"] * K, "#f0d9c8", MASSL, 1.2)
    # Beutel eingezeichnet
    bb, bh = M["beutel_b"] * K, M["beutel_h"] * K
    b.rect(ox + W + 2 * K, oy2 + BO, bb, bh, "#cdd0d6", "#9aa0a8", 1.0)
    b.txt(ox + W + 2 * K + bb / 2, oy2 + BO + bh / 2, "Beutel", 10, "middle", "#5a6068")
    b.mh(ox, ox + ax, oy2 + az + 40, f'{M["aussen_x"]:.1f}'.replace(".", ","), "Außenbreite", von=oy2 + az)
    b.mh(ox + W, ox + W + 2 * K, oy2 - 34, "Luft 2", "", von=oy2, oben=True)
    b.mh(ox + W + 2 * K + bb, ox + ax - W, oy2 - 34, "Luft 2", "", von=oy2, oben=True)
    b.mv(oy2 + BO, oy2 + BO + bh, ox + ax + 40, f'{M["beutel_h"]:.0f}', "Beutelhöhe", von=ox + ax)
    b.mv(oy2 + BO + bh, oy2 + az, ox + ax + 40, f'{M["innen_z"] - M["beutel_h"]:.0f}', "Luft oben", von=ox + ax)
    b.mv(oy2 + az - BO, oy2 + az, ox - 34, f'{M["boden"]:.1f}'.replace(".", ","), "Boden", von=ox)

    b.legende(ox + ax + 150, oy2 + 20, [
        (1, "Bodenzunge nach hinten", "9 lang"),
        (2, "Aufnahme für die Zunge des Vordermanns", "9 tief"),
        (3, "Fenster, spart Material und zeigt den Füllstand", "132 x 114"),
        (4, "Rückwand, schließt den Kanal", "1,6 dick"),
        (5, "Sichtschlitz in der Rückwand", "68 x 106"),
    ], spalten=1)

    b.titel("Mittel- und Endsegment", "Mittelstück beliebig oft wiederholbar, "
            "Endstück schließt hinten ab", "TEIL 02 / 03")
    return b.save("02-mittel-endsegment.svg")


# =====================================================================
def blatt3():
    K = 2.0
    b = Blatt(1300, 860)
    bb = (M["innen_x"] - 1.2) * K
    hh = (M["beutel_h"] - 8) * K
    fu = 36 * K

    ox, oy = 118, 96
    b.ansicht(ox, oy - 78, "SCHIEBER — SEITENANSICHT")
    b.rect(ox, oy, fu, hh, FLAECHE)
    b.rect(ox, oy, 2.6 * K, hh, "#3d3d43")                     # Stuetzplatte
    b.rect(ox, oy + hh - 3 * K, fu, 3 * K, "#d8d3cb")          # Fuss
    ay_ = 4 * K + M["feder_d"] * K / 2
    axh = M["feder_d"] * K / 2 + 4 * K
    b.kreis(ox + ay_, oy + hh - axh, M["feder_d"] * K / 2, "#f0d9c8", MASSL, 1.5)
    b.kreis(ox + ay_, oy + hh - axh, M["achse"] * K / 2, MASSL, MASSL, 1.0)
    b.rect(ox, oy + hh - 3 * K - 3 * K, 2.6 * K + 4, 3 * K, "none", MASSL, 1.3)

    b.pos(1, ox + ay_ + M["feder_d"] * K / 2 - 6, oy + hh - axh - 14,
          ox + fu + 66, oy + 44)
    b.pos(2, ox + ay_, oy + hh - axh, ox + fu + 66, oy + 92)
    b.pos(3, ox + 4, oy + hh - 5 * K, ox - 62, oy + hh + 34)
    b.pos(4, ox + fu / 2, oy + 14, ox + fu / 2, oy - 44)

    b.mh(ox, ox + fu, oy + hh + 44, "36", "Fußlänge", von=oy + hh)
    b.mv(oy, oy + hh, ox - 34, "128", "Schieberhöhe", von=ox)
    b.mv(oy + hh - axh - M["feder_d"] * K / 2, oy + hh - axh + M["feder_d"] * K / 2,
         ox + fu + 150, "26", "max Rollendurchmesser")

    ox2 = ox + fu + 250
    b.ansicht(ox2, oy - 78, "SCHIEBER — VORDERANSICHT")
    b.rect(ox2, oy, bb, hh, FLAECHE)
    kb = (M["feder_b"] + 1.6) * K
    b.rect(ox2 + bb / 2 - kb / 2, oy + hh - (axh + M["feder_d"] * K / 2) - 4 * K,
           kb, axh + M["feder_d"] * K / 2, PAPIER, MASSL, 1.3, "5 3")
    b.mh(ox2, ox2 + bb, oy + hh + 44, "90,8", "Breite, gleitet im Kanal", von=oy + hh)
    b.mh(ox2 + bb / 2 - kb / 2, ox2 + bb / 2 + kb / 2, oy - 34, "17,6", "Federkammer",
         von=oy + hh - (axh + M["feder_d"] * K / 2) - 4 * K, oben=True)

    # Schild
    oy3 = oy + hh + 118
    Ks = 3.0
    b.ansicht(ox, oy3 - 22, "SCHILD — Aufteilung der Fläche")
    Ks2 = 2.6
    sb, sh = M["schild_b"] * Ks2, M["schild_h"] * Ks2
    rand = 4 * Ks2
    text_h = M["schild_h"] * 0.30 * Ks2
    sym_h = sh - text_h - 2 * rand
    b.rect(ox, oy3, sb, sh, "#f0d9c8", MASSL, 1.4)
    # Symbolfeld oben, quadratisch und fuer alle Sorten gleich
    sf = min(M["schild_h"] * 0.70 - 8, M["schild_b"] - 8) * 0.94 * Ks2
    b.rect(ox + sb / 2 - sf / 2, oy3 + rand + sym_h / 2 - sf / 2, sf, sf,
           "none", LINIE, 1.0, "5 3")
    b.txt(ox + sb / 2, oy3 + rand + sym_h / 2 + 4, "SYMBOL",
          11, "middle", GRAU, "700")
    # Namenszeile darunter
    b.rect(ox + rand, oy3 + rand + sym_h, sb - 2 * rand, text_h,
           "none", LINIE, 1.0, "5 3")
    b.txt(ox + sb / 2, oy3 + rand + sym_h + text_h / 2 + 4, "NAME",
          11, "middle", GRAU, "700")

    b.mh(ox, ox + sb, oy3 + sh + 40, f'{M["schild_b"]:.0f}', "Schildbreite",
         von=oy3 + sh)
    b.mv(oy3, oy3 + sh, ox - 34, f'{M["schild_h"]:.0f}', "Schildhöhe", von=ox)
    b.mv(oy3 + rand + sym_h, oy3 + rand + sym_h + text_h, ox + sb + 40,
         f'{M["schild_h"] * 0.30:.0f}', "Namenszeile", von=ox + sb)
    b.mv(oy3 + rand + sym_h / 2 - sf / 2,
         oy3 + rand + sym_h / 2 + sf / 2, ox + sb + 100,
         f'{min(M["schild_h"] * 0.70 - 8, M["schild_b"] - 8) * 0.94:.0f}',
         "Symbolfeld", von=ox + sb)
    b.txt(ox, oy3 + sh + 78, "Symbolfeld und Schriftgröße sind bei jeder Sorte "
          "gleich — die Zeichnungen werden auf dasselbe Feld skaliert,",
          10.5, "start")
    b.txt(ox, oy3 + sh + 96, "die Schrift richtet sich nach dem längsten Namen "
          "(KANINCHEN). So wirken die Tafeln nebeneinander einheitlich.",
          10.5, "start", GRAU)
    b.txt(ox, oy3 + sh + 118, "Platte orange, Symbol und Name 0,6 mm vertieft — "
          "wer zwei Farben hat, druckt den Schriftkörper schwarz dazu.",
          10.5, "start", GRAU)

    # Achse
    ox4 = ox + 520
    b.ansicht(ox4, oy3 - 22, "ACHSE — Zukaufteil")
    b.rect(ox4, oy3 + 12, 210, M["achse"] * Ks, "#d8d3cb")
    b.mh(ox4, ox4 + 210, oy3 + 58, "ca. 90", "Länge, bündig kürzen", von=oy3 + 12 + M["achse"] * Ks)
    b.txt(ox4, oy3 + 88, "Rundstab 3 mm: Stahldraht, Messing", 10.5, "start")
    b.txt(ox4, oy3 + 106, "oder ein Stück 3-mm-Filament", 10.5, "start", GRAU)

    b.legende(ox + 810, oy3 - 22, [
        (1, "Kammer nimmt die Federrolle auf", "17,6 breit"),
        (2, "Achsbohrung durch beide Wangen", "3,2"),
        (3, "Austritt des Federbands nach vorne", "16,8 x 3"),
        (4, "Grifflasche zum Zurückziehen", "32 breit"),
    ], spalten=1)

    b.titel("Schieber, Schild und Achse", "Der Schieber trägt die Feder, das Schild "
            "sitzt in der Frontwand", "TEIL 04 / 05 / 06")
    return b.save("03-schieber-schild.svg")



warnungen = []
for f, k in (blatt1(), blatt2(), blatt3()):
    print("  " + f)
    warnungen += k
if warnungen:
    print("\nUEBERLAPPUNGEN:")
    for w in warnungen:
        print("  ! " + w)
else:
    print("\nkeine Ueberlappungen")
