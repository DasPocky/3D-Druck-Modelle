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


AX, AZ = 95.2, 144.8
SCHILD_B = _scad("schild_breite", 78.0)
LF, LM, LE = 163.0, 160.0, 161.6
BODEN = 4.8
BB, BH, BD = 88.0, 136.0, 19.0
WAND, SPIEL = 1.6, 4.0

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
FOLIE   = mat("Beutel",      (0.44, 0.45, 0.48),   rough=0.38, metal=0.25)
HOLZ    = mat("Boden",       (0.26, 0.19, 0.13),   rough=0.65)

s_front = imp("segment-front.stl")
s_mitte = imp("segment-mitte.stl")
s_end   = imp("segment-end.stl")
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

def kanal(x=0, z=0, luecke=0, segmente=3):
    put(s_front, (x, 0, z), SCHWARZ)
    for i in range(1, segmente - 1):
        put(s_mitte, (x, LF + i * (LM + luecke) - LM + luecke, z), SCHWARZ)
    put(s_end, (x, LF + (segmente - 2) * LM + (segmente - 1) * luecke, z), SCHWARZ)

def schild_an(x=0, z=0, nr=None):
    # Grundplatte orange, Schrift schwarz - Schild steht senkrecht in der Tasche
    pl, tx = SORTEN[nr % len(SORTEN)] if (nr is not None and SORTEN) else (s_schd, s_txt)
    put(pl, (x + (AX - SCHILD_B) / 2, -0.5, z + 6),
        ORANGE, rot=(math.radians(90), 0, 0), bevel=0.1)
    put(tx, (x + (AX - SCHILD_B) / 2, -0.5 - 0.62, z + 6),
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
        w = (v - 0.12) / 0.88
        g = lambda t: 1.0 / (1.0 + math.exp(8.0 * (t - 0.75)))
        f = (g(w) - g(1.0)) / (g(0.0) - g(1.0))
        return 0.032 + 0.968 * f

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
    put(s_schb, (x + 1.8, 4 + n * BD + 1, z + BODEN), ORANGE)

# --------------------------------------------------------------- Szenen
if SZENE == "kanal":
    kanal(); schild_an(); beutel(11); schieber_bei(11)
elif SZENE == "explosion":
    kanal(luecke=70); schild_an()
    put(s_schb, (1.8, LF + LM + 2 * 70 + 60, BODEN), ORANGE)
elif SZENE == "gefuellt":
    kanal(); schild_an(); beutel(13); schieber_bei(13)
elif SZENE == "ebene":
    for i in range(5): kanal(x=i * AX); schild_an(x=i * AX, nr=i)
    beutel(16); schieber_bei(16)
    beutel(9, x=AX); schieber_bei(9, x=AX)
elif SZENE == "gesamt":
    bpy.ops.mesh.primitive_plane_add(size=1, location=(238, 240, -3))
    bd = bpy.context.object; bd.scale = (700, 700, 1)
    bd.data.materials.append(HOLZ)
    fuell = [[18, 11, 15, 7, 13], [14, 17, 9, 12, 6], [10, 8, 16, 5, 13]]
    for e in range(3):
        for i in range(5):
            kanal(x=i * AX, z=e * AZ); schild_an(x=i * AX, z=e * AZ, nr=e * 5 + i)
            beutel(fuell[e][i], x=i * AX, z=e * AZ)
            schieber_bei(fuell[e][i], x=i * AX, z=e * AZ)
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
    put({"front": s_front, "mitte": s_mitte, "end": s_end}[SZENE],
        (0, 0, 0), SCHWARZ)
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
