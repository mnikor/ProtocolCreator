from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re
from docx2pdf import convert
import logging

logger = logging.getLogger(__name__)

class ProtocolFormatter:
    def __init__(self):
        self.doc = Document()
        self.setup_document()

    def setup_document(self):
        """Setup document styles"""
        # Set margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Set up styles
        styles = {
            'Heading 1': {'size': 16, 'bold': True, 'before': 24, 'after': 12},
            'Heading 2': {'size': 14, 'bold': True, 'before': 12, 'after': 6},
            'Heading 3': {'size': 12, 'bold': True, 'before': 6, 'after': 6},
            'Normal': {'size': 11, 'bold': False, 'before': 0, 'after': 6}
        }

        for name, props in styles.items():
            style = self.doc.styles[name]
            font = style.font
            font.size = Pt(props['size'])
            font.bold = props['bold']
            paragraph_format = style.paragraph_format
            paragraph_format.space_before = Pt(props['before'])
            paragraph_format.space_after = Pt(props['after'])

    def clean_text(self, text):
        """Clean text of markdown and escape characters"""
        # Remove escaped characters and extra spaces
        text = text.replace('\\', '').strip()
        # Remove duplicate headings
        text = re.sub(r'# (\w+)\s+# \1', r'# \1', text)
        # Remove escaped hashmarks
        text = re.sub(r'\\\#', '#', text)
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    def parse_table(self, table_text):
        """Parse markdown table into rows and columns"""
        lines = [line.strip() for line in table_text.split('\n') if line.strip()]
        if len(lines) < 3:  # Need header, separator, and at least one row
            return None

        # Remove outer pipes and split
        rows = [[cell.strip() for cell in row.strip('|').split('|')] 
               for row in lines if not all(c in '|-' for c in row)]

        return rows

    def add_table(self, table_text):
        """Add a table to the document"""
        try:
            rows = self.parse_table(table_text)
            if not rows:
                return

            # Create table
            table = self.doc.add_table(rows=len(rows), cols=len(rows[0]))
            table.style = 'Table Grid'

            # Fill table
            for i, row in enumerate(rows):
                for j, cell in enumerate(row):
                    table.cell(i, j).text = cell.strip()

                    # Format header row
                    if i == 0:
                        paragraph = table.cell(i, j).paragraphs[0]
                        run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
                        run.bold = True

            self.doc.add_paragraph()  # Add spacing after table

        except Exception as e:
            logger.error(f"Error adding table: {str(e)}")

    def add_section(self, title, content):
        """Add a section to the protocol document"""
        content = self.clean_text(content)

        # Add section title
        self.doc.add_heading(title.strip('#').strip(), level=1)

        # Process content by paragraphs
        paragraphs = content.split('\n\n')

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Handle tables
            if '|' in para and '-|-' in para:
                self.add_table(para)
                continue

            # Handle headings
            if para.startswith('#'):
                level = len(re.match(r'^#+', para).group())
                text = para.lstrip('#').strip()
                self.doc.add_heading(text, level=min(level, 3))
                continue

            # Handle bullet points
            if para.startswith('- '):
                for line in para.split('\n'):
                    if line.strip():
                        self.doc.add_paragraph(line.strip('- ').strip(), style='List Bullet')
                continue

            # Handle numbered lists
            if re.match(r'^\d+\.', para):
                for line in para.split('\n'):
                    if line.strip():
                        self.doc.add_paragraph(line.strip(), style='List Number')
                continue

            # Regular paragraph
            self.doc.add_paragraph(para)

    def format_protocol(self, sections):
        """Format complete protocol document"""
        # Order sections
        section_order = [
            'background',
            'objectives',
            'study_design',
            'population',
            'procedures',
            'statistical',
            'safety'
        ]

        # Add sections in order
        for section_name in section_order:
            if section_name in sections:
                self.add_section(
                    section_name.replace('_', ' ').title(),
                    sections[section_name]
                )

        return self.doc

    def save_document(self, filename, format='docx'):
        """Save the document in specified format"""
        try:
            # Save as DOCX
            docx_filename = filename if filename.endswith('.docx') else f"{filename}.docx"
            self.doc.save(docx_filename)

            # Convert to PDF if requested
            if format.lower() == 'pdf':
                pdf_filename = filename if filename.endswith('.pdf') else f"{filename}.pdf"
                convert(docx_filename, pdf_filename)
                return pdf_filename

            return docx_filename

        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise