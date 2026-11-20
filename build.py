#!/usr/bin/env python3
"""Bouwt index.html uit data/course.json (+ handmatig bewerkte lessons/NN.html)."""
import json, re, html, os
ROOT = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(f"{ROOT}/data/course.json", encoding="utf-8"))

SECTIONS = [
    ("Basis AI Literacy", [0, 1, 2, 3, 4]),
    ("Impact van AI op onderwijs", [5, 6, 7]),
    ("Toepassingen AI-omgeving voor werk en onderwijs", [8, 9]),
    ("Einde", [10]),
]
TITLES = {
    0: "Introductie: HU-visie en beleid",
    1: "Basiskennis",
    2: "Hoe gebruik je AI?",
    3: "Beperkingen: hallucinaties, inconsistentie en verouderde kennis",
    4: "Ethiek en maatschappij",
    5: "Impact op studenten",
    6: "Impact op constructive alignment",
    7: "Impact op toetsing",
    8: "Persona's en andere toepassingen van de HU AI-omgeving",
    9: "Voorbeelden van binnen en buiten de HU",
    10: "Afsluiting en meer informatie",
}

# ---------- HU-markeringen ----------
FLAG = re.compile(
    r"(UvA AI Chat)|(Universiteit van Amsterdam|\bUvA\b|\bAUC\b|Amsterdam University College|Living Lab AI|\bTLC\b(?: Central| Science)?|Faculteit der [A-Za-zé\- ]+(?:wetenschappen|geleerdheid)|\bFNWI\b)"
)

def flag_text(t):
    def rep(m):
        if m.group(1):
            return '<mark class="todo" title="Vervang door de HU AI-omgeving">HU AI-omgeving</mark>'
        return f'<mark class="flag" title="UvA-specifiek: aanpassen voor de HU">{m.group(0)}</mark>'
    return FLAG.sub(rep, t)

def flag_html(h):
    parts = re.split(r"(<[^>]+>)", h)
    out, in_mark = [], False
    for p in parts:
        if p.startswith("<"):
            if p.startswith("<a ") and re.search(r'href="[^"]*(uva\.nl|illc\.uva|articulate\.com/share|rise\.articulate)', p):
                p = p.replace("<a ", '<a class="flag-link" title="Link naar UvA-bron: vervang door HU-bron" ', 1)
            if p.startswith("<mark"): in_mark = True
            if p.startswith("</mark"): in_mark = False
            out.append(p)
        else:
            out.append(p if in_mark else flag_text(p))
    return "".join(out)

# ---------- opschonen per bloktype ----------
def tidy(h):
    h = h.replace("(opens in a new tab)", "")
    h = re.sub(r"<h([23])><p>(.*?)</p></h\1>", r"<h\1>\2</h\1>", h, flags=re.S)
    h = re.sub(r"<h3><h2>(.*?)</h2></h3>", r"<h3>\1</h3>", h, flags=re.S)
    h = re.sub(r"<h2><strong>(.*?)</strong></h2>", r"<h2>\1</h2>", h, flags=re.S)
    h = h.replace("<br></p>", "</p>")
    h = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', h)
    h = re.sub(r"<p>\s*</p>", "", h)
    return h

def accordion(h):
    parts = re.split(r"<h2>(.*?)</h2>", h, flags=re.S)
    items = "".join(
        f"<details><summary>{parts[i]}</summary>{parts[i+1]}</details>"
        for i in range(1, len(parts) - 1, 2)
    )
    return f'<div class="accordion">{items}</div>'

def timeline(h):
    lis = re.findall(r"<li>(.*?)</li>", h, flags=re.S)
    items = "".join(
        "<details{}>".format(" open" if i == 0 else "") + re.sub(r"<h3>(.*?)</h3>", r"<summary>\1</summary>", li, count=1, flags=re.S) + "</details>"
        for i, li in enumerate(lis)
    )
    return f'<div class="accordion">{items}</div>'

def tabs(h, labels, splitter):
    body = h
    for l in labels:
        body = body.replace(l, "", 1)
    panes = splitter(body)
    assert len(panes) == len(labels), (len(panes), labels)
    tb = "".join(f'<button role="tab" type="button">{l}</button>' for l in labels)
    pn = "".join(f'<div class="pane" role="tabpanel">{p}</div>' for p in panes)
    return f'<div class="tabs"><div class="tablist" role="tablist">{tb}</div>{pn}</div>'

