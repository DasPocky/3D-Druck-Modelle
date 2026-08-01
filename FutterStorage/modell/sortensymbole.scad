// =====================================================================
//  Sortensymbole für die Beschriftungsschilder
//
//  Jedes Tier ist eine geschlossene Silhouette in Seitenansicht, nach
//  rechts gewandt, gezeichnet in ein Feld von 20 x 20 um den Nullpunkt.
//
//  Zwei Regeln, an denen die alte Fassung gescheitert ist:
//
//  1. MITTIG. Die Silhouette muss symmetrisch um (0,0) liegen. resize()
//     im Schild skaliert nur, es verschiebt nicht - ein Symbol, dessen
//     Schwerpunkt daneben liegt, sitzt auch auf dem Schild daneben.
//     Nachgemessen wird das von werkzeuge/symbole-pruefen.py.
//
//  2. MASSIV. Alles unter 1,2 mm Strichstärke verschwindet nach dem
//     Verkleinern auf Schildgröße. Beine, Geweih und Schnabel sind
//     deshalb aus vollen Formen aufgebaut, nicht aus Linien.
//
//  Der Maßstab ist bewusst grob gehalten: auf dem fertigen Schild ist
//  das Symbol rund 38 mm groß, aus zwei Metern Entfernung zählt nur die
//  Umrisslinie.
// =====================================================================

// Ein Bein: oben am Rumpf angesetzt, unten mit Huf/Pfote verbreitert.
module _bein(x, oben, unten, dick = 1.8, huf = 0) {
    translate([x - dick / 2, unten]) square([dick, oben - unten]);
    if (huf > 0)
        translate([x - huf / 2, unten]) square([huf, 1.5]);
}

// Strich mit runden Enden - für Hals, Schwanz, Geweihstangen
module _strich(von, bis, r1, r2) {
    hull() {
        translate(von) circle(r = r1);
        translate(bis) circle(r = r2);
    }
}

// ---------------------------------------------------------------------
//  Huhn - gedrungener Körper, Kamm, Schnabel, Sichelschwanz
//  Feld: x -9,6 .. 9,6   y -10,0 .. 10,0
// ---------------------------------------------------------------------
module sym_huhn() {
    // mittig gerückt, Wert von werkzeuge/symbole-pruefen.py
    translate([0.5, -0.48])
    union() {
        // Rumpf, nach hinten oben ansteigend
        hull() {
            translate([0.4, 0.6]) scale([1.15, 0.95]) circle(r = 5.4);
            translate([-4.0, 2.6]) circle(r = 3.6);
        }
        // Hals und Kopf
        _strich([3.0, 2.4], [4.4, 6.4], 3.0, 2.6);
        translate([4.8, 7.4]) circle(r = 2.7);
        // Kamm - drei Zacken, kräftig genug zum Drucken
        for (k = [0, 1, 2])
            translate([3.4 + k * 1.5, 9.6 - abs(k - 1) * 0.5])
                circle(r = 1.35);
        // Schnabel
        translate([6.9, 7.2]) polygon([[0, 1.5], [2.7, -0.2], [0, -1.5]]);
        // Kehllappen
        translate([5.6, 4.9]) circle(r = 1.3);
        // Sichelschwanz nach hinten oben
        hull() {
            translate([-5.6, 3.4]) circle(r = 2.4);
            translate([-9.0, 8.4]) circle(r = 1.1);
        }
        hull() {
            translate([-5.6, 2.6]) circle(r = 2.2);
            translate([-9.6, 5.4]) circle(r = 1.0);
        }
        // Beine mit Fuß
        _bein(-0.8, -3.6, -8.6, 1.9, 4.4);
        _bein(3.0, -3.2, -8.6, 1.9, 4.4);
        // Standlinie ergänzen, damit die Füße nicht in der Luft enden
        translate([-3.6, -10.0]) square([0.001, 0.001]);
    }
}

