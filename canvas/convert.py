"""Zet de HU-versie van 'AI Literacy voor docenten' om naar Canvas-pagina's met inline opmaak."""
import json, re, sys, copy
from bs4 import BeautifulSoup, NavigableString

SRC = 'src/index.html'
OUT = 'out'
RED = '#e6302b'; INK = '#1d1d1b'; MUTED = '#6f6f6e'; LINE = '#dadada'; SOFT = '#f2f2f2'
REDT = '#fde7e6'; BLUET = '#e3f5fc'; LINK = '#0077a8'
FONT = 'font-family: Arial, Helvetica, sans-serif;'
SHADOW = 'border-bottom: 3px solid #c8c8c8;'

# hoofdstukken die meegaan (origineel nummer -> nieuw nummer)
KEEP = [1, 2, 3, 4, 5, 6, 7, 8, 11]
NEW = {o: i + 1 for i, o in enumerate(KEEP)}
TOTAL = len(KEEP)
SECTION = {1: 'Basis AI Literacy', 2: 'Basis AI Literacy', 3: 'Basis AI Literacy', 4: 'Basis AI Literacy',
           5: 'Basis AI Literacy', 6: 'Impact van AI op onderwijs', 7: 'Impact van AI op onderwijs',
           8: 'Impact van AI op onderwijs', 11: 'Afsluiting'}

KALTURA = ('https://api.eu.kaltura.com/p/120/sp/12000/embedIframeJs/uiconf_id/23449960/partner_id/120?iframeembed=true'
           '&playerId=kaltura_player&entry_id={e}&flashvars[streamerType]=auto&flashvars[localizationCode]=en_US'
           '&flashvars[sideBarContainer.plugin]=true&flashvars[sideBarContainer.position]=left'
           '&flashvars[sideBarContainer.clickToClose]=true&flashvars[chapters.plugin]=true'
           '&flashvars[chapters.layout]=vertical&flashvars[chapters.thumbnailRotator]=false'
           '&flashvars[streamSelector.plugin]=true&flashvars[EmbedPlayer.SpinnerTarget]=videoHolder'
           '&flashvars[dualScreen.plugin]=true&flashvars[hotspots.plugin]=1&flashvars[Kaltura.addCrossoriginToIframe]=true&&wid={w}')

soup = BeautifulSoup(open(SRC, encoding='utf8'), 'html.parser')


def new(tag, style=None, **attrs):
    t = soup.new_tag(tag, **attrs)
    if style:
        t['style'] = style
    return t


def video(src, title):
    wrap = new('div', 'position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 24px 0; border-radius: 8px; background: #000;')
    ifr = new('iframe', 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;',
              src=src, title=title or 'Video', allowfullscreen='allowfullscreen', allow='autoplay *; fullscreen *; encrypted-media *')
    wrap.append(ifr)
    return wrap


