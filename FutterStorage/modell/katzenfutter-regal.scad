// =====================================================================
//  Katzenfutter-Beutel Regalsystem
//
//  Prinzip: waagerechte Kanäle über die volle Schranktiefe. Die Beutel
//  stehen hochkant hintereinander, ein Schieber drückt sie nach vorne.
//  Entnommen wird NACH VORNE: der Beutel ragt 30 mm über die Frontwand
//  hinaus, wird dort und durch die Griffmulde gefasst und nach vorne
//  herausgezogen. Die Frontwand ist 70 mm hoch - hoch genug, dass der
//  Schiebedruck den vordersten Beutel nicht darüber hinauskippt.
//
//  Weil beim Herausziehen nichts nach oben muss, brauchen die Ebenen
//  keinen Greifraum und lassen sich direkt stapeln: kein Sockel,
//  kein Hohlraum darunter.
//
//  Koordinaten: X = Breite, Y = Tiefe (nach hinten), Z = Höhe.
//               Y = 0 ist vorne, dort wird entnommen.
//  Alle Maße in mm.
// =====================================================================

/* [Was soll gerendert werden] */
TEIL = "segment";  // [segment, verbinder, test]

// front = vorderstes Segment mit Anschlagkante und Schildhalter
// mitte = beidseitig offenes Zwischenstück, beliebig oft
// end   = hinterstes Segment mit Rückwand und Bandhaken
segment_typ = "front";  // [front, mitte, end]

/* [Beutel-Maße] */
// Gemessen an einem echten 85-g-Beutel, ungequetscht.
// Höhe des aufrecht stehenden Beutels
beutel_hoch = 136;
// Breite des Beutels -> bestimmt die Kanalbreite
beutel_breit = 88;
// Dicke eines Beutels. Sie lassen sich leicht zusammendrücken, im Stapel
// rechnen wir deshalb mit etwas weniger als dem Maximalmaß von 20 mm.
beutel_dicke = 19;
// Luft in der Breite
spiel = 4;
// Luft über dem Beutel
luft_oben = 28;

/* [Kanal] */
// Länge eines Segments. 160 mm passt auf ein 180er Druckbett.
segment_laenge = 160;
// Wie viele Segmente bilden einen Kanal (nur für Layout und Kapazität)
segment_anzahl = 3;
// Höhe der Frontwand. Muss über dem Angriffspunkt des Schiebedrucks
// liegen (halbe Beutelhöhe), sonst kippt der vorderste Beutel darüber
// hinaus. 70 mm gibt Sicherheit und lässt den Beutel 30 mm herausragen.
anschlag_hoehe = 92;
// Griffmulde in der Frontwand: dort greift man den Beutel
mulde_breite = 58;
// bis auf welche Höhe die Mulde herunterreicht
mulde_bis = 66;

/* [Schrank] */
// Nutzbare Breite: 545 mm abzüglich Scharnier, sicherheitshalber 540
schrank_breite = 540;
schrank_tiefe = 500;
// Höhe ohne Regalboden. Mit Boden wären es 220 mm unten bzw. 280 mm im Fach
// darüber - dann passt nur eine Ebene.
schrank_hoehe = 520;
// nur für die layout-Vorschau
spalten = 5;
ebenen = 3;

/* [Wandstärken] */
wand = 1.6;
boden = 2.4;

/* [Material sparen] */
fenster = true;

/* [Verbindungen] */
// Die Ebenen stehen aufeinander, die Spalten nebeneinander. Beides wird
// gesteckt, sonst verschiebt sich der Verbund beim Herausziehen eines
// Beutels. Beide Verbindungen sind reine Materialfortsetzungen und
// drucken ohne Stützen.
//
// Oben: die Seitenwände laufen als Zapfen weiter, unten im Boden sitzen
// die passenden Taschen. Der Zapfen ist so breit wie die Wand, schwächt
// sie also nicht.
stapel_zapfen = true;
zapfen_h = 2.6;        // wie weit der Zapfen übersteht
zapfen_l = 22;         // Länge eines Zapfens
zapfen_rand = 16;      // Abstand vom Segmentende
// Seitlich: eine Nase am Bodenrand greift in die Tasche des Nachbarn.
// Sie liegt unterhalb des Innenraums und nimmt dem Beutel keinen Platz.
seiten_nase = true;
nase_t = 3.0;          // wie weit sie herausragt
nase_l = 20;           // Länge
nase_h = 3.2;          // Höhe ab Unterkante
// Rastung des seitlichen Verbinders: eine flache Noppe hält die Spalten
// zusammen. Ohne sie würde die Reibung allein nicht reichen - mit ihr
// rastet es spürbar ein und lässt sich mit etwas Zug wieder trennen.
// Die Stapelzapfen brauchen keine Rastung: dort hält das Eigengewicht,
// und eine Noppe an der Wandflanke stünde seitlich über.
rastung = true;
rast_d = 2.6;          // Durchmesser der Noppe
rast_h = 0.45;         // wie weit sie vorsteht

