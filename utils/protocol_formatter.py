import os
import logging
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

logger = logging.getLogger(__name__)

class ProtocolFormatter:
    def __init__(self):
        self.doc = Document()
        self.setup_document()
        self.setup_custom_styles()
        
    def setup_document(self):
        """Initialize document settings"""
        # Set margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            
    def setup_custom_styles(self):
        """Set up custom document styles"""
        styles = {
            'CustomTitle': {'name': 'Protocol Title', 'size': 24, 'bold': True, 'align': 'CENTER'},
            'CustomHeading1': {'name': 'Section Title', 'size': 16, 'bold': True},
            'CustomHeading2': {'name': 'Subsection Title', 'size': 14, 'bold': True},
            'CustomHeading3': {'name': 'Sub-subsection Title', 'size': 12, 'bold': True},
            'BodyText': {'name': 'Body Text', 'size': 11},
            'TableText': {'name': 'Table Text', 'size': 10},
            'TableHeader': {'name': 'Table Header', 'size': 10, 'bold': True},
            'Caption': {'name': 'Figure Caption', 'size': 10, 'italic': True},
            'Reference': {'name': 'Reference Text', 'size': 10},
            'ListBullet': {'name': 'List Bullet', 'size': 11},
            'ListNumber': {'name': 'List Number', 'size': 11}
        }
        
        for style_name, props in styles.items():
            if style_name not in self.doc.styles:
                style = self.doc.styles.add_style(style_name, 1)
                font = style.font
                font.name = 'Arial'
                font.size = Pt(props['size'])
                font.bold = props.get('bold', False)
                font.italic = props.get('italic', False)
                
                para_format = style.paragraph_format
                para_format.space_before = Pt(6)
                para_format.space_after = Pt(6)
                para_format.line_spacing = 1.15
                
                if props.get('align') == 'CENTER':
                    para_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    
    def format_protocol(self, sections):
        """Format complete protocol document"""
        try:
            # Add title page
            title = self.doc.add_paragraph('Clinical Trial Protocol')
            title.style = self.doc.styles['CustomTitle']
            
            # Add each section with proper heading levels
            for section_name, content in sections.items():
                # Add section heading with proper style
                heading = self.doc.add_paragraph(section_name.replace('_', ' ').title())
                heading.style = self.doc.styles['CustomHeading1']
                
                # Split content into subsections if needed
                subsections = content.split('\n\n')
                for subsection in subsections:
                    if subsection.strip():
                        # Check if it's a subsection heading
                        if ':' in subsection and len(subsection.split(':')[0]) < 50:
                            subheading = self.doc.add_paragraph(subsection.split(':')[0])
                            subheading.style = self.doc.styles['CustomHeading2']
                            content_text = ':'.join(subsection.split(':')[1:])
                        else:
                            content_text = subsection
                            
                        # Add content with proper body style
                        if content_text.strip():
                            para = self.doc.add_paragraph(content_text.strip())
                            para.style = self.doc.styles['BodyText']
            
            return self.doc
            
        except Exception as e:
            logger.error(f"Error formatting protocol: {str(e)}")
            raise
            
    def save_document(self, filename, format='docx'):
        """Save document in specified format"""
        try:
            if format.lower() == 'pdf':
                docx_path = f"{filename}.docx"
                pdf_path = f"{filename}.pdf"
                
                # Save as DOCX first
                self.doc.save(docx_path)
                
                # Convert to PDF using libreoffice
                os.system(f"libreoffice --headless --convert-to pdf {docx_path}")
                
                # Check if conversion was successful
                if os.path.exists(pdf_path):
                    os.remove(docx_path)  # Clean up DOCX
                    return pdf_path
                else:
                    raise Exception("PDF conversion failed")
                    
            else:  # DOCX format
                docx_path = f"{filename}.docx"
                self.doc.save(docx_path)
                return docx_path
                
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise
