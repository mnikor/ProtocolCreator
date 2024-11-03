import logging
from fpdf import FPDF
from typing import Dict
import time
import re

logger = logging.getLogger(__name__)

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=35)  # Updated margin
        # Use built-in Arial font for better compatibility
        self.set_font('Arial', '')
        
    def header(self):
        # Add header with page number at the top right
        self.set_y(10)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Protocol - Page {self.page_no()}', 0, 0, 'R')
        
    def footer(self):
        # Add footer with generation date
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        date_str = time.strftime("%B %d, %Y")
        self.cell(0, 10, f'Generated: {date_str}', 0, 0, 'C')

class ProtocolPDFGenerator:
    def __init__(self):
        self.pdf = CustomPDF()
        self.setup_pdf_styles()
    
    def setup_pdf_styles(self):
        '''Setup PDF styles and formatting'''
        # Set wider margins for better readability
        self.pdf.set_margins(35, 35, 35)  # Increase left, top, right margins
        self.pdf.set_auto_page_break(auto=True, margin=35)  # Increase bottom margin
    
    def add_title_page(self, title: str):
        """Add a title page to the PDF with improved styling"""
        self.pdf.add_page()
        
        # Add title with proper positioning and styling
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.ln(60)
        self.pdf.cell(0, 10, title, align='C', ln=True)
        
        # Add subtitle
        self.pdf.set_font('Arial', 'I', 14)
        self.pdf.ln(10)
        self.pdf.cell(0, 10, 'Clinical Study Protocol', align='C', ln=True)
        
        # Add date with proper spacing
        self.pdf.ln(20)
        self.pdf.set_font('Arial', '', 12)
        date_str = time.strftime("%B %d, %Y")
        self.pdf.cell(0, 10, f'Generated: {date_str}', align='C', ln=True)
    
    def add_section(self, section_name: str, content: str):
        """Add a section to the PDF with enhanced formatting"""
        self.pdf.add_page()
        
        # Add section heading with proper styling
        clean_name = section_name.replace('_', ' ').title()
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, clean_name, ln=True)
        self.pdf.ln(5)
        
        # Process content with improved formatting
        self.pdf.set_font('Arial', '', 11)
        self._add_formatted_text(content)

    def _add_formatted_text(self, text: str):
        try:
            # Convert and clean text once at the start
            if isinstance(text, bytes):
                text = text.decode('utf-8')
            
            # Comprehensive character replacements
            replacements = {
                '•': '-',  # bullet
                '–': '-',  # en dash
                '—': '-',  # em dash
                '"': '"',  # left double quote
                '"': '"',  # right double quote
                ''': "'",  # left single quote
                ''': "'",  # right single quote
                '≥': '>=', # greater than or equal
                '≤': '<=', # less than or equal
                '±': '+/-',  # plus-minus
                '°': ' degrees ',  # degree
                '×': 'x',  # multiplication
                '→': '->',  # right arrow
                '←': '<-',  # left arrow
                'μ': 'u',  # micro
                '≈': '~',  # approximately
                '©': '(c)', # copyright
                '®': '(R)', # registered trademark
                '™': '(TM)', # trademark
                '€': 'EUR', # euro
                '£': 'GBP', # pound
                '¥': 'JPY', # yen
                '§': 'Section ', # section
                '†': '*', # dagger
                '‡': '**', # double dagger
                '…': '...', # ellipsis
            }
            
            # Apply all replacements
            for old, new in replacements.items():
                text = text.replace(old, new)
            
            # Process tables first
            if '<table' in text:
                parts = text.split('<table')
                if parts[0].strip():
                    self._add_paragraphs(parts[0])
                
                for part in parts[1:]:
                    table_end = part.find('</table>')
                    if table_end != -1:
                        table_html = '<table' + part[:table_end + 8]
                        remaining_text = part[table_end + 8:]
                        
                        table_text = self._convert_html_table(table_html)
                        if table_text:
                            self._add_table(table_text)
                        
                        if remaining_text.strip():
                            self._add_paragraphs(remaining_text)
            else:
                self._add_paragraphs(text)
                
        except Exception as e:
            logger.error(f"Error in _add_formatted_text: {str(e)}")
            raise
    
    def _add_paragraphs(self, text: str):
        try:
            paragraphs = text.split('\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Split by asterisks for italic formatting
                    parts = paragraph.split('*')
                    for i, part in enumerate(parts):
                        if part.strip():
                            self.pdf.set_font('Arial', 'I' if i % 2 else '', 11)
                            # Clean and encode text
                            clean_text = part.strip()
                            clean_text = ''.join(char if ord(char) < 128 else '_' for char in clean_text)
                            
                            # Calculate effective width accounting for margins
                            effective_width = self.pdf.w - (2 * self.pdf.l_margin)  # Double margin to account for both sides
                            
                            # Use multi_cell with proper width and height
                            self.pdf.multi_cell(
                                w=effective_width,
                                h=6,  # Line height
                                txt=clean_text,
                                align='L'  # Left alignment
                            )
                    
                    # Add proper spacing between paragraphs
                    self.pdf.ln(4)
        except Exception as e:
            logger.error(f"Error in _add_paragraphs: {str(e)}")
            raise
    
    def _add_table(self, table_text: str):
        try:
            self.pdf.ln(4)
            self.pdf.set_fill_color(240, 240, 240)
            
            rows = table_text.split('\n')
            if rows:
                # Calculate effective width for table
                effective_width = self.pdf.w - (2 * self.pdf.l_margin)
                cols = rows[0].count('|') + 1
                col_width = effective_width / cols
                
                # Add header row
                cells = rows[0].split('|')
                self.pdf.set_font('Arial', 'B', 10)
                for cell in cells:
                    clean_cell = ''.join(char if ord(char) < 128 else '_' for char in cell.strip())
                    self.pdf.cell(col_width, 8, clean_cell, 1, 0, 'C', True)
                self.pdf.ln()
                
                # Add data rows
                self.pdf.set_font('Arial', '', 10)
                for row in rows[1:]:
                    if row.strip():
                        cells = row.split('|')
                        for cell in cells:
                            clean_cell = ''.join(char if ord(char) < 128 else '_' for char in cell.strip())
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
                formatted_cells = [cell.strip() for cell in cells]
                formatted_row = ' | '.join(formatted_cells)
                table_text.append(formatted_row)
                
            return '\n'.join(table_text)
        except Exception as e:
            logger.error(f"Error converting HTML table: {str(e)}")
            return ""
    
    def generate_pdf(self, sections: Dict[str, str]) -> bytes:
        try:
            # Initialize PDF
            self.pdf = CustomPDF()
            self.setup_pdf_styles()
            
            # Add title page
            title = sections.get('title', 'Study Protocol')
            self.add_title_page(title)
            
            # Add table of contents
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 16)
            self.pdf.cell(0, 10, 'Table of Contents', ln=True)
            self.pdf.ln(5)
            
            # Add TOC entries
            self.pdf.set_font('Arial', '', 12)
            for section_name in sections.keys():
                clean_name = section_name.replace('_', ' ').title()
                self.pdf.cell(0, 8, f'- {clean_name}', ln=True)
            
            # Add sections
            for section_name, content in sections.items():
                self.add_section(section_name, content)
            
            # Get PDF bytes with proper encoding handling
            return self.pdf.output('', 'S').encode('latin-1')
            
        except Exception as e:
            logger.error(f'Error generating PDF: {str(e)}')
            raise
