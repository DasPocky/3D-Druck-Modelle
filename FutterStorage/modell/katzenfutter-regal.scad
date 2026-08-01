// =====================================================================
//  Katzenfutter-Beutel Regalsystem
//
//  Prinzip: waagerechte Kanäle über die volle Schranktiefe. Die Beutel
//  stehen hochkant hintereinander, ein Schieber drückt sie nach vorne.
//
//  Entnommen wird NACH VORNE: der Beutel ragt 44 mm über die Frontwand
//  hinaus. Gefasst wird er an seiner OBERKANTE - dort greifen Daumen und
//  Zeigefinger zu und ziehen ihn nach vorne heraus. Der Platz dafür ist
//  der Greifraum über dem Beutel (luft_oben), nicht die Frontwand: vorne
//  ist der Kanal oberhalb der Wand ohnehin offen.
//
//  Deshalb hat die Frontwand auch keine Griffmulde. Sie säße dort, wo die
//  Hand gar nicht hinfasst, und nähme nur dem Schild Platz weg.
//
//  Die Frontwand ist 92 mm hoch - hoch genug, dass der Schiebedruck den
//  vordersten Beutel nicht darüber hinauskippt (Angriffspunkt bei halber
//  Beutelhöhe, also 68 mm).
//
//  Koordinaten: X = Breite, Y = Tiefe (nach hinten), Z = Höhe.
//               Y = 0 ist vorne, dort wird entnommen.
//  Alle Maße in mm.
// =====================================================================

/* [Was soll gerendert werden] */
// segment = Kanalsegment (Typ über segment_typ), schieber, schild,
// trommel = Wickeltrommel für die Feder, probe = Passprobe,
// layout = Vorschau im Schrank, schnitt = Längsschnitt,
// test = Kollisionsprüfung gestapelter Ebenen (Ergebnis muss leer sein)
TEIL = "segment";  // [segment, schieber, schild, schild_text, verbinder, trommel, probe, layout, schnitt, test]

// Ein Segment sitzt an drei Stellen zugleich - in der Tiefe, in der Höhe
// und in der Breite. Jede Achse hat ihren eigenen Typ, weil an jedem Rand
// des Verbunds etwas weggelassen wird, das im Inneren gebraucht wird.

// Tiefe (Y): front = vorderstes Segment mit Anschlagkante und Schildhalter
//            mitte = beidseitig offenes Zwischenstück, beliebig oft
//            end   = hinterstes Segment mit Rückwand und Bandhaken
segment_typ = "front";  // [front, mitte, end]

// Höhe (Z): oben  = oberste Ebene, ohne Stapelzapfen - sonst stünden
//                   Zapfen frei nach oben ab
//           unten = unterste Ebene, ohne Zapfentaschen im Boden - dort
//                   kommt nichts mehr darunter
//           mitte = beides, Zapfen oben und Taschen unten
ebene_typ = "mitte";  // [unten, mitte, oben]

// Breite (X): links  = linke Randspalte, ohne Verbindertasche nach links
//             rechts = rechte Randspalte, ohne Tasche nach rechts
//             mitte  = beide Taschen, verbindet nach beiden Seiten
spalte_typ = "mitte";  // [links, mitte, rechts]

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
// Luft über dem Beutel. Das ist der Greifraum: Entnommen wird, indem man
// den Beutel an seiner Oberkante fasst und nach vorne herauszieht. Dafür
// müssen zwei Finger neben die Beutelkante passen - unter 40 mm wird das
// zur Fummelei. 42 mm ergibt eine Ebenenhöhe von 182,8 mm; drei Ebenen
// brauchen damit 548,4 mm Fachhöhe.
luft_oben = 42;

/* [Kanal] */
// Länge eines Segments. 160 mm passt auf ein 180er Druckbett.
segment_laenge = 160;
// Wie viele Segmente bilden einen Kanal (nur für Layout und Kapazität)
segment_anzahl = 3;
// Höhe der Frontwand. Muss über dem Angriffspunkt des Schiebedrucks
// liegen (halbe Beutelhöhe = 68 mm), sonst kippt der vorderste Beutel
// darüber hinaus. 92 mm gibt Sicherheit und lässt den Beutel 44 mm
// herausragen. Eine Griffmulde hat die Wand nicht - gegriffen wird oben
// an der Beutelkante, siehe luft_oben.
anschlag_hoehe = 92;

