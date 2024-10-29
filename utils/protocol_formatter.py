from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

class ProtocolFormatter:
    def __init__(self):
        self.doc = Document()
        self.setup_document()

    def setup_document(self):
        """Setup document styles"""
        # Set up styles for different heading levels
        for i in range(1, 4):
            style = self.doc.styles[f'Heading {i}']
            font = style.font
            font.size = Pt(14 - i)
            font.bold = True

    def add_section(self, title, content):
        """Add a section to the protocol document"""
        self.doc.add_heading(title, level=1)
        self.doc.add_paragraph(content)
        self.doc.add_paragraph()  # Add spacing

    def format_protocol(self, sections):
        """Format complete protocol document"""
        for section_name, content in sections.items():
            self.add_section(section_name.replace('_', ' ').title(), content)
        
        return self.doc

    def save_document(self, filename):
        """Save the document"""
        self.doc.save(filename)
