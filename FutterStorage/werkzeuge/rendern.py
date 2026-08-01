import bpy, math, sys, os

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL  = os.path.join(PROJ, "stl")
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["kanal", "/tmp/o.png"]
SZENE, OUT = args[0], args[1]

# Geometrie aus katzenfutter-regal.scad
def _scad(name, standard):
    """Einen Zahlenwert aus der OpenSCAD-Quelle lesen."""
    q = os.path.join(PROJ, "modell", "katzenfutter-regal.scad")
    if not os.path.exists(q):
        q = os.path.join(PROJ, "katzenfutter-regal.scad")
    for zeile in open(q, encoding="utf-8"):
        t = zeile.split("//")[0].strip().rstrip(";")
        if t.startswith(name) and t.count("=") == 1:
            try:
                return float(t.split("=")[1])
            except ValueError:
                pass
    return standard


# Alle Masse aus der Quelle rechnen, nicht fest eintragen. AZ stand hier
# mit 144,8 mm - dem Wert von vor der Greifraum-Aenderung. Die Ebenen sassen
# dadurch 38 mm zu tief und durchdrangen einander.
BB   = _scad("beutel_breit", 88.0)
BH   = _scad("beutel_hoch", 136.0)
BD   = _scad("beutel_dicke", 19.0)
WAND = _scad("wand", 1.6)
SPIEL = _scad("spiel", 4.0)
LUFT = _scad("luft_oben", 42.0)
BODEN = _scad("boden", 2.4) + _scad("bandnut_tiefe", 1.6) + 0.8
AX = BB + SPIEL + 2 * WAND                 # Spaltenbreite
AZ = BODEN + BH + LUFT                     # Ebenenhoehe
SEGL = _scad("segment_laenge", 160.0)
LF, LM = SEGL + 3.0, SEGL                  # Front- und Mittelsegment
LE = SEGL + WAND                           # Endsegment
SCHILD_B = _scad("schild_breite", 78.0)
# Hoehe, in der die Tafel in der Tasche steht. Stand hier fest als 6 -
# das Modell setzt sie auf 4. Dadurch sass das Schild im Bild 2 mm zu
# hoch, der Rahmen verdeckte oben 6 und unten 2 mm statt gleichmaessig.
SCHILD_Z = _scad("schild_z0", 4.0)

# Federaufnahme: "pusher" = gekauftes Gehaeuse in der Klemmtasche,
# "rolle" = gedruckte Trommel auf einer Achse.
def _bauart():
    q = os.path.join(PROJ, "modell", "katzenfutter-regal.scad")
    if not os.path.exists(q):
        q = os.path.join(PROJ, "katzenfutter-regal.scad")
    for zeile in open(q, encoding="utf-8"):
        t = zeile.split("//")[0].strip().rstrip(";")
        if t.startswith("feder_bauart"):
            return t.split("=")[1].strip().strip('"')
    return "rolle"


BAUART = _bauart()
PUSH_L = _scad("pusher_l", 42.0)
PUSH_B = _scad("pusher_b", 24.0)
PUSH_H = _scad("pusher_h", 22.0)

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.objects):
        for x in list(blk):
            try: blk.remove(x)
            except Exception: pass

def mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

def imp(name):
    before = set(bpy.data.objects)
    try:    bpy.ops.wm.stl_import(filepath=os.path.join(STL, name))
    except AttributeError: bpy.ops.import_mesh.stl(filepath=os.path.join(STL, name))
    o = list(set(bpy.data.objects) - before)[0]
    o.name = name[:-4]
    o.hide_render = True; o.hide_viewport = True
    return o

def put(src, loc, material, rot=(0, 0, 0), bevel=0.22):
    o = src.copy(); o.data = src.data.copy()
    o.hide_render = False; o.hide_viewport = False
    o.location = loc; o.rotation_euler = rot
    o.data.materials.clear(); o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new("bev", 'BEVEL')
        b.width = bevel; b.segments = 2; b.limit_method = 'ANGLE'
        b.angle_limit = math.radians(50); b.use_clamp_overlap = True
    bpy.context.collection.objects.link(o)
    return o

clear()

SCHWARZ = mat("PLA schwarz", (0.022, 0.022, 0.026), rough=0.45)
ORANGE  = mat("PLA orange",  (0.72, 0.24, 0.03),   rough=0.42)
# Der Beutel muss sich auf einen Blick vom Bauteil unterscheiden. Vorher
# war er fast so grau wie das PLA, dadurch sah es aus, als fuelle er die
# ganze Kanalhoehe aus. Jetzt ein helles Folienbeige mit wenig Glanz.
# Warmes Folienbeige: hell genug, um sich vom dunklen PLA abzuheben, aber
# nicht so hell, dass die Beutel im Licht wie Papierblaetter ausbrennen.
# Kein Metallic - der Glanz liess sie zusaetzlich weiss erscheinen.
FOLIE   = mat("Beutel",      (0.60, 0.52, 0.40),   rough=0.44)
HAUT    = mat("Hand",        (0.86, 0.66, 0.52),   rough=0.62)
# Das gekaufte Federgehaeuse ist grauer Kunststoff - deutlich heller
# als das schwarze PLA, damit man sieht, dass es ein Zukaufteil ist.
GEHAEUSE = mat("Federgehäuse", (0.55, 0.56, 0.58), rough=0.55)
HOLZ    = mat("Boden",       (0.26, 0.19, 0.13),   rough=0.65)

# Die Segmente liegen jetzt als Matrix aus Tiefe x Ebene x Spalte vor.
# Fuer die Bilder wird je Position die Variante genommen, die dort auch
# wirklich verbaut wird - sonst zeigte das Rendering Zapfen an Stellen,
# an denen im Ausbau keine sitzen.
_SEG = {}


def seg(tiefe, ebene="mitte", spalte="mitte"):
    schluessel = (tiefe, ebene, spalte)
    if schluessel not in _SEG:
        _SEG[schluessel] = imp(f"segmente/{tiefe}-{ebene}-{spalte}.stl")
    return _SEG[schluessel]


def rand(i, n):
    """Randlage einer Position: erste, letzte oder mittlere."""
    return 0 if i == 0 else (2 if i == n - 1 else 1)


EBENEN_N = ["unten", "mitte", "oben"]
SPALTEN_N = ["links", "mitte", "rechts"]
s_schb  = imp("schieber.stl")
s_schd  = imp("schild.stl")
s_txt   = imp("schild-text.stl")

# Fuer die Uebersichtsbilder: jede Spalte bekommt eine andere Sorte, damit
# man sieht, wofuer das Regal gedacht ist.
def _sorten():
    ordner = os.path.join(STL, "schilder")
    if not os.path.isdir(ordner):
        return []
    platten = sorted(f for f in os.listdir(ordner)
                     if f.endswith(".stl") and not f.endswith("-text.stl"))
    paare, nach_name = [], {}
    for pl in platten:
        txt = pl[:-4] + "-text.stl"
        if os.path.exists(os.path.join(ordner, txt)):
            paar = (imp(os.path.join("schilder", pl)),
                    imp(os.path.join("schilder", txt)))
            paare.append(paar)
            nach_name[pl[:-4]] = paar
    return paare, nach_name

SORTEN, SORTE_NACH_NAME = _sorten()

def kanal(x=0, z=0, luecke=0, segmente=3, ebene="mitte", spalte="mitte"):
    put(seg("front", ebene, spalte), (x, 0, z), SCHWARZ)
    for i in range(1, segmente - 1):
        put(seg("mitte", ebene, spalte),
            (x, LF + i * (LM + luecke) - LM + luecke, z), SCHWARZ)
    put(seg("end", ebene, spalte),
        (x, LF + (segmente - 2) * LM + (segmente - 1) * luecke, z), SCHWARZ)

