#!/usr/bin/env python3
"""Baut das Gesamtpaket: index, Bauanleitung, Technikdoku - alle ASCII-sicher."""
import base64, os, re, shutil, zipfile

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAKET = os.path.join(PROJ, "paket")


# Sprechende Dateinamen im Paket - die Seiten verlinken echte Dateien statt
# base64. So laedt die Seite schnell und jedes Bild ist einzeln zu oeffnen.
NAMEN = {"b_front": "01-segment-front", "b_mitte": "02-segment-mitte",
         "b_end": "03-segment-end", "b_schieber": "04-schieber",
         "b_schild": "05-schild", "b_kanal": "06-kanal-komplett",
         "b_explosion": "07-explosion", "b_gefuellt": "08-funktionsprinzip",
         "b_ebene": "09-eine-ebene", "b_gesamt": "10-vollausbau"}

TITEL = {"b_front": ("Frontsegment", "Vorderstes Kanalstueck mit Frontwand, "
                     "Griffmulde und Schildtasche"),
         "b_mitte": ("Mittelsegment", "Beliebig oft wiederholbar, verlaengert den Kanal"),
         "b_end": ("Endsegment", "Schliesst den Kanal hinten ab"),
         "b_schieber": ("Schieber", "Traegt die Konstantkraftfeder und schiebt den Stapel"),
         "b_schild": ("Schild", "Steckt in der Frontwand und nennt die Sorte"),
         "b_kanal": ("Kanal komplett", "Front-, Mittel- und Endsegment zusammengesteckt"),
         "b_explosion": ("Explosionsdarstellung", "Die drei Segmente und der Schieber "
                         "in Reihenfolge"),
         "b_gefuellt": ("Funktionsprinzip", "Die Feder haelt den Stapel vorne am Anschlag"),
         "b_ebene": ("Eine Ebene", "Fuenf Kanaele nebeneinander, unterschiedlich gefuellt"),
         "b_gesamt": ("Vollausbau", "Drei Ebenen mit fuenfzehn Sorten im Schrank")}

ZTITEL = {"01-frontsegment": ("Frontsegment", "Vorder-, Seiten- und Draufsicht "
                              "mit allen Massen"),
          "02-mittel-endsegment": ("Mittel- und Endsegment", "Beide Bauteile plus "
                                   "gemeinsamer Querschnitt"),
          "03-schieber-schild": ("Schieber, Schild und Achse", "Federkammer, "
                                 "Schildplatte und Zukaufteil"),
          "04-gesamtanordnung": ("Gesamtanordnung", "Wie die Teile im Schrank stehen"),
          "05-beutel-passung": ("Beutel und Passung", "Die gemessenen Beutelmasse "
                                "als Grundlage"),
          "06-verbindungen": ("Verbindungen", "Stapelzapfen und Seitennase im "
                              "Schnitt"),
          "07-zugriff": ("Zugriff", "Wo die Hand hinkommt, auch bei "
                         "gestapelten Ebenen")}

R = {n: f"web/{NAMEN[n]}.jpg" for n in NAMEN}          # fuer die Seiten
V = {n: f"bilder/{NAMEN[n]}.png" for n in NAMEN}       # volle Aufloesung
Z = {n: f"zeichnungen/{n}.svg" for n in ZTITEL}

UML = {"ä": "&auml;", "ö": "&ouml;", "ü": "&uuml;", "Ä": "&Auml;", "Ö": "&Ouml;",
       "Ü": "&Uuml;", "ß": "&szlig;", "—": "&mdash;", "–": "&ndash;",
       "„": "&bdquo;", "“": "&ldquo;", "€": "&euro;", "·": "&middot;",
       "×": "&times;", "≤": "&le;", "→": "&rarr;"}


