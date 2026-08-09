import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_pdf_report(interview_data: dict, output_path: str) -> str:
    """
    Generates a professional PDF interview report using ReportLab for MockMate AI.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#4f46e5"),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#6b7280"),
        spaceAfter=18
    )
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=14,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#374151")
    )
    
    story = []

    # Title Banner
    story.append(Paragraph("MockMate AI - Interview Evaluation Certificate", title_style))
    story.append(Paragraph(f"Domain: <b>{interview_data.get('domain')}</b> | Difficulty: <b>{interview_data.get('difficulty')}</b> | Mode: <b>{interview_data.get('mode')}</b> | Date: <b>{str(interview_data.get('created_at'))[:10]}</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceAfter=15))

    # Overall Score Box
    score_data = [
        ["Overall Score", f"{interview_data.get('total_score', 0.0):.1f} / 10"],
        ["Technical Knowledge", f"{interview_data.get('overall_technical', 0.0):.1f} / 10"],
        ["Accuracy", f"{interview_data.get('overall_accuracy', 0.0):.1f} / 10"],
        ["Relevance", f"{interview_data.get('overall_relevance', 0.0):.1f} / 10"],
        ["Grammar & Structure", f"{interview_data.get('overall_grammar', 0.0):.1f} / 10"],
        ["Communication Quality", f"{interview_data.get('overall_communication', 0.0):.1f} / 10"]
    ]
    t = Table(score_data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f9fafb")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#111827")),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Strengths
    story.append(Paragraph("Key Candidate Strengths", section_style))
    strengths = interview_data.get('strengths', [])
    if isinstance(strengths, str):
        strengths = json.loads(strengths) if strengths.startswith("[") else [strengths]
    for s in strengths:
        story.append(Paragraph(f"• {s}", body_style))
    story.append(Spacer(1, 10))

    # Weaknesses
    story.append(Paragraph("Areas for Improvement", section_style))
    weaknesses = interview_data.get('weaknesses', [])
    if isinstance(weaknesses, str):
        weaknesses = json.loads(weaknesses) if weaknesses.startswith("[") else [weaknesses]
    for w in weaknesses:
        story.append(Paragraph(f"• {w}", body_style))
    story.append(Spacer(1, 10))

    # AI Suggestions
    story.append(Paragraph("MockMate AI Recommendations", section_style))
    suggestions = interview_data.get('suggestions', [])
    if isinstance(suggestions, str):
        suggestions = json.loads(suggestions) if suggestions.startswith("[") else [suggestions]
    for rec in suggestions:
        story.append(Paragraph(f"• {rec}", body_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceAfter=10))
    story.append(Paragraph("Report generated automatically by MockMate AI Performance Evaluation Engine.", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor("#9ca3af"), alignment=1)))

    doc.build(story)
    return output_path
