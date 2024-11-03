import logging
from fpdf import FPDF
import io
from typing import Dict
import time
import re

logger = logging.getLogger(__name__)

class CustomPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

class ProtocolPDFGenerator:
    def __init__(self):
        """Initialize PDF generator with custom styling"""
        self.pdf = CustomPDF()
        self.setup_pdf_styles()
    
    def setup_pdf_styles(self):
        """Setup PDF styles and formatting"""
        self.pdf.set_margins(20, 20, 20)
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        
    def add_title_page(self, title: str):
        """Add a title page to the PDF with improved styling"""
        self.pdf.add_page()
        
        # Add title with proper positioning
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.ln(60)
        self.pdf.cell(0, 10, title, align='C', ln=True)
        
        # Add date with proper spacing
        self.pdf.ln(20)
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f'Generated: {time.strftime("%B %d, %Y")}', align='C', ln=True)
        
        # Add a line separator
        self.pdf.ln(10)
        self.pdf.line(30, self.pdf.get_y(), 180, self.pdf.get_y())
    
    def add_section(self, section_name: str, content: str):
        """Add a section to the PDF with enhanced formatting"""
        self.pdf.add_page()
        
        # Add section heading with proper styling
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, section_name.replace('_', ' ').title(), ln=True)
        self.pdf.ln(5)
        
        # Process content
        self.pdf.set_font('Arial', '', 11)
        
        # Handle Mermaid diagrams
        if '```mermaid' in content:
            parts = content.split('```mermaid')
            
            # Add text before diagram
            if parts[0].strip():
                self._add_formatted_text(parts[0])
            
            # Process diagrams and remaining text
            for part in parts[1:]:
                diagram_end = part.find('```')
                if diagram_end != -1:
                    # Add diagram heading
                    self.pdf.ln(5)
                    self.pdf.set_font('Arial', 'B', 12)
                    self.pdf.cell(0, 10, 'Study Flow Diagram:', ln=True)
                    
                    # Add diagram content in a box
                    self.pdf.set_font('Arial', '', 10)
                    diagram_code = part[:diagram_end].strip()
                    
                    # Draw a box around the diagram
                    start_y = self.pdf.get_y()
                    self.pdf.multi_cell(0, 5, diagram_code)
                    end_y = self.pdf.get_y()
                    self.pdf.rect(20, start_y - 2, 170, end_y - start_y + 4)
                    
                    # Add remaining text
                    remaining_text = part[diagram_end + 3:].strip()
                    if remaining_text:
                        self.pdf.ln(5)
                        self._add_formatted_text(remaining_text)
        else:
            self._add_formatted_text(content)
    
    def _add_formatted_text(self, text: str):
        """Add text with improved formatting including italics and proper spacing"""
        # Handle HTML tables
        if '<table' in text:
            # Extract table HTML and convert to simple text format
            text = re.sub(r'<table.*?>(.*?)</table>', self._convert_html_table, text, flags=re.DOTALL)
        
        # Split text by paragraphs for better spacing
        paragraphs = text.split('\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                # Split by asterisks and add formatting
                parts = paragraph.split('*')
                for i, part in enumerate(parts):
                    if part.strip():
                        # Toggle between regular and italic
                        self.pdf.set_font('Arial', 'I' if i % 2 else '', 11)
                        self.pdf.multi_cell(0, 5, part.strip())
                
                # Add space between paragraphs
                self.pdf.ln(3)
    
    def _convert_html_table(self, match):
        """Convert HTML table to formatted text"""
        table_html = match.group(1)
        # Simple conversion of HTML table to text format
        rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)
        table_text = []
        for row in rows:
            # Extract cells (both th and td)
            cells = re.findall(r'<t[hd]>(.*?)</t[hd]>', row)
            table_text.append(' | '.join(cell.strip() for cell in cells))
        return '\n'.join(table_text)
    
    def generate_pdf(self, sections: Dict[str, str]) -> bytes:
        """Generate PDF from protocol sections with improved formatting"""
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
                self.pdf.cell(0, 8, f'• {section_name.replace("_", " ").title()}', ln=True)
            
            # Add sections with page breaks
            for section_name, content in sections.items():
                self.add_section(section_name, content)
            
            # Get PDF bytes
            pdf_bytes = io.BytesIO()
            self.pdf.output(pdf_bytes)
            pdf_bytes.seek(0)
            return pdf_bytes.getvalue()
            
        except Exception as e:
            logger.error(f'Error generating PDF: {str(e)}')
            raise