# Der Fliesstext ist in ASCII-Umschrift getippt. Diese Tabelle setzt die
# richtige deutsche Schreibung wieder ein, bevor daraus Entities werden.
RECHT = {
 "aenderbar": "änderbar", "Aendert": "Ändert", "aeusserste": "äußerste",
 "anfaengt": "anfängt", "Anlaufschraege": "Anlaufschräge", "Aufloesung": "Auflösung",
 "aussen": "außen", "ausserhalb": "außerhalb", "Befuellen": "Befüllen",
 "befuellten": "befüllten", "bemasste": "bemaßte", "bemassten": "bemaßten",
 "Beutelhoehe": "Beutelhöhe", "Beutelmasse": "Beutelmaße",
 "Bildaufloesung": "Bildauflösung", "Blaetter": "Blätter", "Blaettern": "Blättern",
 "Blattgroesse": "Blattgröße", "Bodenhoehe": "Bodenhöhe", "Bruecken": "Brücken",
 "Buendig": "Bündig", "Dafuer": "Dafür", "darueber": "darüber", "drueckt": "drückt",
 "duenne": "dünne", "Duese": "Düse", "Durchblaettern": "Durchblättern",
 "Ebenenhoehe": "Ebenenhöhe", "eingepraegt": "eingeprägt", "einhaengen": "einhängen",
 "erhoehen": "erhöhen", "Erklaerung": "Erklärung", "faellt": "fällt",
 "Flaeche": "Fläche", "Flaechen": "Flächen", "Flaechennormalen": "Flächennormalen",
 "Folienoberflaeche": "Folienoberfläche", "fruehere": "frühere", "fuehren": "führen",
 "Fuellung": "Füllung", "Fuenf": "Fünf", "fuenf": "fünf",
 "fuenfundzwanzig": "fünfundzwanzig", "fuenfzehn": "fünfzehn", "fuer": "für",
 "Fuss": "Fuß", "geaendert": "geändert", "gefuellt": "gefüllt",
 "geschaetzt": "geschätzt", "gleichmaessig": "gleichmäßig", "gross": "groß",
 "Groesse": "Größe", "grossen": "großen", "Gruende": "Gründe",
 "Grundkoerper": "Grundkörper", "haelt": "hält", "haengen": "hängen",
 "haengt": "hängt", "haette": "hätte", "hinterliessen": "hinterließen",
 "Hoehe": "Höhe", "Innenmass": "Innenmaß", "Kanaele": "Kanäle",
 "Kanalstueck": "Kanalstück", "klaeren": "klären", "Koerper": "Körper",
 "kuerzen": "kürzen", "laedt": "lädt", "Laenge": "Länge", "laengste": "längste",
 "laesst": "lässt", "laeuft": "läuft", "Loecher": "Löcher", "loesen": "lösen",
 "loeste": "löste", "Mass": "Maß", "Massblaetter": "Maßblätter", "Masse": "Maße",
 "Massen": "Maßen", "Masslinie": "Maßlinie", "Masslinien": "Maßlinien",
 "Mittelstuecke": "Mittelstücke", "Modellaenderung": "Modelländerung",
 "Modellmassen": "Modellmaßen", "Moeglichkeit": "Möglichkeit", "muessen": "müssen",
 "Nachfuellen": "Nachfüllen", "naechste": "nächste", "naechsten": "nächsten",
 "Oeffne": "Öffne", "oeffnen": "öffnen", "Projektuebersicht": "Projektübersicht",
 "pruefen": "prüfen", "Pruefer": "Prüfer", "Pruefinstanz": "Prüfinstanz",
 "Pruefskript": "Prüfskript", "prueft": "prüft", "pruefte": "prüfte",
 "Pruefung": "Prüfung", "Pruefungen": "Prüfungen", "Python-Pruefung": "Python-Prüfung",
 "Qualitaet": "Qualität", "Rueckwaende": "Rückwände", "Schichthoehe": "Schichthöhe",
 "Schliessen": "Schließen", "Schliesst": "Schließt", "Schnittkoerper": "Schnittkörper",
 "Schritt-fuer-Schritt-Montage": "Schritt-für-Schritt-Montage",
 "Schweissdraht": "Schweißdraht", "Seitenverhaeltnis": "Seitenverhältnis",
 "Staerken": "Stärken", "staerkere": "stärkere", "Standflaeche": "Standfläche",
 "stiess": "stieß", "Stossflaechen": "Stoßflächen", "Stueck": "Stück",
 "Stueckliste": "Stückliste", "Stuecks": "Stücks", "Stuetzen": "Stützen",
 "Traegt": "Trägt", "ueber": "über", "Ueber": "Über", "ueberbrueckt": "überbrückt",
 "ueberdeckt": "überdeckt", "uebereinander": "übereinander",
 "Ueberhaenge": "Überhänge", "Ueberhang": "Überhang",
 "Ueberschneidung": "Überschneidung", "Ueberschnitt": "Überschnitt",
 "ueberschreibt": "überschreibt", "Uebersicht": "Übersicht",
 "ueberstehen": "überstehen", "Uebrig": "Übrig", "urspruengliche": "ursprüngliche",
 "vergroessern": "vergrößern", "vergroessert": "vergrößert",
 "verlaengert": "verlängert", "veroeffentlicht": "veröffentlicht",
 "Verpackungsmasse": "Verpackungsmaße", "Vollkoerper": "Vollkörper",
 "Vorgaenger": "Vorgänger", "waechst": "wächst", "waehlen": "wählen",
 "waehrend": "während", "Waende": "Wände", "Waenden": "Wänden", "waere": "wäre",
 "waeren": "wären", "Wandstaerke": "Wandstärke", "Wandstaerken": "Wandstärken",
 "weiss": "weiß", "wofuer": "wofür", "Zeichnungsblaetter": "Zeichnungsblätter",
 "zurueck": "zurück", "zurueckgerechnet": "zurückgerechnet",
 "Zurueckziehen": "Zurückziehen", "zurueckziehen": "zurückziehen",
 "zusaetzlich": "zusätzlich", "Zusammenhaenge": "Zusammenhänge",
 "Massaenderung": "Maßänderung", "aendert": "ändert", "aendern": "ändern",
 "Datenblaetter": "Datenblätter", "Fuer": "Für", "Oeffnungen": "Öffnungen",
 "Oeffnung": "Öffnung", "Seitenwaende": "Seitenwände",
 "aeussersten": "äußersten", "dafuer": "dafür", "duennen": "dünnen",
 "duenn": "dünn", "guenstig": "günstig", "hoeher": "höher",
 "schwaecht": "schwächt", "ueberall": "überall", "wuerde": "würde",
 "wuerden": "würden", "zaehlt": "zählt", "zusammenhaelt": "zusammenhält",
 "naechster": "nächster", "spaeter": "später", "waehlt": "wählt",
 "erhoehen": "erhöhen", "erhoeht": "erhöht", "koennen": "können",
 "koennte": "könnte", "moeglich": "möglich", "noetig": "nötig",
 "groesser": "größer", "kuerzer": "kürzer", "laenger": "länger",
 "haeufig": "häufig", "ungefaehr": "ungefähr", "Aussenkante": "Außenkante",
 "schliesst": "schließt", "hoerbar": "hörbar", "buendig": "bündig", "Bodenraendern": "Bodenrändern", "genuegt": "genügt", "Aussenkante": "Außenkante", "Aussenkanten": "Außenkanten", "kraeftiger": "kräftiger", "Loesen": "Lösen", "stoeren": "stören", "Bloecken": "Blöcken", "Bloecke": "Blöcke", "Zwoelf": "Zwölf",
 "blaettert": "blättert", "Sortenschilder": "Sortenschilder",
}
# ---------------------------------------------------------------- Code
# Syntaxhervorhebung ohne Fremdbibliothek: der Text wird einmal zerlegt und
# jedes Stueck bekommt eine Klasse. Kommentare und Zeichenketten werden
# zuerst gefasst, damit darin keine Schluesselwoerter markiert werden.
SCHLUESSEL = {
    "openscad": r"\b(module|function|if|else|for|let|include|use|true|false|"
                r"union|difference|intersection|hull|translate|rotate|scale|"
                r"mirror|linear_extrude|rotate_extrude|cube|cylinder|sphere|"
                r"circle|square|polygon|text|echo|str|min|max|len|floor|sin|cos)\b",
    "python":   r"\b(def|class|return|if|elif|else|for|while|in|not|and|or|"
                r"import|from|as|with|try|except|finally|lambda|None|True|False|"
                r"yield|break|continue|pass|raise|global)\b",
    "bash":     r"\b(for|do|done|if|then|fi|else|in|while|case|esac|function|"
                r"export|echo|cd|mkdir|python3|openscad|blender)\b",
}
_KOM = {"openscad": r"//[^\n]*|/\*.*?\*/", "python": r"#[^\n]*", "bash": r"#[^\n]*"}