// ---------------------------------------------------------------------
//  Rind - massiger Rumpf, Hörner zur Seite, schwerer Kopf
//  Feld: x -10,0 .. 10,0   y -9,0 .. 8,4
// ---------------------------------------------------------------------
module sym_rind() {
    // mittig gerückt, Wert von werkzeuge/symbole-pruefen.py
    translate([-0.2, -0.18])
    union() {
        // Rumpf, deutlich länger als hoch
        hull() {
            translate([-2.6, 1.4]) scale([1.0, 0.92]) circle(r = 5.2);
            translate([3.4, 1.8]) scale([1.0, 0.86]) circle(r = 4.6);
        }
        // Widerrist - macht das Rind vom Pferd unterscheidbar
        translate([-1.0, 5.0]) scale([1.5, 0.6]) circle(r = 3.0);
        // Hals zum Kopf
        _strich([4.6, 2.6], [7.0, 3.4], 3.2, 2.8);
        // Kopf, breit und kantig
        hull() {
            translate([7.2, 3.6]) circle(r = 2.7);
            translate([8.6, 1.4]) circle(r = 1.8);
        }
        // Hörner - nach außen und oben, kräftig
        _strich([6.4, 5.8], [4.6, 8.0], 1.15, 0.75);
        _strich([8.2, 5.6], [9.4, 7.6], 1.15, 0.75);
        // Vier Beine
        _bein(-5.4, -2.0, -8.4, 2.1, 3.0);
        _bein(-2.6, -2.4, -8.4, 2.1, 3.0);
        _bein(2.8, -2.4, -8.4, 2.1, 3.0);
        _bein(5.4, -2.0, -8.4, 2.1, 3.0);
        // Schwanz mit Quaste
        _strich([-7.2, 4.0], [-8.4, -2.0], 1.0, 0.7);
        translate([-8.5, -3.2]) circle(r = 1.3);
    }
}

// ---------------------------------------------------------------------
//  Fisch - Spindel, große Schwanzflosse, Rücken- und Bauchflosse
//  Feld: x -10,0 .. 10,0   y -6,4 .. 6,4
// ---------------------------------------------------------------------
module sym_fisch() {
    // mittig gerückt, Wert von werkzeuge/symbole-pruefen.py
    translate([0.32, -0.4])
    union() {
        // Körper als Linsenform aus zwei Kreisbögen
        intersection() {
            translate([0, -6.2]) circle(r = 11.4);
            translate([0, 6.2]) circle(r = 11.4);
        }
        // Schwanzflosse
        translate([-6.4, 0])
            polygon([[0, 0], [-3.8, 4.6], [-3.8, -4.6]]);
        // Rückenflosse
        translate([-0.6, 3.4])
            polygon([[-2.6, 0], [1.2, 0], [-0.4, 3.4]]);
        // Bauchflosse
        translate([0.4, -3.4])
            polygon([[-2.0, 0], [1.4, 0], [0.2, -2.6]]);
        // Kiemenbogen als Kerbe angedeutet
        translate([4.2, 0]) scale([0.35, 1.0]) circle(r = 2.6);
    }
}

// Das Auge wird ausgespart, damit es auch im einfarbigen Druck sichtbar
// bleibt - eine aufgesetzte Scheibe verschwände in der Silhouette.
module sym_fisch_auge() {
    translate([5.6, 1.2]) circle(r = 1.15);
}