/* [FDM-Toleranzen] */
// Spiel je Flanke bei Steckverbindungen. Mit einem Toleranztest von
// MakerWorld ermitteln. 0.15 = stramm, 0.20 = Standard, 0.25 = leichtgängig.
passung = 0.2;

/* [Hidden] */
$fn = 32;

// ---------------------------------------------------------------------
//  Abgeleitete Maße
// ---------------------------------------------------------------------
innen_x  = beutel_breit + spiel;
innen_z  = beutel_hoch + luft_oben;
aussen_x = innen_x + 2 * wand;
// Bodenverdickung dort, wo die Bandnut liegt
boden_dick = boden;
aussen_z = boden_dick + innen_z;

ist_front = segment_typ == "front";
ist_end   = segment_typ == "end";

// Bauteillänge: Stirnwand nur dort, wo das Segment endet
aussen_y = segment_laenge + (ist_front ? anschlag_dicke() : 0)
                          + (ist_end ? wand : 0);
function anschlag_dicke() = 3.0;

kanal_laenge = segment_anzahl * segment_laenge;
kapazitaet   = floor(kanal_laenge / beutel_dicke);

// Bodenzunge: überlappt die Fuge zum Nachbarsegment, damit die Beutel
// nicht an einer Stufe hängenbleiben
zunge_l = 9;
zunge_h = 1.2;

echo(str(">>> Segment ", segment_typ, ": ", aussen_x, " x ", aussen_y,
         " x ", aussen_z, " mm"));
echo(str(">>> Ebenenhöhe ", aussen_z, " mm  ->  ",
         floor(schrank_hoehe / aussen_z), " Ebenen in ", schrank_hoehe, " mm"));
echo(str(">>> Spaltenbreite ", aussen_x, " mm  ->  ",
         floor(schrank_breite / aussen_x), " Spalten in ", schrank_breite, " mm"));
echo(str(">>> Kanal aus ", segment_anzahl, " Segmenten = ", kanal_laenge,
         " mm = ", kapazitaet, " Beutel"));
echo(str(">>> Ausbau ", spalten, " x ", ebenen, " = ", spalten * ebenen,
         " Sorten, ", spalten * ebenen * kapazitaet, " Beutel"));

// ---------------------------------------------------------------------
//  Hilfsmodule
// ---------------------------------------------------------------------

// Loch mit verrundeten Ecken in einer Wand mit Normale X
module fenster_yz(b, h, r, t) {
    hull()
        for (yp = [r, b - r], zp = [r, h - r])
            translate([0, yp, zp]) rotate([0, 90, 0]) cylinder(r = r, h = t);
}

// Loch mit verrundeten Ecken in einer Wand mit Normale Y
module fenster_xz(b, h, r, t) {
    hull()
        for (xp = [r, b - r], zp = [r, h - r])
            translate([xp, 0, zp]) rotate([-90, 0, 0]) cylinder(r = r, h = t);
}

// Langloch senkrecht durch den Boden
module langloch(b, l, r, h) {
    hull()
        for (px = [r, b - r], py = [r, l - r])
            translate([px, py, 0]) cylinder(r = r, h = h);
}

// ---------------------------------------------------------------------
//  Verbindungen zwischen den Segmenten
// ---------------------------------------------------------------------
// Wo die Stapelzapfen sitzen - zwei je Seitenwand, an beiden Enden.
// Die Taschen der darüberliegenden Ebene benutzen dieselbe Liste,
// deshalb passt jede Ebene auf jede andere.
function zapfen_y() = [zapfen_rand, aussen_y - zapfen_rand - zapfen_l];