def code(text, sprache="openscad"):
    """Gibt den Text als hervorgehobenen <pre>-Block zurueck."""
    stuecke, rest = [], text
    muster = re.compile(
        f'(?P<kom>{_KOM.get(sprache, "#[^\\n]*")})'
        r'|(?P<str>"[^"\n]*"|\'[^\'\n]*\')'
        r"|(?P<zahl>\b\d+(?:\.\d+)?\b)"
        f'|(?P<key>{SCHLUESSEL.get(sprache, "")})'
        r"|(?P<fn>\b[a-zA-Z_][\w]*(?=\())", re.S)
    pos = 0
    for m in muster.finditer(text):
        if m.start() > pos:
            stuecke.append(_esc(text[pos:m.start()]))
        art = m.lastgroup
        stuecke.append(f'<span class="c-{art}">{_esc(m.group(0))}</span>')
        pos = m.end()
    stuecke.append(_esc(text[pos:]))
    kopf = ('<div class="kopf"><span class="punkt"></span><span class="punkt">'
            '</span><span class="punkt"></span>'
            f'<span class="spr">{sprache}</span></div>')
    return (f'<figure class="cd">{kopf}<pre><code>' + "".join(stuecke)
            + "</code></pre></figure>")


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def diagramm(titel, knoten, breite=760):
    """Ein schlichtes Flussdiagramm als SVG - ersetzt die frueheren
    ASCII-Kaesten, die je nach Schriftart auseinanderfielen.
    knoten: Liste aus (Text, Unterzeile, Spalte, Zeile)."""
    zh, zb, lu = 66, 200, 34
    zeilen = max(k[3] for k in knoten) + 1
    spalten = max(k[2] for k in knoten) + 1
    h = zeilen * zh + (zeilen - 1) * lu + 20
    b = max(breite, spalten * (zb + 40))
    el = [f'<svg viewBox="0 0 {b} {h}" width="100%" role="img" '
          f'aria-label="{titel}" style="max-width:{b}px">']
    mitte = {}
    for text, unter, sp, ze in knoten:
        x = (b - (spalten * zb + (spalten - 1) * 40)) / 2 + sp * (zb + 40)
        y = 10 + ze * (zh + lu)
        mitte[(sp, ze)] = (x + zb / 2, y, y + zh)
        el.append(
            f'<rect x="{x}" y="{y}" width="{zb}" height="{zh}" rx="2" '
            f'fill="var(--paper2)" stroke="var(--linie)" stroke-width="1.5"/>'
            f'<text x="{x+zb/2}" y="{y+27}" text-anchor="middle" font-size="14" '
            f'font-weight="650" fill="var(--ink)" '
            f'font-family="var(--sans)">{text}</text>'
            f'<text x="{x+zb/2}" y="{y+47}" text-anchor="middle" font-size="11.5" '
            f'fill="var(--grau)" font-family="var(--mono)">{unter}</text>')
    for (sp, ze), (cx, oben, unten) in mitte.items():
        if (sp, ze + 1) in mitte:
            zx = mitte[(sp, ze + 1)][0]
            el.append(f'<path d="M{cx} {unten} L{cx} {unten+lu-9}" '
                      f'stroke="var(--akzent)" stroke-width="1.6" fill="none"/>'
                      f'<path d="M{zx-4.5} {unten+lu-9} L{zx+4.5} {unten+lu-9} '
                      f'L{zx} {unten+lu-1} z" fill="var(--akzent)"/>')
    el.append("</svg>")
    return f'<figure class="dia">{"".join(el)}<figcaption>{titel}</figcaption></figure>'


# ---------------------------------------------------------------- Projekt
# Was jede Datei tut. Der Baum selbst wird aus dem Dateisystem gelesen,
# damit die Seite nicht behaupten kann, was gar nicht da ist.
ERKLAERT = {
    "modell/": "Die einzige Quelle der Geometrie",
    "modell/katzenfutter-regal.scad":
        "Das ganze Regal als Programm — alle Maße als Variablen",
    "werkzeuge/": "Skripte, die aus dem Modell alles Weitere erzeugen",
    "werkzeuge/stl-bauen.py":
        "Ruft OpenSCAD je Bauteil auf, prüft auf Kollision",
    "werkzeuge/pruefen.py":
        "Wasserdicht, Volumen, Überhänge, Bauraum, Passung",
    "werkzeuge/zeichnungen.py":
        "Bemaßte SVG-Blätter, prüft sich auf Überdeckungen",
    "werkzeuge/rendern.py":
        "Blender-Szene mit automatischer Kamerarahmung",
    "werkzeuge/schilder.py":
        "Ein Schild je Futtersorte, als STL und als Bild",
    "werkzeuge/seiten.py":
        "Baut diese Seiten und schnürt das ZIP",
    "stl/": "Druckfertige Dateien, direkt in den Slicer",
    "stl/schilder/": "Ein fertiges Schild je Sorte",
    "zeichnungen/": "Sieben bemaßte Blätter, beliebig skalierbar",
    "bilder/": "Renderings in voller Auflösung",
    "bilder/web/": "Dieselben Bilder klein, für die Seiten",
    "bilder/schilder/": "Alle Sortenschilder als Bild",
    "README.md": "Kurzfassung fürs Verzeichnis",
    "werkzeuge/abgleich.py": "Vergleicht Modell, STL, Zeichnungen und Bilder",
    "futterstorage.zip": "Alles zusammen, zum Verschicken",
}


def _uml(t):
    """Nur Umlaute zu Entities - ohne die Wortersetzung aus ent()."""
    for k, v in UML.items():
        t = t.replace(k, v)
    return t