def schild_an(x=0, z=0, nr=None):
    # Grundplatte orange, Schrift schwarz - Schild steht senkrecht in der Tasche
    pl, tx = SORTEN[nr % len(SORTEN)] if (nr is not None and SORTEN) else (s_schd, s_txt)
    put(pl, (x + (AX - SCHILD_B) / 2, -0.5, z + SCHILD_Z),
        ORANGE, rot=(math.radians(90), 0, 0), bevel=0.1)
    put(tx, (x + (AX - SCHILD_B) / 2, -0.5 - 0.62, z + SCHILD_Z),
        SCHWARZ, rot=(math.radians(90), 0, 0), bevel=0)

def beutel_mesh(name="Beutel"):
    """Baut die Beutelform als eigenes Netz.

    Aus einem Wuerfel laesst sich das nicht formen: Die Kantenrundung
    begrenzt sich je nach Geometrie selbst, dadurch geraten einzelne Beutel
    anders als die uebrigen. Hier wird die Oberflaeche direkt gerechnet.

    Die Dicke folgt zwei Kurven:
      quer  - am Siegelrand null, zur Mitte hin voll
      hoch  - unten die volle Dicke, nach oben duenn auslaufend,
              wie auf den Fotos: oben sitzt die Naht, der Inhalt sackt.
    """
    NX, NZ = 26, 34
    halb = (BD - 1.4) / 2

    def quer(u):                       # u: 0 links .. 1 rechts
        return math.sin(math.pi * u) ** 0.42

    def hoch(v):                       # v: 0 unten .. 1 oben
        if v < 0.12:                   # unterer Siegelrand, dann bauchig
            return 0.34 + 0.66 * (v / 0.12) ** 0.6
        # Der Beutel bleibt bis weit oben prall und knickt erst kurz vor der
        # Siegelnaht ab. Eine Potenzkurve liefe kegelfoermig zu, deshalb eine
        # S-Kurve mit Wendepunkt bei 75 % der Resthoehe.
        # Wendepunkt weit oben (88 %) und steiler Abfall: der Beutel ist
        # bis kurz unter die Naht prall und knickt dann ab. Mit dem
        # frueheren Wert 0,75 und Steigung 8 lief er kegelfoermig zu und
        # sah aus wie ein Zapfen statt wie ein Paeckchen.
        w = (v - 0.12) / 0.88
        g = lambda t: 1.0 / (1.0 + math.exp(15.0 * (t - 0.88)))
        f = (g(w) - g(1.0)) / (g(0.0) - g(1.0))
        # Oben bleibt Restdicke stehen: dort sitzt die Siegelnaht, und
        # die ist flach, nicht spitz. Mit 0,032 lief der Beutel spitz zu
        # und man sah nicht mehr, wo er endet und wo der Greifraum beginnt.
        return 0.22 + 0.78 * f

    verts, faces = [], []
    for seite in (1, -1):
        basis = len(verts)
        for iz in range(NZ):
            v = iz / (NZ - 1)
            for ix in range(NX):
                u = ix / (NX - 1)
                verts.append((( u - 0.5) * BB,
                              seite * halb * quer(u) * hoch(v),
                              (v - 0.5) * BH))
        for iz in range(NZ - 1):
            for ix in range(NX - 1):
                a0 = basis + iz * NX + ix
                quad = (a0, a0 + 1, a0 + NX + 1, a0 + NX)
                faces.append(quad if seite > 0 else quad[::-1])

    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    for poly in me.polygons:
        poly.use_smooth = True
    return me


_BEUTEL_MESH = None


