from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import uuid
from datetime import datetime


def generate_report(scan_data: dict, reports_dir: str = "reports") -> str:
    os.makedirs(reports_dir, exist_ok=True)
    report_filename = f"report_{uuid.uuid4().hex}.pdf"
    report_path = os.path.join(reports_dir, report_filename)

    doc = SimpleDocTemplate(
        report_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    DARK_BLUE = colors.HexColor("#1a237e")
    LIGHT_BLUE = colors.HexColor("#e3f2fd")
    RED = colors.HexColor("#c62828")
    ORANGE = colors.HexColor("#e65100")
    YELLOW = colors.HexColor("#f9a825")
    GREEN = colors.HexColor("#2e7d32")
    GREY = colors.HexColor("#616161")

    title_style = ParagraphStyle(
        "Title", fontSize=18, fontName="Helvetica-Bold",
        textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", fontSize=11, fontName="Helvetica",
        textColor=GREY, alignment=TA_CENTER, spaceAfter=20
    )
    section_style = ParagraphStyle(
        "Section", fontSize=13, fontName="Helvetica-Bold",
        textColor=DARK_BLUE, spaceBefore=16, spaceAfter=8
    )
    normal_style = ParagraphStyle(
        "Normal2", fontSize=10, fontName="Helvetica",
        textColor=colors.black, spaceAfter=4
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer", fontSize=8, fontName="Helvetica-Oblique",
        textColor=GREY, spaceAfter=4
    )

    elements = []

    # Header
    elements.append(Paragraph("SECURESCAN", title_style))
    elements.append(Paragraph("Forensic Document Verification Certificate", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE))
    elements.append(Spacer(1, 0.3*cm))

    # Scan info
    scan_info = [
        ["Scan Reference:", scan_data.get("scan_id", "N/A")],
        ["Date & Time:", datetime.now().strftime("%d %B %Y, %H:%M:%S")],
        ["Document Filename:", scan_data.get("filename", "N/A")],
        ["File Format:", scan_data.get("file_format", "N/A")],
        ["File Size:", f"{scan_data.get('file_size_kb', 0)} KB"],
    ]
    info_table = Table(scan_info, colWidths=[4*cm, 13*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), DARK_BLUE),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*cm))

    # SHA-256 Hash
    elements.append(Paragraph("Document SHA-256 Hash Fingerprint", section_style))
    hash_val = scan_data.get("sha256_hash", "Not computed")
    elements.append(Paragraph(
        f"<font name='Courier' size='8'>{hash_val}</font>", normal_style))
    elements.append(Spacer(1, 0.2*cm))

    # Layer 1 Metadata
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    elements.append(Paragraph("Layer 1 — Metadata and XMP Analysis", section_style))

    metadata_result = scan_data.get("layer1_metadata", {})
    anomalies = metadata_result.get("anomalies", [])
    completeness = metadata_result.get("completeness_score", 0)

    elements.append(Paragraph(
        f"Metadata Completeness Score: {completeness}%", normal_style))
    elements.append(Paragraph(
        f"Total Anomalies Detected: {len(anomalies)}", normal_style))
    elements.append(Spacer(1, 0.2*cm))

    if anomalies:
        anomaly_data = [["Rule ID", "Field", "Severity", "Interpretation"]]
        for a in anomalies:
            anomaly_data.append([
                a.get("rule_id", ""),
                a.get("field", ""),
                a.get("severity", ""),
                a.get("interpretation", "")[:80] + "..."
            ])
        anomaly_table = Table(
            anomaly_data, colWidths=[2*cm, 3*cm, 2.5*cm, 9.5*cm])
        anomaly_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, LIGHT_BLUE]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(anomaly_table)
    else:
        elements.append(Paragraph(
            "No metadata anomalies detected.", normal_style))

    # Layer 2 ELA
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=colors.lightgrey))
    elements.append(Paragraph(
        "Layer 2 — Error Level Analysis (ELA)", section_style))

    ela_result = scan_data.get("layer2_ela", {})
    ela_score = ela_result.get("ela_score", 0)
    ela_flag = ela_result.get("suspicion_flag", False)
    ela_interp = ela_result.get("interpretation", "N/A")

    elements.append(Paragraph(f"ELA Score: {ela_score}", normal_style))
    elements.append(Paragraph(
        f"Suspicion Flag: {'YES — Manipulation Indicators Detected' if ela_flag else 'NO — No Strong Indicators'}",
        normal_style))
    elements.append(Paragraph(
        f"Interpretation: {ela_interp}", normal_style))

    # Layer 3 Hash
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=colors.lightgrey))
    elements.append(Paragraph(
        "Layer 3 — SHA-256 Hash Integrity Verification", section_style))

    hash_result = scan_data.get("layer3_hash", {})
    match_status = hash_result.get("match_status", "NOT_IN_DATABASE")
    matched_inst = hash_result.get("matched_institution") or "N/A"
    hash_interp = hash_result.get("interpretation", "N/A")

    elements.append(Paragraph(
        f"Match Status: {match_status}", normal_style))
    elements.append(Paragraph(
        f"Matched Institution: {matched_inst}", normal_style))
    elements.append(Paragraph(
        f"Interpretation: {hash_interp}", normal_style))

    # Overall Risk
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE))
    elements.append(Paragraph("Overall Risk Assessment", section_style))

    risk_score = scan_data.get("risk_score", 0)
    risk_verdict = scan_data.get("risk_verdict", "UNKNOWN")
    recommendation = scan_data.get("recommendation", "")

    verdict_colors = {
        "AUTHENTIC": GREEN,
        "SUSPICIOUS": YELLOW,
        "LIKELY FORGED": ORANGE,
        "FORGED": RED
    }
    verdict_color = verdict_colors.get(risk_verdict, GREY)

    verdict_style = ParagraphStyle(
        "Verdict", fontSize=16, fontName="Helvetica-Bold",
        textColor=verdict_color, alignment=TA_CENTER, spaceAfter=8
    )

    elements.append(Paragraph(
        f"Risk Score: {risk_score} / 100", normal_style))
    elements.append(Paragraph(
        f"VERDICT: {risk_verdict}", verdict_style))
    elements.append(Paragraph(
        f"Recommended Action: {recommendation}", normal_style))

    # Disclaimer
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=colors.lightgrey))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph("DISCLAIMER", ParagraphStyle(
        "DisclaimerTitle", fontSize=9, fontName="Helvetica-Bold",
        textColor=GREY, alignment=TA_CENTER
    )))
    elements.append(Paragraph(
        "This certificate is produced by SecureScan, an automated forensic "
        "screening tool developed at the University of Bamenda College of "
        "Technology. The findings constitute prima facie forensic evidence "
        "and do not represent a definitive legal determination. Human review "
        "of all flagged documents is required before any institutional action "
        "is taken.",
        disclaimer_style
    ))

    doc.build(elements)
    return report_path