def dateibaum(wurzel, tiefe=2):
    """Liest das Projektverzeichnis und gibt es als zweispaltige Liste aus:
    links der Baum, rechts die Erklaerung. Frueher stand beides in einer
    Zeile - lange Beschreibungen brachen um und zerrissen die Struktur."""
    ueber = {"paket", ".git", "__pycache__", ".DS_Store"}
    zeilen = []

    def geh(pfad, rel, ebene, praefix=""):
        try:
            eintraege = sorted(os.listdir(pfad))
        except OSError:
            return
        sicht = [e for e in eintraege if not e.startswith(".") and e not in ueber]
        ordner = [e for e in sicht if os.path.isdir(os.path.join(pfad, e))]
        dateien = [e for e in sicht if not os.path.isdir(os.path.join(pfad, e))]
        if len(dateien) > 4:
            dateien = dateien[:3] + [f"&#8230; und {len(dateien)-3} weitere"]
        alle = ordner + dateien
        for i, e in enumerate(alle):
            letzte = i == len(alle) - 1
            ast = "&#9492;&#9472;&#160;" if letzte else "&#9500;&#9472;&#160;"
            if e.startswith("&#8230;"):
                zeilen.append((f'{praefix}&#9492;&#9472;&#160;'
                               f'<span class="rest">{e}</span>', "", ""))
                continue
            voll = os.path.join(pfad, e)
            r = rel + e + ("/" if os.path.isdir(voll) else "")
            was = _uml(ERKLAERT.get(r, ""))
            if os.path.isdir(voll):
                n = len([x for x in os.listdir(voll) if not x.startswith(".")])
                zeilen.append((f'{praefix}{ast}<span class="ord">{e}/</span>',
                               was or f"{n} Dateien", ""))
                if ebene < tiefe:
                    geh(voll, r, ebene + 1,
                        praefix + ("&#160;&#160;&#160;&#160;" if letzte
                                   else "&#9474;&#160;&#160;&#160;"))
            else:
                gr = os.path.getsize(voll)
                grt = f"{gr/1024:.0f} kB" if gr < 1e6 else f"{gr/1048576:.1f} MB"
                zeilen.append((f"{praefix}{ast}{e}", was, grt))

    geh(wurzel, "", 0)
    reihen = "".join(
        f'<tr><td class="pf">{p}</td><td class="gr">{g}</td>'
        f'<td class="be">{w}</td></tr>' for p, w, g in zeilen)
    return ('<div class="baum"><table><thead><tr><th>Datei</th><th>Gr&#246;&#223;e</th>'
            f'<th>Wozu</th></tr></thead><tbody>{reihen}</tbody></table></div>')


_WORT = re.compile(r"[A-Za-z][A-Za-z-]*")
# Attributwerte, CSS, Skript und Codebeispiele bleiben unangetastet - dort
# stehen Klassennamen und Dateinamen, die nicht "korrigiert" werden duerfen.
_SCHUTZ = re.compile(r"<style>.*?</style>|<script>.*?</script>"
                     r"|<pre[^>]*>.*?</pre>|<code>.*?</code>"
                     r'|<div class="baum">.*?</div>|<svg.*?</svg>'
                     r'|\w[\w-]*="[^"]*"', re.S)


# Woerter, die tatsaechlich so geschrieben werden - alles andere mit ae/oe/ue
# oder ss im Fliesstext ist ein Fehler und wird beim Bauen gemeldet.
ERLAUBT = {
    "quer", "querschnitt", "quersteg", "zuerst", "neues", "neuer", "neue", "neu",
    "teuerste", "teuer", "umbauen", "steuert", "gesteuert", "steuerung",
    "silhouette", "sequenz", "aequivalent", "abenteuer", "erneuern", "feuer",
    "dass", "muss", "muessen", "lassen", "laesst", "passen", "passt", "passung",
    "passprobe", "passung", "presst", "fasst", "fassung", "messing", "wissen",
    "weiss", "gross", "bewusste", "kompromiss", "durchmesser", "loslassen",
    "passieren", "passiert", "musste", "quelle", "aussahen", "anfassen",
    "wasserdicht", "essen", "klasse", "prozess", "adresse", "interesse",
    "openscad-quelldatei", "gnu", "eu", "queue",
    "gemessen", "gemessene", "gemessenen", "gemessener", "bauen", "stl-bauen",
    "passend", "passende", "passenden", "zueinander", "quelldatei",
    "rollendurchmesser", "aussparung", "aussparungen", "fassen", "dasselbe",
    "bildausschnitt", "neuen", "beutel-passung", "g-nassfutterbeutel",
    "aufbauen", "einbauen", "umbauen", "anbauen", "zusammenbauen", "erbauen",
    "voraussetzung", "ausserdem", "ausser",
}
_VERDACHT = re.compile(r"\b[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß-]{2,}\b")


FUNDE = []
_AKT = {"datei": "?"}


def rechtschreibpruefung(html, datei):
    """Meldet Woerter, die noch in ASCII-Umschrift stehen. Attribute, Code
    und der Dateibaum bleiben aussen vor - dort sind es echte Bezeichner.
    Laeuft vor der Entity-Wandlung, solange die Umlaute noch Umlaute sind."""
    sicht = _SCHUTZ.sub(" ", html)
    fund = set()
    for w in _VERDACHT.findall(sicht):
        k = w.lower()
        if k in ERLAUBT or "&" in w:
            continue
        if re.search(r"ae|oe|ue|ss", k) and not re.search(r"[äöüß]", w):
            fund.add(w)
    return [f"{datei}: {w}" for w in sorted(fund)]


def ent(t):
    halde = []

    def merken(m):
        halde.append(m.group(0))
        return f"\x00{len(halde)-1}\x00"

    t = _SCHUTZ.sub(merken, t)
    t = _WORT.sub(lambda m: RECHT.get(m.group(0), m.group(0)), t)
    FUNDE.extend(rechtschreibpruefung(t, _AKT["datei"]))
    t = re.sub(r"\x00(\d+)\x00", lambda m: halde[int(m.group(1))], t)
    for k, v in UML.items():
        t = t.replace(k, v)
    return t


