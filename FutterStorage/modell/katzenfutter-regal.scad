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
TEIL = "segment";  // [segment]

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
