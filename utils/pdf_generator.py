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
        # Use built-in Arial font for better compatibility
        self.set_font('Arial', '')
        
    def header(self):
        # Add header with page number at the top right
        self.set_y(10)
        self.set_font('Arial', 'I', 8)
        header_text = f'Protocol - Page {self.page_no()}'.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 10, header_text, 0, 0, 'R')
        
    def footer(self):
        # Add footer with generation date
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        date_str = time.strftime("%B %d, %Y").encode('latin-1', 'replace').decode('latin-1')
        footer_text = f'Generated: {date_str}'.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 10, footer_text, 0, 0, 'C')

class ProtocolPDFGenerator:
    def __init__(self):
        self.pdf = CustomPDF()
        self.setup_pdf_styles()
    
    def setup_pdf_styles(self):
        '''Setup PDF styles and formatting'''
        # Set margins for better readability
        self.pdf.set_margins(25, 25, 25)
        # Line height is handled by multi_cell spacing
    
    def add_title_page(self, title: str):
        """Add a title page to the PDF with improved styling"""
        self.pdf.add_page()
        
        # Clean and encode title
        clean_title = title.encode('latin-1', 'replace').decode('latin-1')
        
        # Add title with proper positioning and styling
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.ln(60)
        self.pdf.cell(0, 10, clean_title, align='C', ln=True)
        
        # Add subtitle
        subtitle = 'Clinical Study Protocol'.encode('latin-1', 'replace').decode('latin-1')
        self.pdf.set_font('Arial', 'I', 14)
        self.pdf.ln(10)
        self.pdf.cell(0, 10, subtitle, align='C', ln=True)
        
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
        
        # Add section heading with proper styling
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, clean_name, ln=True)
        self.pdf.ln(5)
        
        # Process content with improved formatting
        self.pdf.set_font('Arial', '', 11)
        self._add_formatted_text(content)
    
    def _add_formatted_text(self, text: str):
        """Add formatted text with enhanced styling"""
        try:
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
                        
                        # Convert and add table with improved styling
                        table_text = self._convert_html_table(table_html)
                        if table_text:
                            self._add_table(table_text)
                        
                        # Add remaining text
                        if remaining_text.strip():
                            self._add_paragraphs(remaining_text)
            else:
                self._add_paragraphs(text)
        except Exception as e:
            logger.error(f"Error in _add_formatted_text: {str(e)}")
            raise
    
    def _add_paragraphs(self, text: str):
        """Add paragraphs with improved formatting"""
        try:
            # Pre-process text to handle encoding
            if isinstance(text, bytes):
                text = text.decode('utf-8')
            
            # Replace problematic characters
            text = text.replace('•', '-')
            text = text.replace('•', '-')  # Bullet point
            text = text.replace('–', '-')  # En dash
            text = text.replace('—', '-')  # Em dash
            text = text.replace('"', '"')  # Left double quote
            text = text.replace('"', '"')  # Right double quote
            text = text.replace(''', "'")  # Left single quote
            text = text.replace(''', "'")  # Right single quote
            
            paragraphs = text.split('\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Split by asterisks for italic formatting
                    parts = paragraph.split('*')
                    for i, part in enumerate(parts):
                        if part.strip():
                            # Toggle between regular and italic
                            self.pdf.set_font('Arial', 'I' if i % 2 else '', 11)
                            # Clean and encode text
                            clean_text = part.strip()
                            clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
                            # Add text with proper line spacing
                            self.pdf.multi_cell(0, 6, clean_text)
                    
                    # Add space between paragraphs
                    self.pdf.ln(4)
        except Exception as e:
            logger.error(f"Error in _add_paragraphs: {str(e)}")
            raise
    
    def _add_table(self, table_text: str):
        """Add table with improved styling"""
        try:
            # Add table header
            self.pdf.ln(4)
            self.pdf.set_fill_color(240, 240, 240)  # Light gray background for header
            
            rows = table_text.split('\n')
            if rows:
                # Calculate column widths
                cols = rows[0].count('|') + 1
                col_width = (self.pdf.w - 50) / cols  # Account for margins
                
                # Add header row
                cells = rows[0].split('|')
                self.pdf.set_font('Arial', 'B', 10)
                for cell in cells:
                    clean_cell = cell.strip().encode('latin-1', 'replace').decode('latin-1')
                    self.pdf.cell(col_width, 8, clean_cell, 1, 0, 'C', True)
                self.pdf.ln()
                
                # Add data rows
                self.pdf.set_font('Arial', '', 10)
                for row in rows[1:]:
                    if row.strip():
                        cells = row.split('|')
                        for cell in cells:
                            clean_cell = cell.strip().encode('latin-1', 'replace').decode('latin-1')
                            self.pdf.cell(col_width, 6, clean_cell, 1, 0, 'L')
                        self.pdf.ln()
                
                self.pdf.ln(4)
        except Exception as e:
            logger.error(f"Error in _add_table: {str(e)}")
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
                
            return '\n'.join(table_text)
        except Exception as e:
            logger.error(f"Error converting HTML table: {str(e)}")
            return ""
    
    def generate_pdf(self, sections: Dict[str, str]) -> bytes:
        try:
            # Add title page
            title = sections.get('title', 'Study Protocol')
            self.add_title_page(title)
            
            # Add table of contents
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 16)
            # Encode TOC title
            toc_title = 'Table of Contents'.encode('latin-1', 'replace').decode('latin-1')
            self.pdf.cell(0, 10, toc_title, ln=True)
            self.pdf.ln(5)
            
            # Add TOC entries with encoding
            self.pdf.set_font('Arial', '', 12)
            for section_name in sections.keys():
                clean_name = section_name.replace('_', ' ').title()
                clean_name = clean_name.encode('latin-1', 'replace').decode('latin-1')
                self.pdf.cell(0, 8, f'- {clean_name}', ln=True)
            
            # Add sections with proper encoding
            for section_name, content in sections.items():
                self.add_section(section_name, content)
            
            # Return PDF bytes
            return self.pdf.output().encode('latin-1')
            
        except Exception as e:
            logger.error(f'Error generating PDF: {str(e)}')
            raise
