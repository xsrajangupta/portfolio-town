"""
Builds public/resume.pdf from the same JSON data used in-game, so the two
never drift out of sync. Re-run after editing src/data/resume.json,
src/data/about.json, or src/data/skills.json.
"""
import json
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

BASE = "/home/claude/uploaded_project"
about = json.load(open(f"{BASE}/src/data/about.json"))
resume = json.load(open(f"{BASE}/src/data/resume.json"))
skills = json.load(open(f"{BASE}/src/data/skills.json"))
contact = json.load(open(f"{BASE}/src/data/contact.json"))

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=HexColor("#1a1a1a"), fontSize=24)
role_style = ParagraphStyle("Role", parent=styles["Normal"], fontSize=13, textColor=HexColor("#3f6fb0"), spaceAfter=10)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, textColor=HexColor("#222"), spaceBefore=14, spaceAfter=6)
body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10.5, leading=15)
meta = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=9.5, textColor=HexColor("#555"), spaceAfter=2)

doc = SimpleDocTemplate(f"{BASE}/public/resume.pdf", pagesize=LETTER,
                         topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                         leftMargin=0.75 * inch, rightMargin=0.75 * inch)

flow = []
flow.append(Paragraph(about["name"], title_style))
flow.append(Paragraph(about["role"], role_style))
flow.append(Paragraph(
    f'{contact["email"]} &nbsp;·&nbsp; {contact["phone"]} &nbsp;·&nbsp; {contact["location"]}',
    meta,
))
flow.append(Spacer(1, 10))
flow.append(Paragraph(resume["summary"], body))

flow.append(Paragraph("Experience", h2))
for item in resume["experience"]:
    flow.append(Paragraph(f'<b>{item["role"]}</b> — {item["org"]}', body))
    flow.append(Paragraph(item["period"], meta))
    if item.get("detail"):
        flow.append(Paragraph(item["detail"], body))
    flow.append(Spacer(1, 6))

flow.append(Paragraph("Education", h2))
for item in resume["education"]:
    flow.append(Paragraph(f'<b>{item["role"]}</b> — {item["org"]}', body))
    flow.append(Paragraph(item["period"], meta))
    flow.append(Spacer(1, 6))

flow.append(Paragraph("Skills", h2))
for group in skills["groups"]:
    names = ", ".join(i["name"] for i in group["items"])
    flow.append(Paragraph(f'<b>{group["name"]}:</b> {names}', body))
    flow.append(Spacer(1, 3))

doc.build(flow)
print("resume.pdf written")