def beutel(n, x=0, z=0):
    """Setzt n Beutel hintereinander in den Kanal.

    Sie stehen nicht exakt senkrecht: Weil der Schieber von hinten drueckt
    und jeder Beutel sich am naechsten abstuetzt, lehnen sie leicht nach
    vorne - mit ein paar Grad Streuung, wie ein Stapel es real tut.
    """
    global _BEUTEL_MESH
    if _BEUTEL_MESH is None:
        _BEUTEL_MESH = beutel_mesh()
    abstand = BD - 1.0                      # minimaler Spalt, sie beruehren sich
    for k in range(n):
        o = bpy.data.objects.new(f"beutel_{x:.0f}_{z:.0f}_{k}", _BEUTEL_MESH)
        # leichte Neigung nach vorne, deterministisch gestreut
        kipp = 2.6 + ((k * 37) % 11) * 0.28
        o.rotation_euler = (math.radians(-kipp), 0, 0)
        # der Kippwinkel hebt die Oberkante nach vorne, unten bleibt der Fuss
        o.location = (x + WAND + SPIEL / 2 + BB / 2,
                      4 + k * abstand + (BD - 1.4) / 2
                      + math.sin(math.radians(kipp)) * BH / 2,
                      z + BODEN + BH / 2 * math.cos(math.radians(kipp)))
        o.data.materials.clear()
        o.data.materials.append(FOLIE)
        bpy.context.collection.objects.link(o)


def schieber_bei(n, x=0, z=0):
    y = 4 + n * BD + 1
    put(s_schb, (x + 1.8, y, z + BODEN), ORANGE)
    # Beim Warenpusher steckt das gekaufte Gehaeuse in der Klemmtasche.
    # Es als Quader anzudeuten ist ehrlicher, als die Tasche leer zu
    # zeigen - die genaue Form kennen wir erst am Teil.
    if BAUART == "pusher":
        bpy.ops.mesh.primitive_cube_add(size=1)
        o = bpy.context.object
        o.scale = (PUSH_B, PUSH_L, PUSH_H)
        o.location = (x + 1.8 + (BB + SPIEL) / 2, y + 4 + PUSH_L / 2,
                      z + BODEN + 3.0 + PUSH_H / 2)
        o.name = "federgehaeuse"
        o.data.materials.clear()
        o.data.materials.append(GEHAEUSE)


def finger(x, y, z, laenge=62, d=17.5):
    """Zwei Finger als masstaebliche Zylinder.

    Kein Modellierkunststueck, sondern ein Massstab: 17,5 mm ist die Dicke
    eines Erwachsenenfingers. Wer im Bild sieht, dass beide Finger neben
    die Beutelkante passen, braucht die Rechnung nicht nachzuvollziehen.
    """
    for k, versatz in enumerate((-11.0, 11.0)):
        bpy.ops.mesh.primitive_cylinder_add(radius=d / 2, depth=laenge,
                                            location=(x + versatz, y, z))
        o = bpy.context.object
        o.rotation_euler = (math.radians(90), 0, 0)
        o.name = f"finger_{k}"
        # Kuppe abrunden, sonst wirkt es wie ein Rohr
        m = o.modifiers.new("bev", 'BEVEL')
        m.width = 4.0; m.segments = 4; m.limit_method = 'ANGLE'
        m.angle_limit = math.radians(40); m.use_clamp_overlap = True
        o.data.materials.clear()
        o.data.materials.append(HAUT)


def beutel_entnahme(x=0, z=0):
    """Der vorderste Beutel, an der Oberkante gefasst und nach vorne
    herausgezogen - der Vorgang, um den es beim Greifraum geht."""
    global _BEUTEL_MESH
    if _BEUTEL_MESH is None:
        _BEUTEL_MESH = beutel_mesh()
    o = bpy.data.objects.new("beutel_entnahme", _BEUTEL_MESH)
    # Der Beutel kippt beim Herausziehen ueber die Frontwandkante nach
    # vorne: der Fuss steht noch im Kanal, die Oberkante steht frei.
    # Vorher stand er senkrecht bei y = 3 und damit MITTEN in der
    # Frontwand - das war der sichtbare Durchdringungsfehler im Bild.
    kipp = 25.0
    fuss_y = 4.5                       # knapp hinter der Anschlagwand
    o.rotation_euler = (math.radians(-kipp), 0, 0)
    o.location = (x + WAND + SPIEL / 2 + BB / 2,
                  fuss_y - BH / 2 * math.sin(math.radians(kipp)),
                  z + BODEN + BH / 2 * math.cos(math.radians(kipp)))
    o.data.materials.clear()
    o.data.materials.append(FOLIE)
    bpy.context.collection.objects.link(o)
    return o


# --------------------------------------------------------------- Szenen
if SZENE == "kanal":
    kanal(); schild_an(); beutel(11); schieber_bei(11)
elif SZENE == "explosion":
    kanal(luecke=70); schild_an()
    put(s_schb, (1.8, LF + LM + 2 * 70 + 60, BODEN), ORANGE)
elif SZENE == "gefuellt":
    kanal(); schild_an(); beutel(13); schieber_bei(13)
elif SZENE == "ebene":
    # Eine vollstaendige Ebene. Die aeusseren Spalten sind links- bzw.
    # rechts-Varianten, sonst zeigte das Bild Taschen ins Leere.
    for i in range(5):
        kanal(x=i * AX, ebene="unten", spalte=SPALTEN_N[rand(i, 5)])
        schild_an(x=i * AX, nr=i)
    beutel(16); schieber_bei(16)
    beutel(9, x=AX); schieber_bei(9, x=AX)
elif SZENE == "gesamt":
    bpy.ops.mesh.primitive_plane_add(size=1, location=(238, 240, -3))
    bd = bpy.context.object; bd.scale = (700, 700, 1)
    bd.data.materials.append(HOLZ)
    fuell = [[18, 11, 15, 7, 13], [14, 17, 9, 12, 6], [10, 8, 16, 5, 13]]
    for e in range(3):
        for i in range(5):
            kanal(x=i * AX, z=e * AZ,
                  ebene=EBENEN_N[rand(e, 3)], spalte=SPALTEN_N[rand(i, 5)])
            schild_an(x=i * AX, z=e * AZ, nr=e * 5 + i)
            beutel(fuell[e][i], x=i * AX, z=e * AZ)
            schieber_bei(fuell[e][i], x=i * AX, z=e * AZ)
elif SZENE == "entnahme":
    # Nur der vordere Ausschnitt: ein Frontsegment und darueber das
    # naechste. Der ganze Kanal wuerde die Kamera so weit zuruecknehmen,
    # dass vom Vorgang nichts mehr zu erkennen ist.
    put(seg("front", "mitte", "mitte"), (0, 0, 0), SCHWARZ)
    put(seg("front", "oben", "mitte"), (0, 0, AZ), SCHWARZ)
    schild_an()
    beutel(7)
    beutel_entnahme()
    # Bewusst ohne Hand: zwei Zylinder als Finger sahen aus wie Wuerste
    # und lagen neben dem Beutel statt an ihm. Den Massnachweis fuehrt
    # das Zugriffsblatt der Zeichnungen, dort passt eine Silhouette.
elif SZENE == "greifraum":
    # Derselbe Ausschnitt ohne Hand, dafuer mit freiem Blick auf den Spalt
    # zwischen Beutelkante und der Ebene darueber.
    put(seg("front", "mitte", "mitte"), (0, 0, 0), SCHWARZ)
    put(seg("front", "oben", "mitte"), (0, 0, AZ), SCHWARZ)
    schild_an()
    beutel(8)
elif SZENE == "wanne":
    # Blick von hinten oben in den Schieberfuss: dort sitzt die Wanne mit
    # dem gekauften Federgehaeuse. Ohne eigenes Bild musste sich die
    # Teileuebersicht bisher das Schieberbild teilen - zwei verschiedene
    # Teile mit derselben Abbildung.
    put(s_schb, (0, 0, 0), ORANGE)
    if BAUART == "pusher":
        bpy.ops.mesh.primitive_cube_add(size=1)
        o = bpy.context.object
        o.scale = (PUSH_B, PUSH_L, PUSH_H)
        o.location = ((BB + SPIEL) / 2, 4 + PUSH_L / 2, 3.0 + PUSH_H / 2)
        o.name = "federgehaeuse"
        o.data.materials.clear()
        o.data.materials.append(GEHAEUSE)