def style_inline(root):
    """Pas alle bekende klassen toe als inline stijl."""
    # verwijder 'Doorgaan'-ankers en hidden-attributen
    for c in root.select('.cont'):
        c.decompose()
    # markeringen
    for m in root.select('mark.flag'):
        m.unwrap()
    for m in root.select('mark.todo'):
        m.name = 'span'
        m['style'] = f'background-color: {BLUET}; color: #00507a; font-weight: bold; padding: 0 4px; border-radius: 3px;'
        del m['class']
        if m.has_attr('title'):
            del m['title']
    for a in root.select('a.flag-link'):
        del a['class']
        if a.has_attr('title'):
            del a['title']
    # video's
    for k in root.select('.kaltura'):
        k.replace_with(video(KALTURA.format(e=k['data-entry'], w=k['data-wid']), k.get('data-title')))
    for e in root.select('.embed'):
        f = e.find('iframe')
        e.replace_with(video(f['src'], f.get('title')))
    # afbeeldingen
    for fig in root.find_all('figure'):
        fig['style'] = 'margin: 28px 0;'
        img = fig.find('img')
        if img:
            img['style'] = 'max-width: 100%; height: auto; border-radius: 10px; display: block;'
        cap = fig.find('figcaption')
        if cap:
            cap['style'] = f'{FONT} font-size: 13px; line-height: 1.5; color: {MUTED}; margin-top: 8px;'
    # statement
    for s in root.select('.statement'):
        s['style'] = f'margin: 32px 0; padding: 22px 28px; background-color: {RED}; color: #ffffff; font-weight: bold; font-size: 1.15em; border-radius: 10px;'
        for a in s.find_all('a'):
            a['style'] = 'color: #ffffff; text-decoration: underline;'
        for sp in s.find_all('span', style=True):
            sp['style'] = 'background-color: #ffffff; color: #00507a; font-weight: bold; padding: 0 4px; border-radius: 3px;'
        for p in s.find_all('p'):
            p['style'] = 'margin: 0;'
    # callout
    for c in root.select('.callout'):
        c['style'] = f'margin: 32px 0; padding: 6px 24px 14px; background-color: {BLUET}; border-radius: 10px; border-left: 6px solid #00a1e1;'
    # quote
    for q in root.select('.quote'):
        img = q.find('img'); body = q.find('div')
        tbl = new('table', 'width: 100%; border: 0; margin: 32px 0; border-collapse: collapse;', role='presentation')
        tr = new('tr'); tbl.append(tr)
        if img:
            td1 = new('td', 'width: 120px; vertical-align: middle; padding: 0 18px 0 0; border: 0;')
            img['style'] = 'width: 110px; height: 110px; border-radius: 50%; object-fit: cover; display: block;'
            td1.append(img.extract()); tr.append(td1)
        td2 = new('td', 'vertical-align: middle; border: 0; padding: 0;')
        bq = body.find('blockquote')
        if bq:
            bq['style'] = f'margin: 0; font-style: italic; border-left: 4px solid {RED}; padding-left: 16px;'
        cap = body.find('figcaption')
        if cap:
            cap.name = 'div'
            cap['style'] = f'{FONT} font-size: 14px; color: {MUTED}; margin-top: 6px; padding-left: 20px;'
        for ch in list(body.children):
            td2.append(ch.extract())
        tr.append(td2)
        q.replace_with(tbl)
    # tabs -> uitklapblokken
    for t in root.select('.tabs'):
        acc = new('div', 'class_ignored')
        acc.attrs = {'class': ['accordion']}
        labels = [b for b in t.select('.tablist [role=tab]')]
        panes = t.select('.pane')
        for b, p in zip(labels, panes):
            d = new('details'); s = new('summary')
            for ch in list(b.children):
                s.append(ch.extract())
            d.append(s)
            for ch in list(p.children):
                d.append(ch.extract())
            acc.append(d)
        t.replace_with(acc)
    # accordion
    for acc in root.select('.accordion'):
        acc['style'] = f'margin: 24px 0; border: 1px solid {LINE}; border-radius: 10px; {SHADOW}'
        del acc['class']
        ds = acc.find_all('details', recursive=False)
        for i, d in enumerate(ds):
            if d.has_attr('open'):
                del d['open']
            d['style'] = f'border-bottom: 1px solid {LINE};' if i < len(ds) - 1 else ''
            if not d['style']:
                del d['style']
            s = d.find('summary')
            s['style'] = f'cursor: pointer; padding: 14px 18px; font-weight: bold; {FONT} color: {INK};'
            inner = new('div', 'padding: 4px 18px 14px;')
            for ch in list(d.children):
                if ch is not s:
                    inner.append(ch.extract())
            d.append(inner)
    # knoppen/kaarten
    for b in root.select('.buttons'):
        b['style'] = 'margin: 24px 0;'
        del b['class']
        for card in b.find_all('div', recursive=False):
            card['style'] = f'display: inline-block; vertical-align: top; width: 42%; min-width: 220px; margin: 0 12px 14px 0; padding: 16px; border: 1px solid {LINE}; border-radius: 10px; {SHADOW}'
    for a in root.select('a.btn'):
        del a['class']
        a['style'] = f'display: inline-block; margin-top: 6px; padding: 8px 16px; border-radius: 6px; background-color: {RED}; color: #ffffff; text-decoration: none; font-weight: bold; {FONT} font-size: 14px;'
    # proces/stappen
    for p in root.select('.process'):
        p['style'] = 'margin: 28px 0;'
        del p['class']
    for st in root.select('.step'):
        st.name = 'div'
        st['style'] = f'margin: 0 0 14px; padding: 6px 22px 12px; border: 1px solid {LINE}; border-radius: 10px; {SHADOW} border-top: 4px solid {RED};'
        del st['class']
    for sn in root.select('.step-n'):
        sn['style'] = f'{FONT} font-size: 12px; font-weight: bold; color: {RED}; margin-top: 14px;'
        sn.string = sn.get_text().upper()
        del sn['class']
    for h in root.find_all(['h2']):
        h['style'] = f'{FONT} font-weight: bold; color: {INK}; margin-top: 36px;'
    for h in root.find_all(['h3']):
        h['style'] = f'{FONT} font-weight: bold; color: {INK};'
    for a in root.find_all('a'):
        if not a.get('style'):
            a['style'] = f'color: {LINK};'
        if a.get('href', '').startswith('http'):
            a['target'] = '_blank'; a['rel'] = 'noopener'
    for el in root.find_all(class_=True):
        del el['class']
    return root


