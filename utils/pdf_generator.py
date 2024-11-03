import logging
from fpdf import FPDF
from typing import Dict
import time
import re

logger = logging.getLogger(__name__)

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # Use built-in Arial font
        self.set_font('Arial', '')
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

class ProtocolPDFGenerator:
    def __init__(self):
        self.pdf = CustomPDF()
        self.setup_pdf_styles()
    
    def setup_pdf_styles(self):
        """Setup PDF styles and formatting"""
        self.pdf.set_margins(20, 20, 20)
    
    def add_title_page(self, title: str):
        """Add a title page to the PDF with improved styling"""
        self.pdf.add_page()
        
        # Clean and encode title
        clean_title = title.encode('latin-1', 'replace').decode('latin-1')
        
        # Add title with proper positioning
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.ln(60)
        self.pdf.cell(0, 10, clean_title, align='C', ln=True)
        
        # Add date with proper spacing
        self.pdf.ln(20)
        self.pdf.set_font('Arial', '', 12)
        date_str = time.strftime("%B %d, %Y").encode('latin-1', 'replace').decode('latin-1')
        self.pdf.cell(0, 10, f'Generated: {date_str}', align='C', ln=True)
    
    def add_section(self, section_name: str, content: str):
        """Add a section to the PDF with enhanced formatting"""
        self.pdf.add_page()
        
        # Clean and encode section name
        clean_name = section_name.replace('_', ' ').title()
        clean_name = clean_name.encode('latin-1', 'replace').decode('latin-1')
        
        # Add section heading
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, clean_name, ln=True)
        self.pdf.ln(5)
        
        # Process content
        self.pdf.set_font('Arial', '', 11)
        self._add_formatted_text(content)
    
    def _add_formatted_text(self, text: str):
        # Handle HTML tables first
        if '<table' in text:
            parts = text.split('<table')
            
            # Add text before first table
            if parts[0].strip():
                self._add_paragraphs(parts[0])
            
            # Process each table and remaining text
            for part in parts[1:]:
                table_end = part.find('</table>')
                if table_end != -1:
                    table_html = '<table' + part[:table_end + 8]
                    remaining_text = part[table_end + 8:]
                    
                    # Convert and add table
                    table_text = self._convert_html_table(table_html)
                    if table_text:
                        self._add_paragraphs(table_text)
                    
                    # Add remaining text
                    if remaining_text.strip():
                        self._add_paragraphs(remaining_text)
        else:
            self._add_paragraphs(text)

    def _add_paragraphs(self, text: str):
        try:
            # Ensure text is properly encoded
            if isinstance(text, bytes):
                text = text.decode('utf-8')
            
            paragraphs = text.split('\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Split by asterisks and add formatting
                    parts = paragraph.split('*')
                    for i, part in enumerate(parts):
                        if part.strip():
                            # Toggle between regular and italic
                            self.pdf.set_font('Arial', 'I' if i % 2 else '', 11)
                            # Encode text properly for FPDF
                            clean_text = part.strip().encode('latin-1', 'replace').decode('latin-1')
                            self.pdf.multi_cell(0, 5, clean_text)
                    
                    # Add space between paragraphs
                    self.pdf.ln(3)
        except Exception as e:
            logger.error(f"Error in _add_paragraphs: {str(e)}")
            raise
    
    def _convert_html_table(self, table_html: str) -> str:
        """Convert HTML table to formatted text"""
        try:
            rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)
            table_text = []
            
            for row in rows:
                cells = re.findall(r'<t[hd]>(.*?)</t[hd]>', row)
                formatted_cells = [cell.strip().encode('latin-1', 'replace').decode('latin-1') for cell in cells]
                formatted_row = ' | '.join(formatted_cells)
                table_text.append(formatted_row)
                
            return '\n'.join('  ' + row for row in table_text)
        except Exception as e:
            logger.error(f"Error converting HTML table: {str(e)}")
            return ""
    
    def generate_pdf(self, sections: Dict[str, str]) -> bytes:
        try:
            # Add title page
            self.add_title_page('Study Protocol')
            
            # Add table of contents
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 14)
            self.pdf.cell(0, 10, 'Table of Contents', ln=True)
            self.pdf.ln(5)
            
            # Add TOC entries
            self.pdf.set_font('Arial', '', 12)
            for section_name in sections.keys():
                # Clean section name for PDF
                clean_name = section_name.replace('_', ' ').title()
                clean_name = clean_name.encode('latin-1', 'replace').decode('latin-1')
                self.pdf.cell(0, 8, f'- {clean_name}', ln=True)
            
            # Add sections
            for section_name, content in sections.items():
                self.add_section(section_name, content)
            
            # Return PDF bytes
            return self.pdf.output(dest='S').encode('latin-1')
            
        except Exception as e:
            logger.error(f'Error generating PDF: {str(e)}')
            raise