/* [Schrank] */
// Nutzbare Breite: 545 mm abzüglich Scharnier, sicherheitshalber 540
schrank_breite = 540;
schrank_tiefe = 500;
// Fachhöhe von der Standfläche bis zur Unterkante dessen, was darüber kommt.
// Der Regalboden wird dafür höher gesetzt: 550 mm reichen für drei Ebenen
// à 182,8 mm (548,4 mm) und lassen jeder Ebene 42 mm Greifraum über dem
// Beutel. Mit den ursprünglichen 520 mm blieben nur 28 mm - zu wenig, um
// den Beutel oben zu fassen.
schrank_hoehe = 550;
// nur für die layout-Vorschau
spalten = 5;
ebenen = 3;

/* [Wandstärken] */
wand = 1.6;
boden = 2.4;

/* [Material sparen] */
fenster = true;
boden_offen = true;

/* [Konstantkraftfeder] */
// Der Schieber legt bis zu 480 mm zurück. Ein Gummiband kann das nicht:
// es müsste vorne schon gespannt sein und wäre hinten um über 1500 %
// gedehnt. Deshalb eine Konstantkraftfeder - ein aufgerolltes Stahlband,
// das über den ganzen Weg gleich stark zieht. Die Rolle sitzt im Schieber,
// das Bandende hängt vorne im Haken des Frontsegments.
bandnut = true;
// Nut im Boden, in der das Federband läuft
bandnut_breite = 15;   // Band + 2 mm Luft
bandnut_tiefe = 1.6;

// ---------------------------------------------------------------------
//  Federauswahl - die Kraft ergibt sich aus dem Beutelgewicht
// ---------------------------------------------------------------------
// Die Feder schiebt gegen die Reibung des ganzen Stapels. Nach unten ist
// sie also durch den vollen Kanal begrenzt, nach oben durch den Beutel
// selbst: die volle Federkraft liegt IMMER auf dem vordersten, egal wie
// viele dahinterstehen. Zu viel Kraft drückt ihn flach, er weicht seitlich
// aus und klemmt - im 92er Kanal hat ein 88er Beutel nur 4 mm Spiel.
//
//   Gewicht im vollen Kanal   25 × 85 g = 2,125 kg = 20,9 N
//   Reibbeiwert Folie auf PLA 0,3 bis 0,4 (gemessen wird das erst am Teil)
//   -> nötig                  6,3 bis 8,3 N
//   -> Obergrenze             rund 12 N, darüber verformt der Beutel merklich
//
// Gewählt: CF025-0198 mit 8,8 N. Sie deckt den ungünstigen Reibungsfall ab
// und bleibt deutlich unter der Quetschgrenze. Die zuvor eingetragene
// CF030-0237 hatte 10,5 N - unnötig viel, und ihr 15-mm-Band verlangte eine
// breitere Nut und eine größere Trommel.
//
// Andere Feder? Nur diese drei Zeilen ändern, alles Weitere rechnet sich
// daraus. Passend ist, was 8 bis 12 N liefert und mindestens 480 mm auszieht.
feder_kraft   = 8.8;   // N, konstant über den Weg
feder_band_b  = 12.7;  // Bandbreite
feder_auszug  = 557;   // Lmax laut Datenblatt - darüber reißt die Feder
feder_rolle_d = 15.5;  // Außendurchmesser der aufgerollten Feder

feder_achse_d = 3.2;   // Bohrung für die Achse: 3-mm-Rundstab, Spielpassung

// Die Feder wickelt NICHT auf der 3-mm-Achse: ihr natürlicher
// Innendurchmesser liegt bei 11-17 mm. Der Hersteller verlangt eine
// Trommel 10-20 % über diesem Maß. Zu klein heißt höhere Biegespannung
// und kürzere Lebensdauer. Die Trommel wird mitgedruckt (TEIL="trommel")
// und läuft frei auf der Achse.
trommel_d = 14.5;      // Wickeldurchmesser, 10-20 % über dem Innen-Ø
trommel_b = 14.7;      // Wickelbreite = Band + 2 mm Luft.
                       // Fester Wert, keine Formel: die Werkzeuge
                       // lesen aus dieser Datei nur Zahlen aus.
