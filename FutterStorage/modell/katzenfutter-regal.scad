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
// segment = Kanalsegment (Typ über segment_typ), schieber, schild,
// probe = Passprobe, layout = Vorschau im Schrank, schnitt = Längsschnitt,
// test = Kollisionsprüfung gestapelter Ebenen (Ergebnis muss leer sein)
TEIL = "segment";  // [segment, schieber, schild, schild_text, verbinder, probe, layout, schnitt, test]

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
bandnut_breite = 18;
bandnut_tiefe = 1.6;
// Maße der Federrolle - nach dem Kauf hier eintragen
feder_rolle_d = 26;    // Durchmesser der aufgerollten Feder
feder_band_b  = 16;    // Bandbreite
feder_achse_d = 3.2;   // Bohrung für die Achse (3 mm Stab oder Filament)

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
// Laengster vorkommender Sortenname in Zeichen. Danach richtet sich die
// Schriftgroesse aller Schilder, damit sie einheitlich aussehen.
schild_namen_max = 9;
schild_dicke = 1.5;

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
module schildhalter() {
    sp = schild_dicke + 0.4;
    rb = 1.2;
    b  = schild_breite + 3.2;
    x0 = (aussen_x - b) / 2;
    // nur so hoch wie das Schild plus etwas Einfuehrung, sonst bleibt
    // ueber der Tafel ein leerer Rahmen stehen
    h  = min(anschlag_hoehe - 2, schild_hoehe + 3);
    difference() {
        // taucht 0,6 mm in die Anschlagkante ein
        translate([x0, -(sp + rb), 3]) cube([b, sp + rb + 0.6, h]);
        // Spalt für das Schild, nach oben offen
        translate([x0 + 1.6, -sp, 4]) cube([b - 3.2, sp, h]);
        // Sichtfenster
        translate([x0 + 3.5, -(sp + rb) - 1, 5])
            fenster_xz(b - 7, h - 6, 2.5, rb + 2);
    }
}

