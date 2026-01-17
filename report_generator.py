import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ==================== CONFIGURATION & STYLES ====================

# Professional Medical Color Palette
PALETTE = {
    'primary': colors.HexColor('#1a3c5e'),      # Deep Navy (Headers)
    'secondary': colors.HexColor('#4a90e2'),    # Bright Blue (Subheaders)
    'accent': colors.HexColor('#e74c3c'),       # Red (Critical)
    'warning': colors.HexColor('#f39c12'),      # Orange (Warning)
    'success': colors.HexColor('#27ae60'),      # Green (Normal)
    'light_bg': colors.HexColor('#f4f6f7'),     # Light Grey (Backgrounds)
    'white': colors.white
}

def get_doc_styles():
    """Define distinct professional styles."""
    styles = getSampleStyleSheet()
    
    # Custom Style Dictionary
    # RENAMED 'BodyText' -> 'ReportBody' to fix the error
    custom = {
        'MainTitle': ParagraphStyle(
            'MainTitle', parent=styles['Heading1'],
            fontSize=22, textColor=PALETTE['primary'], spaceAfter=12, leading=26
        ),
        'SectionHeader': ParagraphStyle(
            'SectionHeader', parent=styles['Heading2'],
            fontSize=14, textColor=PALETTE['primary'], spaceBefore=15, spaceAfter=8,
            borderPadding=5, borderColor=PALETTE['light_bg'], borderWidth=0, backColor=PALETTE['light_bg']
        ),
        'SidebarHeader': ParagraphStyle(
            'SidebarHeader', parent=styles['Normal'],
            fontSize=11, textColor=PALETTE['secondary'], fontName='Helvetica-Bold', spaceAfter=6
        ),
        'ReportBody': ParagraphStyle(  # Changed name here
            'ReportBody', parent=styles['Normal'],
            fontSize=9, leading=13, textColor=colors.HexColor('#333333')
        ),
        'CriticalAlert': ParagraphStyle(
            'CriticalAlert', parent=styles['Normal'],
            fontSize=12, textColor=PALETTE['white'], backColor=PALETTE['accent'],
            alignment=TA_CENTER, borderPadding=10, leading=16, fontName='Helvetica-Bold'
        ),
        'SmallLabel': ParagraphStyle(
            'SmallLabel', parent=styles['Normal'],
            fontSize=8, textColor=colors.grey
        )
    }
    
    # Safe add: Only add if not already present
    for name, style in custom.items():
        if name not in styles:
            styles.add(style)
        else:
            # If it exists, we replace it (though with unique names this won't trigger)
            styles[name] = style
            
    return styles

# ==================== LOGIC ENGINES ====================

def get_treatment_protocol(diagnosis):
    """
    Returns a specific protocol title and list of actions based on the diagnosis keyword.
    """
    d_lower = str(diagnosis).lower()
    
    # 1. TRAUMA / SHOCK PROTOCOL (Crucial Addition)
    if any(x in d_lower for x in ['trauma', 'injury', 'fracture', 'accident', 'hemorrhage', 'bleed']):
        return "TRAUMA / ATLS PROTOCOL", [
            ("Primary Survey", "ABCDE Assessment (Airway, Breathing, Circulation)"),
            ("Resuscitation", "2 Large-bore IVs, 1L Crystalloid Bolus for BP < 90"),
            ("Imaging", "FAST Exam (US) & CT Pan-scan (Trauma Protocol)"),
            ("Stabilization", "Spine Immobilization, Control External Hemorrhage")
        ]

    # 2. SEPSIS / INFECTION PROTOCOL
    elif any(x in d_lower for x in ['sepsis', 'infection', 'septic', 'shock']):
        return "SEPSIS BUNDLE (1-HOUR TARGET)", [
            ("Resuscitation", "Initiate IV Crystalloids (30mL/kg rapid bolus)"),
            ("Medication", "Broad-spectrum Antibiotics (Vancomycin/Zosyn)"),
            ("Diagnostics", "Blood Cultures x2 (prior to antibiotics), Lactate"),
            ("Monitoring", "Target MAP > 65mmHg, Urine Output > 0.5mL/kg/hr")
        ]
        
    # 3. CARDIAC / ACS PROTOCOL
    elif any(x in d_lower for x in ['cardiac', 'myocardial', 'infarction', 'stemi', 'heart', 'acs']):
        return "ACUTE CORONARY SYNDROME PROTOCOL", [
            ("Immediate", "Aspirin 325mg (chewable) + Nitroglycerin SL"),
            ("Diagnostics", "12-Lead ECG (STAT), Troponin I/T Series"),
            ("Oxygenation", "Supplemental O2 if Saturation < 90%"),
            ("Intervention", "Cardiology Consult: Eval for PCI/Thrombolysis")
        ]
        
    # 4. RESPIRATORY PROTOCOL
    elif any(x in d_lower for x in ['pneumonia', 'copd', 'asthma', 'respiratory', 'embolism']):
        return "RESPIRATORY DISTRESS PROTOCOL", [
            ("Support", "Titrate O2 to maintain SpO2 > 92%"),
            ("Medication", "Nebulized Bronchodilators (Albuterol/Ipratropium)"),
            ("Diagnostics", "CXR, ABG (if severe hypoxia), D-Dimer"),
            ("Steroids", "Consider IV Methylprednisolone for exacerbation")
        ]
        
    # 5. NEUROLOGICAL PROTOCOL
    elif any(x in d_lower for x in ['stroke', 'cva', 'tia', 'brain', 'seizure']):
        return "ACUTE NEUROLOGICAL PROTOCOL", [
            ("Imaging", "CT Head Non-Contrast (Door-to-CT < 20 mins)"),
            ("Vitals", "Strict BP management (Permissive HTN if ischemic)"),
            ("Assessment", "NIH Stroke Scale Documentation q15min"),
            ("Access", "Two large-bore IVs, NPO status")
        ]

    # DEFAULT / GENERAL PROTOCOL
    return "GENERAL CLINICAL MANAGEMENT", [
        ("Assessment", "Complete Physical Exam & History"),
        ("Diagnostics", "CBC, CMP, Urinalysis as indicated"),
        ("Monitoring", "Routine Vital Signs q4h"),
        ("Referral", "Specialist consultation if symptoms persist")
    ]

    # DEFAULT / GENERAL PROTOCOL
    return "GENERAL CLINICAL MANAGEMENT", [
        ("Assessment", "Complete Physical Exam & History"),
        ("Diagnostics", "CBC, CMP, Urinalysis as indicated"),
        ("Monitoring", "Routine Vital Signs q4h"),
        ("Referral", "Specialist consultation if symptoms persist")
    ]

def create_vital_row(param, value, unit, min_val, max_val, styles):
    """Creates a formatted row for the vital signs table with visual indicators."""
    try:
        val_float = float(value)
        status_color = PALETTE['success']
        arrow = "•"
        
        if val_float > max_val:
            status_color = PALETTE['accent']
            arrow = "▲" # Up arrow for High
        elif val_float < min_val:
            status_color = PALETTE['secondary']
            arrow = "▼" # Down arrow for Low
            
        val_display = f"{val_float}{unit}"
    except:
        val_display = str(value)
        status_color = colors.grey
        arrow = "-"

    # Create styling for the status arrow
    status_style = ParagraphStyle('Status', parent=styles['Normal'], fontSize=12, textColor=status_color)
    
    # UPDATED: Uses 'ReportBody' instead of 'BodyText'
    return [
        Paragraph(param, styles['ReportBody']),
        Paragraph(f"<b>{val_display}</b>", styles['ReportBody']),
        Paragraph(arrow, status_style)
    ]

# ==================== COMPONENT GENERATORS ====================