trommel_spiel = 0.25;  // Luft auf der Achse, damit sie frei dreht

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

/* [Beschriftung] */
schild_text = "HUHN";
// Symbol über dem Text: huhn, rind, lachs, kaninchen, ente, truthahn,
// lamm, thunfisch, wild, gefluegel, leer
schild_symbol = "huhn";
schild_breite = 78;
schild_hoehe = 62;
// Breitester vorkommender Sortenname. Danach richtet sich die Schriftgröße
// ALLER Schilder, damit sie einheitlich aussehen. Nicht die Zeichenzahl
// zählt, sondern die tatsächliche Breite - gemessen bei Größe 10:
// KANINCHEN 83,3 mm, GEFLÜGEL 75,6 mm, TRUTHAHN 77,1 mm.
schild_ref_name = "KANINCHEN";
schild_dicke = 1.5;
// Randabstand rings um Symbol und Schrift - überall gleich
schild_rand = 5;
// Höhe der Textzeile am unteren Rand
schild_text_h = 13;
// Luft zwischen Schrift und Symbol
schild_steg = 3;

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
boden_dick = bandnut ? boden + bandnut_tiefe + 0.8 : boden;
aussen_z = boden_dick + innen_z;

ist_front = segment_typ == "front";
ist_end   = segment_typ == "end";

// Was an welchem Rand des Verbunds wegfällt. Im Inneren ist alles da;
// nach außen hin bleibt weg, was ins Leere greifen würde.
hat_zapfen   = stapel_zapfen && ebene_typ != "oben";    // Zapfen nach oben
hat_taschen  = stapel_zapfen && ebene_typ != "unten";   // Taschen im Boden
nase_links   = seiten_nase && spalte_typ != "links";    // Tasche nach links
nase_rechts  = seiten_nase && spalte_typ != "rechts";   // Tasche nach rechts

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
// Prüft die Federwahl gegen das, was der volle Kanal verlangt. Der
// Reibbeiwert 0,4 ist der ungünstige Fall; gemessen wird er erst am Teil.
feder_noetig = 0.40 * kapazitaet * 0.085 * 9.81;
echo(str(">>> Feder: ", feder_kraft, " N vorhanden, ", feder_noetig,
         " N nötig (", kapazitaet, " Beutel, Reibbeiwert 0,4)"));
echo(str(">>> Federweg: ", feder_auszug, " mm Auszug, ",
         kanal_laenge - 10, " mm gebraucht"));

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
    // Die Fase darf höchstens ein Viertel der Wandstärke betragen - bei
    // wand/2 würde der obere Querschnitt zu null und der Zapfen verschwände
    // spurlos aus dem Körper.
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
            // In der obersten Ebene weggelassen: dort stünden sie frei ab.
            if (hat_zapfen)
                for (yz = zapfen_y())
                    for (xz = [0, aussen_x - wand])
                        zapfen(xz, yz);


        }

        // --- Innenraum ---
        translate([wand, y0, boden_dick])
            cube([innen_x, y1 - y0 + (ist_end ? 0 : zunge_l + 1), innen_z + 1]);

        // --- Front: oberhalb der Anschlagwand ist der Kanal offen ---
        // Hier greift die Hand an die Beutelkante. Keine Mulde in der Wand:
        // gefasst wird oben, nicht durch die Wand hindurch.
        if (ist_front)
            translate([wand, -1, boden_dick + anschlag_hoehe])
                cube([innen_x, anschlag_dicke() + 1, innen_z + 1]);

        // --- Aufnahme für die Zunge des vorderen Nachbarn ---
        if (!ist_front)
            translate([wand, -1, boden_dick - zunge_h - passung])
                cube([innen_x, zunge_l + 1, zunge_h + passung]);

        // --- Bandnut im Boden ---
        if (bandnut)
            translate([(aussen_x - bandnut_breite) / 2, -1,
                       boden_dick - bandnut_tiefe])
                cube([bandnut_breite, aussen_y + 2, bandnut_tiefe + 1]);

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

        // --- Langlöcher im Boden, beidseits der Bandnut ---
        if (boden_offen) {
            lb = (innen_x - bandnut_breite) / 2 - 9;
            ll = (y1 - y0) - 26;
            if (lb > 8 && ll > 20)
                for (sx = [wand + 5,
                           aussen_x - wand - 5 - lb])
                    translate([sx, y0 + 13, -1])
                        langloch(lb, ll, 5, boden_dick + 2);
        }

        // --- Taschen für die Zapfen der Ebene darunter ---
        // In der untersten Ebene weggelassen: dort kommt nichts mehr drunter.
        if (hat_taschen)
            for (yz = zapfen_y())
                for (xz = [0, aussen_x - wand])
                    zapfentasche(xz, yz);

        // --- Taschen für die seitlichen Verbinder ---
        // An den Randspalten fällt die äußere Tasche weg: dort steht kein
        // Nachbar, und eine offene Tasche an der Außenkante fängt nur Staub.
        for (yn = zapfen_y()) {
            if (nase_links)  nasentasche(yn + (zapfen_l - nase_l) / 2, true);
            if (nase_rechts) nasentasche(yn + (zapfen_l - nase_l) / 2, false);
        }

        // --- Sichtschlitz in der Rückwand ---
        if (ist_end)
            translate([(aussen_x - (innen_x - 24)) / 2, aussen_y - wand - 1,
                       boden_dick + 16])
                fenster_xz(innen_x - 24, innen_z - 34, 6, wand + 2);
    }

    // --- Schildhalter an der Frontwand ---
    if (ist_front) schildhalter();

    // --- Haken für das Gummiband, quer durch die Bodennut ---
    if (ist_front && bandnut)
        translate([(aussen_x - bandnut_breite) / 2 - 1.5,
                   anschlag_dicke() + 7, boden_dick - bandnut_tiefe])
            difference() {
                cube([bandnut_breite + 3, 4, bandnut_tiefe + 3.5]);
                translate([1.5, -1, -1])
                    cube([bandnut_breite, 6, bandnut_tiefe + 1]);
            }
}

