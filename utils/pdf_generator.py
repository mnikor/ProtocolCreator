import logging
from fpdf2 import FPDF
import io
from typing import Dict
import re

logger = logging.getLogger(__name__)

class ProtocolPDFGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.setup_pdf_styles()
    
    def setup_pdf_styles(self):
        """Setup PDF styles and formatting"""
        self.pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        self.pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
        self.pdf.add_font('DejaVu', 'I', 'DejaVuSansCondensed-Oblique.ttf', uni=True)
    
    def add_title_page(self, title: str):
        """Add a title page to the PDF"""
        self.pdf.add_page()
        self.pdf.set_font('DejaVu', 'B', 24)
        self.pdf.cell(0, 60, title, align='C')
        self.pdf.ln(20)
        self.pdf.set_font('DejaVu', '', 12)
        self.pdf.cell(0, 10, f'Generated: {time.strftime("%B %d, %Y")}', align='C')
    
    def add_section(self, section_name: str, content: str):
        """Add a section to the PDF with proper formatting"""
        self.pdf.add_page()
        
        # Add section heading
        self.pdf.set_font('DejaVu', 'B', 16)
        self.pdf.cell(0, 10, section_name.replace('_', ' ').title(), ln=True)
        self.pdf.ln(5)
        
        # Process content
        self.pdf.set_font('DejaVu', '', 12)
        
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
                    # Add diagram as text box
                    diagram_code = part[:diagram_end].strip()
                    self.pdf.set_font('DejaVu', 'B', 12)
                    self.pdf.cell(0, 10, 'Study Flow Diagram:', ln=True)
                    self.pdf.set_font('DejaVu', '', 10)
                    self.pdf.multi_cell(0, 5, diagram_code)
                    
                    # Add remaining text
                    remaining_text = part[diagram_end + 3:].strip()
                    if remaining_text:
                        self._add_formatted_text(remaining_text)
        else:
            self._add_formatted_text(content)
    
    def _add_formatted_text(self, text: str):
        """Add text with italic formatting"""
        # Split by asterisks and add formatting
        parts = text.split('*')
        for i, part in enumerate(parts):
            if part.strip():
                self.pdf.set_font('DejaVu', 'I' if i % 2 else '', 12)
                self.pdf.multi_cell(0, 5, part.strip())
    
    def generate_pdf(self, sections: Dict[str, str]) -> bytes:
        """Generate PDF from protocol sections"""
        try:
            # Add title page
            self.add_title_page('Study Protocol')
            
            # Add sections
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