// ---------------------------------------------------------------------
//  Schieber
//
//  Drückt die Beutel nach vorne. Unten ein Haken für ein Gummiband, das
//  in der Bodennut nach vorne läuft; die Grifflasche erlaubt zusätzlich
//  das Nachschieben von Hand.
// ---------------------------------------------------------------------
module schieber() {
    b   = innen_x - 1.2;
    h   = beutel_hoch - 8;
    d   = 2.6;
    fu  = 36;                         // Fußlänge, nimmt die Federrolle auf
    kb  = feder_band_b + 1.6;         // lichte Breite der Federkammer
    kx  = (b - kb) / 2;               // Kammer mittig
    ax  = feder_rolle_d / 2 + 4;      // Achshöhe über dem Boden
    ay  = 4 + feder_rolle_d / 2;      // Achsposition in der Tiefe

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
                    cube([3.2, fu - d, ax + feder_rolle_d / 2 + 4]);
            // Aussteifungen außerhalb der Kammer. Sie greifen 0,6 mm in die
            // Stützfläche hinein - eine bloße Berührung ergäbe zwei Flächen
            // auf derselben Ebene und damit ein undichtes Netz.
            for (xp = [4, b - 12])
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
        translate([10, -1, ax + feder_rolle_d / 2 + 10])
            cube([b - 20, d + 2, h - ax - feder_rolle_d / 2 - 24]);
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
// Jedes Symbol zeichnet in ein Feld von 20 x 20 um den Nullpunkt. Sie
// sind aus Kreisen und Polygonen zusammengesetzt statt aus einer langen
// Punktliste - so bleibt jede Form einzeln nachvollziehbar und änderbar.
module sym_huhn() {
    union() {
        scale([1.0, 0.85]) circle(r = 6.2);              // Rumpf
        translate([3.6, 6.2]) circle(r = 3.3);           // Kopf
        hull() { translate([3.6, 6.2]) circle(r = 2.6);
                 translate([1.6, 1.0]) circle(r = 3.4); }// Hals
        translate([6.4, 6.8]) polygon([[0,1.6],[3.9,0],[0,-1.6]]);   // Schnabel
        for (k = [0, 1, 2])                              // Kamm
            translate([2.2 + k * 1.5, 9.2 + (k == 1 ? 0.7 : 0)]) circle(r = 1.25);
        translate([1.0, 3.4]) circle(r = 1.0);           // Kehllappen
        hull() { translate([-5.2, 1.4]) circle(r = 2.2);  // Schwanzfedern
                 translate([-9.4, 7.6]) circle(r = 1.0);
                 translate([-8.6, 3.0]) circle(r = 1.0); }
        for (bx = [-1.8, 1.8])                           // Beine
            translate([bx - 0.7, -9.4]) square([1.5, 5.0]);
        for (bx = [-2.5, 1.1])
            translate([bx, -9.8]) square([3.0, 1.4]);
    }
}

module sym_rind() {
    union() {
        translate([-0.5, 0.6]) scale([1.25, 0.78]) circle(r = 6.4);  // Rumpf
        translate([6.0, 3.4]) scale([0.95, 1.0]) circle(r = 3.5);    // Kopf
        translate([7.4, 0.6]) scale([0.8, 1.0]) circle(r = 2.3);     // Maul
        for (s = [-1, 1])                                            // Hörner
            translate([5.2, 6.4]) rotate(s * 34)
                hull() { circle(r = 1.15); translate([0, 3.6]) circle(r = 0.62); }
        for (bx = [-6.2, -3.0, 2.4, 5.2])                            // Beine
            translate([bx, -10.2]) square([2.1, 6.2]);
        hull() { translate([-7.4, 3.6]) circle(r = 1.0);             // Schwanz
                 translate([-9.6, -3.4]) circle(r = 0.55); }
        translate([-9.9, -4.6]) circle(r = 1.25);                    // Quaste
    }
}

module sym_fisch() {
    union() {
        // Rumpf: vorne rund, hinten spitz zulaufend
        hull() { translate([-1.0, 0]) scale([1.0, 0.92]) circle(r = 6.0);
                 translate([8.6, 0]) circle(r = 1.6); }
        hull() { translate([-1.0, 0]) scale([1.0, 0.92]) circle(r = 5.8);
                 translate([-7.4, 0]) circle(r = 1.4); }
        translate([-7.0, 0])                                          // Schwanzflosse
            polygon([[0,1.8],[-4.8,5.6],[-3.6,0],[-4.8,-5.6],[0,-1.8]]);
        translate([-1.2, 4.4]) polygon([[-3.4,0.6],[1.2,4.6],[4.0,0.2]]);  // Rücken
        translate([-0.6, -4.4]) polygon([[-2.6,-0.4],[0.6,-3.6],[3.2,-0.2]]); // Bauch
        translate([5.6, 1.6]) circle(r = 1.05);                      // Auge
    }
}

module sym_kaninchen() {
    union() {
        // Sitzendes Kaninchen im Profil: runder Rumpf, Kopf deutlich höher
        // abgesetzt, darüber zwei senkrechte Ohren mit sichtbarer Lücke.
        translate([-2.4, -3.4]) scale([1.1, 1.0]) circle(r = 5.4);   // Rumpf
        translate([3.8, 3.0]) circle(r = 3.1);                       // Kopf
        hull() { translate([3.8, 3.0]) circle(r = 2.4);              // Hals
                 translate([0.6, -1.6]) circle(r = 3.0); }
        for (s = [0, 1])                                             // Ohren
            translate([2.4 + s * 3.4, 5.4])
                hull() { scale([0.58, 1]) circle(r = 1.2);
                         translate([s ? 0.9 : -0.9, 6.6])
                             scale([0.46, 1]) circle(r = 0.85); }
        translate([6.6, 2.0]) scale([1.0, 0.82]) circle(r = 1.5);    // Schnauze
        translate([-8.0, -2.6]) circle(r = 2.1);                     // Blume
        for (bx = [-5.0, -0.6])                                      // Läufe
            translate([bx, -9.6]) scale([1.7, 0.62]) circle(r = 2.2);
    }
}

module sym_ente() {
    union() {
        translate([-1.0, -1.4]) scale([1.35, 0.8]) circle(r = 6.0);  // Rumpf
        translate([4.4, 5.0]) circle(r = 3.0);                       // Kopf
        hull() { translate([4.4, 5.0]) circle(r = 2.4);
                 translate([2.4, -0.6]) circle(r = 3.0); }           // Hals
        translate([6.8, 4.6]) polygon([[0,1.5],[4.6,0.4],[4.6,-0.8],[0,-1.5]]); // Schnabel
        hull() { translate([-6.0, 0.4]) circle(r = 2.0);             // Schwanz
                 translate([-10.2, 3.2]) circle(r = 0.7); }
        translate([-1.0, -1.0]) rotate(-16) scale([1.0, 0.45]) circle(r = 4.0); // Flügel
    }
}

module sym_truthahn() {
    union() {
        // Radschlagender Schwanz: ein Halbkreis hinter dem Körper, aus dem
        // schmale Kerben die einzelnen Federn schneiden
        translate([-1.8, 0.6]) difference() {
            scale([0.92, 1.0]) circle(r = 10.4);
            for (k = [-3 : 3]) rotate(96 + k * 24)
                translate([5.0, 0]) square([12, 1.5], center = true);
            translate([0, -12]) square([26, 12], center = true);
            circle(r = 4.2);
        }
        translate([2.0, -1.6]) scale([1.0, 0.92]) circle(r = 5.2);   // Rumpf
        translate([5.8, 3.8]) circle(r = 2.6);                       // Kopf
        hull() { translate([5.8, 3.8]) circle(r = 2.1);
                 translate([3.4, -1.0]) circle(r = 2.8); }           // Hals
        translate([8.0, 4.0]) polygon([[0,1.3],[3.2,0],[0,-1.3]]);   // Schnabel
        hull() { translate([7.4, 2.4]) circle(r = 0.85);             // Stirnlappen
                 translate([8.6, -1.0]) circle(r = 0.62); }
        for (bx = [0.6, 3.4]) translate([bx, -9.8]) square([1.5, 4.2]);
    }
}

module sym_lamm() {
    union() {
        for (p = [[-4.6,1.4],[-1.4,3.4],[2.0,2.6],[-3.0,-1.6],[0.4,-0.8]])
            translate(p) circle(r = 3.5);                            // Wollrücken
        translate([5.6, 2.6]) scale([0.86, 1.0]) circle(r = 3.0);    // Kopf
        for (s = [-1, 1])                                            // Ohren
            translate([5.0, 4.4 * s + 1.0]) rotate(s * 26)
                scale([1.0, 0.44]) circle(r = 2.6);
        translate([7.2, 0.6]) circle(r = 1.5);                       // Schnauze
        for (bx = [-4.4, -1.2, 2.0, 4.6])
            translate([bx, -9.0]) square([1.7, 5.0]);
    }
}

module sym_wild() {                                                   // Hirsch
    union() {
        translate([-0.8, 0]) scale([1.2, 0.8]) circle(r = 5.8);      // Rumpf
        translate([5.6, 4.2]) scale([0.8, 1.0]) circle(r = 2.8);     // Kopf
        hull() { translate([5.6, 4.2]) circle(r = 2.2);
                 translate([3.0, -0.6]) circle(r = 3.0); }           // Hals
        translate([7.4, 2.0]) scale([0.9, 0.7]) circle(r = 1.8);     // Nase
        for (s = [0, 1])                                             // Geweih
            translate([4.6 + s * 2.2, 6.6]) rotate(s ? 22 : -16) {
                hull() { circle(r = 0.85); translate([0, 4.2]) circle(r = 0.5); }
                translate([0, 2.0]) rotate(s ? 42 : -42)
                    hull() { circle(r = 0.7); translate([0, 2.6]) circle(r = 0.42); }
            }
        for (bx = [-5.4, -2.4, 1.8, 4.4])
            translate([bx, -9.8]) square([1.7, 6.0]);
        hull() { translate([-6.4, 2.6]) circle(r = 1.4);
                 translate([-7.6, 5.0]) circle(r = 0.8); }           // Wedel
    }
}

// Sortensymbol nach Name. Unbekannte Namen ergeben kein Symbol.
module schild_sym(name) {
    if      (name == "huhn"      || name == "gefluegel") sym_huhn();
    else if (name == "rind")                             sym_rind();
    else if (name == "lachs"     || name == "thunfisch"
          || name == "fisch"     || name == "forelle")   sym_fisch();
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
module schild_schrift(h = schild_gravur) {
    hat_sym = schild_symbol != "leer" && schild_symbol != "";
    rand    = 4;
    breite  = schild_breite - 2 * rand;
    // untere Zone für den Namen, der Rest gehört dem Symbol
    text_h  = hat_sym ? schild_hoehe * 0.30 : schild_hoehe - 2 * rand;
    sym_h   = schild_hoehe - text_h - 2 * rand;
    // Die Schriftgröße richtet sich nach dem längsten vorkommenden Namen,
    // nicht nach dem gerade gesetzten. Sonst stünde auf jedem Schild eine
    // andere Größe und die Tafeln wirkten uneinheitlich.
    // Versalien in Helvetica Bold sind rund 0,78 em breit.
    groesse = min(text_h * 0.92, breite / (schild_namen_max * 0.78));
    translate([0, 0, schild_dicke - schild_gravur]) linear_extrude(height = h) {
        if (hat_sym)
            // resize bringt jedes Symbol auf dasselbe Feld. Ohne das wäre
            // der breite Fisch groß und das schmale Huhn klein, weil die
            // Zeichnungen unterschiedliche Eigenmaße haben.
            translate([schild_breite / 2, rand + text_h + sym_h / 2])
                resize([sym_feld(), sym_feld()], auto = true)
                    schild_sym(schild_symbol);
        translate([schild_breite / 2, rand + text_h / 2])
            text(schild_text, size = groesse, halign = "center",
                 valign = "center", font = "Helvetica:style=Bold");
    }
}

// Kantenlänge des quadratischen Symbolfelds - für alle Sorten gleich
function sym_feld() = min(schild_hoehe * 0.70 - 8, schild_breite - 8) * 0.94;

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
        // Front oberhalb der Wand offen, plus Griffmulde
        translate([wand, -1, boden_dick + anschlag_hoehe])
            cube([innen_x, anschlag_dicke() + 1, innen_z + 1]);
        translate([0, anschlag_dicke() + 1, 0])
            rotate([90, 0, 0])
                linear_extrude(height = anschlag_dicke() + 2)
                    polygon([
                        [aussen_x/2 - mulde_breite/2, boden_dick + anschlag_hoehe + 1],
                        [aussen_x/2 + mulde_breite/2, boden_dick + anschlag_hoehe + 1],
                        [aussen_x/2 + mulde_breite/2, boden_dick + mulde_bis + 11],
                        [aussen_x/2 + mulde_breite/2 - 11, boden_dick + mulde_bis],
                        [aussen_x/2 - mulde_breite/2 + 11, boden_dick + mulde_bis],
                        [aussen_x/2 - mulde_breite/2, boden_dick + mulde_bis + 11]
                    ]);
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
