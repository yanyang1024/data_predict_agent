#!/usr/bin/env python3
from pathlib import Path
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

ROOT = Path(__file__).resolve().parents[1]
manual = ROOT / "source_docs" / "validation_manual.md"
pdf = ROOT / "source_docs" / "validation_manual.pdf"
styles = getSampleStyleSheet()
doc = SimpleDocTemplate(str(pdf), pagesize=landscape(letter), leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
story = []
text = manual.read_text(encoding="utf-8")
story.append(Paragraph("Synthetic Validation Manual", styles["Title"]))
story.append(Spacer(1, 12))
story.append(Paragraph("This PDF is generated from the Markdown manual for teaching rich-text rule extraction.", styles["BodyText"]))
story.append(Spacer(1, 12))
data = [
    ["Rule ID", "Intent", "Native Pattern", "Expected Evidence", "Review"],
    ["RESET_STABILITY", "Verify reset release stability", "SET RESET_N=0; WAIT 10ns; SET RESET_N=1; WAIT 20ns; CHECK READY==1", "READY becomes 1", "Confirm reset polarity"],
    ["VOLTAGE_SWEEP", "Validate voltage range", "FOR VDD IN [0.9, 1.0, 1.1]: SET VDD; RUN BASIC_OP; CHECK PASS==1", "PASS remains 1", "Confirm voltage range"],
    ["JITTER_TOLERANCE", "Validate clock jitter tolerance", "SET CLK_JITTER=50ps; RUN BASIC_OP; CHECK ERROR_COUNT==0", "ERROR_COUNT remains zero", "Confirm jitter model"],
]
table = Table(data, colWidths=[90, 150, 310, 120, 130])
table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("FONTSIZE", (0,0), (-1,-1), 6),
]))
story.append(table)
story.append(Spacer(1, 12))
story.append(Paragraph("Environment Adaptation Rules", styles["Heading2"]))
for line in [
    "Native signal RESET_N maps to environment signal rst_n.",
    "Native signal READY maps to environment signal ready.",
    "Native signal VDD maps to environment parameter supply_vdd.",
    "Native signal CLK_JITTER maps to environment parameter clock_jitter_ps.",
    "Native macro BASIC_OP maps to environment function basic_transaction().",
]:
    story.append(Paragraph(line, styles["BodyText"]))
story.append(Spacer(1, 12))
story.append(Paragraph("Human Review Gate", styles["Heading2"]))
story.append(Paragraph("The reviewer must confirm polarity, legal voltage range, jitter model, and expected evidence.", styles["BodyText"]))
doc.build(story)
print(pdf)