def split_by(markers):
    def f(body):
        idx = [0] + [body.index(m) for m in markers]
        idx.append(len(body))
        # markers die de start van een <p> zijn: neem de <p> mee
        out = []
        for a, b in zip(idx, idx[1:]):
            out.append(body[a:b])
        # zet <p> die achter het einde van een pane is blijven staan terug bij de volgende pane
        fixed = []
        carry = ""
        for seg in out:
            seg = carry + seg
            carry = ""
            m = re.search(r"<p>(?:<[^>]+>)*$", seg)
            if m:
                carry = m.group(0)
                seg = seg[: m.start()]
            fixed.append(seg)
        return fixed
    return f

def split_context(body):
    parts = re.split(r"(?=<p><strong>Context</strong>:)", body)
    return [p for p in parts if p.strip()]

def process(h):
    m = re.search(r"1 of 5(.*?)2 of 5Step 1(.*?)3 of 5Step 2(.*?)4 of 5Step 3(.*?)5 of 5(.*)", h, flags=re.S)
    intro, s1, s2, s3, summ = m.groups()
    intro = intro.replace("START", "")
    summ = summ.replace("START AGAIN", "")
    steps = [("Introductie", intro), ("Stap 1", s1), ("Stap 2", s2), ("Stap 3", s3), ("Samenvatting", summ)]
    cards = "".join(
        f'<section class="step"><div class="step-n">{n}</div>{t}</section>' for n, t in steps
    )
    return f'<div class="process">{cards}</div>'

SORT_ITEMS = [
    ("Je argumentatie opbouwen en onder woorden brengen", "goed"),
    ("Handmatig metingen uit je notities overtypen in Excel", "onnodig"),
    ("Een tekst die je als bron wil gebruiken nauwkeurig ontleden", "goed"),
    ("De verschillen zoeken tussen twee versies van hetzelfde document", "onnodig"),
    ("Een complexe theorie analyseren en een eigen standpunt innemen", "goed"),
    ("Dubbele spaties uit je tekst halen", "onnodig"),
    ("Tien gelijksoortige tabellen opmaken", "onnodig"),
    ("Je onderzoeksmethoden binnen een theoretisch kader plaatsen", "goed"),
    ("Snel scannen of de auteurs een ANOVA of een Kruskal-Wallis-test hebben gebruikt", "onnodig"),
    ("Een discussie schrijven over de beperkingen van de gekozen meetmethode", "goed"),
    ("Termen uit het Latijn cursief maken", "onnodig"),
]

def sorting():
    items = json.dumps(SORT_ITEMS, ensure_ascii=False).replace("'", "&#39;")
    return (
        '<div class="sorting" data-items=\'' + items + '\'>'
        '<p class="hint"><mark class="todo" title="Antwoordsleutel afgeleid; controleer">[controleer antwoordsleutel]</mark> '
        'Is dit goede frictie (helpt je leren) of onnodige frictie (kost alleen tijd)?</p>'
        '<div class="sort-card"></div>'
        '<div class="sort-actions"><button type="button" data-a="goed">Goede frictie</button>'
        '<button type="button" data-a="onnodig">Onnodige frictie</button></div>'
        '<div class="sort-fb" aria-live="polite"></div></div>'
    )