def generate_sidebar_content(patient_data, styles):
    """Generates the content for the left sidebar (Patient Info + Vitals)."""
    elements = []
    
    # 1. Patient Demographics Block
    elements.append(Paragraph("PATIENT PROFILE", styles['SidebarHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=PALETTE['secondary']))
    elements.append(Spacer(1, 5))
    
    # UPDATED: Uses 'ReportBody'
    p_info = [
        [Paragraph("ID:", styles['SmallLabel']), Paragraph(f"<b>{patient_data.get('patient_id', 'Unknown')}</b>", styles['ReportBody'])],
        [Paragraph("Age/Sex:", styles['SmallLabel']), Paragraph(f"{patient_data.get('age')} / {patient_data.get('gender')}", styles['ReportBody'])],
        [Paragraph("Admitted:", styles['SmallLabel']), Paragraph(datetime.now().strftime("%Y-%m-%d"), styles['ReportBody'])],
    ]
    t_info = Table(p_info, colWidths=[1.8*cm, 3.2*cm])
    t_info.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(t_info)
    elements.append(Spacer(1, 15))

    # 2. Vital Signs Block
    elements.append(Paragraph("VITAL SIGNS", styles['SidebarHeader']))
    elements.append(HRFlowable(width="100%", thickness=1, color=PALETTE['secondary']))
    
    # Vital parameters configuration: (Name, Key, Unit, Min, Max)
    vital_config = [
        ('Temp', 'temperature', '°C', 36.5, 37.5),
        ('HR', 'heartRate', ' bpm', 60, 100),
        ('BP Sys', 'systolicBP', '', 90, 120),
        ('BP Dia', 'diastolicBP', '', 60, 80),
        ('Resp', 'respiratoryRate', '/min', 12, 20),
        ('SpO2', 'oxygenSaturation', '%', 95, 100),
    ]

    vital_rows = []
    for label, key, unit, min_v, max_v in vital_config:
        val = patient_data.get(key, 'N/A')
        vital_rows.append(create_vital_row(label, val, unit, min_v, max_v, styles))

    t_vitals = Table(vital_rows, colWidths=[2*cm, 2*cm, 1*cm])
    t_vitals.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.lightgrey),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_vitals)
    
    # Legend
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("▲ High  ▼ Low  • Normal", styles['SmallLabel']))
    
    return elements

def generate_main_content(prediction, patient_data, styles):
    """
    Generates the content for the right main area with DYNAMIC TREATMENT PLANS.
    """
    elements = []
    
    # --- 1. Alert Banner ---
    severity = float(prediction.get('severity_score', 0))
    if severity >= 0.8:
        elements.append(Paragraph(f"⚠️ CRITICAL ALERT: {prediction.get('urgency_level', 'IMMEDIATE ATTENTION')}", styles['CriticalAlert']))
    elif severity >= 0.5:
        elements.append(Paragraph(f"⚠️ CLINICAL WARNING: {prediction.get('urgency_level', 'URGENT')}", styles['SectionHeader']))
    
    elements.append(Spacer(1, 10))

    # --- 2. Diagnosis Section ---
    elements.append(Paragraph("AI DIAGNOSTIC ASSESSMENT", styles['SectionHeader']))
    
    # Diagnosis Card (Main Title)
    diag_text = prediction.get('primary_diagnosis', 'Undetermined')
    conf_val = prediction.get('confidence', 0)
    
    # Dynamic Color for Confidence
    conf_color = PALETTE['success'] if conf_val > 0.8 else PALETTE['warning'] if conf_val > 0.5 else PALETTE['accent']
    
    diag_data = [
        [Paragraph("Primary Diagnosis:", styles['SmallLabel']), Paragraph("AI Confidence:", styles['SmallLabel'])],
        [Paragraph(f"<b>{diag_text.upper()}</b>", styles['MainTitle']), 
         Paragraph(f"<font color='{conf_color.hexval()}'><b>{conf_val:.1%}</b></font>", styles['MainTitle'])]
    ]
    t_diag = Table(diag_data, colWidths=[8.5*cm, 3.5*cm])
    elements.append(t_diag)
    
    # Symptoms Check
    # UPDATED: Uses 'ReportBody'
    symptoms = [s.replace('_', ' ').title() for s in patient_data.get('symptoms', [])]
    if symptoms:
        elements.append(Paragraph(f"<b>Presenting Features:</b> {', '.join(symptoms)}", styles['ReportBody']))
    
    elements.append(Spacer(1, 10))

    # --- 3. Clinical Reasoning ---
    elements.append(Paragraph("CLINICAL REASONING", styles['SectionHeader']))
    reasoning = prediction.get('clinical_reasoning', 'Analysis not available.')
    # UPDATED: Uses 'ReportBody'
    elements.append(Paragraph(reasoning, styles['ReportBody']))
    
    elements.append(Spacer(1, 10))

    # --- 4. DYNAMIC TREATMENT PLAN ---
    protocol_title, treatment_steps = get_treatment_protocol(diag_text)
    
    elements.append(Paragraph(f"PLAN: {protocol_title}", styles['SectionHeader']))
    
    t_data = []
    for category, action in treatment_steps:
        # UPDATED: Uses 'ReportBody'
        row = [
            Paragraph(f"<b>{category}</b>", styles['ReportBody']),
            Paragraph(action, styles['ReportBody'])
        ]
        t_data.append(row)
        
    t_plan = Table(t_data, colWidths=[3*cm, 9*cm])
    t_plan.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (0,-1), PALETTE['light_bg']), 
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white]), 
    ]))
    elements.append(t_plan)
    
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("<i>* Protocol suggestions must be validated by attending physician.</i>", styles['SmallLabel']))

    return elements