// ---------------------------------------------------------------------
//  Kaninchen - aufrecht sitzend, zwei lange Ohren, Blume hinten
//  Feld: x -8,0 .. 8,0   y -10,0 .. 10,0
// ---------------------------------------------------------------------
module sym_kaninchen() {
    // mittig gerückt, Wert von werkzeuge/symbole-pruefen.py
    translate([0.90, -1.10])
    union() {
        // Sitzender Rumpf, hinten hoch
        hull() {
            translate([-2.2, -3.4]) scale([1.15, 1.0]) circle(r = 4.6);
            translate([-3.4, 0.2]) circle(r = 3.7);
        }
        // Brust zum Kopf
        _strich([1.8, -2.4], [2.8, 1.4], 2.7, 2.3);
        // Kopf - kleiner als vorher, damit die Ohren daneben Platz haben
        translate([3.4, 2.6]) scale([1.05, 0.92]) circle(r = 2.3);
        // Schnauze
        translate([5.4, 1.8]) circle(r = 1.3);
        // Zwei Ohren. Sie sind DAS Erkennungsmerkmal und müssen frei über
        // dem Kopf stehen - vorher waren sie so breit und tief angesetzt,
        // dass sie mit ihm zu einem Klumpen verschmolzen.
        translate([2.4, 7.0]) rotate(-10)
            scale([0.34, 1.0]) circle(r = 4.3);
        translate([4.8, 6.8]) rotate(12)
            scale([0.34, 1.0]) circle(r = 4.1);
        // Vorderlauf
        _bein(3.0, -4.6, -8.2, 1.7, 3.0);
        // Hinterlauf, angewinkelt
        hull() {
            translate([-3.0, -6.4]) scale([1.5, 0.8]) circle(r = 2.8);
            translate([0.6, -7.4]) circle(r = 1.7);
        }
        // Blume
        translate([-6.6, -0.8]) circle(r = 1.9);
    }
}

// ---------------------------------------------------------------------
//  Ente - schwimmend, langer Hals, flacher breiter Schnabel
//  Feld: x -9,4 .. 9,4   y -5,0 .. 9,6
// ---------------------------------------------------------------------
module sym_ente() {
    // mittig gerückt, Wert von werkzeuge/symbole-pruefen.py
    translate([-0.45, -2.3])
    union() {
        // Schwimmkörper
        hull() {
            translate([-1.0, -0.6]) scale([1.35, 0.9]) circle(r = 5.0);
            translate([-6.6, 1.6]) circle(r = 2.6);
        }
        // Hochgestellter Schwanz
        translate([-6.0, 0.6])
            polygon([[0, 2.4], [-3.4, 4.4], [-2.0, -0.6]]);
        // Hals - typisch S-förmig
        _strich([2.6, 0.4], [4.2, 4.6], 2.7, 2.0);
        _strich([4.2, 4.6], [4.8, 6.6], 2.0, 2.2);
        // Kopf
        translate([5.2, 7.2]) circle(r = 2.5);
        // Flacher Schnabel - das Erkennungsmerkmal, deshalb breit
        hull() {
            translate([7.0, 6.6]) circle(r = 1.2);
            translate([9.4, 6.2]) circle(r = 0.9);
        }
        // Flügelandeutung
        translate([-1.2, 0.8]) scale([1.25, 0.5]) circle(r = 3.4);
        // Wasserlinie, damit sie schwimmt statt zu schweben
        translate([-8.4, -4.2]) square([16.8, 1.6]);
    }
}

// ---------------------------------------------------------------------
//  Truthahn - aufgefächerter Schwanz, Kehllappen
//  Feld: x -10,0 .. 10,0   y -9,4 .. 9,4
// ---------------------------------------------------------------------
module sym_truthahn() {
    // mittig gerückt, Wert von werkzeuge/symbole-pruefen.py
    translate([0.93, -0.84])
    union() {
        // Der Fächer bestimmt die Silhouette - halbrund hinter dem Tier
        difference() {
            translate([-2.0, 1.0]) circle(r = 8.4);
            translate([-2.0, 1.0]) circle(r = 5.4);
            translate([-2.0, -9.0]) square([20, 20]);
        }
        // Federspitzen auf dem Fächer
        for (a = [20 : 28 : 160])
            translate([-2.0 + 7.4 * cos(a), 1.0 + 7.4 * sin(a)])
                circle(r = 1.5);
        // Rumpf
        translate([1.0, 0.4]) scale([1.0, 1.1]) circle(r = 4.4);
        // Hals und Kopf
        _strich([2.8, 3.0], [4.4, 6.0], 2.2, 1.9);
        translate([4.8, 7.0]) circle(r = 2.1);
        // Schnabel
        translate([6.4, 6.8]) polygon([[0, 1.2], [2.2, 0], [0, -1.2]]);
        // Kehllappen - hängt am Schnabelansatz herunter
        hull() {
            translate([6.2, 5.6]) circle(r = 1.1);
            translate([6.6, 3.0]) circle(r = 0.9);
        }
        // Beine
        _bein(0.0, -3.0, -8.0, 1.9, 4.0);
        _bein(3.0, -2.8, -8.0, 1.9, 4.0);
    }
}