def sorting_to_text(srt):
    items = json.loads(srt['data-items'])
    box = new('div', f'margin: 28px 0; padding: 20px 24px; background-color: {SOFT}; border: 1px solid {LINE}; border-radius: 10px;')
    p = new('p', 'margin-top: 0;'); p.append(BeautifulSoup('<strong>Oefening: goede of onnodige frictie?</strong> Bepaal voor elke taak of het <em>goede frictie</em> is (de moeite helpt je leren) of <em>onnodige frictie</em> (kost alleen tijd). Doe de oefening als korte kennischeck: <strong>Kennischeck: goede of onnodige frictie?</strong> staat in de module direct na dit hoofdstuk. Of klap hieronder de antwoorden open.', 'html.parser'))
    box.append(p)
    d = new('details', f'background-color: #ffffff; border: 1px solid {LINE}; border-radius: 8px;')
    s = new('summary', f'cursor: pointer; padding: 12px 16px; font-weight: bold; {FONT}'); s.string = 'Bekijk alle taken met het antwoord'
    d.append(s)
    ul = new('ul', 'padding: 4px 18px 14px 36px; margin: 0;')
    for txt, a in items:
        li = new('li', 'margin: 4px 0;')
        li.append(txt + ' – ')
        b = new('strong', f'color: {RED if a == "goed" else MUTED};'); b.string = 'goede frictie' if a == 'goed' else 'onnodige frictie'
        li.append(b); ul.append(li)
    d.append(ul); box.append(d)
    return box, items


def banner(eyebrow, title, sub=None):
    html = f'''<div style="background-color: {RED}; color: #ffffff; padding: 28px 30px 26px; border-radius: 12px; margin: 0 0 28px;">
<p style="{FONT} font-size: 12px; font-weight: bold; margin: 0 0 8px; color: #ffffff;">{eyebrow.upper()}</p>
<h2 style="{FONT} font-size: 1.9em; line-height: 1.2; font-weight: bold; margin: 0; color: #ffffff;">{title}</h2>
{f'<p style="margin: 10px 0 0; color: #ffffff; font-size: 1.05em;">{sub}</p>' if sub else ''}
</div>'''
    return html


def wrap(inner):
    return f'<div style="max-width: 800px; margin: 0 auto; {FONT} font-size: 16px; line-height: 1.65; color: {INK};">\n{inner}\n</div>'


def attribution():
    return (f'<div style="margin-top: 44px; padding: 16px 20px; border: 1px solid {LINE}; border-radius: 8px; background-color: {SOFT}; {FONT} font-size: 13px; line-height: 1.55; color: {MUTED};">'
            'Bewerking van <a style="color: #0077a8;" href="https://share.articulate.com/svX7iZbENb4ocjD2biC6-#/" target="_blank" rel="noopener">“AI Literacy voor docenten”</a> van TLC Central &amp; TLC Science, Universiteit van Amsterdam, gebruikt met toestemming. '
            'Licentie: <a style="color: #0077a8;" href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.nl" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>. Logo’s en huisstijlelementen van UvA en HU vallen niet onder deze licentie.</div>')


