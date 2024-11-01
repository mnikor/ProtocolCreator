# protocol_formatter.py

import os
import logging
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

logger = logging.getLogger(__name__)

class ProtocolFormatter:
    def __init__(self):
        self.doc = Document()
        self.setup_document()
        self.setup_custom_styles()

        # Track section numbers and content hashes to avoid duplication
        self.section_numbers = {}
        self.content_hashes = set()

        # Define canonical section names and their numbers
        self.section_structure = {
            "title": {"number": "1", "title": "Protocol Title"},
            "background": {"number": "2", "title": "Background"},
            "objectives": {"number": "3", "title": "Objectives"},
            "study_design": {"number": "4", "title": "Study Design"},
            "population": {"number": "5", "title": "Study Population"},
            "procedures": {"number": "6", "title": "Study Procedures"},
            "statistical_analysis": {"number": "7", "title": "Statistical Analysis"},
            "safety": {"number": "8", "title": "Safety"}
        }

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
        '''Set up custom document styles'''
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

    def _clean_section_content(self, content):
        """Clean up section content"""
        if not content:
            return ""
            
        return re.sub(r'\n{3,}', '\n\n', content.strip())

    def format_protocol(self, sections):
        try:
            # Add title page
            title = self.doc.add_paragraph('Clinical Trial Protocol')
            title.style = self.doc.styles['Title']  # Use built-in Title style
            self.doc.add_page_break()
            
            # Add table of contents
            toc_heading = self.doc.add_paragraph("Table of Contents")
            toc_heading.style = self.doc.styles['Heading1']
            self.doc.add_paragraph()  # Placeholder for TOC
            self.doc.add_page_break()
            
            # Process sections
            for section_name, section_info in self.section_structure.items():
                if section_name in sections:
                    content = self._clean_section_content(sections[section_name])
                    if content:
                        # Add section heading
                        heading = self.doc.add_paragraph(
                            f"{section_info['number']} {section_info['title']}"
                        )
                        heading.style = self.doc.styles['Heading1']
                        
                        # Add content with proper formatting
                        for para in content.split('\n\n'):
                            if para.strip():
                                p = self.doc.add_paragraph(para.strip())
                                p.style = self.doc.styles['Body']
            
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

                # Convert to PDF
                os.system(f"libreoffice --headless --convert-to pdf {docx_path}")

                if os.path.exists(pdf_path):
                    os.remove(docx_path)
                    return pdf_path
                else:
                    raise Exception("PDF conversion failed")
            else:
                docx_path = f"{filename}.docx"
                self.doc.save(docx_path)
                return docx_path

        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise
