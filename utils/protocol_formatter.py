# protocol_formatter.py

import os
import logging
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

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
            "statistical_analysis": {"number": "7", "title": "Statistical Analysis"},  # Updated name
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
        """Set up custom document styles"""
        styles = {
            'CustomTitle': {'name': 'Protocol Title', 'size': 24, 'bold': True, 'align': WD_ALIGN_PARAGRAPH.CENTER},
            'CustomHeading1': {'name': 'Section Title', 'size': 16, 'bold': True},
            'CustomHeading2': {'name': 'Subsection Title', 'size': 14, 'bold': True},
            'CustomHeading3': {'name': 'Sub-subsection Title', 'size': 12, 'bold': True},
            'CustomBody': {'name': 'Body Text', 'size': 11},
            'CustomTableText': {'name': 'Table Text', 'size': 10},
            'CustomTableHeader': {'name': 'Table Header', 'size': 10, 'bold': True},
            'CustomCaption': {'name': 'Figure Caption', 'size': 10, 'italic': True}
        }

        for style_name, props in styles.items():
            try:
                if style_name not in self.doc.styles:
                    style = self.doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
                else:
                    style = self.doc.styles[style_name]
                
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

    def _clean_section_content(self, content):
        """Clean up section content"""
        if not content:
            return ""
            
        return re.sub(r'\n{3,}', '\n\n', content.strip())

    def _format_section(self, section_name, content, parent_number):
        """Format a single section with proper numbering"""
        if not content:
            return

        section_info = self.section_structure.get(section_name)
        if not section_info:
            return

        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        subsection_number = 1
        current_level = 1

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if it's a heading
            if re.match(r'^#+\s+|^\d+\.[\d\.]*\s+|^[A-Z][A-Z\s]+$', para):
                # Clean up heading text
                heading_text = re.sub(r'^#+\s+|^\d+\.[\d\.]*\s+', '', para)

                # Determine heading level and add with proper style
                if current_level == 1:
                    heading = self.doc.add_paragraph(
                        f"{parent_number} {heading_text}",
                        style='CustomHeading1'
                    )
                else:
                    heading = self.doc.add_paragraph(
                        f"{parent_number}.{subsection_number} {heading_text}",
                        style='CustomHeading2'
                    )
                    subsection_number += 1

            # Handle bullet points and numbered lists
            elif para.startswith('•') or para.startswith('-'):
                p = self.doc.add_paragraph(style='CustomBody')
                p.add_run('• ').bold = True
                p.add_run(para[1:].strip())
            elif re.match(r'^\d+\.', para):
                p = self.doc.add_paragraph(para, style='CustomBody')
            else:
                # Regular paragraph
                p = self.doc.add_paragraph(para, style='CustomBody')

    def format_protocol(self, sections):
        """Format complete protocol with proper structure"""
        try:
            # Add title page
            title = self.doc.add_paragraph('Clinical Trial Protocol')
            title.style = self.doc.styles['CustomTitle']
            self.doc.add_page_break()

            # Add table of contents
            toc_heading = self.doc.add_paragraph("Table of Contents")
            toc_heading.style = self.doc.styles['CustomHeading1']
            self.doc.add_paragraph()  # Placeholder for TOC
            self.doc.add_page_break()

            # Process sections in order
            for section_name, section_info in self.section_structure.items():
                if section_name in sections:
                    content = self._clean_section_content(sections[section_name])
                    if content:
                        self._format_section(
                            section_name,
                            content,
                            section_info["number"]
                        )

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
