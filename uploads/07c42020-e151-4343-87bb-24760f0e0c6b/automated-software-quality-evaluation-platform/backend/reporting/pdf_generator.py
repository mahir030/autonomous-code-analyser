import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch


def generate_pdf_report(output_path, overall_score, software_metrics, file_results):

    doc = SimpleDocTemplate(
        output_path,
        pagesize=pagesizes.A4
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    section_style = styles["Heading2"]
    normal = styles["Normal"]

    elements.append(Paragraph("Software Quality Evaluation Report", title_style))
    elements.append(Spacer(1, 0.4 * inch))

    elements.append(Paragraph(f"Overall Score: {overall_score}%", section_style))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Software-Level Metrics", section_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [["Metric", "Score (%)"]]

    for key, value in software_metrics.items():
        data.append([key.capitalize(), value])

    table = Table(data, colWidths=[3 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph("File-Level Analysis", section_style))
    elements.append(Spacer(1, 0.3 * inch))

    for file in file_results:
        elements.append(Paragraph(f"File: {file['filename']}", styles["Heading3"]))
        elements.append(Spacer(1, 0.1 * inch))

        file_data = [
            ["Language", file["language"]],
            ["Lines of Code", file["loc"]],
            ["Final Score (%)", file["score"]],
        ]

        for metric, value in file["breakdown"].items():
            file_data.append([metric.capitalize(), value])

        file_table = Table(file_data, colWidths=[3 * inch, 2 * inch])
        file_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))

        elements.append(file_table)
        elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)