CSS = """
:root{--ink:#17171b;--ink2:#3d3d43;--paper:#f7f5f2;--paper2:#fff;--akzent:#bd4d0a;
--grau:#6e6a65;--linie:#e3ded7;--code:#eee9e2;--bild:#d7d8dc;
--schatten:0 1px 2px rgba(23,23,27,.05),0 10px 28px rgba(23,23,27,.05);
--sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
--mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
@media(prefers-color-scheme:dark){:root{--ink:#eceae6;--ink2:#bcb8b1;--paper:#131316;
--paper2:#1c1c21;--akzent:#ff8a47;--grau:#918c85;--linie:#2d2d33;--code:#232329;
--bild:#25252a;--schatten:0 1px 2px rgba(0,0,0,.45),0 10px 28px rgba(0,0,0,.32)}}
:root[data-theme=dark]{--ink:#eceae6;--ink2:#bcb8b1;--paper:#131316;--paper2:#1c1c21;
--akzent:#ff8a47;--grau:#918c85;--linie:#2d2d33;--code:#232329;--bild:#25252a;
--schatten:0 1px 2px rgba(0,0,0,.45),0 10px 28px rgba(0,0,0,.32)}
:root[data-theme=light]{--ink:#17171b;--ink2:#3d3d43;--paper:#f7f5f2;--paper2:#fff;
--akzent:#bd4d0a;--grau:#6e6a65;--linie:#e3ded7;--code:#eee9e2;--bild:#d7d8dc;
--schatten:0 1px 2px rgba(23,23,27,.05),0 10px 28px rgba(23,23,27,.05)}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
font-size:16.5px;line-height:1.68;-webkit-font-smoothing:antialiased}
.wrap{max-width:1160px;margin:0 auto;padding:0 26px 110px}
.text{max-width:70ch}
nav{border-bottom:1px solid var(--linie);margin-bottom:0}
nav .in{max-width:1160px;margin:0 auto;padding:14px 26px;display:flex;gap:26px;
align-items:baseline;flex-wrap:wrap}
nav a{color:var(--grau);text-decoration:none;font-size:.92rem}
nav a:hover{color:var(--akzent)}
nav a.hier{color:var(--ink);font-weight:600}
nav .marke{font-family:var(--mono);font-size:.8rem;letter-spacing:.12em;
text-transform:uppercase;color:var(--akzent);margin-right:auto}
header{padding:66px 0 32px;border-bottom:2px solid var(--ink)}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.15em;
text-transform:uppercase;color:var(--akzent);margin:0 0 14px}
h1{font-size:clamp(2rem,5vw,3.1rem);line-height:1.06;margin:0 0 18px;
letter-spacing:-.026em;font-weight:780;text-wrap:balance;max-width:17ch}
.lead{font-size:1.12rem;color:var(--ink2);margin:0;max-width:62ch}
.kz-reihe{display:grid;grid-template-columns:repeat(auto-fit,minmax(124px,1fr));
gap:1px;background:var(--linie);border:1px solid var(--linie);margin:40px 0 0}
.kz{background:var(--paper);padding:16px 18px}
.kz b{display:block;font-family:var(--mono);font-size:1.5rem;font-weight:600;
letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.kz span{font-size:12.5px;color:var(--grau)}
section{padding-top:70px}
h2{font-size:1.58rem;letter-spacing:-.02em;margin:0 0 6px;font-weight:720;
display:flex;align-items:baseline;gap:14px}
h2::before{content:attr(data-nr);font-family:var(--mono);font-size:.8rem;
color:var(--akzent);font-weight:500}
h3{font-size:1.07rem;margin:34px 0 8px;font-weight:670}
h4{font-size:.99rem;margin:20px 0 6px;font-weight:660}
.unter{color:var(--grau);margin:0 0 22px;font-size:.96rem;max-width:66ch}
p{margin:0 0 15px}
ul,ol{margin:0 0 15px;padding-left:20px}
li{margin-bottom:7px}
a{color:var(--akzent);text-underline-offset:2px}
.karten{display:grid;grid-template-columns:repeat(auto-fit,minmax(288px,1fr));gap:22px}
.karten{align-items:stretch}
.karte{background:var(--paper2);border:1px solid var(--linie);
box-shadow:var(--schatten);display:flex;flex-direction:column}
.karte figure{aspect-ratio:4/3;overflow:hidden;display:flex}
.karte img{object-fit:contain;height:100%}
.karte figure{margin:0;background:var(--bild)}
.karte img{display:block;width:100%;height:auto}
.karte .txt{padding:16px 18px 19px;display:flex;flex-direction:column;gap:9px;flex:1}
.karte h4{margin:0;font-size:1.02rem;font-weight:690}
.dat{font-family:var(--mono);font-size:12.5px;color:var(--grau);
font-variant-numeric:tabular-nums}
.karte p{margin:0;font-size:.93rem;color:var(--ink2)}
.anz{align-self:flex-start;font-family:var(--mono);font-size:11.5px;letter-spacing:.05em;
text-transform:uppercase;background:var(--akzent);color:#fff;padding:3px 9px}
:root[data-theme=dark] .anz{color:#17171b}
@media(prefers-color-scheme:dark){.anz{color:#17171b}}
figure.gross{margin:26px 0 6px;background:var(--bild);border:1px solid var(--linie)}
figure.gross img{display:block;width:100%;height:auto}
figure.plan{margin:26px 0 6px;background:#f7f5f2;border:1px solid var(--linie);padding:0}
figure.plan img{display:block;width:100%;height:auto}
figcaption{font-size:.89rem;color:var(--grau);padding:10px 2px 0;max-width:78ch}
.kauf{border:2px solid var(--akzent);background:var(--paper2);padding:24px 26px;
margin:22px 0 8px}
.kauf h3{margin-top:0}
.kauf dl{display:grid;grid-template-columns:max-content 1fr;gap:8px 22px;margin:0}
.kauf dt{font-family:var(--mono);font-size:12.5px;color:var(--grau)}
.kauf dd{margin:0}
.tab{overflow-x:auto;margin:20px 0;border:1px solid var(--linie)}
table{border-collapse:collapse;width:100%;font-size:.93rem;background:var(--paper2)}
th,td{text-align:left;padding:11px 15px;border-bottom:1px solid var(--linie);
white-space:nowrap}
th{font-family:var(--mono);font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;
color:var(--grau);font-weight:500;background:var(--code)}
td.num{font-family:var(--mono);font-variant-numeric:tabular-nums}
td.w{white-space:normal;min-width:210px}
tbody tr:last-child td{border-bottom:none}
tfoot td{font-weight:650;background:var(--code);border-bottom:none}
ol.schritte{list-style:none;counter-reset:s;padding:0;margin:24px 0 0;max-width:74ch}
ol.schritte>li{counter-increment:s;position:relative;padding:0 0 26px 52px;
border-left:1px solid var(--linie);margin-left:15px}
ol.schritte>li:last-child{border-left-color:transparent;padding-bottom:0}
ol.schritte>li::before{content:counter(s);position:absolute;left:-15px;top:-3px;
width:30px;height:30px;border-radius:50%;background:var(--ink);color:var(--paper);
font-family:var(--mono);font-size:13px;font-weight:600;display:grid;place-items:center}
ol.schritte h4{margin:3px 0 6px;font-size:1.03rem;font-weight:680}
ol.schritte p{font-size:.96rem;color:var(--ink2)}
.hinweis{border-left:3px solid var(--akzent);padding:2px 0 2px 17px;margin:18px 0;
color:var(--ink2);font-size:.96rem;max-width:70ch}
code{font-family:var(--mono);font-size:.89em;background:var(--code);padding:1px 5px}
pre{background:var(--code);padding:16px 18px;overflow-x:auto;font-family:var(--mono);
font-size:.84rem;line-height:1.55;margin:14px 0;border-left:3px solid var(--linie)}
pre code{background:none;padding:0}
.kachel{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px;
margin:30px 0 0}
.kachel{align-items:stretch}
.kachel a{display:flex;flex-direction:column;background:var(--paper2);
border:1px solid var(--linie);padding:22px 24px;text-decoration:none;
color:var(--ink);box-shadow:var(--schatten)}
.kachel a p{margin-bottom:0}
.kachel a:hover{border-color:var(--akzent)}
.kachel .nr{font-family:var(--mono);font-size:.76rem;letter-spacing:.1em;
color:var(--akzent);text-transform:uppercase}
.kachel h3{margin:8px 0 6px;font-size:1.12rem}
.kachel p{margin:0;font-size:.93rem;color:var(--grau)}
footer{margin-top:80px;padding-top:20px;border-top:1px solid var(--linie);
font-size:.87rem;color:var(--grau)}
/* Codeblock: eigener dunkler Grund, damit die Hervorhebung in beiden
   Themes identisch und kontraststark bleibt. */
figure.cd{margin:22px 0 6px;border-radius:8px;overflow:hidden;
background:#1b1d23;border:1px solid #2b2e37;box-shadow:var(--schatten)}
figure.cd .kopf{display:flex;align-items:center;gap:9px;padding:9px 14px;
background:#22252d;border-bottom:1px solid #2b2e37}
figure.cd .punkt{width:9px;height:9px;border-radius:50%;background:#3a3e49;flex:none}
figure.cd .spr{margin-left:4px;font-family:var(--mono);font-size:11px;
letter-spacing:.1em;text-transform:uppercase;color:#8b91a1}
figure.cd pre{margin:0;padding:16px 18px;background:none;border:none;
font-size:.85rem;line-height:1.62;color:#d6dae4;overflow-x:auto}
figure.cd code{background:none;padding:0;color:inherit}
.c-kom{color:#6b7385;font-style:italic}
.c-str{color:#9ecb8a}
.c-zahl{color:#e0a458}
.c-key{color:#c98cf1;font-weight:600}
.c-fn{color:#78b8f0}
figure.dia{margin:26px 0 6px;padding:22px 18px;background:var(--paper2);
border:1px solid var(--linie);overflow-x:auto}
figure.dia svg{display:block;margin:0 auto}
figure.dia figcaption{padding-top:14px;text-align:center}
nav.toc{margin:38px 0 0;padding:22px 26px;background:var(--paper2);
border:1px solid var(--linie);box-shadow:var(--schatten)}
nav.toc ol{list-style:none;margin:0;padding:0;display:grid;
grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:2px 30px}
nav.toc li{margin:0}
nav.toc a{display:flex;gap:12px;align-items:baseline;padding:6px 0;
text-decoration:none;color:var(--ink);font-size:.95rem;border-bottom:1px solid transparent}
nav.toc a:hover{color:var(--akzent)}
nav.toc .tnr{font-family:var(--mono);font-size:.78rem;color:var(--akzent);
min-width:1.6em;font-variant-numeric:tabular-nums}
h2{scroll-margin-top:22px}
.klein{font-size:.86em;color:var(--grau)}
ul.quellen{list-style:none;padding:0;margin:14px 0 18px}
ul.quellen li{margin-bottom:9px;display:flex;gap:12px;align-items:baseline;
flex-wrap:wrap}
ul.quellen a{font-weight:600;text-decoration:none;border-bottom:1px solid var(--linie)}
ul.quellen a:hover{border-color:var(--akzent)}
td.w strong{font-weight:660}
.baum{margin:18px 0;border:1px solid var(--linie);overflow-x:auto}
.baum table{border-collapse:collapse;width:100%;background:var(--paper2);
font-size:.88rem}
.baum th{font-family:var(--mono);font-size:11px;letter-spacing:.07em;
text-transform:uppercase;color:var(--grau);font-weight:500;background:var(--code);
text-align:left;padding:9px 14px;white-space:nowrap}
.baum td{padding:5px 14px;border-bottom:1px solid var(--linie);vertical-align:top}
.baum tbody tr:last-child td{border-bottom:none}
.baum tr:hover td{background:var(--code)}
.baum .pf{font-family:var(--mono);white-space:pre;color:var(--ink);
font-size:.86rem;width:1%}
.baum .gr{font-family:var(--mono);font-size:.8rem;color:var(--grau);
text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;width:1%}
.baum .be{color:var(--ink2);font-size:.88rem;line-height:1.5;min-width:16ch}
.baum table{table-layout:auto}
.baum .ord{color:var(--akzent);font-weight:600}
.baum .rest{color:var(--grau);font-style:italic}
.blaettern{display:flex;justify-content:space-between;gap:18px;margin-top:76px;
padding-top:22px;border-top:1px solid var(--linie)}
.blaettern a{text-decoration:none;color:var(--ink);font-weight:620;font-size:.97rem}
.blaettern a:hover{color:var(--akzent)}
.blaettern .weiter{margin-left:auto;text-align:right}
.gal{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:26px;
margin-top:34px}
.gal figure{margin:0;background:var(--paper2);border:1px solid var(--linie);
box-shadow:var(--schatten);display:flex;flex-direction:column}
.gal .bild{background:var(--bild);cursor:zoom-in;display:block;border:none;padding:0;
width:100%;aspect-ratio:4/3;overflow:hidden}
.gal img{display:block;width:100%;height:100%;object-fit:contain}
.gal figcaption{padding:14px 17px 17px;flex:1;display:flex;flex-direction:column}
.gal .roh{margin-top:auto;align-self:flex-start}
.gal h4{margin:0 0 4px;font-size:1.02rem;font-weight:680;color:var(--ink)}
.gal p{margin:0 0 9px;font-size:.92rem;color:var(--ink2)}
.gal .roh{font-family:var(--mono);font-size:12px;color:var(--grau);text-decoration:none;
border-bottom:1px solid var(--linie)}
.gal .roh:hover{color:var(--akzent);border-color:var(--akzent)}
.plaene{display:grid;gap:34px;margin-top:34px}
.plaene figure{margin:0}
.plaene .blatt{background:#f7f5f2;border:1px solid var(--linie);box-shadow:var(--schatten);
cursor:zoom-in;display:block;padding:0;width:100%;border-radius:0}
.plaene img{display:block;width:100%;height:auto}
.plaene figcaption{display:flex;gap:16px;align-items:baseline;flex-wrap:wrap;
padding:12px 2px 0;color:var(--grau);font-size:.9rem}
.plaene b{color:var(--ink);font-size:1rem}
/* Lightbox: der Dialog fuellt den Bildschirm, das Bild wird darin zentriert.
   Ein am Inhalt bemessener Dialog haette je nach Bildformat versetzt gesessen. */
dialog.lupe{border:none;padding:0;background:transparent;width:100vw;height:100vh;
max-width:100vw;max-height:100vh;overflow:hidden}
dialog.lupe::backdrop{background:rgba(10,10,12,.9)}
dialog.lupe .rahmen{width:100vw;height:100vh;display:flex;flex-direction:column;
align-items:center;justify-content:center;gap:14px;padding:56px 32px 40px}
dialog.lupe img{display:block;max-width:calc(100vw - 64px);max-height:calc(100vh - 130px);
width:auto;height:auto;object-fit:contain}
dialog.lupe .bu{color:#e8e5e0;font-size:.92rem;text-align:center;max-width:70ch}
dialog.lupe .zu{position:fixed;top:14px;right:20px;background:none;border:none;
color:#f2efea;font-size:32px;line-height:1;cursor:pointer;font-family:var(--mono);
padding:4px 10px}
dialog.lupe .zu:hover{color:var(--akzent)}
.gal.eng{grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:18px}
.gal.eng .bild{aspect-ratio:16/7}
.gal.eng figcaption{padding:10px 13px 13px}
.gal.eng h4{font-size:.92rem;font-family:var(--mono);letter-spacing:.04em}
section.block{padding-top:56px}
@media(max-width:640px){.wrap{padding:0 17px 70px}ol.schritte>li{padding-left:42px}
.gal{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

JS = """<dialog class="lupe">
<button class="zu" aria-label="Schliessen">&times;</button>
<div class="rahmen"><img alt=""><p class="bu"></p></div></dialog>
<script>
(function(){
  var d=document.querySelector('dialog.lupe'),
      b=d.querySelector('img'), u=d.querySelector('.bu'),
      k=Array.prototype.slice.call(document.querySelectorAll('[data-gross]')),
      i=0;
  function zeig(n){
    if(!k.length) return;
    i=(n+k.length)%k.length;
    b.src=k[i].dataset.gross; b.alt=k[i].dataset.was||'';
    u.textContent=k[i].dataset.was||'';
  }
  k.forEach(function(el,n){
    el.addEventListener('click',function(){zeig(n); d.showModal();});
  });
  d.querySelector('.zu').addEventListener('click',function(){d.close()});
  d.addEventListener('click',function(e){
    if(e.target===d||e.target.classList.contains('rahmen')) d.close();
  });
  d.addEventListener('close',function(){b.removeAttribute('src')});
  document.addEventListener('keydown',function(e){
    if(!d.open) return;
    if(e.key==='ArrowRight') zeig(i+1);
    if(e.key==='ArrowLeft')  zeig(i-1);
  });
})();
</script>"""


SEITEN = [("index.html", "Uebersicht"),
          ("bauanleitung.html", "Bauanleitung"),
          ("technik.html", "Technische Umsetzung"),
          ("projekt.html", "Projektaufbau"),
          ("zeichnungen.html", "Zeichnungen"),
          ("galerie.html", "Bilder")]


def seite(titel, nav_aktiv, inhalt):
    _AKT["datei"] = nav_aktiv
    nav = ('<nav><div class="in"><a href="index.html" class="marke">'
           'FutterStorage</a>')
    for href, name in SEITEN:
        k = ' class="hier"' if href == nav_aktiv else ""
        nav += f'<a href="{href}"{k}>{name}</a>'
    nav += "</div></nav>"
    # Blaettern am Fuss: Vorgaenger und Nachfolger in der Reihenfolge oben
    i = [h for h, _ in SEITEN].index(nav_aktiv)
    zur = '<div class="blaettern">'
    zur += (f'<a href="{SEITEN[i-1][0]}" class="zurueck">&larr; {SEITEN[i-1][1]}</a>'
            if i > 0 else "<span></span>")
    zur += (f'<a href="{SEITEN[i+1][0]}" class="weiter">{SEITEN[i+1][1]} &rarr;</a>'
            if i < len(SEITEN) - 1 else "<span></span>")
    zur += "</div>"
    inhalt = _inhaltsverzeichnis(inhalt)
    kopf, _, rest = inhalt.rstrip().rpartition("</div>")
    inhalt = kopf + zur + "</div>" + rest
    return ent(f"<title>{titel}</title>\n<style>{CSS}</style>\n{nav}\n{inhalt}\n{JS}")


def _inhaltsverzeichnis(inhalt):
    """Sammelt alle Abschnittsueberschriften, gibt ihnen einen Anker und
    stellt ein Verzeichnis hinter den Seitenkopf. Ab drei Abschnitten."""
    kapitel = re.findall(r'<h2 data-nr="([^"]*)">(.*?)</h2>', inhalt, re.S)
    if len(kapitel) < 3:
        return inhalt

    def anker(m):
        nr, name = m.group(1), m.group(2)
        kurz = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        return f'<h2 id="k-{kurz}" data-nr="{nr}">{name}</h2>'

    inhalt = re.sub(r'<h2 data-nr="([^"]*)">(.*?)</h2>', anker, inhalt, flags=re.S)
    zeilen = []
    for nr, name in kapitel:
        kurz = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        zeilen.append(f'<li><a href="#k-{kurz}"><span class="tnr">{nr or "&bull;"}'
                      f'</span>{name}</a></li>')
    toc = f'<nav class="toc" aria-label="Inhalt"><ol>{"".join(zeilen)}</ol></nav>'
    return inhalt.replace("</header>", "</header>\n" + toc, 1)


# =====================================================================
INDEX = f"""
<div class="wrap">
<header>
  <p class="eyebrow">Projektuebersicht</p>
  <h1>FutterStorage</h1>
  <p class="lead">Ein gedrucktes Regalsystem fuer 85-g-Nassfutterbeutel. Waagerechte
  Kanaele ueber die volle Schranktiefe, eine Feder schiebt die Beutel nach vorne,
  entnommen wird immer der vorderste. Die Ebenen stapeln direkt aufeinander.</p>
  <div class="kz-reihe">
    <div class="kz"><b>15</b><span>Sorten</span></div>
    <div class="kz"><b>375</b><span>Beutel maximal</span></div>
    <div class="kz"><b>5&times;3</b><span>Spalten &times; Ebenen</span></div>
    <div class="kz"><b>0 L</b><span>toter Raum</span></div>
    <div class="kz"><b>8</b><span>Teiletypen</span></div>
  </div>
