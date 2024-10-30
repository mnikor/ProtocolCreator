import logging
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from bs4 import BeautifulSoup
import re
import os
from weasyprint import HTML
import graphviz

logger = logging.getLogger(__name__)

class ProtocolFormatter:
    def __init__(self):
        self.doc = Document()
        self._setup_document()
        self._setup_styles()
        self.content_sections = []

    def _setup_document(self):
        """Initialize document settings"""
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

    def _setup_styles(self):
        """Set up document styles"""
        styles = {
            'Title': {'name': 'Protocol Title', 'size': 24, 'bold': True, 'align': WD_ALIGN_PARAGRAPH.CENTER},
            'Heading1': {'name': 'Section Title', 'size': 16, 'bold': True},
            'Heading2': {'name': 'Subsection Title', 'size': 14, 'bold': True},
            'Heading3': {'name': 'Sub-subsection Title', 'size': 12, 'bold': True},
            'Normal': {'name': 'Body Text', 'size': 11}
        }

        for style_name, props in styles.items():
            style = self.doc.styles[style_name]
            font = style.font
            font.name = 'Arial'
            font.size = Pt(props['size'])
            font.bold = props.get('bold', False)
            
            if props.get('align'):
                style.paragraph_format.alignment = props['align']

    def _add_heading(self, text, level=1):
        """Add a heading with proper formatting"""
        heading = self.doc.add_heading('', level=level)
        heading.add_run(text)
        return heading

    def _add_paragraph(self, text):
        """Add a paragraph with proper formatting"""
        para = self.doc.add_paragraph()
        para.add_run(text)
        return para

    def _add_table(self, table_data):
        """Add a table with proper formatting"""
        if not table_data:
            return None
        
        rows = len(table_data)
        cols = len(table_data[0])
        table = self.doc.add_table(rows=rows, cols=cols)
        table.style = 'Table Grid'
        
        for i, row in enumerate(table_data):
            for j, cell in enumerate(row):
                table.cell(i, j).text = str(cell)
        
        return table

    def _process_markdown(self, content):
        """Process markdown content into document elements"""
        if not content:
            return

        paragraphs = content.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Handle headings
            if para.startswith('#'):
                level = len(para.split()[0].strip('#'))
                text = para.lstrip('#').strip()
                self._add_heading(text, level)
                continue

            # Handle lists
            if para.startswith(('- ', '* ', '1. ')):
                lines = para.split('\n')
                for line in lines:
                    line = line.lstrip('- *1234567890. ')
                    self._add_paragraph('• ' + line)
                continue

            # Handle tables
            if para.startswith('|'):
                rows = [
                    [cell.strip() for cell in row.strip('|').split('|')]
                    for row in para.split('\n')
                    if '|' in row and not row.strip('| -').isspace()
                ]
                if rows:
                    self._add_table(rows)
                continue

            # Handle regular paragraphs
            self._add_paragraph(para)

    def format_protocol(self, sections):
        """Format complete protocol document"""
        try:
            # Add title page
            self._add_heading('Clinical Trial Protocol', 0)
            self.doc.add_page_break()

            # Add table of contents
            self._add_heading('Table of Contents', 1)
            self.doc.add_paragraph('Contents will be generated automatically')
            self.doc.add_page_break()

            # Process each section
            for section_name, content in sections.items():
                title = section_name.replace('_', ' ').title()
                self._add_heading(title, 1)
                self._process_markdown(content)
                self.doc.add_page_break()

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
                self.doc.save(docx_path)
                # Convert to PDF using a system command
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