elif SZENE == "varianten":
    # Die drei Ebenenlagen nebeneinander. Der Unterschied sitzt oben und
    # unten: unten ohne Taschen im Boden, oben ohne Zapfen, mitte mit
    # beidem. Im Verbund sieht man das nicht mehr - hier schon.
    for i, lage in enumerate(("unten", "mitte", "oben")):
        put(seg("front", lage, "mitte"), (i * (AX + 26), 0, 0), SCHWARZ)
elif SZENE == "varianten_spalte":
    # Dasselbe fuer die Spaltenlagen. Der Unterschied ist die
    # Verbindertasche am Bodenrand, deshalb von schraeg unten betrachtet.
    for i, lage in enumerate(("links", "mitte", "rechts")):
        put(seg("front", "mitte", lage), (i * (AX + 26), 0, 0), SCHWARZ)
elif SZENE == "schild":
    put(s_schd, (0, 0, 0), ORANGE, bevel=0.1)
    put(s_txt, (0, 0, 0.02), SCHWARZ, bevel=0)
elif SZENE.startswith("schild:"):
    # Ein einzelnes Sortenschild, gerendert wie alle anderen Teile - damit
    # die Farben zu den uebrigen Bildern passen. Aufruf: schild:03-lachs
    # Die Schilder sind oben schon geladen - ein zweiter Import derselben
    # Datei liefert kein neues Objekt und legte sonst zwei Platten uebereinander.
    pl, tx = SORTE_NACH_NAME[SZENE.split(":", 1)[1]]
    put(pl, (0, 0, 0), ORANGE, bevel=0)
    put(tx, (0, 0, 0.03), SCHWARZ, bevel=0)
elif SZENE == "schieber":
    put(s_schb, (0, 0, 0), ORANGE)
elif SZENE in ("front", "mitte", "end"):
    # Einzelteil in der Mittellage - die Variante mit allen Merkmalen:
    # Zapfen oben, Taschen unten, Verbindertaschen zu beiden Seiten.
    put(seg(SZENE, "mitte", "mitte"), (0, 0, 0), SCHWARZ)
    if SZENE == "front": schild_an()

# --------------------------------------------------------------- Licht
def area(loc, rot, size, energy, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.object.data
    L.size = size; L.energy = energy; L.color = color
    bpy.context.object.rotation_euler = rot

# Bezugsgröße der Szene bestimmen
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.hide_render]
xs = [v[0] for o in objs for v in o.bound_box_world] if False else None
import mathutils
mn = mathutils.Vector((1e9, 1e9, 1e9)); mx = mathutils.Vector((-1e9, -1e9, -1e9))
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ mathutils.Vector(c)
        mn = mathutils.Vector((min(mn[i], w[i]) for i in range(3)))
        mx = mathutils.Vector((max(mx[i], w[i]) for i in range(3)))
ctr = (mn + mx) / 2
diag = (mx - mn).length

area((ctr.x - 0.35 * diag, mn.y - 0.9 * diag, mx.z + 0.9 * diag),
     (math.radians(30), 0, 0), diag * 1.3, diag * diag * 26)
area((mx.x + 0.9 * diag, ctr.y, mx.z + 0.4 * diag),
     (math.radians(70), 0, math.radians(-60)), diag * 0.8, diag * diag * 9,
     (1.0, 0.95, 0.88))
area((mn.x - 0.9 * diag, ctr.y + 0.3 * diag, mx.z + 0.3 * diag),
     (math.radians(75), 0, math.radians(62)), diag * 0.8, diag * diag * 6,
     (0.86, 0.91, 1.0))

w = bpy.context.scene.world
if w is None:
    w = bpy.data.worlds.new("W"); bpy.context.scene.world = w
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.86, 0.88, 0.92, 1)
bg.inputs[1].default_value = 1.5

# --------------------------------------------------------------- Kamera
bpy.ops.object.camera_add()
cam = bpy.context.object
cam.data.lens = 62
cam.data.sensor_fit = 'HORIZONTAL'

