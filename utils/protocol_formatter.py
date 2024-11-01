import re
import logging
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx2pdf import convert

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
        try:
            # First ensure Normal style exists as base
            if 'Normal' not in self.doc.styles:
                self.doc.styles.add_style('Normal', WD_STYLE_TYPE.PARAGRAPH)
                
            styles = {
                'Title': {'name': 'Protocol Title', 'size': 24, 'bold': True, 'align': WD_ALIGN_PARAGRAPH.CENTER},
                'Heading1': {'name': 'Section Title', 'size': 16, 'bold': True},
                'Heading2': {'name': 'Subsection Title', 'size': 14, 'bold': True},
                'Heading3': {'name': 'Sub-subsection Title', 'size': 12, 'bold': True},
                'Body': {'name': 'Body Text', 'size': 11},
                'TableText': {'name': 'Table Text', 'size': 10},
                'TableHeader': {'name': 'Table Header', 'size': 10, 'bold': True},
                'Caption': {'name': 'Figure Caption', 'size': 10, 'italic': True}
            }

            for style_name, props in styles.items():
                try:
                    # Use built-in style if it exists, otherwise create new
                    if style_name in ['Title', 'Heading1', 'Heading2', 'Heading3']:
                        style = self.doc.styles[style_name]
                    else:
                        style = self.doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
                    
                    font = style.font
                    font.name = 'Arial'
                    font.size = Pt(props['size'])
                    font.bold = props.get('bold', False)
                    font.italic = props.get('italic', False)
                    
                    para_format = style.paragraph_format
                    para_format.space_before = Pt(6)
                    para_format.space_after = Pt(6)
                    para_format.line_spacing = 1.15
                    
                    if props.get('align'):
                        para_format.alignment = props['align']
                        
                except Exception as e:
                    logger.error(f"Error setting up style {style_name}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in setup_custom_styles: {str(e)}")

    def format_protocol(self, sections):
        try:
            # Add title page with proper style
            title = self.doc.add_paragraph('Clinical Trial Protocol')
            title.style = 'Title'  # Use built-in style
            self.doc.add_page_break()
            
            # Process sections with proper styling
            section_number = 1
            for section_name, content in sections.items():
                if content:
                    # Add section heading
                    heading = self.doc.add_paragraph(
                        f"{section_number}. {section_name.replace('_', ' ').title()}"
                    )
                    heading.style = 'Heading1'
                    
                    # Add content with proper formatting
                    for para in content.split('\n\n'):
                        if para.strip():
                            p = self.doc.add_paragraph(para.strip())
                            p.style = 'Normal'
                            
                    section_number += 1
                    
            return self.doc
            
        except Exception as e:
            logger.error(f"Error formatting protocol: {str(e)}")
            raise

    def save_document(self, filename, format='docx'):
        try:
            # Always save as DOCX first
            docx_path = f"{filename}.docx"
            self.doc.save(docx_path)
            
            if format.lower() == 'pdf':
                try:
                    pdf_path = f"{filename}.pdf"
                    convert(docx_path, pdf_path)
                    return pdf_path
                except Exception as pdf_error:
                    logger.error(f"Error converting to PDF: {str(pdf_error)}")
                    raise ValueError(
                        "Could not convert to PDF. Please try downloading as DOCX instead."
                    )
            return docx_path
                
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise
