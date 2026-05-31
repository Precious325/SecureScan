from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
from datetime import datetime


def generate_report(scan_data: dict, output_dir: str = "reports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    scan_id = scan_data.get("scan_id", "unknown")
    output_path = os.path.join(output_dir, f"SecureScan_Report_{scan_id[:8]}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    NAVY   = colors.HexColor("#0A1628")
    BLUE   = colors.HexColor("#1A56DB")
    TEAL   = colors.HexColor("#0D9488")
    GREEN  = colors.HexColor("#059669")
    YELLOW = colors.HexColor("#D97706")
    ORANGE = colors.HexColor("#EA580C")
    RED    = colors.HexColor("#DC2626")
    LGRAY  = colors.HexColor("#F1F5F9")
    MUTED  = colors.HexColor("#64748B")
    WHITE  = colors.white

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("Title", fontSize=18, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=4)
    sub_style = ParagraphStyle("Sub", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#BFDBFE"), alignment=TA_CENTER, spaceAfter=2)
    section_style = ParagraphStyle("Section", fontSize=12, fontName="Helvetica-Bold",
        textColor=NAVY, spaceBefore=12, spaceAfter=4)
    body_style = ParagraphStyle("Body", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#1E293B"), alignment=TA_JUSTIFY,
        spaceAfter=4, leading=14)
    label_style = ParagraphStyle("Label", fontSize=9, fontName="Helvetica-Bold",
        textColor=MUTED, spaceAfter=2)
    disclaimer_style = ParagraphStyle("Disclaimer", fontSize=8, fontName="Helvetica",
        textColor=MUTED, alignment=TA_JUSTIFY, leading=12)

    def verdict_color(verdict):
        mapping = {
            "AUTHENTIC": GREEN,
            "SUSPICIOUS": YELLOW,
            "LIKELY FORGED": ORANGE,
            "FORGED": RED
        }
        return mapping.get(verdict, MUTED)

    def ela_interpretation(ela_score):
        if ela_score is None:
            return "ELA analysis could not be completed for this document format."
        if ela_score < 0.05:
            return "Very low error level detected. Pixel-level content appears uniform and consistent with an unmodified document."
        elif ela_score < 0.15:
            return "Low error level detected. No strong indicators of pixel-level manipulation. Document compression artefacts appear normal."
        elif ela_score < 0.25:
            return "Moderate error level detected. Some regions show elevated compression artefacts. May indicate minor editing or format conversion."
        elif ela_score < 0.35:
            return "Elevated error level detected. Differential compression patterns suggest possible pixel-level modification in certain regions."
        else:
            return "High error level detected. Significant differential compression artefacts detected, consistent with image manipulation or heavy re-encoding."

    def hash_interpretation(match_status, institution=None):
        if match_status == "MATCH":
            inst = institution or "a verified institution"
            return (f"The document's SHA-256 hash fingerprint matches an authenticated reference "
                    f"template registered by {inst}. This provides strong cryptographic evidence "
                    f"that the document content is identical to the authenticated original.")
        elif match_status == "NO_MATCH":
            return ("The document's SHA-256 hash fingerprint does not match any authenticated "
                    "reference template in the SecureScan database. This indicates that the document "
                    "content differs from all registered authentic templates — either the document "
                    "has been modified, or no template has been registered for this document type.")
        else:
            return ("No reference template has been registered in the SecureScan database for this "
                    "document type. Hash verification is inapplicable. The absence of a match does "
                    "not indicate forgery — it indicates that institutional templates have not yet "
                    "been added for this document category.")

    def risk_recommendation(verdict, score):
        if verdict == "AUTHENTIC":
            return ("No significant forensic indicators were detected across all three analysis "
                    "layers. The document may be accepted pending standard institutional "
                    "verification procedures.")
        elif verdict == "SUSPICIOUS":
            return ("Low-level forensic anomalies were detected. It is recommended that a human "
                    "reviewer examine the specific findings listed in this certificate before "
                    "accepting the document. The anomalies may have innocent explanations such "
                    "as format conversion or digital transfer.")
        elif verdict == "LIKELY FORGED":
            return ("Multiple significant forensic anomalies were detected across one or more "
                    "analysis layers. Institutional cross-verification with the issuing authority "
                    "is strongly recommended before any decision is made based on this document.")
        else:
            return ("Critical forensic indicators were detected. This document should be rejected "
                    "and referred for full investigation. Do not accept or act upon this document "
                    "without further verification.")

    content = []
    risk_verdict = scan_data.get("risk_verdict", "UNKNOWN")

    # Header
    header_table = Table(
        [[Paragraph("SECURESCAN", title_style)],
         [Paragraph("Forensic Document Verification Certificate", sub_style)],
         [Paragraph("University of Bamenda — College of Technology", sub_style)]],
        colWidths=[17*cm]
    )
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    content.append(header_table)
    content.append(Spacer(1, 0.4*cm))

    # Scan reference
    scan_id = scan_data.get("scan_id", "N/A")
    now = datetime.now().strftime("%d %B %Y, %H:%M:%S")
    ref_table = Table(
        [["Scan Reference:", scan_id],
         ["Date & Time:", now]],
        colWidths=[4*cm, 13*cm]
    )
    ref_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), MUTED),
        ('TEXTCOLOR', (1, 0), (1, -1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    content.append(ref_table)
    content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
    content.append(Spacer(1, 0.3*cm))

    # Document Information
    content.append(Paragraph("Document Information", section_style))
    filename = scan_data.get("filename") or scan_data.get("original_filename", "N/A")
    file_format = scan_data.get("file_format", "N/A")
    file_size = scan_data.get("file_size_kb", "N/A")
    sha256 = scan_data.get("sha256_hash", "N/A")

    doc_table = Table(
        [["Document Filename:", filename],
         ["File Format:", file_format],
         ["File Size:", f"{file_size} KB"],
         ["SHA-256 Hash:", sha256]],
        colWidths=[4*cm, 13*cm]
    )
    doc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), MUTED),
        ('TEXTCOLOR', (1, 0), (1, -1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('BACKGROUND', (0, 3), (-1, 3), LGRAY),
        ('FONTNAME', (1, 3), (1, 3), 'Courier'),
        ('FONTSIZE', (1, 3), (1, 3), 8),
    ]))
    content.append(doc_table)
    content.append(Spacer(1, 0.3*cm))

    # Layer 1
    content.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    content.append(Spacer(1, 0.2*cm))

    layer1 = scan_data.get("layer1_metadata", {})
    anomalies = layer1.get("anomalies", [])
    completeness = layer1.get("completeness_score", 0)
    anomaly_count = len(anomalies)

    layer1_header = Table([["Layer 1 — Metadata and XMP Analysis"]], colWidths=[17*cm])
    layer1_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    content.append(layer1_header)
    content.append(Spacer(1, 0.2*cm))

    l1_table = Table(
        [["Metadata Completeness Score:", f"{completeness}%"],
         ["Total Anomalies Detected:", str(anomaly_count)]],
        colWidths=[6*cm, 11*cm]
    )
    l1_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), MUTED),
        ('TEXTCOLOR', (1, 0), (1, -1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    content.append(l1_table)

    if anomalies:
        content.append(Spacer(1, 0.2*cm))
        content.append(Paragraph("Detected Anomalies:", label_style))
        anom_rows = [["Rule ID", "Severity", "Description"]]
        for a in anomalies:
            anom_rows.append([a.get("rule_id", ""), a.get("severity", ""), a.get("description", "")])
        anom_table = Table(anom_rows, colWidths=[2.5*cm, 2.5*cm, 12*cm])
        anom_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(anom_table)
    else:
        content.append(Paragraph(
            "No metadata anomalies detected. All metadata fields appear consistent with an authentic document.",
            body_style
        ))

    content.append(Spacer(1, 0.3*cm))

    # Layer 2
    content.append(HRFlowable(width="100%", thickness=1, color=TEAL))
    content.append(Spacer(1, 0.2*cm))

    layer2 = scan_data.get("layer2_ela", {})
    ela_score_val = layer2.get("ela_score", 0)
    ela_flag = layer2.get("suspicion_flag", False)
    ela_flag_text = ("YES — Elevated Compression Artefacts Detected"
                     if ela_flag else
                     "NO — No Strong Indicators of Pixel-Level Manipulation")

    layer2_header = Table([["Layer 2 — Error Level Analysis (ELA)"]], colWidths=[17*cm])
    layer2_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), TEAL),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    content.append(layer2_header)
    content.append(Spacer(1, 0.2*cm))

    l2_table = Table(
        [["ELA Score:", f"{ela_score_val:.4f}" if ela_score_val else "0.0000"],
         ["Suspicion Flag:", ela_flag_text],
         ["Interpretation:", Paragraph(ela_interpretation(ela_score_val), body_style)]],
        colWidths=[4.5*cm, 12.5*cm]
    )
    l2_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), MUTED),
        ('TEXTCOLOR', (1, 0), (1, 1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    content.append(l2_table)
    content.append(Spacer(1, 0.3*cm))

    # Layer 3
    content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7C3AED")))
    content.append(Spacer(1, 0.2*cm))

    layer3 = scan_data.get("layer3_hash", {})
    match_status = layer3.get("match_status", scan_data.get("hash_match_status", "NOT_IN_DATABASE"))
    matched_institution = layer3.get("matched_institution")

    if matched_institution and matched_institution != "N/A":
        institution_display = matched_institution
    elif match_status == "NO_MATCH":
        institution_display = "No matching template found in database"
    elif match_status == "MATCH":
        institution_display = matched_institution or "Verified institution"
    else:
        institution_display = "Not applicable — no template registered for this document type"

    layer3_header = Table([["Layer 3 — SHA-256 Hash Integrity Verification"]], colWidths=[17*cm])
    layer3_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F5F3FF")),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#7C3AED")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    content.append(layer3_header)
    content.append(Spacer(1, 0.2*cm))

    l3_table = Table(
        [["Match Status:", match_status],
         ["Matched Institution:", institution_display],
         ["Interpretation:", Paragraph(hash_interpretation(match_status, matched_institution), body_style)]],
        colWidths=[4.5*cm, 12.5*cm]
    )
    l3_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), MUTED),
        ('TEXTCOLOR', (1, 0), (1, 1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    content.append(l3_table)
    content.append(Spacer(1, 0.3*cm))

    # Overall Risk Assessment
    content.append(HRFlowable(width="100%", thickness=2, color=verdict_color(risk_verdict)))
    content.append(Spacer(1, 0.2*cm))

    risk_score = scan_data.get("risk_score", 0)
    recommendation = risk_recommendation(risk_verdict, risk_score)

    verdict_header = Table([[f"Overall Risk Assessment — {risk_verdict}"]], colWidths=[17*cm])
    verdict_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), verdict_color(risk_verdict)),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('TEXTCOLOR', (0, 0), (-1, -1), WHITE),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    content.append(verdict_header)
    content.append(Spacer(1, 0.2*cm))

    risk_table = Table(
        [["Risk Score:", f"{risk_score} / 100"],
         ["Risk Verdict:", risk_verdict],
         ["Recommended Action:", Paragraph(recommendation, body_style)]],
        colWidths=[4.5*cm, 12.5*cm]
    )
    risk_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), MUTED),
        ('TEXTCOLOR', (1, 0), (1, 0), NAVY),
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1, 1), (1, 1), verdict_color(risk_verdict)),
        ('FONTSIZE', (1, 1), (1, 1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    content.append(risk_table)
    content.append(Spacer(1, 1*cm))

    # Disclaimer
    content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
    content.append(Spacer(1, 0.2*cm))
    content.append(Paragraph(
        "DISCLAIMER: This certificate is produced by SecureScan, an automated forensic screening tool "
        "developed at the University of Bamenda College of Technology as part of a final year Computer "
        "Engineering project. The findings constitute prima facie forensic evidence and do not represent "
        "a definitive legal determination. Human review of all flagged documents is required before any "
        "institutional action is taken. SecureScan is a first-line screening tool only.",
        disclaimer_style
    ))

    doc.build(content)
    return output_path