// Ein Zapfen: Fortsetzung der Seitenwand nach oben, oben angefast,
// damit er sich beim Aufsetzen von selbst fängt.
module zapfen(x0, y0) {
    // Die Fase darf hoechstens ein Viertel der Wandstaerke betragen - bei
    // wand/2 wuerde der obere Querschnitt zu null und der Zapfen verschwaende
    // spurlos aus dem Koerper.
    fase = min(0.5, wand / 4);
    union() {
        hull() {
            translate([x0, y0, aussen_z]) cube([wand, zapfen_l, 0.01]);
            translate([x0 + fase, y0 + fase, aussen_z + zapfen_h])
                cube([wand - 2 * fase, zapfen_l - 2 * fase, 0.01]);
        }
    }
}

// Die Tasche dazu, von unten in den Boden geschnitten. Sie ist ringsum
// um die Passung größer und reicht 0,3 mm tiefer als der Zapfen hoch ist,
// damit die Ebenen auf den Wänden aufliegen und nicht auf den Zapfen.
module zapfentasche(x0, y0) {
    union() {
        translate([x0 - passung, y0 - passung, -1])
            cube([wand + 2 * passung, zapfen_l + 2 * passung, zapfen_h + 1.3]);
    }
}

// Seitliche Verbindung: beide Bodenränder bekommen dieselbe Tasche, das
// verbindende Plättchen liegt lose dazwischen. Eine angeformte Nase stünde
// an der äußersten Spalte ins Leere - so bleibt jede Außenkante bündig,
// und alle Segmente sind gleich.
module nasentasche(y0, links = true) {
    x0 = links ? -1 : aussen_x - nase_t - passung;
    union() {
        translate([x0, y0 - passung, -1])
            cube([nase_t + 1 + passung, nase_l + 2 * passung, nase_h + 1 + passung]);
        // Mulde für die Rastnoppe des Verbinders
        if (rastung)
            translate([links ? nase_t / 2 : aussen_x - nase_t / 2,
                       y0 + nase_l / 2, nase_h + passung])
                rast_form(rast_d + 2 * passung, rast_h + 0.15);
    }
}

// Die Rastform: ein flacher Kegelstumpf. Beim Zusammenschieben drückt die
// schräge Flanke den Verbinder kurz herunter, in der Mulde federt er zurück.
// Sie hält den Verbund zusammen, lässt sich aber mit etwas Zug wieder lösen.
module rast_form(d, h) {
    cylinder(d1 = d, d2 = d * 0.55, h = h);
}

// Das Plättchen selbst: greift je zur Hälfte in zwei benachbarte Spalten.
// An den Enden angefast, damit es sich einfädeln lässt.
module verbinder() {
    b = 2 * nase_t;
    union() {
        hull() {
            translate([0.7, 0, 0]) cube([b - 1.4, nase_l, 0.01]);
            translate([0, 0, 0.7]) cube([b, nase_l, nase_h - 1.4]);
            translate([0.7, 0, nase_h - 0.01]) cube([b - 1.4, nase_l, 0.01]);
        }
        // je Hälfte eine Noppe - eine allein könnte sich herausdrehen
        if (rastung)
            for (sx = [nase_t / 2, 1.5 * nase_t])
                translate([sx, nase_l / 2, nase_h - 0.01])
                    rast_form(rast_d, rast_h);
    }
}

// ---------------------------------------------------------------------
//  Kanalsegment
// ---------------------------------------------------------------------
module segment() {
    y0 = ist_front ? anschlag_dicke() : 0;   // Innenraum beginnt dahinter
    y1 = aussen_y - (ist_end ? wand : 0);    // und endet davor