az = {"gesamt": 27, "ebene": 25, "kanal": 30, "gefuellt": 90,
      "explosion": 22, "schild": 40, "schieber": 38}.get(SZENE, 34)
el = {"gefuellt": 0, "gesamt": 28, "ebene": 27, "schild": 34}.get(SZENE, 25)

a, e = math.radians(az), math.radians(el)
richtung = mathutils.Vector((math.sin(a) * math.cos(e),
                             -math.cos(a) * math.cos(e),
                             math.sin(e)))
cam.location = ctr + richtung * diag
cam.rotation_euler = (ctr - mathutils.Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
bpy.context.view_layer.update()

sichtbar = [o for o in bpy.context.scene.objects
            if o.type == 'MESH' and not o.hide_render]

def punkte_in_kamera(cam, objekte):
    """Alle Vertices im Kamerakoordinatensystem, bezogen auf das Zentrum."""
    R = cam.matrix_world.to_3x3().transposed()
    out = []
    for o in objekte:
        m = o.matrix_world
        me = o.data
        quelle = me.vertices if len(me.vertices) else None
        if quelle is not None:
            out.extend(R @ ((m @ v.co) - ctr) for v in quelle)
        else:
            out.extend(R @ ((m @ mathutils.Vector(c)) - ctr) for c in o.bound_box)
    return out

# Silhouette messen und daraus das Bildformat ableiten, damit kein
# Leerraum entsteht. Erst grob bei fester Distanz projizieren.
P = punkte_in_kamera(cam, sichtbar)
d0 = diag * 2.2
sx = max(abs(v.x) / (d0 - v.z) for v in P)
sy = max(abs(v.y) / (d0 - v.z) for v in P)
seite = max(0.55, min(3.4, sx / sy))          # Breite zu Hoehe

BASIS = 2_600_000                              # Zielflaeche in Pixeln
ry = int(round((BASIS / seite) ** 0.5 / 2) * 2)
rx = int(round(ry * seite / 2) * 2)
sc0 = bpy.context.scene
sc0.render.resolution_x, sc0.render.resolution_y = rx, ry

# Abstand und Bildmitte gemeinsam bestimmen. Die Silhouette liegt selten
# symmetrisch um das Objektzentrum - ohne Versatz klebt sie an einer Seite
# und laesst auf der anderen Luft.
tan_h = math.tan(cam.data.angle / 2)
tan_v = tan_h / (rx / ry)

d = max(max(abs(v.x) / tan_h + v.z, abs(v.y) / tan_v + v.z) for v in P) * 1.02
for _ in range(6):
    xs = [v.x / (d - v.z) for v in P]
    ys = [v.y / (d - v.z) for v in P]
    mx_, my_ = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    hx, hy = (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2
    # Abstand so, dass die halbe Ausdehnung genau ins Bild passt
    d = d * max(hx / tan_h, hy / tan_v) * 1.02
    if d <= 0:
        break
# endgueltige Lage der Silhouette bestimmen
xs = [v.x / (d - v.z) for v in P]
ys = [v.y / (d - v.z) for v in P]
mx_, my_ = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
cam.data.shift_x = mx_ / (2 * tan_h)
cam.data.shift_y = my_ / (2 * tan_h)

cam.location = ctr + richtung * d
cam.data.clip_start = max(1.0, d / 200)
cam.data.clip_end = d * 6
bpy.context.scene.camera = cam
print(f"FORMAT {rx}x{ry}  seite={seite:.2f}  abstand={d:.0f}")

# --------------------------------------------------------------- Render
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for dv in prefs.devices: dv.use = True
    sc.cycles.device = 'GPU'
except Exception as ex:
    print("CPU:", ex)
sc.cycles.samples = 320
sc.cycles.use_denoising = True
sc.render.film_transparent = False
sc.view_settings.look = 'None'
sc.view_settings.exposure = 0.3
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("FERTIG", OUT)