// ---------------------------------------------------------------------
//  Lamm - wolliger Rumpf aus Bögen, schmaler Kopf
//  Feld: x -9,2 .. 9,2   y -8,6 .. 7,8
// ---------------------------------------------------------------------
module sym_lamm() {
    // mittig gerückt, Wert von werkzeuge/symbole-pruefen.py
    translate([0.1, -0.05])
    union() {
        // Wollkörper: Grundform plus aufgesetzte Bögen
        translate([-1.4, 1.2]) scale([1.3, 1.0]) circle(r = 5.2);
        for (a = [0 : 45 : 359])
            translate([-1.4 + 6.0 * cos(a) * 1.1, 1.2 + 5.0 * sin(a)])
                circle(r = 2.1);
        // Hals und Kopf
        _strich([4.4, 2.4], [6.4, 4.0], 2.2, 2.2);
        hull() {
            translate([6.6, 4.4]) circle(r = 2.3);
            translate([8.4, 2.8]) circle(r = 1.5);
        }
        // Ohr, hängend
        translate([5.6, 5.8]) rotate(35) scale([1.0, 0.5]) circle(r = 1.9);
        // Vier dünne Beine
        _bein(-4.4, -2.6, -8.2, 1.7, 2.6);
        _bein(-1.8, -3.0, -8.2, 1.7, 2.6);
        _bein(2.2, -3.0, -8.2, 1.7, 2.6);
        _bein(4.6, -2.6, -8.2, 1.7, 2.6);
    }
}

// ---------------------------------------------------------------------
//  Wild - Hirsch. Das Geweih ist das Erkennungsmerkmal und deshalb
//  bewusst groß: in der alten Fassung war es so klein, dass das Tier
//  wie ein Lama aussah.
//  Feld: x -9,6 .. 9,6   y -9,0 .. 10,0
// ---------------------------------------------------------------------
module sym_wild() {
    // mittig gerückt, Wert von werkzeuge/symbole-pruefen.py
    translate([-1.11, -0.85])
    union() {
        // Schlanker Rumpf
        hull() {
            translate([-3.0, -0.8]) scale([1.0, 0.94]) circle(r = 4.4);
            translate([2.6, -0.4]) scale([1.0, 0.9]) circle(r = 4.0);
        }
        // Langer aufrechter Hals
        _strich([3.8, 1.4], [5.4, 5.2], 2.6, 1.9);
        // Kopf mit Schnauze
        hull() {
            translate([5.6, 6.0]) circle(r = 2.0);
            translate([7.8, 4.8]) circle(r = 1.3);
        }
        // Geweih: zwei Stangen mit je zwei Enden, weit ausladend
        for (sp = [[-1, 3.8], [1, 6.4]]) {
            sx = sp[0];
            bx = sp[1];
            // Hauptstange
            _strich([bx, 7.4], [bx + sx * 2.6, 9.8], 1.05, 0.7);
            // vorderes Ende
            _strich([bx + sx * 0.8, 8.2], [bx + sx * 3.4, 8.2], 0.85, 0.6);
            // Ansatz zum Kopf
            _strich([bx, 7.4], [5.6, 6.4], 1.0, 1.0);
        }
        // Vier Läufe
        _bein(-5.6, -3.4, -8.8, 1.8, 2.4);
        _bein(-2.4, -3.8, -8.8, 1.8, 2.4);
        _bein(2.0, -3.8, -8.8, 1.8, 2.4);
        _bein(4.6, -3.4, -8.8, 1.8, 2.4);
        // Kurzer Wedel
        translate([-7.0, 1.6]) scale([0.7, 1.0]) circle(r = 1.7);
    }
}