// Tasche vor der Anschlagkante, Schild wird von oben eingeschoben
// Der Rahmen überdeckt den Schildrand ringsum um dieses Maß. Er ist Teil
// des Segments und deshalb in dessen Farbe - so verschwindet die Kante der
// farbigen Tafel und man sieht nicht, wo sie eingeschoben wird.
schild_ueberdeckung = 4;

// Wo das Schild in der Tasche steht und was davon zu sehen ist. Das
// Layout auf dem Schild richtet sich nach dem SICHTBAREN Ausschnitt,
// nicht nach der Plattenkante - sonst sitzt das Symbol optisch zu hoch.
schild_z0 = 4;         // Unterkante der Tafel in der Tasche.
                       // Variable, nicht Funktion: rendern.py liest sie aus.
function schild_sicht_u() = schild_ueberdeckung;         // ab hier sichtbar
function schild_sicht_o() = schild_hoehe - schild_ueberdeckung;
function schild_sicht_h() = schild_sicht_o() - schild_sicht_u();

module schildhalter() {
    sp = schild_dicke + 0.4;
    rb = 1.2;
    b  = schild_breite + 3.2;
    x0 = (aussen_x - b) / 2;
    // nur so hoch wie das Schild plus etwas Einführung, sonst bleibt
    // über der Tafel ein leerer Rahmen stehen
    h  = min(anschlag_hoehe - 2, schild_hoehe + 3);
    u  = schild_ueberdeckung;
    difference() {
        // taucht 0,6 mm in die Anschlagkante ein
        translate([x0, -(sp + rb), 3]) cube([b, sp + rb + 0.6, h]);
        // Spalt für das Schild, nach oben offen
        translate([x0 + 1.6, -sp, 4]) cube([b - 3.2, sp, h]);
        // Sichtfenster: ringsum um die Überdeckung kleiner als die Tafel
        translate([x0 + (b - schild_breite) / 2 + u,
                   -(sp + rb) - 1, schild_z0 + u])
            fenster_xz(schild_breite - 2 * u, schild_hoehe - 2 * u,
                       2.5, rb + 2);
    }
}

