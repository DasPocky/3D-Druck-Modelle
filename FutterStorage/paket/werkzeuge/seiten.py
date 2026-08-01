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
         "b_greifraum": "09-greifraum", "b_entnahme": "10-entnahme",
         "b_ebene": "11-eine-ebene", "b_gesamt": "12-vollausbau"}

TITEL = {"b_front": ("Frontsegment", "Vorderstes Kanalstueck mit Frontwand "
                     "und Schildtasche"),
         "b_mitte": ("Mittelsegment", "Beliebig oft wiederholbar, verlaengert den Kanal"),
         "b_end": ("Endsegment", "Schliesst den Kanal hinten ab"),
         "b_schieber": ("Schieber", "Traegt die Konstantkraftfeder und schiebt den Stapel"),
         "b_schild": ("Schild", "Steckt in der Frontwand und nennt die Sorte"),
         "b_kanal": ("Kanal komplett", "Front-, Mittel- und Endsegment zusammengesteckt"),
         "b_explosion": ("Explosionsdarstellung", "Die drei Segmente und der Schieber "
                         "in Reihenfolge"),
         "b_gefuellt": ("Funktionsprinzip", "Die Feder haelt den Stapel vorne am Anschlag"),
         "b_greifraum": ("Greifraum", "Ueber dem Beutel bleiben 42 mm - dort "
                         "fasst die Hand zu"),
         "b_entnahme": ("Entnahme", "Der vorderste Beutel wird an der Oberkante "
                        "gefasst und nach vorne herausgezogen"),
         "b_ebene": ("Eine Ebene", "Fuenf Kanaele nebeneinander, unterschiedlich gefuellt"),
         "b_gesamt": ("Vollausbau", "Drei Ebenen mit fuenfzehn Sorten im Schrank")}

