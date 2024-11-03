import logging
from fpdf import FPDF
from typing import Dict
import time

# Initialize logging
logger = logging.getLogger(__name__)

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=35)  # Set margin for page breaks
        # Use standard font instead of custom Unicode font
        self.set_font('Arial', '', 12)

    def header(self):
        # Header with page number
        self.set_y(10)
        self.set_font('Arial', 'I', 8)
        header_text = f'Protocol - Page {self.page_no()}'
        self.cell(0, 10, header_text, 0, 0, 'R')

    def footer(self):
        # Footer with generation date
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        date_str = time.strftime("%B %d, %Y")
        footer_text = f'Generated: {date_str}'
        self.cell(0, 10, footer_text, 0, 0, 'C')

class ProtocolPDFGenerator:
    def __init__(self):
        self.pdf = CustomPDF()

    def generate_pdf(self, sections: Dict[str, str]) -> bytes:
        try:
            self.pdf.add_page()

            # Add title
            if 'title' in sections:
                self.pdf.set_font('Arial', 'B', 14)
                self.pdf.multi_cell(0, 10, sections['title'])
                self.pdf.ln(10)

            # Add content sections
            for section_name, content in sections.items():
                if section_name != 'title':  # Skip title as it's already added
                    # Add section title
                    self.pdf.set_font('Arial', 'B', 12)
                    self.pdf.cell(0, 10, section_name.replace('_', ' ').title(), ln=True)
                    self.pdf.ln(5)

                    # Add section content
                    self.pdf.set_font('Arial', '', 11)
                    # Clean text for PDF compatibility
                    clean_content = content.encode('latin-1', 'replace').decode('latin-1')
                    self.pdf.multi_cell(0, 6, clean_content)
                    self.pdf.ln(10)

            # Return PDF bytes
            return bytes(self.pdf.output())

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