</header>

<section>
  <h2 data-nr="">Wo es weitergeht</h2>
  <div class="kachel">
    <a href="bauanleitung.html">
      <div class="nr">Dokument 1</div>
      <h3>Bauanleitung</h3>
      <p>Was gedruckt wird, was gekauft werden muss, wie es zusammengesetzt wird.
      Mit Teileliste, Druckeinstellungen und Schritt-fuer-Schritt-Montage.</p>
    </a>
    <a href="technik.html">
      <div class="nr">Dokument 2</div>
      <h3>Technische Umsetzung</h3>
      <p>Wie das Modell entstanden ist: welche Programme, welcher Code, wie die
      Pruefungen laufen und wo die Fallstricke lagen.</p>
    </a>
    <a href="zeichnungen.html">
      <div class="nr">Anhang</div>
      <h3>Zeichnungen</h3>
      <p>Sieben bemasste Blaetter mit allen Massen, Positionsnummern und
      Erklaerung, welches Mass wofuer steht.</p>
    </a>
    <a href="galerie.html">
      <div class="nr">Anhang</div>
      <h3>Bilder</h3>
      <p>Zehn Renderings vom Einzelteil bis zum vollen Schrank, klickbar in
      voller Aufloesung.</p>
    </a>
  </div>
</section>