# ==================== MAIN GENERATOR ====================

def generate_pdf_report(patient_data, prediction, filename):
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm
    )
    styles = get_doc_styles()
    story = []

    # --- Header ---
    header_data = [[
        Paragraph("MEDIPATIENT AI", styles['MainTitle']),
        Paragraph("CLINICAL DECISION REPORT", styles['SidebarHeader'])
    ]]
    t_head = Table(header_data, colWidths=[12*cm, 7*cm])
    t_head.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT'), ('VALIGN', (0,0), (-1,-1), 'BOTTOM')]))
    story.append(t_head)
    story.append(HRFlowable(width="100%", thickness=2, color=PALETTE['primary']))
    story.append(Spacer(1, 20))

    # --- Master Layout (The Grid) ---
    sidebar_content = generate_sidebar_content(patient_data, styles)
    main_content = generate_main_content(prediction, patient_data, styles)

    # Sidebar Cell
    t_sidebar = Table([[x] for x in sidebar_content], colWidths=[5.5*cm])
    t_sidebar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PALETTE['light_bg']),
        ('PADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))

    # Main Cell
    t_main = Table([[x] for x in main_content], colWidths=[12.5*cm])
    t_main.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))

    # Master Table
    master_data = [[t_sidebar, t_main]]
    t_master = Table(master_data, colWidths=[6*cm, 13*cm])
    t_master.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (0,0), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(t_master)

    # --- Footer ---
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Confidential Medical Document", styles['SmallLabel']))

    try:
        doc.build(story)
        print(f"✅ Enhanced Report Generated: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ==================== TEST EXECUTION ====================
if __name__ == "__main__":
    p_data = {
        'patient_id': 'PT-2026-889', 'age': 65, 'gender': 'Male',
        'temperature': 39.5, 'heartRate': 115, 'systolicBP': 85, 'diastolicBP': 50,
        'respiratoryRate': 28, 'oxygenSaturation': 88,
        'symptoms': ['fever', 'shortness_of_breath', 'confusion']
    }
    pred = {
        'primary_diagnosis': 'Sepsis', 'confidence': 0.581,
        'severity_score': 0.93, 'urgency_level': 'EMERGENCY',
        'clinical_reasoning': 'Patient exhibits classical signs of distributive shock with hypotension (BP 85/50), tachycardia (115 bpm), and fever. Combined with confusion (altered mental status), this aligns with Sepsis criteria.'
    }
    
    generate_pdf_report(p_data, pred, "Enhanced_Medical_Report.pdf")