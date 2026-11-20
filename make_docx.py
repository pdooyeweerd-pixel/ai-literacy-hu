#!/usr/bin/env python3
"""Maakt HU-aanpassingen-en-advies.docx uit data/rows.json en data/links.json (python-docx)."""
import json, sys, os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(f"{ROOT}/data/rows.json", encoding="utf-8"))
links = json.load(open(f"{ROOT}/data/links.json", encoding="utf-8"))
RED = RGBColor(0xCD, 0x17, 0x12)

d = Document()
s = d.sections[0]
s.orientation = WD_ORIENT.LANDSCAPE
s.page_width, s.page_height = Cm(29.7), Cm(21.0)
for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(s, m, Cm(1.6))
st = d.styles["Normal"]; st.font.name = "Arial"; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
for name, size in (("Title", 22), ("Heading 1", 14)):
    h = d.styles[name]; h.font.name = "Arial"; h.font.size = Pt(size); h.font.bold = True; h.font.color.rgb = RED
    h.element.rPr.rFonts.set(qn("w:ascii"), "Arial"); h.element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), fill); tcPr.append(sh)

def para(text, bold=False, size=None, style=None):
    p = d.add_paragraph(style=style); r = p.add_run(text); r.bold = bold
    if size: r.font.size = Pt(size)
    return p

d.add_paragraph("AI Literacy voor docenten – HU-versie", style="Title")
para("Wat nog moet worden aangepast, met advies voor een HU-alternatief", bold=True, size=12)
para("Stand: 20 november 2026. Bewerking van “AI Literacy voor docenten” van TLC Central & TLC Science (UvA), CC BY-NC-SA 4.0.")

d.add_heading("Zo lees je dit overzicht", level=1)
for t in [
    "In de webversie staan de plekken die moeten worden aangepast gemarkeerd: blauw = HU-invulling nodig, geel = nog UvA-specifiek. Met het vinkje bovenin zet je de markering uit.",
    "De adviezen komen uit publiek vindbare HU-bronnen (hu.nl, husite.nl, Trajectum, de HU-bibliotheek). Veel van die bronnen zijn van 2024 of eerder. Controleer daarom of het actueel is voordat je het overneemt.",
    "Waar ik niets kon vinden staat “Nog aan te leveren door HU”. Daar is input van jullie nodig.",
]:
    d.add_paragraph(t, style="List Bullet")

d.add_heading("Belangrijkste punten vooraf", level=1)
for t in [
    "Er is bij de HU geen eigen “HU AI Chat” gevonden zoals bij de UvA. Op basis van de bronnen is Microsoft Copilot de aanbevolen tool. De teksten over de eigen AI-omgeving moeten daarom inhoudelijk worden herschreven, niet alleen van naam veranderd.",
    "Een los HU-beleidskader voor GenAI in het onderwijs heb ik niet gevonden. Wel de Handreiking generatieve AI en toetsing, het HU-toetsbeleid en de richtlijn onregelmatigheden.",
    "De HU-voorbeelden (hoofdstuk 6, 9 en 10) kunnen alleen jullie aanleveren. Dat is ook inhoudelijk het grootste verschil met het origineel.",
]:
    d.add_paragraph(t, style="List Bullet")

d.add_heading("Overzicht", level=1)
widths = [Cm(2.2), Cm(5.6), Cm(9.6), Cm(5.6), Cm(3.5)]
heads = ["Hoofdstuk", "Wat staat er nu (UvA)", "Advies voor de HU", "Bron", "Status"]
t = d.add_table(rows=1, cols=5); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
def fill_row(cells, vals, size=8.5, bold_first=False, header=False):
    for i, (c, v) in enumerate(zip(cells, vals)):
        c.width = widths[i]; c.text = ""
        r = c.paragraphs[0].add_run(v); r.font.size = Pt(size)
        if header: r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255); shade(c, "CD1712")
        elif i == 0: r.bold = True
        if not header and i == 4: shade(c, "FFE4E1" if "aan te leveren" in v else "FFF4CC")
fill_row(t.rows[0].cells, heads, size=9, header=True)
trPr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
for r in rows:
    row = t.add_row(); fill_row(row.cells, r)
    cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); row._tr.get_or_add_trPr().append(cs)

d.add_heading("Gebruikte bronnen", level=1)
for text, url in links:
    p = d.add_paragraph(style="List Bullet"); p.add_run(f"{text}: ").bold = False; r = p.add_run(url); r.font.size = Pt(8.5)

out = sys.argv[1]; d.save(out); print("ok", len(rows), "rijen ->", out)