# Opdrachten per hoofdstuk (zelfsturend, niet inleveren)
TASKS = {
    1: ('Aan de slag', ['Zoek op welke AI-tools je binnen de HU mag gebruiken en welke afspraken jouw opleiding hanteert.',
                       'Open de AI-omgeving van de HU (of Copilot met je HU-account) en stel één vraag over je eigen vak.',
                       'Noteer in één zin wat “human in the lead” voor jouw eigen onderwijs betekent.']),
    2: ('Aan de slag', ['Bekijk minimaal één van de video’s en leg daarna in eigen woorden uit wat een LLM doet als het “het volgende woord voorspelt”.',
                       'Kies drie begrippen uit de lijst die je nog niet goed kende en schrijf voor jezelf een korte definitie op.']),
    3: ('Aan de slag: oefen met prompten', ['Kies een taak uit je eigen werk (bijvoorbeeld een lesopzet, een casus of een e-mail aan studenten).',
                       'Schrijf een eerste, korte prompt en bekijk het resultaat.',
                       'Laat de AI daarna je prompt verbeteren (“Welke informatie mis je om dit goed te doen?”) en vergelijk beide resultaten.',
                       'Bewaar de beste prompt: je kunt hem gebruiken in sessie 1.']),
    4: ('Aan de slag: controleer de AI', ['Vraag een AI-tool om drie wetenschappelijke bronnen over een onderwerp uit je vak, met auteurs en jaartal.',
                       'Controleer of de bronnen bestaan en of ze zeggen wat de AI beweert.',
                       'Stel dezelfde vraag nog een keer in een nieuw gesprek. Wat is er anders?']),
    5: ('Aan de slag: ethiek in jouw vak', ['Kies één van de drie kwesties (energie, auteursrecht of bias) die het meest speelt in jouw vakgebied.',
                       'Bedenk één vraag waarmee je dit onderwerp met studenten zou kunnen bespreken.',
                       'Test jezelf met de <strong>Kennischeck: Basis AI Literacy</strong> (hoofdstuk 1 tot en met 5) in deze module.']),
    6: ('Aan de slag', ['Doe de kennischeck <strong>Goede of onnodige frictie?</strong> in deze module.',
                       'Kies een opdracht uit je eigen onderwijs: welke stappen zijn goede frictie die studenten zelf moeten blijven doen?']),
    7: ('Aan de slag: kies je onderwijseenheid', ['Kies de onderwijseenheid die je tijdens de training gaat herontwerpen.',
                       'Zet de leerdoelen, de toets en de belangrijkste leeractiviteiten onder elkaar. Waar raakt AI aan elk van de drie?',
                       'Neem deze eerste analyse mee naar sessie 1.']),
    8: ('Aan de slag: two-lane approach', ['Neem de toets van je gekozen onderwijseenheid erbij.',
                       'Bepaal per leerdoel: hoort dit in lane 1 (gecontroleerd, zonder AI) of lane 2 (AI beschikbaar, onderbouwde keuzes)?',
                       'Test jezelf met de <strong>Kennischeck: Impact van AI op onderwijs</strong> (hoofdstuk 6 tot en met 8) in deze module.']),
    11: ('Afronden van de voorbereiding', ['Doe de kennischecks in deze module als je dat nog niet gedaan hebt.',
                       'Lever de opdracht <strong>Zelfstudie vooraf</strong> in (module Start) vóór sessie 1.']),
}


def task_box(n):
    title, steps = TASKS[n]
    lis = ''.join(f'<li style="margin: 6px 0;">{s}</li>' for s in steps)
    return (f'<div style="margin: 40px 0 8px; padding: 18px 24px 16px; border: 2px solid {RED}; border-radius: 12px; background-color: {REDT};">'
            f'<p style="{FONT} font-size: 12px; font-weight: bold; color: {RED}; margin: 0 0 4px;">OPDRACHT · CA. 10 MINUTEN · NIET INLEVEREN</p>'
            f'<h3 style="{FONT} font-weight: bold; margin: 0 0 8px; color: {INK};">{title}</h3>'
            f'<ol style="margin: 0; padding-left: 22px;">{lis}</ol></div>')


pages = []
sorting_items = None
for o in KEEP:
    art = copy.copy(soup.select_one(f'article[data-n="{o}"]'))
    title = art.find('header').find('h1').get_text(strip=True)
    art.find('header').decompose()
    srt = art.select_one('.sorting')
    if srt:
        box, sorting_items = sorting_to_text(srt)
        srt.replace_with(box)
    for st in art.select('.statement'):
        if 'Sleep de voorbeelden' in st.get_text():
            st.find('p').string = 'Wat beschouw jij als goede of onnodige frictie? Probeer het hieronder.'
    art = style_inline(art)
    for nav in art.select('.nav-btns'):
        nav.decompose()
    body = ''.join(str(c) for c in art.children)
    n = NEW[o]
    ttl = 'Afsluiting en meer informatie' if o == 11 else title
    head = banner(f'Hoofdstuk {n} van {TOTAL} · {SECTION[o]}', ttl)
    html = wrap(head + body + task_box(o) + attribution())
    pages.append({'orig': o, 'n': n, 'title': f'{n}. {ttl}', 'html': html})