    difference() {
        union() {
            // --- Grundkörper ---
            cube([aussen_x, aussen_y, aussen_z]);

            // --- Bodenzunge hinten: schiebt sich unter das Nachbarsegment ---
            if (!ist_end)
                translate([wand + 0.3, aussen_y, boden_dick - zunge_h])
                    cube([innen_x - 0.6, zunge_l, zunge_h]);

            // --- Zapfen für die Ebene darüber ---
            if (stapel_zapfen)
                for (yz = zapfen_y())
                    for (xz = [0, aussen_x - wand])
                        zapfen(xz, yz);


        }

        // --- Innenraum ---
        translate([wand, y0, boden_dick])
            cube([innen_x, y1 - y0 + (ist_end ? 0 : zunge_l + 1), innen_z + 1]);

        // --- Front: oberhalb der Wand offen, plus Griffmulde in der Mitte ---
        if (ist_front) {
            translate([wand, -1, boden_dick + anschlag_hoehe])
                cube([innen_x, anschlag_dicke() + 1, innen_z + 1]);
            // Mulde mit 45-Grad-Auslauf unten, damit sie stützenfrei druckt
            cx = aussen_x / 2;
            zt = boden_dick + mulde_bis;
            fa = 11;
            translate([0, anschlag_dicke() + 1, 0])
                rotate([90, 0, 0])
                    linear_extrude(height = anschlag_dicke() + 2)
                        polygon([
                            [cx - mulde_breite/2, boden_dick + anschlag_hoehe + 1],
                            [cx + mulde_breite/2, boden_dick + anschlag_hoehe + 1],
                            [cx + mulde_breite/2, zt + fa],
                            [cx + mulde_breite/2 - fa, zt],
                            [cx - mulde_breite/2 + fa, zt],
                            [cx - mulde_breite/2, zt + fa]
                        ]);
        }

        // --- Aufnahme für die Zunge des vorderen Nachbarn ---
        if (!ist_front)
            translate([wand, -1, boden_dick - zunge_h - passung])
                cube([innen_x, zunge_l + 1, zunge_h + passung]);

        // --- Fenster in den Seitenwänden ---
        if (fenster) {
            f_von = y0 + 14;
            f_bis = y1 - 14;
            f_b = f_bis - f_von;
            if (f_b > 30)
                for (xp = [-1, aussen_x - wand - 1])
                    translate([xp, f_von, boden_dick + 14])
                        fenster_yz(f_b, innen_z - 26, 7, wand + 2);
        }

        // --- Taschen für die Zapfen der Ebene darunter ---
        if (stapel_zapfen)
            for (yz = zapfen_y())
                for (xz = [0, aussen_x - wand])
                    zapfentasche(xz, yz);

        // --- Taschen für die seitlichen Verbinder, beide Seiten gleich ---
        if (seiten_nase)
            for (yn = zapfen_y()) {
                nasentasche(yn + (zapfen_l - nase_l) / 2, true);
                nasentasche(yn + (zapfen_l - nase_l) / 2, false);
            }

        // --- Sichtschlitz in der Rückwand ---
        if (ist_end)
            translate([(aussen_x - (innen_x - 24)) / 2, aussen_y - wand - 1,
                       boden_dick + 16])
                fenster_xz(innen_x - 24, innen_z - 34, 6, wand + 2);
    }

}

// ---------------------------------------------------------------------
//  Ausgabe
// ---------------------------------------------------------------------
if (TEIL == "segment")       segment();
else if (TEIL == "verbinder") verbinder();
else if (TEIL == "test")
    // Ebene darüber darf sich nicht mit dieser durchdringen
    intersection() {
        segment();
        translate([0, 0, aussen_z]) segment();
    }
else if (TEIL == "test_seite")
    // Spalte daneben ebenso: die Nase muss in die Tasche passen, ohne
    // dass sich die Körper überschneiden
    intersection() {
        segment();
        translate([aussen_x, 0, 0]) segment();
    }
else if (TEIL == "test_diagonal")
    // Der Nachbar schräg darüber: hier treffen Stapelzapfen und Seitennase
    // gleichzeitig aufeinander. Wenn eine der beiden Verbindungen zu weit
    // ausgreift, fällt es nur in dieser Paarung auf.
    intersection() {
        segment();
        translate([aussen_x, 0, aussen_z]) segment();
    }
else if (TEIL == "verbund")
    // Vier Segmente als 2x2-Feld - so steht das Regal später wirklich.
    // Sichtprüfung im Vorschaufenster.
    for (sx = [0, aussen_x], sz = [0, aussen_z])
        translate([sx, 0, sz]) segment();
