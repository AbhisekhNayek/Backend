from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors

def get_base_styles():
    styles = getSampleStyleSheet()
    
    # Custom Styles to avoid key collisions
    title_style = ParagraphStyle(
        name='DocTitle',
        parent=styles['Normal'],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#2C3E50")
    )
    
    right_date_style = ParagraphStyle(
        name='RightDate',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        fontName='Helvetica',
        textColor=colors.HexColor("#7F8C8D")
    )
    
    section_heading = ParagraphStyle(
        name='SecHeading',
        parent=styles['Normal'],
        fontSize=14,
        leading=18,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#2C3E50"),
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        name='DocBody',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        fontName='Helvetica',
        textColor=colors.HexColor("#34495E")
    )
    
    sub_body_style = ParagraphStyle(
        name='DocSubBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        fontName='Helvetica',
        textColor=colors.HexColor("#7F8C8D"),
        leftIndent=15
    )
    
    footer_style = ParagraphStyle(
        name='DocFooter',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor("#95A5A6")
    )
    
    return title_style, right_date_style, section_heading, body_style, sub_body_style, footer_style

def generate_prescription_pdf(data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    title_style, right_date_style, section_heading, body_style, sub_body_style, footer_style = get_base_styles()
    story = []
    
    # Title
    story.append(Paragraph("EDOCHUB DIGITAL PRESCRIPTION", title_style))
    story.append(Spacer(1, 15))
    
    # Date
    curr_date = datetime.now().strftime("%d/%m/%Y")
    story.append(Paragraph(f"Date: {curr_date}", right_date_style))
    story.append(Spacer(1, 15))
    
    # Doctor Details
    story.append(Paragraph("Doctor Details", section_heading))
    story.append(Paragraph(f"Name: {data.get('doctorName')}", body_style))
    story.append(Paragraph(f"Specialization: {data.get('specialization', 'N/A')}", body_style))
    story.append(Spacer(1, 15))
    
    # Patient Details
    story.append(Paragraph("Patient Details", section_heading))
    story.append(Paragraph(f"Name: {data.get('patientName')}", body_style))
    story.append(Paragraph(f"Age: {data.get('patientAge', 'N/A')}", body_style))
    story.append(Paragraph(f"Gender: {data.get('patientGender', 'N/A')}", body_style))
    story.append(Spacer(1, 15))
    
    # Medications
    story.append(Paragraph("Medications", section_heading))
    meds = data.get("medications", [])
    for idx, med in enumerate(meds):
        name = med.get("name")
        dosage = med.get("dosage")
        freq = med.get("frequency")
        dur = med.get("duration")
        inst = med.get("instructions")
        
        story.append(Paragraph(f"{idx + 1}. {name} ({dosage})", body_style))
        story.append(Paragraph(f"Frequency: {freq} | Duration: {dur}", sub_body_style))
        if inst:
            story.append(Paragraph(f"Instructions: {inst}", sub_body_style))
        story.append(Spacer(1, 6))
        
    story.append(Spacer(1, 15))
    
    # Advice
    advice = data.get("advice")
    if advice:
        story.append(Paragraph("Advice", section_heading))
        story.append(Paragraph(advice, body_style))
        story.append(Spacer(1, 20))
        
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("This is a digitally generated prescription.", footer_style))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_visit_report_pdf(data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    title_style, right_date_style, section_heading, body_style, sub_body_style, footer_style = get_base_styles()
    story = []
    
    # Title
    story.append(Paragraph("PATIENT VISIT REPORT", title_style))
    story.append(Spacer(1, 15))
    
    # Date
    curr_date = datetime.now().strftime("%d/%m/%Y")
    story.append(Paragraph(f"Date: {curr_date}", right_date_style))
    story.append(Spacer(1, 15))
    
    # Patient Name
    story.append(Paragraph("Patient Details", section_heading))
    story.append(Paragraph(f"Name: {data.get('patientName')}", body_style))
    story.append(Spacer(1, 15))
    
    # Vitals
    story.append(Paragraph("Vitals", section_heading))
    vitals = data.get("vitals", {})
    story.append(Paragraph(f"Temperature: {vitals.get('temperature', 'N/A')}", body_style))
    story.append(Paragraph(f"Blood Pressure: {vitals.get('bloodPressure', 'N/A')}", body_style))
    story.append(Paragraph(f"Pulse Rate: {vitals.get('pulseRate', 'N/A')}", body_style))
    story.append(Paragraph(f"SpO2: {vitals.get('spO2', 'N/A')}", body_style))
    story.append(Paragraph(f"Weight: {vitals.get('weight', 'N/A')}", body_style))
    story.append(Spacer(1, 15))
    
    # Chief Complaints
    cc = data.get("chiefComplaints")
    if cc:
        story.append(Paragraph("Chief Complaints", section_heading))
        story.append(Paragraph(cc, body_style))
        story.append(Spacer(1, 15))
        
    # Diagnosis
    diag = data.get("diagnosis")
    if diag:
        story.append(Paragraph("Diagnosis", section_heading))
        story.append(Paragraph(diag, body_style))
        story.append(Spacer(1, 15))
        
    # Observations
    obs = data.get("observations")
    if obs:
        story.append(Paragraph("Observations", section_heading))
        story.append(Paragraph(obs, body_style))
        
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
