"""
MEDICAL REPORT GENERATOR
Takes the combined AI Diagnosis and formats it into a professional PDF.
"""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch

def generate_pdf_report(patient_data, prediction, filename):
    """
    Generates a PDF report from the Orchestrator's results.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Create the document
    doc = SimpleDocTemplate(
        filename, pagesize=letter,
        rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Header', parent=styles['Heading1'], fontSize=24, spaceAfter=20, textColor=colors.HexColor('#2c3e50')))
    styles.add(ParagraphStyle(name='SubHeader', parent=styles['Heading2'], fontSize=14, spaceAfter=10, textColor=colors.HexColor('#34495e')))
    styles.add(ParagraphStyle(name='Normal_Small', parent=styles['Normal'], fontSize=10, leading=14))
    
    story = []

    # --- 1. Header ---
    story.append(Paragraph("MediPatient AI Diagnostic Report", styles['Header']))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
    story.append(Spacer(1, 20))
    
    # --- 2. Patient Vitals ---
    story.append(Paragraph("Patient Vitals", styles['SubHeader']))
    
    p_data = [
        ['Age / Gender:', f"{patient_data.get('age', 'N/A')} / {patient_data.get('gender', 'N/A')}"],
        ['Temperature:', f"{patient_data.get('temperature')} C"],
        ['Heart Rate:', f"{patient_data.get('heartRate')} bpm"],
        ['Blood Pressure:', f"{patient_data.get('systolicBP')}/{patient_data.get('diastolicBP')} mmHg"],
        ['Oxygen Saturation:', f"{patient_data.get('oxygenSaturation')}%"]
    ]
    
    t_patient = Table(p_data, colWidths=[2*inch, 4*inch])
    t_patient.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_patient)
    story.append(Spacer(1, 20))

    # --- 3. AI Diagnosis Results ---
    story.append(Paragraph("AI Diagnosis Results", styles['SubHeader']))
    
    dx_name = prediction.get('primary_diagnosis', 'Unknown')
    confidence = prediction.get('confidence', 0.0)
    urgency = prediction.get('urgency_level', 'ROUTINE')
    
    # Color code urgency
    urgency_color = colors.green
    if urgency in ['CRITICAL', 'URGENT']: urgency_color = colors.red
    elif urgency == 'PRIORITY': urgency_color = colors.orange

    dx_data = [
        ['Primary Diagnosis:', dx_name],
        ['Confidence:', f"{confidence:.1%}"],
        ['Urgency Level:', urgency]
    ]
    
    t_dx = Table(dx_data, colWidths=[2*inch, 4*inch])
    t_dx.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1,2), (1,2), urgency_color),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
    ]))
    story.append(t_dx)
    story.append(Spacer(1, 15))

    # --- 4. Clinical Reasoning (From Gemini Diagnosis Key) ---
    story.append(Paragraph("AI Clinical Reasoning", styles['SubHeader']))
    reasoning_text = prediction.get('reasoning', 'No specific reasoning provided.')
    story.append(Paragraph(reasoning_text, styles['Normal']))
    story.append(Spacer(1, 15))

    # --- 5. Treatment Plan ---
    treatments = prediction.get('treatment_plan', {})
    
    if treatments and isinstance(treatments, dict):
        story.append(Paragraph("Recommended Treatment Plan", styles['SubHeader']))
        
        # Immediate
        if 'immediate_interventions' in treatments:
            story.append(Paragraph("<b>Immediate Interventions:</b>", styles['Normal']))
            for item in treatments['immediate_interventions']:
                story.append(Paragraph(f"• {item}", styles['Normal_Small']))
            story.append(Spacer(1, 10))
            
        # Definitive
        if 'definitive_treatment' in treatments:
            story.append(Paragraph("<b>Definitive Treatment:</b>", styles['Normal']))
            for item in treatments['definitive_treatment']:
                story.append(Paragraph(f"• {item}", styles['Normal_Small']))

    # --- Footer ---
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Report Generated: {timestamp} | MediPatient AI", styles['Normal_Small']))
    story.append(Paragraph("Disclaimer: This is an AI-generated report. Consult a physician.", styles['Normal_Small']))

    # Build PDF
    try:
        doc.build(story)
        print(f"✅ PDF Report generated: {filename}")
        return filename
    except Exception as e:
        print(f"❌ PDF Generation Failed: {e}")
        return None