<section>
  <h2 data-nr="">Das fertige Regal</h2>
  <figure class="gross"><img src="{R['b_gesamt']}" alt="Das komplette Regal"></figure>
  <figcaption>Fuenf Kanaele nebeneinander, drei Ebenen uebereinander. Jeder Kanal
  fasst 25 Beutel einer Sorte.</figcaption>
</section>

<section>
  <h2 data-nr="">Was im Paket liegt</h2>
  <div class="tab"><table>
    <thead><tr><th>Ordner</th><th>Inhalt</th></tr></thead>
    <tbody>
      <tr><td class="num">stl/</td><td class="w">Sieben druckfertige Dateien &mdash;
        die drei Segmenttypen, Schieber, Schild, Schildtext und die Passprobe</td></tr>
      <tr><td class="num">zeichnungen/</td><td class="w">Sechs bemasste Zeichnungsblaetter
        als SVG, beliebig skalierbar und druckbar</td></tr>
      <tr><td class="num">bilder/</td><td class="w">Zehn Renderings in voller
        Aufloesung</td></tr>
      <tr><td class="num">modell/</td><td class="w">Die OpenSCAD-Quelldatei &mdash;
        alle Masse parametrisch aenderbar</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2 data-nr="">Die Ausgangslage</h2>
  <div class="text">
    <div class="tab"><table>
      <thead><tr><th></th><th>Mass</th></tr></thead>
      <tbody>
        <tr><td>Schrankbreite nutzbar</td><td class="num">540 mm</td></tr>
        <tr><td>Schranktiefe</td><td class="num">500 mm</td></tr>
        <tr><td>Hoehe ohne Regalboden</td><td class="num">520 mm</td></tr>
        <tr><td>Beutel (gemessen)</td><td class="num">88 &times; 136 &times; 20 mm</td></tr>
      </tbody>
    </table></div>
    <p>Der Regalboden laesst sich herausnehmen. Bleibt er drin, passt in das untere
    Fach nur eine Ebene mit fuenf Sorten &mdash; ohne ihn sind es drei Ebenen mit
    fuenfzehn.</p>
  </div>
</section>

<footer>Erstellt mit OpenSCAD und Blender &middot; alle Masse in Millimetern</footer>
</div>
"""

os.makedirs(PAKET, exist_ok=True)
for datei, titel, inhalt in [
        ("index.html", "FutterStorage &mdash; Uebersicht", INDEX)]:
    with open(os.path.join(PAKET, datei), "w", encoding="utf-8") as f:
        f.write(seite(titel, datei, inhalt))
    print(f"{datei:22s}{os.path.getsize(os.path.join(PAKET, datei))/1024:7.0f} kB")

if FUNDE:
    print("\nASCII-UMSCHRIFT STATT UMLAUT:")
    for f in FUNDE:
        print("  ! " + f)
else:
    print("\nSchreibung geprueft: alle Umlaute gesetzt")