# ---- startpagina ----
ov = copy.copy(soup.select_one('#overview .wrap'))
intro_ps = [p for p in ov.find_all('p', recursive=False)][:2]
goals = ov.find('ul')
lis = [li for li in goals.find_all('li')]
lis[-1].decompose()  # 'Praktisch aan de slag met HU AI-omgeving' hoort bij weggelaten deel
for i in intro_ps:
    style_inline(i)
style_inline(goals)
for li in goals.find_all('li'):
    li['style'] = 'margin: 4px 0;'
todo_q = ov.find_all('p', recursive=False)
contact = [p for p in todo_q if 'Vragen over de inhoud' in p.get_text()]
for c in contact:
    style_inline(c)
start_items = ''
sec = None
for pg in pages:
    s = SECTION[pg['orig']]
    if s != sec:
        start_items += f'<p style="{FONT} font-size: 12px; font-weight: bold; color: {RED}; margin: 26px 0 4px;">{s.upper()}</p>'
        sec = s
    start_items += (f'<p style="margin: 0; padding: 10px 4px; border-bottom: 1px solid {LINE};">'
                    f'<span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; border-radius: 50%; background-color: {SOFT}; font-size: 13px; margin-right: 12px;">{pg["n"]}</span>'
                    f'<a style="color: {INK}; text-decoration: none;" href="{{{{PAGE:{pg["n"]}}}}}">{pg["title"][len(str(pg["n"]))+2:]}</a></p>')
hero = f'''<div style="background-color: #ffffff; border: 1px solid {LINE}; border-radius: 12px 12px 0 0; padding: 18px 24px;"><img style="width: 190px; height: auto; display: block;" src="{{{{LOGO}}}}" alt="Hogeschool Utrecht"></div>
<div style="background-color: {RED}; color: #ffffff; padding: 44px 30px 34px; border-radius: 0 0 12px 12px; margin-bottom: 32px;">
<p style="{FONT} font-size: 13px; font-weight: bold; margin: 0 0 10px; color: #ffffff;">ZELFSTUDIE VOORAF · E-LEARNING VOOR DOCENTEN</p>
<h2 style="{FONT} font-size: 2.3em; line-height: 1.15; font-weight: bold; margin: 0 0 12px; color: #ffffff;">AI Literacy voor docenten</h2>
<p style="font-size: 1.1em; margin: 0 0 22px; color: #ffffff;">Ongeveer één uur · {TOTAL} hoofdstukken · los van elkaar te volgen</p>
<a style="display: inline-block; padding: 12px 28px; border-radius: 6px; background-color: #ffffff; color: {INK}; font-weight: bold; text-decoration: none; " href="{{{{PAGE:1}}}}">START</a>
</div>'''
how = (f'<div style="margin: 28px 0; padding: 6px 24px 14px; background-color: {BLUET}; border-radius: 10px; border-left: 6px solid #00a1e1;">'
       f'<h3 style="{FONT} font-weight: bold;">Zo werk je met deze module</h3>'
       '<ul style="margin: 0; padding-left: 22px;"><li>Lees de hoofdstukken in je eigen tempo; gebruik de knop <strong>Volgende</strong> onderaan elke pagina.</li>'
       '<li>Elk hoofdstuk eindigt met een korte <strong>opdracht</strong> om het meteen toe te passen op je eigen vak. Die hoef je niet in te leveren.</li>'
       '<li>Test jezelf met de <strong>kennischecks</strong>. Ze tellen niet mee en je kunt ze zo vaak maken als je wilt.</li>'
       '<li>Rond af met de opdracht <strong>Zelfstudie vooraf</strong> vóór sessie 1.</li></ul></div>')
start_html = wrap(hero + ''.join(str(p) for p in intro_ps)
                  + f'<h3 style="{FONT} font-weight: bold;">Na het doorlopen van deze e-learning kun je:</h3>' + str(goals)
                  + how + f'<h3 style="{FONT} font-weight: bold; margin-top: 36px;">Hoofdstukken</h3>' + start_items
                  + ''.join(str(c) for c in contact) + attribution())

json.dump({'start': start_html, 'pages': pages, 'sorting': sorting_items}, open('out.json', 'w'), ensure_ascii=False, indent=1)
open('preview.html', 'w').write('<meta charset=utf-8><body style="margin:20px">' + start_html.replace('{{LOGO}}', 'src/assets/hu-logo.svg') + '<hr>' + '<hr>'.join(p['html'] for p in pages))
print('ok', [p['title'] for p in pages], len(start_html), sum(len(p['html']) for p in pages))
