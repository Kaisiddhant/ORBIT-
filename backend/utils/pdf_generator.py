from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os

class PolicyPDFGenerator:
    def __init__(self, output_folder='pdfs'):
        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12
        )
    
    def generate_policy_document(self, policy_data, user_data):
        """
        Generate a professional insurance policy PDF
        """
        filename = f"policy_{policy_data['policy_number']}.pdf"
        filepath = os.path.join(self.output_folder, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        story = []
        
        # Header
        story.append(Paragraph("ORBIT INSURANCE", self.title_style))
        story.append(Paragraph("Insurance Policy Certificate", self.styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Policy Details Table
        policy_info = [
            ['Policy Number:', policy_data['policy_number']],
            ['Issue Date:', datetime.now().strftime('%B %d, %Y')],
            ['Status:', policy_data['status'].upper()],
        ]
        
        policy_table = Table(policy_info, colWidths=[2*inch, 4*inch])
        policy_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(policy_table)
        story.append(Spacer(1, 20))
        
        # Policyholder Information
        story.append(Paragraph("Policyholder Information", self.heading_style))
        
        user_info = [
            ['Full Name:', user_data.get('full_name', 'N/A')],
            ['Email:', user_data.get('email', 'N/A')],
            ['Phone:', user_data.get('phone', 'N/A')],
            ['Age:', str(user_data.get('age', 'N/A'))],
        ]
        
        user_table = Table(user_info, colWidths=[2*inch, 4*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(user_table)
        story.append(Spacer(1, 20))
        
        # Coverage Details
        story.append(Paragraph("Coverage Details", self.heading_style))
        
        plan = policy_data.get('plan', {})
        coverage_info = [
            ['Plan Name:', plan.get('name', 'N/A')],
            ['Provider:', plan.get('provider', 'N/A')],
            ['Type:', plan.get('type', 'N/A')],
            ['Coverage Amount:', f"${policy_data.get('coverage_amount', 0):,.2f}"],
            ['Annual Premium:', f"${policy_data.get('premium', 0):,.2f}"],
            ['Monthly Premium:', f"${policy_data.get('premium', 0)/12:,.2f}"],
        ]
        
        coverage_table = Table(coverage_info, colWidths=[2*inch, 4*inch])
        coverage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3e0')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(coverage_table)
        story.append(Spacer(1, 20))
        
        # Features
        if plan.get('features'):
            story.append(Paragraph("Plan Features", self.heading_style))
            for feature in plan['features']:
                story.append(Paragraph(f"• {feature}", self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Terms and Conditions
        story.append(Paragraph("Terms and Conditions", self.heading_style))
        terms = """
        This policy is subject to the terms and conditions set forth by ORBIT Insurance and the underwriting provider. 
        Coverage becomes effective upon receipt of the first premium payment. The policyholder agrees to pay premiums 
        on time and provide accurate information. Claims must be filed within the specified timeframe as outlined 
        in the complete policy documentation.
        """
        story.append(Paragraph(terms, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Paragraph(footer_text, self.styles['Italic']))
        
        # Build PDF
        doc.build(story)
        
        return filepath