// ---------------------------------------------------------------------
//  Wickeltrommel für die Konstantkraftfeder
//
//  Die Feder darf nicht auf der 3-mm-Achse aufwickeln - ihr natürlicher
//  Innendurchmesser ist um ein Vielfaches größer, und ein zu enger Wickel
//  erhöht die Biegespannung im Band. Diese Trommel bringt sie auf das vom
//  Hersteller verlangte Maß und läuft frei auf der Achse.
//
//  Liegend drucken (Achse senkrecht): dann ist die Bohrung rund und es
//  braucht keine Stützen.
// ---------------------------------------------------------------------
function trommel_bord_d() = trommel_d + 3.0;   // Bordscheiben-Durchmesser
function trommel_bord_b() = 1.2;               // Dicke einer Bordscheibe
function trommel_ganz_b() = trommel_b + 2 * trommel_bord_b();

module trommel() {
    bohrung = 3.0 + 2 * trommel_spiel;
    difference() {
        union() {
            // Wickelkörper
            translate([0, 0, trommel_bord_b()])
                cylinder(d = trommel_d, h = trommel_b);
            // Bordscheiben, damit das Band nicht seitlich von der Rolle läuft
            for (zp = [0, trommel_bord_b() + trommel_b])
                translate([0, 0, zp])
                    cylinder(d = trommel_bord_d(), h = trommel_bord_b());
        }
        // Achsbohrung, durchgehend
        translate([0, 0, -1])
            cylinder(d = bohrung, h = trommel_ganz_b() + 2);
        // Fase an beiden Enden, damit sie sich auf die Achse fädeln lässt
        for (zp = [0, trommel_ganz_b()])
            translate([0, 0, zp])
                rotate([zp > 0 ? 0 : 180, 0, 0])
                    cylinder(d1 = bohrung + 1.2, d2 = bohrung, h = 0.6);
    }
}

// ---------------------------------------------------------------------
//  Schieber
//
//  Drückt die Beutel nach vorne. Im Fuß sitzt die Federtrommel auf einer
//  3-mm-Achse; das Band läuft unten nach vorne in die Bodennut. Die
//  Grifflasche erlaubt zusätzlich das Nachschieben von Hand.
// ---------------------------------------------------------------------
module schieber() {
    b   = innen_x - 1.2;
    h   = beutel_hoch - 8;
    d   = 2.6;
    fu  = 36;                         // Fußlänge, nimmt die Federrolle auf
    kb  = trommel_ganz_b() + 1.2;     // lichte Breite der Federkammer
    kx  = (b - kb) / 2;               // Kammer mittig
    // Achse so hoch, dass Trommel und aufgewickelte Feder frei laufen
    rmax = max(feder_rolle_d, trommel_bord_d()) / 2;
    ax  = rmax + 4;                   // Achshöhe über dem Boden
    ay  = 4 + rmax;                   // Achsposition in der Tiefe

    difference() {
        union() {
            // Stützfläche für die Beutel
            cube([b, d, h]);
            // Fuß nach hinten gegen das Kippen
            cube([b, fu, 3.0]);
            // Gleitkufen, damit nur wenig Fläche schleift
            for (xp = [2.5, b - 8.5])
                translate([xp, 0, 0]) cube([6, fu, 3.6]);
            // Wangen der Federkammer, tragen die Achse
            for (xp = [kx - 3.2, kx + kb])
                translate([xp, d, 0])
                    cube([3.2, fu - d, ax + rmax + 4]);
            // Aussteifungen außerhalb der Kammer. Sie greifen 0,6 mm in die
            // Stützfläche hinein - eine bloße Berührung ergäbe zwei Flächen
            // auf derselben Ebene und damit ein undichtes Netz.
            // Achtung Richtung: rotate([0,-90,0]) legt die Extrusion nach
            // -X, jede Rippe wächst also von xp aus nach links. Deshalb
            // xp = 12 und nicht 4 - sonst ragt die linke Rippe über die
            // Bauteilkante hinaus und der Schieber klemmt im Kanal.
            for (xp = [12, b - 4])
                translate([xp, 0, 0])
                    rotate([0, -90, 0])
                        linear_extrude(height = 8)
                            polygon([[0, d - 0.6], [0, fu - 3], [30, d - 0.6]]);
            // Grifflasche oben, nach hinten geneigt. Sie taucht 3 mm in die
            // Stützfläche ein, damit beide Körper sicher verschmelzen.
            translate([b / 2 - 16, d, h - 3])
                rotate([24, 0, 0]) cube([32, d, 25]);
        }
        // Achsbohrung durch beide Wangen
        translate([-1, ay, ax]) rotate([0, 90, 0])
            cylinder(d = feder_achse_d, h = b + 2);
        // Austrittsschlitz: das Federband läuft unten nach vorne in die Nut
        translate([(b - feder_band_b - 0.8) / 2, -1, 3.2])
            cube([feder_band_b + 0.8, d + 2, 3.0]);
        // Gewicht sparen, oberhalb der Kammer
        translate([10, -1, ax + rmax + 10])
            cube([b - 20, d + 2, h - ax - rmax - 24]);
    }
}

