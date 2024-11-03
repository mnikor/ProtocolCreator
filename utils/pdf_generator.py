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

            # Add content sections
            for section_name, content in sections.items():
                # Add section title
                self.pdf.set_font('Arial', 'B', 12)
                self.pdf.cell(0, 10, section_name.replace('_', ' ').title(), ln=True)
                self.pdf.ln(5)  # Space between title and content

                # Add section content
                self.pdf.set_font('Arial', '', 10)
                self.pdf.multi_cell(0, 10, content)
                self.pdf.ln(10)  # Space between sections

            # Return PDF bytes
            return bytes(self.pdf.output())
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
