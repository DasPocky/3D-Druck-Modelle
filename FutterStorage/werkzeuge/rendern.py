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