// ---------------------------------------------------------------------
//  Beschriftungsschild
//
//  Die Grundplatte wird orange gedruckt, die Schrift liegt 0,6 mm vertieft.
//  Wer zwei Farben hat, druckt zusätzlich TEIL="schild_text" in Schwarz und
//  klebt ihn ein - oder wechselt beim Drucken auf der letzten Schicht die
//  Farbe. Ohne zweite Farbe genügt ein Filzstift in der Vertiefung.
// ---------------------------------------------------------------------
schild_gravur = 0.6;

module schild_platte() {
    linear_extrude(height = schild_dicke)
        hull()
            for (px = [1.4, schild_breite - 1.4],
                 py = [1.4, schild_hoehe - 1.4])
                translate([px, py]) circle(r = 1.4);
}

// ---------------------------------------------------------------------
//  Sortensymbole
// ---------------------------------------------------------------------
// Die Silhouetten stehen in einer eigenen Datei - acht Tiere mit je einem
// Dutzend Formen machten die Hauptdatei unübersichtlich, und geändert
// wird an ihnen unabhängig von der Geometrie des Regals.
include <sortensymbole.scad>

// Sortensymbol nach Name. Unbekannte Namen ergeben kein Symbol.
module schild_sym(name) {
    // Fische bekommen ein ausgespartes Auge, damit es auch einfarbig
    // sichtbar bleibt - deshalb hier ein difference() statt eines Aufrufs.
    if (name == "lachs" || name == "thunfisch"
        || name == "fisch" || name == "forelle") {
        difference() {
            sym_fisch();
            sym_fisch_auge();
        }
    }
    else if (name == "huhn"      || name == "gefluegel") sym_huhn();
    else if (name == "rind")                             sym_rind();
    else if (name == "kaninchen")                        sym_kaninchen();
    else if (name == "ente")                             sym_ente();
    else if (name == "truthahn")                         sym_truthahn();
    else if (name == "lamm")                             sym_lamm();
    else if (name == "wild")                             sym_wild();
}

// Symbol oben, Name darunter - beides mittig. So füllt das Schild die
// Frontwand über die ganze Höhe aus und ist schon von weitem zu erkennen.
// Lange Sortennamen wie KANINCHEN werden schmaler gesetzt, damit sie nicht
// über den Rand laufen.
// Breite eines Schriftzugs. textmetrics() misst exakt, ist aber ein
// experimentelles Feature - ohne --enable=textmetrics gibt es undef
// zurück. Dann greift die Schätzung: 1,0 em je Versalie liegt über dem
// breitesten gemessenen Wert (LAMM mit 1,04 em ist kurz genug, dass die
// Reserve reicht) und lässt lieber etwas Luft, als über den Rand zu laufen.
function text_breite(t, groesse) =
    let (tm = textmetrics(text = t, size = groesse, font = schild_font))
    is_undef(tm) ? len(t) * groesse * 1.0 : tm.advance[0];

schild_font = "Helvetica:style=Bold";

module schild_schrift(h = schild_gravur) {
    hat_sym = schild_symbol != "leer" && schild_symbol != "";

    // Gerechnet wird im SICHTBAREN Ausschnitt, nicht auf der ganzen Tafel:
    // der Rahmen des Halters überdeckt ringsum schild_ueberdeckung, und was
    // darunter verschwindet, darf die Aufteilung nicht mitbestimmen. Sonst
    // sitzt das Symbol optisch zu hoch und klebt am Rahmen.
    su      = schild_sicht_u();          // untere Kante des Ausschnitts
    sh      = schild_sicht_h();          // seine Höhe
    rand    = schild_rand;
    breite  = schild_breite - 2 * schild_ueberdeckung - 2 * rand;

