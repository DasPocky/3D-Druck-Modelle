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

