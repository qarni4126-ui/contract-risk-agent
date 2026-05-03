# pdf_generator.py

"""
Generate PDF report from risk analysis.
Simple, clean PDF with risk scores & summary.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime


def generate_risk_report_pdf(filename: str, risk_summary: dict, summary: str) -> bytes:
    """
    Generate a clean, simple PDF report.
    
    Args:
        filename: Original document name
        risk_summary: Risk analysis results
        summary: Contract summary text
    
    Returns:
        PDF bytes
    """
    
    # Create PDF in memory
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Content list
    content = []
    
    # ============ HEADER ============
    content.append(Paragraph("Contract Risk Analysis Report", title_style))
    content.append(Spacer(1, 0.3*inch))
    
    # Metadata
    meta_text = f"<b>Document:</b> {filename}<br/><b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    content.append(Paragraph(meta_text, styles['Normal']))
    content.append(Spacer(1, 0.3*inch))
    
    # ============ RISK SCORE (PROMINENT) ============
    content.append(Paragraph("Risk Assessment", heading_style))
    
    # Risk level with color
    score = risk_summary['overall_score']
    level = risk_summary['overall_level']
    
    if level == "HIGH":
        level_color = "#d32f2f"  # Red
    elif level == "MEDIUM":
        level_color = "#f57c00"  # Orange
    else:
        level_color = "#388e3c"  # Green
    
    risk_text = f"""
    <font size=18 color="{level_color}"><b>{level} RISK</b></font><br/>
    <font size=14>Score: <b>{score}/100</b></font>
    """
    content.append(Paragraph(risk_text, styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    # Risk breakdown table
    breakdown_data = [
        ['Category', 'Count'],
        ['High Risk', str(risk_summary['high_risk_count'])],
        ['Medium Risk', str(risk_summary['medium_risk_count'])],
        ['Low Risk', str(risk_summary['low_risk_count'])],
        ['Total Issues', str(risk_summary['total_risks'])]
    ]
    
    breakdown_table = Table(breakdown_data, colWidths=[3*inch, 2*inch])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(breakdown_table)
    content.append(Spacer(1, 0.3*inch))
    
    # ============ TOP RISKS ============
    if risk_summary['top_risks']:
        content.append(Paragraph("Top Issues Found", heading_style))
        
        for i, risk in enumerate(risk_summary['top_risks'], 1):
            risk_item = f"""
            <b>{i}. {risk['risk_text'][:100]}</b><br/>
            Score: {risk['score']}/100 | Category: {risk['category']}<br/>
            Reasons: {', '.join(risk['reasons'][:2])}
            """
            content.append(Paragraph(risk_item, styles['Normal']))
            content.append(Spacer(1, 0.15*inch))
    
    content.append(Spacer(1, 0.2*inch))
    
    # ============ SUMMARY ============
    content.append(Paragraph("Contract Summary", heading_style))
    content.append(Paragraph(summary, styles['Normal']))
    
    # ============ BUILD PDF ============
    doc.build(content)
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()