    // Höhe der Textzeile und des Symbolfeldes. Zwischen beiden bleibt ein
    // Steg, damit das Symbol nicht auf der Schrift sitzt.
    text_h  = hat_sym ? schild_text_h : sh - 2 * rand;
    sym_h   = sh - text_h - 2 * rand - schild_steg;

    // Die Schriftgröße richtet sich nach dem BREITESTEN vorkommenden Namen,
    // nicht nach dem gerade gesetzten - sonst stünde auf jedem Schild eine
    // andere Größe und die Tafeln wirkten uneinheitlich. Gemessen wird der
    // Referenzname bei Größe 10, daraus skaliert.
    ref_b   = text_breite(schild_ref_name, 10);
    // 3 % Reserve: der Referenzname soll nicht exakt bis an die
    // Randlinie laufen, sondern sichtbar Luft lassen.
    groesse = min(text_h, breite * 10 / ref_b * 0.97);

    translate([0, 0, schild_dicke - schild_gravur]) linear_extrude(height = h) {
        if (hat_sym)
            // resize bringt jedes Symbol auf dasselbe Feld. Ohne das wäre
            // der breite Fisch groß und das schmale Huhn klein, weil die
            // Zeichnungen unterschiedliche Eigenmaße haben. Dass die
            // Silhouette dabei mittig bleibt, hängt daran, dass sie um
            // (0,0) zentriert gezeichnet ist - resize verschiebt nicht.
            translate([schild_breite / 2,
                       su + rand + text_h + schild_steg + sym_h / 2])
                resize([sym_feld(), sym_feld()], auto = true)
                    schild_sym(schild_symbol);
        translate([schild_breite / 2, su + rand + text_h / 2])
            text(schild_text, size = groesse, halign = "center",
                 valign = "center", font = schild_font);
    }
}

// Kantenlänge des quadratischen Symbolfelds - für alle Sorten gleich.
// Sie folgt der Zone, die nach Rand, Textzeile und Steg übrig bleibt,
// damit das Symbol den Platz ausfüllt statt darin zu schwimmen.
function sym_feld() = min(schild_sicht_h() - 2 * schild_rand
                          - schild_text_h - schild_steg,
                          schild_breite - 2 * schild_ueberdeckung
                          - 2 * schild_rand);

module schild() {
    difference() {
        schild_platte();
        translate([0, 0, 0.001]) schild_schrift(schild_gravur + 1);
    }
}

// ---------------------------------------------------------------------
//  Passprobe: 35 mm Stück des Kanalprofils mit eingeprägtem Innenmaß.
//  Vor dem großen Druck einen echten Beutel hineinstellen.
// ---------------------------------------------------------------------
module probe() {
    pl = 35;
    difference() {
        cube([aussen_x, pl, boden_dick + anschlag_hoehe + 22]);
        translate([wand, -1, boden_dick])
            cube([innen_x, pl + 2, innen_z + 1]);
        if (bandnut)
            translate([(aussen_x - bandnut_breite) / 2, -1,
                       boden_dick - bandnut_tiefe])
                cube([bandnut_breite, pl + 2, bandnut_tiefe + 1]);
        translate([aussen_x / 2, wand + 0.3, boden_dick + 11])
            rotate([90, 0, 0]) rotate([0, 0, 180])
                linear_extrude(height = 0.8)
                    text(str(innen_x), size = 9, halign = "center",
                         valign = "center");
    }
}

// ---------------------------------------------------------------------
//  Beutel-Attrappe
// ---------------------------------------------------------------------
module beutel_reihe(n, y_start = 6) {
    for (k = [0 : n - 1])
        translate([wand + spiel / 2, y_start + k * beutel_dicke, boden_dick])
            cube([beutel_breit, beutel_dicke - 1.4, beutel_hoch]);
}

// Ein kompletter Kanal aus front + n x mitte + end
module kanal_reihe(fuellung) {
    // Front
    segment_stueck("front", 0);
    for (i = [1 : segment_anzahl - 2])
        segment_stueck("mitte", anschlag_dicke() + i * segment_laenge
                                - segment_laenge);
    segment_stueck("end", anschlag_dicke() + (segment_anzahl - 1) * segment_laenge
                          - segment_laenge);
    color("Silver", 0.95)
        translate([0, anschlag_dicke(), 0]) beutel_reihe(fuellung, 2);
}