ZTITEL = {"01-frontsegment": ("Frontsegment", "Vorder-, Seiten- und Draufsicht "
                              "mit allen Massen"),
          "02-mittel-endsegment": ("Mittel- und Endsegment", "Beide Bauteile plus "
                                   "gemeinsamer Querschnitt"),
          "03-schieber-schild": ("Schieber, Schild, Trommel und Achse",
                                 "Federkammer, Schildplatte, Wickeltrommel "
                                 "und Zukaufteil"),
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
 "kürzen": "kürzen", "laedt": "lädt", "Laenge": "Länge", "laengste": "längste",
 "laesst": "lässt", "laeuft": "läuft", "Loecher": "Löcher", "loesen": "lösen",
 "loeste": "löste", "Mass": "Maß", "Massblaetter": "Maßblätter", "Masse": "Maße",
 "Massen": "Maßen", "Masslinie": "Maßlinie", "Masslinien": "Maßlinien",
 "Mittelstuecke": "Mittelstücke", "Modellaenderung": "Modelländerung",
 "Modellmassen": "Modellmaßen", "Moeglichkeit": "Möglichkeit", "müssen": "müssen",
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
 "Stueckliste": "Stückliste", "Stuecks": "Stücks", "Stützen": "Stützen",
 "Traegt": "Trägt", "ueber": "über", "Ueber": "Über", "ueberbrueckt": "überbrückt",
 "ueberdeckt": "überdeckt", "uebereinander": "übereinander",
 "Ueberhaenge": "Überhänge", "Ueberhang": "Überhang",
 "Ueberschneidung": "Überschneidung", "Ueberschnitt": "Überschnitt",
 "ueberschreibt": "überschreibt", "Uebersicht": "Übersicht",
 "ueberstehen": "überstehen", "Uebrig": "Übrig", "urspruengliche": "ursprüngliche",
 "vergroessern": "vergrößern", "vergroessert": "vergrößert",
 "verlaengert": "verlängert", "veroeffentlicht": "veröffentlicht",
 "Verpackungsmasse": "Verpackungsmaße", "Vollkoerper": "Vollkörper",
 "Vorgaenger": "Vorgänger", "wächst": "wächst", "waehlen": "wählen",
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
 "erhoehen": "erhöhen", "erhöht": "erhöht", "koennen": "können",
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
    "dass", "muss", "müssen", "lassen", "laesst", "passen", "passt", "passung",
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
    # Woerter mit doppeltem s, die keine Umschrift sind - die
    # Regel "ss" allein trifft sie sonst faelschlich.
    "gefasst", "hinfasst", "fasst", "passt", "passte", "misst",
    "dass", "muss", "musste", "wusste", "gross",
    "innendurchmesser", "aussendurchmesser", "lebensdauer",
    "durchmesser", "messer",
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
        <tr><td>Fachhöhe, Regalboden hoeher gesetzt</td><td class="num">550 mm</td></tr>
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

# =====================================================================
BAU = f"""
<div class="wrap">
<header>
  <p class="eyebrow">Dokument 1</p>
  <h1>Bauanleitung</h1>
  <p class="lead">Von der Passprobe bis zum befuellten Regal. Alle Teile, alle Masse,
  alle Handgriffe.</p>
</header>

<section>
  <h2 data-nr="01">So funktioniert es</h2>
  <figure class="gross"><img src="{R['b_gefuellt']}" alt="Kanal von der Seite"></figure>
  <figcaption>Ein Kanal von der Seite. Die Beutel stehen hochkant hintereinander, der
  orange Schieber steht direkt hinter dem letzten und drueckt den Stapel nach vorne.</figcaption>

  <div class="text">
    <h3>Entnehmen</h3>
    <p>Gefasst wird der Beutel an seiner <strong>Oberkante</strong>: Daumen und
    Zeigefinger greifen dort zu und ziehen ihn nach vorne heraus. Der vorderste
    Beutel ragt 44 mm ueber die Frontwand hinaus und kippt beim Herausziehen
    ueber deren Kante.</p>

    <figure class="gross"><img src="{R['b_entnahme']}" alt="Entnahme"></figure>
    <figcaption>Der vorderste Beutel, an der Oberkante gefasst und nach vorne
    herausgezogen.</figcaption>

    <h4>Kommt man mit den Fingern hin?</h4>
    <p>Das entscheidet ein einziges Mass: der <strong>Greifraum</strong> von
    42 mm zwischen der Beutelkante und dem Boden der Ebene darueber. Ein
    Erwachsenenfinger ist rund 17,5 mm dick, zwei davon passen also neben die
    Kante. Unter 40 mm wird es zur Fummelei &mdash; deshalb ist der Regalboden
    hoeher gesetzt, damit 550 mm Fachhöhe zur Verfügung stehen.</p>

    <figure class="gross"><img src="{R['b_greifraum']}" alt="Greifraum"></figure>
    <figcaption>Der Spalt ueber dem Beutelstapel. Er bestimmt die Ebenenhoehe
    von 182,8 mm.</figcaption>

    <p>Vorne ist der Kanal oberhalb der Frontwand ohnehin offen &mdash; dort
    steht nichts im Weg. Die Frontwand braucht deshalb <em>keine</em>
    Griffmulde; eine solche säße dort, wo die Hand gar nicht hinfasst, und
    nähme nur dem Schild Platz weg.</p>

    <p>Seitlich neben den Beutel kommt man nicht: dort sind nur zwei Millimeter
    Luft, und der Nachbarkanal steht unmittelbar daneben.</p>

    <h3>Nachfuellen</h3>
    <p>Schieber an der Grifflasche nach hinten ziehen, Beutel hochkant von oben
    einstellen, Schieber loslassen. Die Feder drueckt den Stapel wieder nach vorne.</p>

    <h3>Sorte wechseln</h3>
    <p>Schild aus der Tasche an der Frontwand ziehen, neues einschieben.</p>
  </div>
</section>

<section>
  <h2 data-nr="02">Bevor du druckst</h2>
  <div class="text">
    <h3>Die Passprobe</h3>
    <p>Das ganze System steht und faellt mit der Beutelbreite. Gemessen sind 88 mm,
    daraus ergibt sich die Spaltenbreite von 95,2 mm und damit fuenf Spalten in
    540 mm Schrankbreite.</p>
    <p>Drucke zuerst <code>probe.stl</code> &mdash; 34 g, gut eine halbe Stunde. Das
    Innenmass ist eingepraegt. Stell einen echten Beutel hinein: Passt er mit ein, zwei
    Millimetern Luft, stimmen alle weiteren Masse.</p>

    <h3>Dann ein einzelner Kanal</h3>
    <p>Die zweite offene Frage ist die Reibung: Ob sich sechzehn aneinanderlehnende
    Beutel sauber schieben lassen, haengt an der Folienoberflaeche. Bau deshalb erst
    einen kurzen Kanal aus Front- und Endsegment &mdash; 325 mm, 16 Beutel. Funktioniert
    der, kannst du die Serie starten.</p>
  </div>

  <figure class="plan"><img src="{Z['05-beutel-passung']}" alt="Zeichnung Beutel und Passung"></figure>
  <figcaption>Die gemessenen Beutelmasse und wie der Beutel im Kanal sitzt.</figcaption>
</section>

<section>
  <h2 data-nr="03">Die Teile</h2>
  <p class="unter">Sechs Teiletypen. Die Mengen gelten je Kanal &mdash; und ein Kanal
  ist eine Sorte.</p>

  <div class="karten">
    <article class="karte">
      <figure><img src="{R['b_front']}" alt="Frontsegment"></figure>
      <div class="txt"><span class="anz">1&times; je Kanal</span>
      <h4>Frontsegment</h4>
      <div class="dat">95 &times; 175 &times; 145 mm &middot; 100 g</div>
      <p>Kommt nach vorne. Traegt die 92 mm hohe Frontwand, die
      Schildtasche und den Haken fuer das Federband.</p></div>
    </article>
    <article class="karte">
      <figure><img src="{R['b_mitte']}" alt="Mittelsegment"></figure>
      <div class="txt"><span class="anz">beliebig oft</span>
      <h4>Mittelsegment</h4>
      <div class="dat">95 &times; 169 &times; 145 mm &middot; 70 g</div>
      <p>Beidseitig offen. Jedes Stueck verlaengert den Kanal um 160 mm, also um
      acht Beutel.</p></div>
    </article>
    <article class="karte">
      <figure><img src="{R['b_end']}" alt="Endsegment"></figure>
      <div class="txt"><span class="anz">1&times; je Kanal</span>
      <h4>Endsegment</h4>
      <div class="dat">95 &times; 162 &times; 145 mm &middot; 82 g</div>
      <p>Schliesst hinten ab. Durch den Sichtschlitz siehst du, ob noch Vorrat
      im Kanal ist.</p></div>
    </article>
    <article class="karte">
      <figure><img src="{R['b_schieber']}" alt="Schieber"></figure>
      <div class="txt"><span class="anz">1&times; je Kanal</span>
      <h4>Schieber</h4>
      <div class="dat">95 &times; 42 &times; 149 mm &middot; 50 g</div>
      <p>Im Fuss sitzt die Kammer fuer die Federrolle. Unten Gleitkufen, oben die
      Grifflasche zum Zurueckziehen.</p></div>
    </article>
    <article class="karte">
      <figure><img src="{R['b_schild']}" alt="Schild"></figure>
      <div class="txt"><span class="anz">1&times; je Kanal</span>
      <h4>Schild</h4>
      <div class="dat">74 &times; 18 &times; 2 mm &middot; 2 g</div>
      <p>Orange Platte, Schrift 0,6 mm vertieft. Mit zwei Farben zusaetzlich
      <code>schild-text.stl</code> in Schwarz drucken und einkleben.</p></div>
    </article>
    <article class="karte">
      <figure><img src="{R['b_kanal']}" alt="Fertiger Kanal"></figure>
      <div class="txt"><span class="anz">Ergebnis</span>
      <h4>Ein fertiger Kanal</h4>
      <div class="dat">95 &times; 485 &times; 145 mm &middot; 304 g</div>
      <p>Front + Mitte + End + Schieber + Schild. Eine Sorte mit Platz fuer
      25 Beutel.</p></div>
    </article>
  </div>

  <h3>Zeichnungen</h3>
  <figure class="plan"><img src="{Z['01-frontsegment']}" alt="Zeichnung Frontsegment"></figure>
  <figure class="plan"><img src="{Z['02-mittel-endsegment']}" alt="Zeichnung Mittel- und Endsegment"></figure>
  <figure class="plan"><img src="{Z['03-schieber-schild']}" alt="Zeichnung Schieber und Schild"></figure>

  <h3>Wie viele Segmente</h3>
  <div class="tab"><table>
    <thead><tr><th>Kanal</th><th>Aufbau</th><th>Laenge</th><th>Beutel</th>
      <th>Filament</th></tr></thead>
    <tbody>
      <tr><td>kurz</td><td class="w">Front + End</td><td class="num">325 mm</td>
        <td class="num">16</td><td class="num">263 g</td></tr>
      <tr><td>mittel</td><td class="w">Front + 1&times; Mitte + End</td>
        <td class="num">485 mm</td><td class="num">25</td><td class="num">336 g</td></tr>
      <tr><td>lang</td><td class="w">Front + 2&times; Mitte + End</td>
        <td class="num">645 mm</td><td class="num">33</td><td class="num">409 g</td></tr>
    </tbody>
  </table></div>
  <p class="unter">In deinen Schrank passt der mittlere Kanal genau.</p>

  <h3>Stueckliste</h3>
  <div class="tab"><table>
    <thead><tr><th>Stufe</th><th>Sorten</th><th>Beutel</th><th>Teile</th>
      <th>Filament</th><th>Druckzeit ca.</th></tr></thead>
    <tbody>
      <tr><td>Testkanal, kurz</td><td class="num">1</td><td class="num">16</td>
        <td class="num">5</td><td class="num">263 g</td><td class="num">15 h</td></tr>
      <tr><td>Eine Ebene</td><td class="num">5</td><td class="num">125</td>
        <td class="num">30</td><td class="num">1,68 kg</td><td class="num">99 h</td></tr>
      <tr><td>Zwei Ebenen</td><td class="num">10</td><td class="num">250</td>
        <td class="num">60</td><td class="num">3,36 kg</td><td class="num">198 h</td></tr>
    </tbody>
    <tfoot><tr><td>Drei Ebenen</td><td class="num">15</td><td class="num">375</td>
      <td class="num">90</td><td class="num">5,04 kg</td><td class="num">297 h</td></tr></tfoot>
  </table></div>
  <p class="unter">Je Kanal sechs Druckteile: Front-, Mittel- und Endsegment, Schieber, Schild und Wickeltrommel. Druckzeit grob mit 17 g/h. Bei zehn Sorten reichen zwei Ebenen.</p>
</section>

<section>
  <h2 data-nr="04">Einkaufsliste</h2>
  <p class="unter">Zwei Zukaufteile je Kanal. Keine Schrauben, keine Muttern,
  kein Kleber &mdash; alles Übrige wird gedruckt.</p>

  <div class="tab"><table>
    <thead><tr><th>Teil</th><th>Was genau</th><th>Menge</th><th>Preis</th></tr></thead>
    <tbody>
      <tr>
        <td class="w"><strong>Konstantkraftfeder</strong><br>
          <span class="klein">aufgerolltes Federstahlband</span></td>
        <td class="w"><strong>CF030-0237</strong> &middot; 10,5 N &middot;
          Auszug 610 mm &middot; Band 15,0 mm &middot; Rolle 22 mm &middot;
          Federstahl 1.4310, rostfrei</td>
        <td class="num">1 je Kanal</td>
        <td class="num">16,40 &euro;</td>
      </tr>
      <tr>
        <td class="w"><strong>Achse</strong><br>
          <span class="klein">trägt die Wickeltrommel</span></td>
        <td class="w">Rundstab <strong>3 mm</strong>, 90 mm lang &mdash;
          Edelstahl V2A (1.4301), blank gezogen, Toleranz h9.
          Ein 500-mm-Stab reicht fuer fuenf Achsen.</td>
        <td class="num">1 je Kanal</td>
        <td class="num">1,05 &euro;<br>
          <span class="klein">je 500-mm-Stab</span></td>
      </tr>
    </tbody>
    <tfoot><tr><td>Material je Kanal</td><td>&nbsp;</td><td class="num">1 + 1</td>
      <td class="num">ca. 17,45 &euro;</td></tr></tfoot>
  </table></div>

  <div class="text">
    <h3>Warum kein 16-mm-Band?</h3>
    <p>Die erste Auslegung ging von 16 mm aus. <strong>Das gibt es bei
    8&ndash;12 N nicht ab Lager.</strong> Die Kraft einer Rollfeder wächst mit
    Bandbreite mal Banddicke im Quadrat: Bei 15,87 mm Band liegt die
    Standardfeder schon bei 14,7 N &mdash; zu stark. Im Zielbereich sind die
    Bänder 12,7 bis 15,0 mm breit. Das Modell ist auf 15,0 mm ausgelegt.</p>

    <h3>Die Trommel wird gedruckt</h3>
    <div class="hinweis">Die Feder darf <strong>nicht</strong> auf der 3-mm-Achse
    aufwickeln. Ihr natürlicher Innendurchmesser liegt bei 11&ndash;17 mm, der
    Hersteller verlangt eine Trommel 10&ndash;20 % darueber. Ein zu enger Wickel
    erhöht die Biegespannung im Band und verkürzt die Lebensdauer.</div>
    <p>Deshalb liegt <code>stl/trommel.stl</code> bei: 20,7 mm Wickelfläche,
    17 mm breit, mit Bordscheiben gegen seitliches Ablaufen, Bohrung 3,5 mm.
    Sie laeuft frei auf der Achse. <strong>Liegend drucken</strong> &mdash; dann
    ist die Bohrung rund und es braucht keine Stützen.</p>

    <h3>Wo es die Feder gibt</h3>
    <p>Der Fachbegriff ist entscheidend: <strong>Konstantkraftfeder</strong>, auch
    Rollfeder, englisch <em>constant force spring</em>. Dasselbe Bauteil steckt in
    den Warenschiebern im Supermarktregal.</p>
    <ul class="quellen">
      <li><a href="https://www.sodemann-federn.de/cf030-0237"
        rel="noopener">Sodemann Federn &mdash; CF030-0237</a>
        <span class="klein">deutscher Shop, Preise sichtbar, Lagerware</span></li>
      <li><a href="https://www.febrotec.de/de-DE/konstantkraftfedern-rollfedern"
        rel="noopener">Febrotec, Halver</a>
        <span class="klein">dieselbe Feder als 0CF030-0237, Sonderfertigung moeglich</span></li>
      <li><a href="https://www.stahl-shop24.de/Edelstahl/Edelstahl-rund/"
        rel="noopener">Stahl-Shop24 &mdash; Rundstab 3 mm</a>
        <span class="klein">fuer die Achse</span></li>
    </ul>
    <div class="hinweis"><strong>Vorsicht bei der Montage:</strong> Die Bandkanten
    sind scharf &mdash; Handschuhe und Schutzbrille tragen. Die Rolle kontrolliert
    halten, sie wickelt sich beim Loslassen schlagartig zurueck. Das Band nie
    knicken, kürzen oder ueber scharfe Kanten laufen lassen, und bei vollem
    Auszug müssen mindestens anderthalb Windungen auf der Trommel bleiben.</div>
    <p>Reichen 10,5 N nicht, ist der Weg <em>nicht</em> ein breiteres Band,
    sondern zwei schmalere Federn nebeneinander &mdash; ihre Kräfte addieren
    sich.</p>
  </div>
</section>

<section>
  <h2 data-nr="05">Druckeinstellungen</h2>
  <div class="tab"><table>
    <thead><tr><th>Einstellung</th><th>Wert</th><th>Warum</th></tr></thead>
    <tbody>
      <tr><td>Duese</td><td class="num">0,4 mm</td><td class="w">Standard</td></tr>
      <tr><td>Schichthoehe</td><td class="num">0,2 mm</td>
        <td class="w">Kompromiss aus Zeit und Qualitaet</td></tr>
      <tr><td>Wandlinien</td><td class="num">4</td>
        <td class="w">Wandstaerke 1,6 mm geht exakt in vier Linien auf</td></tr>
      <tr><td>Infill</td><td class="num">15 %</td>
        <td class="w">die Waende tragen, viel Fuellung gibt es nicht</td></tr>
      <tr><td>Stützen</td><td class="num">nein</td>
        <td class="w">Ueberhaenge unter 3 %, nur kurze Bruecken</td></tr>
      <tr><td>Ausrichtung</td><td class="num">wie modelliert</td>
        <td class="w">Boden aufs Bett, nichts drehen</td></tr>
      <tr><td>Material</td><td class="num">PLA</td>
        <td class="w">reicht, im Schrank wird nichts warm</td></tr>
    </tbody>
  </table></div>

  <div class="text">
    <h3>Passung</h3>
    <p>Ein Parameter im Modell steuert alle Steckverbindungen:</p>
    {code('passung = 0.2;   // Spiel je Flanke in mm', 'openscad')}
    <p>Betrifft die Bodenzunge zwischen den Segmenten und die Schildtasche. 0,15 sitzt
    stramm, 0,20 ist Standard, 0,25 laeuft leicht. Einmal mit einem Toleranztest
    ermitteln und eintragen.</p>
    <div class="hinweis">Das Frontsegment ist mit 175 mm das laengste Teil. Auf einem
    180er Bett bleiben 5 mm Reserve.</div>
  </div>
</section>

<section>
  <h2 data-nr="06">Zusammenbau</h2>
  <figure class="gross"><img src="{R['b_explosion']}" alt="Explosionsdarstellung"></figure>
  <figcaption>Die drei Segmente auseinandergezogen. Am hinteren Ende jedes Stuecks
  sitzt die Bodenzunge, die sich unter das naechste schiebt.</figcaption>

  <ol class="schritte">
    <li><h4>Segmente aneinanderreihen</h4>
    <p>Frontsegment nach vorne, dahinter die Mittelstuecke, hinten das Endsegment. Die
    Bodenzunge schiebt sich unter den Boden des naechsten Teils und ueberbrueckt die
    Fuge &mdash; so bleibt kein Beutel an einer Stufe haengen. Nichts verschrauben:
    Der Schieberdruck presst die Segmente gegeneinander.</p></li>

    <li><h4>Feder in den Schieber einsetzen</h4>
    <p>Im Fuss des Schiebers sitzt eine Kammer mit zwei Wangen. Federrolle hineinlegen,
    den 3-mm-Stab durch beide Bohrungen schieben. Der Stab darf seitlich nicht
    ueberstehen, sonst schleift er an der Kanalwand.</p></li>

    <li><h4>Band nach vorne fuehren</h4>
    <p>Das Bandende tritt unten aus dem Schieber aus und laeuft in der 18 mm breiten
    Nut mittig durch den Boden aller Segmente nach vorne.</p></li>

    <li><h4>Band vorne einhaengen</h4>
    <p>Im Frontsegment sitzt ein Quersteg in der Bodennut. Bandende dort einhaengen
    &mdash; die meisten Federn haben ein Loch im Band. Sonst eines bohren oder mit
    einem Kabelbinder befestigen.</p></li>

    <li><h4>Funktion pruefen</h4>
    <p>Schieber nach hinten ziehen und loslassen. Er sollte gleichmaessig nach vorne
    laufen und an der Frontwand anschlagen.</p></li>

    <li><h4>Schild einschieben</h4>
    <p>Von oben in die Tasche an der Frontwand.</p></li>

    <li><h4>Befuellen</h4>
    <p>Schieber zurueckziehen, Beutel hochkant von oben einstellen &mdash; alle in
    derselben Richtung &mdash; und loslassen.</p></li>

    <li><h4>Spalten nebeneinandersetzen</h4>
    <p>In beiden Bodenraendern jedes Segments sitzt dieselbe Tasche. Lege je
    Segmentfuge einen <strong>Verbinder</strong> ein und schiebe die naechste
    Spalte dagegen, bis die Rastnoppe hoerbar einschnappt. Zum Loesen genuegt
    kraeftiger Zug &mdash; werkzeuglos.</p>
    <p>Weil die Nase nicht angeformt ist, bleibt jede Aussenkante buendig:
    Die aeusserste Spalte laesst ihre Tasche einfach leer, dort steht nichts
    ueber.</p></li>

    <li><h4>Ebenen stapeln</h4>
    <p>Auf den Oberkanten der Seitenwaende stehen vier Zapfen &uuml;ber, im Boden
    der naechsten Ebene sitzen die passenden Taschen. Die Ebene von oben aufsetzen,
    bis sie satt auf den Waenden aufliegt &mdash; nicht auf den Zapfen. Kein Sockel,
    kein Kleber, kein Werkzeug.</p>
    <p>Jedes Segment gibt es in drei Ebenenlagen: <code>unten</code> ohne
    Taschen im Boden, <code>mitte</code> mit beidem, <code>oben</code> ohne
    Zapfen. Fuer die oberste Lage also die <code>-oben-</code>-Dateien nehmen
    &mdash; dann schliesst der Stapel glatt ab und es steht nichts frei nach
    oben. Ebenso gibt es <code>links</code>, <code>mitte</code> und
    <code>rechts</code> fuer die Spalten: an den Aussenkanten entfällt die
    Verbindertasche, die dort ins Leere zeigen wuerde.</p></li>
  </ol>
</section>

<section>
  <h2 data-nr="07">Wie der Verbund zusammenhaelt</h2>
  <p class="unter">Zwei Steckverbindungen, beide ohne Zusatzteile.</p>
  <figure class="plan"><img src="{Z['06-verbindungen']}" alt="Zeichnung Verbindungen"></figure>
  <div class="text">
    <p>Beim Herausziehen eines Beutels wirkt eine Kraft nach vorne. Ohne Verbindung
    wuerde sich der Stapel mit der Zeit verschieben. Deshalb greifen die Teile
    ineinander:</p>
    <ul>
      <li><strong>Nach oben</strong> laufen die Seitenwaende als Zapfen weiter und
        stecken in Taschen im Boden der Ebene darueber. Der Zapfen ist genauso breit
        wie die Wand &mdash; er schwaecht sie also nicht und druckt ohne Stützen.</li>
      <li><strong>Zur Seite</strong> greift eine Nase am Bodenrand in die Tasche der
        Nachbarspalte. Beide liegen unterhalb des Innenraums und nehmen dem Beutel
        keinen Platz weg.</li>
    </ul>
    <div class="hinweis">Ringsum sind 0,2 mm Spiel eingerechnet. Sitzt es zu stramm,
    in der Modelldatei <code>passung</code> auf 0,25 erhoehen und die Segmente neu
    bauen &mdash; sitzt es zu locker, auf 0,15 verringern.</div>
  </div>
</section>

<section>
  <h2 data-nr="08">Anordnung im Schrank</h2>
  <figure class="plan"><img src="{Z['04-gesamtanordnung']}" alt="Zeichnung Gesamtanordnung"></figure>
  <figure class="gross"><img src="{R['b_ebene']}" alt="Eine Ebene"></figure>
  <figcaption>Eine Ebene: fuenf Kanaele nebeneinander, 476 von 540 mm Breite.</figcaption>
</section>

<section>
  <h2 data-nr="09">Wenn etwas klemmt</h2>
  <div class="text">
    <h4>Der Stapel rutscht nicht nach</h4>
    <p>Meist ist die Feder zu schwach &mdash; rechne mit 0,25 N je Beutel. Zweite
    Moeglichkeit: Ein Beutel steht quer. Durch die Seitenfenster siehst du, wo es hakt.</p>
    <h4>Ein Beutel bleibt an der Fuge haengen</h4>
    <p>Die Bodenzunge sitzt nicht sauber unter dem naechsten Segment. Segmente fest
    zusammenschieben, notfalls <code>passung</code> auf 0,25 erhoehen.</p>
    <h4>Der Schieber verkantet</h4>
    <p>Die Achse steht seitlich ueber und schleift. Buendig kürzen.</p>
    <h4>Der vorderste Beutel faellt heraus</h4>
    <p>Sollte nicht passieren, die Frontwand ist mit 92 mm hoch genug. Falls doch:
    Feder ist zu stark.</p>
  </div>
</section>

<footer>Alle Masse in Millimetern &middot; Modell parametrisch in
<code>katzenfutter-regal.scad</code></footer>
</div>
"""

TECHNIK = f"""
<div class="wrap">
<header>
  <p class="eyebrow">Dokument 2</p>
  <h1>Technische Umsetzung</h1>
  <p class="lead">Wie das Modell entstanden ist: welche Programme, welche Sprachen,
  wie sie zusammenspielen und woran die Qualitaet haengt.</p>
</header>

<section>
  <h2 data-nr="01">Die Werkzeugkette</h2>
  <div class="text">
    <p>Drei Programme, jedes fuer eine Aufgabe. Keines wird per Maus bedient &mdash;
    alle drei werden geschrieben und ueber die Kommandozeile aufgerufen. Das ist der
    Grund, warum sich das Modell in Minuten umbauen laesst.</p>
  </div>

  <div class="tab"><table>
    <thead><tr><th>Programm</th><th>Sprache</th><th>Aufgabe</th><th>Ergebnis</th></tr></thead>
    <tbody>
      <tr><td>OpenSCAD</td><td class="num">eigene Sprache</td>
        <td class="w">Geometrie beschreiben</td><td class="num">STL</td></tr>
      <tr><td>Blender</td><td class="num">Python</td>
        <td class="w">Bilder rendern</td><td class="num">PNG</td></tr>
      <tr><td>Python</td><td class="num">Python</td>
        <td class="w">pruefen, zeichnen, dokumentieren</td><td class="num">SVG, HTML</td></tr>
    </tbody>
  </table></div>

  {diagramm("Von der Quelle zum fertigen Paket", [
      ("Modell", "katzenfutter-regal.scad", 1, 0),
      ("Geometrie", "stl/*.stl", 1, 1),
      ("Bilder", "Blender", 0, 2),
      ("Pr&#252;fung", "pruefen.py", 1, 2),
      ("Zeichnungen", "zeichnungen.py", 2, 2),
      ("Dokumentation", "paket/*.html", 1, 3),
  ])}
</section>

<section>
  <h2 data-nr="02">OpenSCAD: Geometrie als Programm</h2>
  <div class="text">
    <p>Der entscheidende Unterschied zu Fusion oder SolidWorks: Man klickt nicht,
    man schreibt. Ein Bauteil ist ein Programm, das bei jedem Aufruf neu gerechnet
    wird.</p>

    {code('cube([95.2, 163, 144.8]);           // ein Quader\ntranslate([1.6, 3, 4.8])           // verschieben\n    cube([92, 157, 140]);          // und noch einer', 'openscad')}

    <p>Gebaut wird mit drei Operationen &mdash; das nennt sich Constructive Solid
    Geometry:</p>
  </div>

  <div class="tab"><table>
    <thead><tr><th>Operation</th><th>Wirkung</th></tr></thead>
    <tbody>
      <tr><td class="num">union()</td><td class="w">Koerper verschmelzen</td></tr>
      <tr><td class="num">difference()</td>
        <td class="w">vom ersten alle folgenden abziehen</td></tr>
      <tr><td class="num">intersection()</td>
        <td class="w">nur die Schnittmenge behalten</td></tr>
    </tbody>
  </table></div>

  <div class="text">
    <h3>Ein Vollkoerper, aus dem alles herausgestochen wird</h3>
    <p>Jedes Segment entsteht als ein einziger Grundkoerper, aus dem Innenraum,
    Fenster, Bodennut und Steckverbindungen herausgeschnitten werden. Das ist eine bewusste
    Entscheidung: Eine fruehere Fassung setzte den Kanal aus einzelnen Waenden
    zusammen, und an den Stossflaechen entstanden 28 Netzfehler.</p>

    <h3>Alles parametrisch</h3>
    <p>Ganz oben in der Datei stehen die Masse als Variablen, alles Weitere leitet
    sich ab:</p>
    {code('beutel_breit = 88;\nwand         = 1.6;\nspiel        = 4;\ninnen_x  = beutel_breit + spiel;     // 92\naussen_x = innen_x + 2 * wand;       // 95,2', 'openscad')}
    <p>Aendert sich die gemessene Beutelbreite, wächst das ganze Modell mit &mdash;
    Wandstaerken, Fensterpositionen, Spaltenzahl. Genau das ist passiert: Die erste
    Auslegung ging von 72 mm aus, gemessen wurden 88. Ein Wert geaendert, alles
    andere folgte automatisch.</p>

    <h3>Eine Datei, sieben Teile</h3>
    <p>Ueber Parameter von aussen wird gesteuert, welches Teil erzeugt wird:</p>
    {code('openscad -o stl/segment-mitte.stl --export-format=binstl \\\\\n         -D \'TEIL="segment"\' -D \'segment_typ="mitte"\' \\\\\n         katzenfutter-regal.scad', 'bash')}
    <p>Das <code>-D</code> ueberschreibt eine Variable. Deshalb liefert eine Datei
    alle Segmenttypen, den Schieber, das Schild und die Passprobe.</p>
  </div>
</section>

<section>
  <h2 data-nr="03">STL: was dabei verloren geht</h2>
  <div class="text">
    <p>Ein STL ist nur noch eine Liste von Dreiecken &mdash; drei Punkte und eine
    Normale, sonst nichts. Kein Wissen mehr ueber Bohrungen, Parameter oder
    Zusammenhaenge. Ein Zylinder wird zum 32-eckigen Prisma.</p>
    <p>Das ist der Grund, warum im Blender-Skript alle Positionen noch einmal stehen:
    Die STL-Datei weiss nicht, dass sie ein Mittelsegment ist, das bei 163 mm
    anfaengt.</p>
  </div>
</section>

<section>
  <h2 data-nr="04">Blender: Bilder ueber Python</h2>
  <div class="text">
    <p>Blender wird ueber seine Python-Schnittstelle gesteuert. Auch hier kein
    Klicken, sondern ein Skript, das die STLs importiert, Materialien zuweist, Licht
    und Kamera setzt und rendert.</p>

    {code('bpy.ops.wm.stl_import(filepath="stl/segmente/front-mitte-mitte.stl")\nmaterial.inputs["Base Color"].default_value = (0.022, 0.022, 0.026, 1)\nscene.cycles.samples = 320\nbpy.ops.render.render(write_still=True)', 'openscad')}

    <p>Gerendert wird mit <strong>Cycles</strong>, einem Pathtracer: Er verfolgt
    Lichtstrahlen physikalisch. Deshalb wirken die Bilder wie Fotos &mdash; die weichen
    Schatten und die Reflexe auf dem orangen Schieber sind nicht gemalt, sondern
    gerechnet. 320 Strahlen pro Bildpunkt, rund 25 Sekunden je Bild auf der Grafikkarte.</p>

    <h3>Der Bildausschnitt wird gerechnet, nicht geschaetzt</h3>
    <p>Anfangs stand die Kamera auf einem festen Abstand, und Teile des Objekts lagen
    ausserhalb. Jetzt laeuft es umgekehrt:</p>
    <ul>
      <li>Jeden Eckpunkt aller Objekte ins Kamerakoordinatensystem umrechnen</li>
      <li>Daraus das Seitenverhaeltnis der Silhouette bestimmen und die
        Bildaufloesung passend setzen</li>
      <li>Den Abstand loesen, bei dem der aeusserste Punkt gerade noch im
        Sichtkegel liegt</li>
      <li>Die Bildmitte auf die Silhouette schieben, nicht auf das Objektzentrum
        &mdash; sonst klebt das Motiv an einer Seite</li>
    </ul>
    <p>Damit ist rechnerisch garantiert, dass nichts abgeschnitten wird und wenig
    Rand bleibt.</p>
  </div>
</section>

<section>
  <h2 data-nr="05">Python: die Pruefinstanz</h2>
  <div class="text">
    <p>Das ist der Teil, der ueber die Qualitaet entscheidet. Ein gerendertes Bild
    zeigt nicht, ob ein Netz Loecher hat oder ob zwei Teile sich durchdringen.
    Deshalb rechnet ein Pruefskript jede erzeugte Datei durch:</p>
  </div>

  <div class="tab"><table>
    <thead><tr><th>Pruefung</th><th>Verfahren</th><th>Sollwert</th></tr></thead>
    <tbody>
      <tr><td>Wasserdicht</td>
        <td class="w">Jede Kante muss in genau zwei Dreiecken vorkommen</td>
        <td class="num">0 offene</td></tr>
      <tr><td>Volumen</td>
        <td class="w">Divergenzsatz ueber alle Dreiecke</td>
        <td class="num">Gramm</td></tr>
      <tr><td>Ueberhaenge</td>
        <td class="w">Flaechennormalen gegen 45 Grad, Bettauflage gefiltert</td>
        <td class="num">unter 3 %</td></tr>
      <tr><td>Kollision</td>
        <td class="w">intersection() zweier Nachbarteile</td>
        <td class="num">0 cm&sup3;</td></tr>
      <tr><td>Bauraum</td>
        <td class="w">Bounding Box gegen das Druckbett</td>
        <td class="num">unter 180 mm</td></tr>
    </tbody>
  </table></div>

  <div class="text">
    <h3>Was die Pruefungen gefunden haben</h3>
    <p>Diese Tests haben echte Fehler aufgedeckt, die im Bild unsichtbar waren:</p>
    <ul>
      <li><strong>Flaechen ohne Volumen.</strong> Zwei Schnittkoerper endeten exakt
        auf derselben Ebene und hinterliessen eine Flaeche der Dicke null. Der Slicer
        haette 14 % des Teils als Ueberhang gesehen. Ein Ueberschnitt von 0,02 mm
        loeste es.</li>
      <li><strong>Eine Kollision von 0,16 cm&sup3;.</strong> Eine Anlaufschraege am
        Verbinder stiess in die Nachbarwand. Der Kollisionstest fand es sofort.</li>
      <li><strong>Fehlende Fenster.</strong> Bei kurzen Segmenten pruefte die
        Fensterlogik nur einen Bereich &mdash; die Teile waeren 20 % schwerer geworden.</li>
    </ul>

    <h3>Und einmal war die Physik der Pruefer</h3>
    <p>Die urspruengliche Anschlagkante war 18 mm hoch. Der Schiebedruck greift auf
    halber Beutelhoehe an, also bei 68 mm &mdash; Hebelarm 50 mm. Dagegen haelt nur
    das Eigengewicht auf der schmalen Standflaeche. Der vorderste Beutel waere schon
    bei 0,13 N gekippt, waehrend die Feder mit rund 6 N drueckt. Die Frontwand musste
    auf 92 mm wachsen, ueber den Angriffspunkt hinaus.</p>
  </div>
</section>

<section>
  <h2 data-nr="06">Die Bruchstellen zwischen den Programmen</h2>
  <div class="text">
    <p>OpenSCAD und Blender teilen sich nur die STL-Datei. Alle Positionen müssen
    doppelt gepflegt werden:</p>
    {code('# render2.py — muss zu katzenfutter-regal.scad passen\nAX, AZ = 95.2, 144.8       # Spaltenbreite, Ebenenhoehe\nLF, LM, LE = 163.0, 160.0, 161.6\nBODEN = 4.8', 'openscad')}
    <p>Aendert sich ein Mass im Modell und das Skript zieht nicht nach, stehen die
    Teile falsch. Genau das ist passiert: Nach einer Modellaenderung stand die
    Bodenhoehe im Skript noch auf 6,4 statt 4,8 mm &mdash; die Beutel schwebten
    1,6 mm zu hoch.</p>

    <h3>Der teuerste Fehler war eine Einheit</h3>
    <p>Blender rechnet in Metern, OpenSCAD in Millimetern. Ein 95-mm-Segment wird
    beim Import zu einem 95 <em>Meter</em> grossen Objekt. Die Kamera stand rund
    900 Einheiten entfernt &mdash; Blenders Standard-Clipping endet bei 100. Alles
    dahinter wurde weggeschnitten: die hintere Reihe, Teile der Sockel, ganze
    Rueckwaende. Uebrig blieben Fragmente, die wie Bildfehler aussahen. Ein
    <code>clip_end = 20000</code> behob es.</p>
  </div>
</section>

<section>
  <h2 data-nr="07">Die technischen Zeichnungen</h2>
  <div class="text">
    <p>Die bemassten Blaetter entstehen nicht aus dem STL, sondern direkt aus den
    Modellmassen &mdash; ein Python-Skript schreibt SVG. Das hat zwei Gruende: Die
    Masse sind exakt statt aus Dreiecken zurueckgerechnet, und Masslinien,
    Positionsnummern und Legende lassen sich frei setzen.</p>
    <p>Jede Masslinie bekommt mit <code>von=</code> die Kante mitgeteilt, an der
    sie ansetzt. Daraus zieht das Skript die duenne Hilfslinie bis zum Bauteil, so
    dass immer sichtbar bleibt, welche zwei Kanten ein Mass verbindet:</p>
    {code('def mh(self, x1, x2, y, zahl, was="", von=None, oben=False):\n    # von = Objektkante -> Hilfslinie laeuft von dort bis zur Masslinie\n    if von is not None:\n        for x in (x1, x2):\n            self.line(x, von, x, y - 6, HILF, 0.7)\n    self.line(x1, y, x2, y, MASSL)                   # die Masslinie\n    if (x2 - x1) < breite(zahl) + 10:                # zu eng fuer die Zahl?\n        ...                                          # dann steht sie daneben\n    self.txt((x1+x2)/2, y+3.6,  zahl, mono=True)     # die Zahl\n    self.txt((x1+x2)/2, y+17,   was,  klein, grau)   # wofuer sie steht', 'python')}
    <p>Damit sich nichts ueberdeckt, merkt sich das Skript zu jeder Beschriftung
    ein Rechteck und prueft am Ende alle Paare gegeneinander. Meldet es eine
    Ueberschneidung, wandert die betroffene Angabe, bis der Lauf still bleibt.
    Dieselbe Buchhaltung liefert die Blattgroesse: Das SVG wird genau um den
    belegten Bereich geschnitten, deshalb steht auf keinem Blatt eine leere
    Flaeche.</p>
    <p>SVG ist Vektorgrafik: Die Blaetter lassen sich beliebig vergroessern und
    ausdrucken, ohne unscharf zu werden.</p>
  </div>
</section>

<section>
  <h2 data-nr="08">Was dieser Weg nicht kann</h2>
  <div class="text">
    <p>Alles bisher Beschriebene rechnet. Es kann nicht anfassen, nicht drucken,
    nicht ausprobieren. Zwei Dinge bleiben offen und lassen sich nur am echten Teil
    klaeren:</p>
    <ul>
      <li><strong>Die Beutelmasse.</strong> Sie sind gemessen, nicht aus einem
        Datenblatt &mdash; Purina veroeffentlicht keine Verpackungsmasse. Deshalb
        steht die Passprobe am Anfang der Bauanleitung.</li>
      <li><strong>Die Reibung.</strong> Ob sich fuenfundzwanzig aneinanderlehnende
        Beutel sauber schieben lassen, haengt an der Folienoberflaeche. Dafuer gibt
        es keine Formel, nur den Versuch mit einem kurzen Kanal.</li>
    </ul>
  </div>
</section>

<footer>Modell, Skripte und Pruefungen liegen im Paket &middot; alle Masse in
Millimetern</footer>
</div>
"""

# =====================================================================
# Die Bildstrecke ist in Bloecke gegliedert: erst die Einzelteile, dann
# die Baugruppen, zuletzt der Ausbau. Jeder Block ist eine eigene Galerie.
BLOECKE = [
    ("Einzelteile", "Was gedruckt wird - jedes Teil fuer sich",
     ["b_front", "b_mitte", "b_end", "b_schieber", "b_schild"]),
    ("Zusammengebaut", "Wie die Teile ineinandergreifen",
     ["b_explosion", "b_kanal", "b_gefuellt"]),
    ("Entnahme", "Wie der Beutel herauskommt und wieviel Platz die Hand hat",
     ["b_greifraum", "b_entnahme"]),
    ("Im Schrank", "Eine Ebene und der volle Ausbau",
     ["b_ebene", "b_gesamt"]),
]


def _bild(n):
    return (f'<figure>'
            f'<button class="bild" data-gross="{V[n]}" data-was="{TITEL[n][0]}">'
            f'<img src="{R[n]}" alt="{TITEL[n][0]}" loading="lazy"></button>'
            f'<figcaption><h4>{TITEL[n][0]}</h4><p>{TITEL[n][1]}</p>'
            f'<a class="roh" href="{V[n]}" download>{NAMEN[n]}.png &darr;</a>'
            f'</figcaption></figure>')


_gal = "".join(
    f'<section class="block"><h2 data-nr="">{titel}</h2>'
    f'<p class="unter">{unter}</p>'
    f'<div class="gal">{"".join(_bild(n) for n in bilder)}</div></section>'
    for titel, unter, bilder in BLOECKE)

_schilder = ""
_sv = os.path.join(PROJ, "bilder", "schilder")
if os.path.isdir(_sv):
    kacheln = []
    for f in sorted(os.listdir(_sv)):
        if not f.endswith(".png"):
            continue
        name = f[:-4]
        sorte = name.split("-", 1)[1].replace("_", " ").upper()
        sorte = {"GEFLUEGEL": "GEFL&Uuml;GEL"}.get(sorte, sorte)
        kacheln.append(
            f'<figure><button class="bild" data-gross="schilder/{f}" '
            f'data-was="Schild {sorte}">'
            f'<img src="schilder/{f}" alt="Schild {sorte}" loading="lazy"></button>'
            f'<figcaption><h4>{sorte}</h4></figcaption></figure>')
    if kacheln:
        _schilder = (
            '<section class="block"><h2 data-nr="">Sortenschilder</h2>'
            '<p class="unter">Zwoelf fertige Schilder liegen im Paket. Weitere '
            'Sorten entstehen durch eine Zeile in werkzeuge/schilder.py.</p>'
            f'<div class="gal eng">{"".join(kacheln)}</div></section>')

_pl = "".join(f"""
  <figure>
    <button class="blatt" data-gross="{Z[n]}" data-was="{ZTITEL[n][0]}">
      <img src="{Z[n]}" alt="{ZTITEL[n][0]}" loading="lazy"></button>
    <figcaption><b>{ZTITEL[n][0]}</b><span>{ZTITEL[n][1]}</span>
      <a class="roh" href="{Z[n]}" download>{n}.svg &darr;</a></figcaption>
  </figure>""" for n in ZTITEL)

GALERIE = f"""
<div class="wrap">
<header>
  <p class="eyebrow">Bildstrecke</p>
  <h1>Alle Ansichten</h1>
  <p class="lead">Nach Bloecken geordnet: erst die Einzelteile, dann die
  Baugruppen, zuletzt der Ausbau im Schrank. Ein Klick vergroessert das Bild,
  mit den Pfeiltasten blaettert man durch, der Link darunter laedt die volle
  Aufloesung.</p>
</header>

{_gal}
{_schilder}

<footer>Alle Bilder mit Blender gerendert, direkt aus den STL-Dateien &middot;
PNG in voller Aufloesung im Ordner bilder/</footer>
</div>
"""

ZEICHNUNGEN = f"""
<div class="wrap">
<header>
  <p class="eyebrow">Massblaetter</p>
  <h1>Technische Zeichnungen</h1>
  <p class="lead">Sieben bemasste Blaetter. Jede Masslinie nennt darunter, welches
  Mass sie zeigt; die eingekreisten Ziffern verweisen auf die Liste am Blattrand.
  Alle Blaetter sind Vektorgrafik und lassen sich beliebig gross ausdrucken.</p>
</header>

<section style="padding-top:34px">
  <div class="plaene">{_pl}</div>
</section>

<footer>Erzeugt aus denselben Massen wie das Modell &middot; alle Masse in
Millimetern</footer>
</div>
"""

PROJEKT = f"""
<div class="wrap">
<header>
  <p class="eyebrow">Projektaufbau</p>
  <h1>Wie das Projekt aufgebaut ist</h1>
  <p class="lead">Eine Quelldatei, fuenf Skripte, der Rest ist erzeugt. Wer eine
  Zahl im Modell aendert, laesst die Skripte laufen und bekommt neue STLs,
  neue Zeichnungen, neue Bilder und diese Seiten &mdash; alles wieder zueinander
  passend.</p>
</header>

<section>
  <h2 data-nr="01">Der Verzeichnisbaum</h2>
  <p class="unter">Direkt aus dem Projektordner gelesen &mdash; was hier steht,
  liegt auch wirklich dort.</p>
  {dateibaum(PROJ)}
</section>

<section>
  <h2 data-nr="02">Erzeugt und von Hand geschrieben</h2>
  <div class="text">
    <p>Nur zwei Dinge sind handgeschrieben: das Modell und die Skripte. Alles
    andere entsteht daraus. Das ist der Grund, warum eine Massaenderung nicht
    an zehn Stellen nachgezogen werden muss.</p>
  </div>
  <div class="tab"><table>
    <thead><tr><th>Ordner</th><th>Herkunft</th><th>Was passiert, wenn das Modell
      sich aendert</th></tr></thead>
    <tbody>
      <tr><td class="num">modell/</td><td>von Hand</td>
        <td class="w">hier wird geaendert</td></tr>
      <tr><td class="num">werkzeuge/</td><td>von Hand</td>
        <td class="w">bleibt gleich</td></tr>
      <tr><td class="num">stl/</td><td>erzeugt</td>
        <td class="w">neu bauen mit stl-bauen.py</td></tr>
      <tr><td class="num">zeichnungen/</td><td>erzeugt</td>
        <td class="w">Masse werden aus dem Modell gelesen, nur neu laufen lassen</td></tr>
      <tr><td class="num">bilder/</td><td>erzeugt</td>
        <td class="w">Blender liest die neuen STLs</td></tr>
      <tr><td class="num">paket/</td><td>erzeugt</td>
        <td class="w">seiten.py baut alles neu zusammen</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2 data-nr="03">Alles neu bauen</h2>
  <div class="text">
    <p>Die Reihenfolge ist wichtig: erst die Geometrie, dann die Pruefung, dann
    was daraus abgeleitet wird.</p>
    {code('''# 1. Bauteile aus dem Modell erzeugen
python3 werkzeuge/stl-bauen.py

# 2. pruefen, bevor irgendwas darauf aufbaut
python3 werkzeuge/pruefen.py

# 3. Schilder fuer alle Sorten
python3 werkzeuge/schilder.py beide

# 4. bemasste Blaetter
python3 werkzeuge/zeichnungen.py

# 5. Bilder, je Szene ein Aufruf
for s in front mitte end schieber schild kanal explosion gefuellt ebene gesamt; do
    blender -b -P werkzeuge/rendern.py -- $s bilder/b_$s.png
done

# 6. Seiten und ZIP
python3 werkzeuge/seiten.py''', 'bash')}
    <div class="hinweis">Schritt 2 bricht mit einem Fehlercode ab, wenn ein Bauteil
    undicht ist, nicht aufs Druckbett passt oder eine Steckverbindung klemmt.
    Damit faellt ein Fehler auf, bevor Stunden Druckzeit darauf gehen.</div>
  </div>
</section>

<footer>Der Baum wird bei jedem Bau dieser Seite neu eingelesen</footer>
</div>
"""

os.makedirs(PAKET, exist_ok=True)
for datei, titel, inhalt in [
        ("index.html", "FutterStorage &mdash; Uebersicht", INDEX),
        ("projekt.html", "Projektaufbau &mdash; FutterStorage", PROJEKT),
        ("bauanleitung.html", "Bauanleitung &mdash; FutterStorage", BAU),
        ("technik.html", "Technische Umsetzung &mdash; FutterStorage", TECHNIK),
        ("zeichnungen.html", "Technische Zeichnungen &mdash; FutterStorage",
         ZEICHNUNGEN),
        ("galerie.html", "Alle Ansichten &mdash; FutterStorage", GALERIE)]:
    with open(os.path.join(PAKET, datei), "w", encoding="utf-8") as f:
        f.write(seite(titel, datei, inhalt))
    print(f"{datei:22s}{os.path.getsize(os.path.join(PAKET, datei))/1024:7.0f} kB")

if FUNDE:
    print("\nASCII-UMSCHRIFT STATT UMLAUT:")
    for f in FUNDE:
        print("  ! " + f)
else:
    print("\nSchreibung geprueft: alle Umlaute gesetzt")

# ---------------------------------------------------------------- Paket
import shutil, zipfile

for ordner in ("stl", "stl/schilder", "zeichnungen", "bilder",
               "bilder/schilder", "modell", "web", "werkzeuge",
               "schilder"):
    ziel = os.path.join(PAKET, ordner)
    os.makedirs(ziel, exist_ok=True)

for f in os.listdir(os.path.join(PROJ, "stl")):
    if f.endswith(".stl"):
        shutil.copy2(os.path.join(PROJ, "stl", f), os.path.join(PAKET, "stl", f))
for f in os.listdir(os.path.join(PROJ, "zeichnungen")):
    if f.endswith(".svg"):
        shutil.copy2(os.path.join(PROJ, "zeichnungen", f),
                     os.path.join(PAKET, "zeichnungen", f))

for alt, neu in NAMEN.items():
    q = os.path.join(PROJ, "bilder", alt + ".png")
    if os.path.exists(q):
        shutil.copy2(q, os.path.join(PAKET, "bilder", neu + ".png"))
    w = os.path.join(PROJ, "bilder", "web", alt + ".jpg")
    if os.path.exists(w):
        shutil.copy2(w, os.path.join(PAKET, "web", neu + ".jpg"))

shutil.copy2(os.path.join(PROJ, "modell", "katzenfutter-regal.scad"),
             os.path.join(PAKET, "modell", "katzenfutter-regal.scad"))
for f in sorted(os.listdir(os.path.join(PROJ, "werkzeuge"))):
    if f.endswith(".py"):
        shutil.copy2(os.path.join(PROJ, "werkzeuge", f),
                     os.path.join(PAKET, "werkzeuge", f))
# Die Schilderbilder liegen zusaetzlich flach unter schilder/, weil die
# Galerie sie von dort laedt.
_sq = os.path.join(PROJ, "bilder", "schilder")
if os.path.isdir(_sq):
    for f in sorted(os.listdir(_sq)):
        if f.endswith(".png"):
            shutil.copy2(os.path.join(_sq, f), os.path.join(PAKET, "schilder", f))
for u in ("stl/schilder", "bilder/schilder"):
    q = os.path.join(PROJ, u)
    if os.path.isdir(q):
        for f in sorted(os.listdir(q)):
            if not f.startswith("."):
                shutil.copy2(os.path.join(q, f), os.path.join(PAKET, u, f))

liesmich = """FUTTERSTORAGE
=============

Oeffne index.html im Browser - von dort aus ist alles verlinkt.

  index.html          Uebersicht und Einstieg
  bauanleitung.html   Was gedruckt und gekauft wird, wie es zusammengeht
  technik.html        Wie das Modell entstanden ist, Code und Werkzeuge
  zeichnungen.html    Die fuenf bemassten Blaetter zum Durchblaettern
  galerie.html        Alle zehn Renderings, klickbar in voller Groesse

  stl/                Sieben druckfertige Dateien fuer den Slicer
  zeichnungen/        Sieben bemasste Blaetter (SVG, beliebig skalierbar)
  bilder/             Zehn Renderings in voller Aufloesung (PNG)
  web/                Dieselben Bilder klein - werden von den Seiten geladen
  modell/             Die OpenSCAD-Quelldatei, alle Masse parametrisch

Die Seiten laufen ohne Internet: einfach index.html doppelklicken.
Alle Masse in Millimetern.
"""
with open(os.path.join(PAKET, "LIESMICH.txt"), "w") as f:
    f.write(liesmich)

zipname = os.path.join(PROJ, "futterstorage.zip")
if os.path.exists(zipname):
    os.remove(zipname)
with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for wurzel, _, dateien in os.walk(PAKET):
        for d in sorted(dateien):
            voll = os.path.join(wurzel, d)
            rel = os.path.relpath(voll, PAKET)
            z.write(voll, os.path.join("FutterStorage", rel))

print(f"\nfutterstorage.zip  {os.path.getsize(zipname)/1048576:.1f} MB")