def convert(b, lesson):
    t, h = b["t"], b["html"]
    if h.strip() in ("Continued", "") or h.strip().startswith("Continued"):
        return ""
    h = tidy(h)
    if t == "block-text":
        return flag_html(h)
    if t == "block-image":
        if h.startswith("<img") and "<figcaption>" in h:
            img, cap = h.split("<figcaption>", 1)
            return f"<figure>{img}<figcaption>{flag_html(cap.replace('</figcaption>',''))}</figcaption></figure>"
        if h.startswith("<img") and h.count("<img") == 1 and h.rstrip().endswith(">") and "<p>" not in h:
            return f'<figure>{h}</figure>'
        return flag_html(re.sub(r"<img ([^>]*)>", r'<figure><img \1 alt=""></figure>', h))
    if t == "block-statement":
        return f'<div class="statement">{flag_html(h)}</div>'
    if t == "block-list":
        h = re.sub(r"<li>•", "<li>", h)
        return flag_html(h)
    if t == "block-quote":
        img = re.match(r'<img src="([^"]+)">', h)
        rest = h[img.end():] if img else h
        im = f'<img src="{img.group(1)}" alt="">' if img else ""
        return f'<div class="quote">{im}<div>{flag_html(rest)}</div></div>'
    if t == "block-embed":
        h2 = h.replace("<iframe ", '<iframe loading="lazy" allowfullscreen ')
        return '<div class="embed">' + h2 + '</div>'
    if t == "blocks-accordion":
        return flag_html(accordion(h))
    if t == "block-timeline":
        return flag_html(timeline(h))
    if t == "blocks-buttonstack":
        pieces = re.findall(r"(<p>.*?</p>(?:<p>.*?</p>)?)<a href=\"([^\"]+)\"[^>]*>(.*?)</a>", h, flags=re.S)
        cards = "".join(f'<div>{p}<a class="btn" href="{u}" target="_blank" rel="noopener">{l}</a></div>' for p, u, l in pieces)
        return flag_html(f'<div class="buttons">{cards}</div>')
    if t == "block-sorting-activity":
        return sorting()
    if t == "block-process":
        return flag_html(process(h))
    if t == "blocks-tabs":
        if "Marketingseminar" in h:
            labels = ["Marketingseminar (Faculteit der Maatschappij- en Gedragswetenschappen)",
                      "Privaatrecht (Faculteit der Rechtsgeleerdheid)",
                      "Grote vragen in AI en Data (Amsterdam University College)"]
            return flag_html(tabs(h, labels, split_by(["<p>Binnen de master Privaatrecht", "<p>Aan het begin van de cursus"])))
        labels = ["Tegen-debatant", "UvA Makerspace assistent", "Onderwijsassistent"]
        return flag_html(tabs(h, labels, split_context))
    return f'<div class="raw">{flag_html(h)}</div>'

import html as _html
CONT = json.load(open(f"{ROOT}/data/cont.json", encoding="utf-8"))

def sig(b):
    h = b["html"]
    txt = _html.unescape(re.sub(r"<[^>]+>", "", h))
    txt = re.sub(r"[\s\u00a0]+", " ", txt).strip()
    if b["t"] == "block-sorting-activity": return "SORT"
    if b["t"] == "block-process": return "PROCESS"
    if txt: return "t:" + txt[:30]
    m = re.search(r'<img[^>]+src="[^"]*/([^"/]+)"', h)
    if m: return "i:" + m.group(1)[:12]
    return "e"

def with_markers(i):
    blocks = [b for b in D[str(i)]["blocks"] if b["html"].strip() not in ("", "Continued")]
    marks = CONT[i][:-1]  # laatste knop = naar volgend hoofdstuk
    out, k, pending = [], 0, False
    for b in blocks:
        sg = sig(b)
        if pending and sg != "e":
            out.append('<div class="cont"></div>'); pending = False
        out.append(convert(b, i))
        if k < len(marks) and sg != "e" and (sg == marks[k] or sg[:20] == marks[k][:20] or (marks[k].startswith("i:") and marks[k][2:] in b["html"])):
            pending = True; k += 1
    if k < len(marks):
        print(f"WAARSCHUWING hoofdstuk {i+1}: {len(marks)-k} markering(en) niet geplaatst")
    return "\n".join(out)

def lesson_html(i):
    p = f"{ROOT}/lessons/{i+1:02d}.html"
    if os.path.exists(p):
        body = open(p, encoding="utf-8").read()
    else:
        body = with_markers(i)
    return body

# ---------- pagina ----------
def nav():
    out = []
    for name, ids in SECTIONS:
        out.append(f'<div class="nav-sec">{name}</div>')
        for i in ids:
            out.append(f'<a href="#/{i+1}" data-n="{i+1}"><span class="num">{i+1}</span><span class="t">{TITLES[i]}</span><span class="badge" hidden></span></a>')
    return "\n".join(out)

def overview_list():
    out = []
    for name, ids in SECTIONS:
        out.append(f'<h3 class="sec">{name}</h3><ul class="chapters">')
        for i in ids:
            out.append(f'<li><a href="#/{i+1}"><span class="num">{i+1}</span>{TITLES[i]}</a></li>')
        out.append("</ul>")
    return "\n".join(out)

articles = "\n".join(
    f'<article data-n="{i+1}" hidden><header><div class="eyebrow">Hoofdstuk {i+1} van 11</div><h1>{TITLES[i]}</h1></header>{lesson_html(i)}</article>'
    for i in range(11)
)

page = open(f"{ROOT}/template.html", encoding="utf-8").read()
page = page.replace("{{NAV}}", nav()).replace("{{OVERVIEW_LIST}}", overview_list()).replace("{{ARTICLES}}", articles)
open(f"{ROOT}/index.html", "w", encoding="utf-8").write(page)
print("index.html geschreven:", len(page), "bytes")