// Hilfskonstrukt: ein Segment an Position y mit gegebenem Typ.
// OpenSCAD kennt keine Parameterüberschreibung, daher wird die Geometrie
// hier direkt nachgebildet, indem das Modul mit gesetzten Globals gerendert
// und verschoben wird. Für die Vorschau genügt der einfache Quader-Umriss.
module segment_stueck(typ, ypos) {
    translate([0, ypos, 0]) segment();
}

// ---------------------------------------------------------------------
//  Längsschnitt
// ---------------------------------------------------------------------
module schnitt() {
    difference() {
        union() {
            color([0.17, 0.17, 0.19]) segment();
            color("Silver", 0.95)
                translate([0, ist_front ? anschlag_dicke() + 2 : 2, 0])
                    beutel_reihe(floor((segment_laenge - 8) / beutel_dicke), 0);
        }
        translate([aussen_x / 2, -30, -10])
            cube([aussen_x, aussen_y + 60, aussen_z + 40]);
    }
}

// ---------------------------------------------------------------------
//  Layout-Vorschau: Spalten x Ebenen im Schrank
// ---------------------------------------------------------------------
module layout() {
    color("Tan", 0.22)
        translate([-10, -10, -4]) cube([schrank_breite, schrank_tiefe, 4]);

    fuell = [[46, 30, 18], [38, 46, 12], [22, 34, 46]];

    for (e = [0 : ebenen - 1], sx = [0 : spalten - 1])
        translate([sx * aussen_x, 0, e * aussen_z]) {
            color([0.17, 0.17, 0.19]) kanal_vorschau();
            if (sx < 3)
                color(sx == 0 ? "Silver"
                              : (sx == 1 ? [0.74, 0.74, 0.78] : [0.62, 0.62, 0.66]))
                    translate([0, anschlag_dicke(), 0])
                        beutel_reihe(fuell[e][sx], 2);
        }
}

// Vereinfachter Kanalumriss über die volle Länge für die Vorschau
module kanal_vorschau() {
    L = kanal_laenge + anschlag_dicke() + wand;
    difference() {
        cube([aussen_x, L, aussen_z]);
        // Innenraum
        translate([wand, anschlag_dicke(), boden_dick])
            cube([innen_x, L - anschlag_dicke() - wand, innen_z + 1]);
        // Front oberhalb der Wand offen - dort wird gegriffen
        translate([wand, -1, boden_dick + anschlag_hoehe])
            cube([innen_x, anschlag_dicke() + 1, innen_z + 1]);
        // Bandnut
        if (bandnut)
            translate([(aussen_x - bandnut_breite) / 2, -1,
                       boden_dick - bandnut_tiefe])
                cube([bandnut_breite, L + 2, bandnut_tiefe + 1]);
        // Fenster je Segment
        for (i = [0 : segment_anzahl - 1]) {
            f_von = anschlag_dicke() + i * segment_laenge + 14;
            f_b = segment_laenge - 28;
            for (xp = [-1, aussen_x - wand - 1])
                translate([xp, f_von, boden_dick + 14])
                    fenster_yz(f_b, innen_z - 26, 7, wand + 2);
        }
        // Sichtschlitz hinten
        translate([(aussen_x - (innen_x - 24)) / 2, L - wand - 1, boden_dick + 16])
            fenster_xz(innen_x - 24, innen_z - 34, 6, wand + 2);
    }
    schildhalter();
}

// ---------------------------------------------------------------------
//  Ausgabe
// ---------------------------------------------------------------------
if (TEIL == "segment")       segment();
else if (TEIL == "schieber") schieber();
else if (TEIL == "schild")   schild();
else if (TEIL == "verbinder") verbinder();
else if (TEIL == "trommel")  trommel();
else if (TEIL == "symbol")
    // Nur das nackte Sortensymbol, 1 mm dick. Damit misst
    // werkzeuge/symbole-pruefen.py nach, ob es mittig sitzt und wie
    // groß es wirklich ist - beides sieht man dem Schild nicht an.
    linear_extrude(height = 1) schild_sym(schild_symbol);
else if (TEIL == "schild_text") schild_schrift();
else if (TEIL == "probe")    probe();
else if (TEIL == "schnitt")  schnitt();
else if (TEIL == "layout")   layout();
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
