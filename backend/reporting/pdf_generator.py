from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors, pagesizes
from reportlab.lib.units import inch
from datetime import datetime


def generate_pdf_report(output_path, overall_score, software_metrics, file_results):

    doc = SimpleDocTemplate(
        output_path,
        pagesize=pagesizes.A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=60,
        bottomMargin=50
    )

    elements = []
    styles = getSampleStyleSheet()

    # =========================
    # Premium Color Palette
    # =========================
    NAVY = colors.HexColor("#0F172A")
    GOLD = colors.HexColor("#D4AF37")
    DARK = colors.HexColor("#111827")
    LIGHT_BG = colors.HexColor("#F8FAFC")
    BORDER = colors.HexColor("#E5E7EB")

    # =========================
    # Typography System
    # =========================
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=26,
        textColor=NAVY,
        spaceAfter=20,
        alignment=1  # center
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        alignment=1,
        spaceAfter=25
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=DARK,
        spaceBefore=20,
        spaceAfter=10
    )

    file_title_style = ParagraphStyle(
        "FileTitle",
        parent=styles["Heading3"],
        fontSize=13,
        textColor=NAVY,
        spaceAfter=6
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=4
    )

    # =========================
    # HEADER / TITLE
    # =========================
    elements.append(Paragraph("ENTERPRISE SOFTWARE QUALITY REPORT", title_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        subtitle_style
    ))

    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    elements.append(Spacer(1, 0.3 * inch))

    # =========================
    # OVERALL SCORE (Highlight Box)
    # =========================
    score_table = Table(
        [["Overall Quality Score", f"{overall_score}%"]],
        colWidths=[4 * inch, 1.5 * inch]
    )

    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 16),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))

    elements.append(score_table)
    elements.append(Spacer(1, 0.4 * inch))

    # =========================
    # SOFTWARE LEVEL METRICS
    # =========================
    if software_metrics:
        elements.append(Paragraph("Software-Level Metrics", section_style))

        metric_data = [["Metric", "Score (%)"]]
        for key, value in software_metrics.items():
            metric_data.append([str(key), f"{value}%"])

        metric_table = Table(metric_data, colWidths=[4 * inch, 1.5 * inch])

        metric_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))

        elements.append(metric_table)

    # =========================
    # FILE LEVEL ANALYSIS
    # =========================
    elements.append(Paragraph("File-Level Analysis", section_style))

    for file in file_results:

        elements.append(Spacer(1, 0.25 * inch))

        elements.append(Paragraph(f"{file['filename']}", file_title_style))

        meta_table = Table([
            ["Language", file.get("language", "N/A")],
            ["Lines of Code", file.get("loc", "N/A")],
            ["Final Score", f"{file['score']}%"],
        ], colWidths=[2 * inch, 3.5 * inch])

        meta_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(meta_table)
        elements.append(Spacer(1, 0.15 * inch))

        # Breakdown table
        if "breakdown" in file and file["breakdown"]:
            breakdown_data = [["Metric", "Score (%)"]]
            for key, value in file["breakdown"].items():
                breakdown_data.append([str(key), f"{value}%"])

            breakdown_table = Table(breakdown_data, colWidths=[4 * inch, 1.5 * inch])

            breakdown_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]))

            elements.append(breakdown_table)

    doc.build(elements)
