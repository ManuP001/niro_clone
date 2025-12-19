import os
import logging
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors

logger = logging.getLogger(__name__)

class AstroPrescriptionPDF:
    """
    Generate "Astro-Prescription" PDF reports
    Format: Diagnosis + Remedy + Timeline
    """
    
    def __init__(self, output_dir: str = "/app/backend/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_pdf(self, report_data: Dict[str, Any]) -> str:
        """
        Generate PDF report
        
        Args:
            report_data: Dictionary containing:
                - report_id
                - report_type
                - user_name
                - birth_details
                - interpreted_text
                - raw_json (optional)
        
        Returns:
            str: Path to generated PDF file
        """
        report_id = report_data.get('report_id', 'unknown')
        filename = f"astro_prescription_{report_id}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        logger.info(f"Generating PDF: {filepath}")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#3949ab'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#212121'),
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=16
        )
        
        # Title
        elements.append(Paragraph("🌟 Astro-Prescription Report 🌟", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        report_type_names = {
            'yearly_prediction': 'Yearly Prediction (The Compass)',
            'love_marriage': 'Love & Marriage Compatibility (The Harmony)',
            'career_job': 'Career & Job Success (The Climber)'
        }
        
        report_type = report_data.get('report_type', 'unknown')
        report_name = report_type_names.get(report_type, report_type)
        
        elements.append(Paragraph(f"<b>Report Type:</b> {report_name}", body_style))
        elements.append(Paragraph(f"<b>Report ID:</b> {report_id}", body_style))
        elements.append(Paragraph(f"<b>Generated On:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}", body_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # User details
        if 'user_name' in report_data:
            elements.append(Paragraph("<b>Prepared For:</b>", subheading_style))
            elements.append(Paragraph(f"Name: {report_data['user_name']}", body_style))
            
            if 'birth_details' in report_data:
                bd = report_data['birth_details']
                elements.append(Paragraph(f"Date of Birth: {bd.get('dob', 'N/A')}", body_style))
                elements.append(Paragraph(f"Time of Birth: {bd.get('tob', 'N/A')}", body_style))
                elements.append(Paragraph(f"Place of Birth: {bd.get('location', 'N/A')}", body_style))
            
            elements.append(Spacer(1, 0.3*inch))
        
        # Main content - Interpreted text
        elements.append(Paragraph("📋 Your Astrological Analysis", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        interpreted_text = report_data.get('interpreted_text', 'Report content not available.')
        
        # Split text into paragraphs and add to PDF
        paragraphs = interpreted_text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Clean markdown formatting first
                para = para.strip()
                
                # Remove ### markdown headers
                if para.startswith('###'):
                    para = para[3:].strip()
                    # Remove any surrounding ** markers
                    para = para.strip('*').strip()
                    elements.append(Paragraph(para, subheading_style))
                elif para.startswith('##'):
                    para = para[2:].strip()
                    para = para.strip('*').strip()
                    elements.append(Paragraph(para, heading_style))
                elif para.startswith('#'):
                    para = para[1:].strip()
                    para = para.strip('*').strip()
                    elements.append(Paragraph(para, heading_style))
                else:
                    # Regular paragraph - clean up markdown
                    # Replace ** bold markers properly
                    import re
                    para = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', para)
                    # Replace single * with bullet
                    para = para.replace('* ', '• ')
                    # Remove any remaining single asterisks
                    para = para.replace('*', '')
                    elements.append(Paragraph(para, body_style))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#757575'),
            alignment=TA_CENTER
        )
        
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", footer_style))
        elements.append(Paragraph(
            "This report is generated using Vedic Astrology principles and AI interpretation.<br/>"
            "For personalized consultation, please consult a qualified astrologer.<br/>"
            "<b>Astro-Trust Engine</b> • Powered by Gemini AI",
            footer_style
        ))
        
        # Build PDF
        doc.build(elements)
        
        logger.info(f"PDF generated successfully: {filepath}")
        return filepath
    
    def get_pdf_url(self, filepath: str) -> str:
        """Convert file path to accessible URL (for MVP, just return filename)"""
        filename = os.path.basename(filepath)
        return f"/api/reports/download/{filename}"
