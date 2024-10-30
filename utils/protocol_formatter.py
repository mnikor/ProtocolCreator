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

class ProtocolPostProcessor:
    def __init__(self):
        self.section_numbers = {}
        self.current_section = None

    def post_process_document(self, doc):
        """Post-process the document content"""
        # Process each paragraph in the document
        current_numbers = [0] * 6  # For heading levels 1-6
        prev_level = 0
        
        for para in doc.paragraphs:
            # Fix heading hierarchy and numbering
            if para.style.name.startswith(('Heading', 'Title')):
                level = int(para.style.name[-1]) if para.style.name != 'Title' else 0
                
                # Reset lower level numbers
                for i in range(level + 1, 6):
                    current_numbers[i] = 0
                    
                # Increment current level
                current_numbers[level] += 1
                
                # Generate section number (skip for Title)
                if level > 0:
                    number = '.'.join(str(n) for n in current_numbers[:level + 1] if n > 0)
                    para.text = f"{number} {para.text.strip()}"

            # Fix list numbering
            elif para.style.name == 'List Number':
                if not para.text.strip().startswith(('1.', '2.', '3.')):
                    para.text = f"• {para.text.strip()}"

        # Fix table formatting
        for table in doc.tables:
            table.style = 'Table Grid'
            # Apply consistent formatting to header row
            if len(table.rows) > 0:
                header_row = table.rows[0]
                for cell in header_row.cells:
                    for paragraph in cell.paragraphs:
                        paragraph.style = doc.styles['Heading3']

        return doc

    def _fix_mermaid_diagrams(self, content):
        """Convert Mermaid diagrams to images"""
        mermaid_pattern = r'```mermaid\n(.*?)\n```'
        diagrams = re.finditer(mermaid_pattern, content, re.DOTALL)
        
        for i, match in enumerate(diagrams):
            try:
                diagram_code = match.group(1)
                dot = graphviz.Source(diagram_code)
                image_path = f'diagram_{i}'
                dot.render(image_path, format='png', cleanup=True)
                
                # Replace the Mermaid code with an image reference
                content = content.replace(
                    match.group(0),
                    f'![Study Design Diagram]({image_path}.png)'
                )
            except Exception as e:
                logger.error(f"Error processing Mermaid diagram: {str(e)}")
                
        return content

class ProtocolFormatter:
    def __init__(self):
        self.doc = Document()
        self._setup_document()
        self._setup_styles()
        self.post_processor = ProtocolPostProcessor()

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
            'Normal': {'name': 'Body Text', 'size': 11},
            'List Number': {'name': 'List Text', 'size': 11}
        }

        for style_name, props in styles.items():
            style = self.doc.styles[style_name]
            font = style.font
            font.name = 'Arial'
            font.size = Pt(props['size'])
            font.bold = props.get('bold', False)
            
            para_format = style.paragraph_format
            para_format.space_before = Pt(6)
            para_format.space_after = Pt(6)
            para_format.line_spacing = 1.15
            
            if props.get('align'):
                para_format.alignment = props['align']

    def _process_markdown(self, content):
        """Process markdown content into document elements"""
        if not content:
            return
        
        # Pre-process Mermaid diagrams
        content = self.post_processor._fix_mermaid_diagrams(content)
        
        # Process content by paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Handle headings
            if para.startswith('#'):
                level = len(para.split()[0].strip('#'))
                text = para.lstrip('#').strip()
                self.doc.add_heading(text, level=level)
                continue

            # Handle lists
            if para.startswith(('- ', '* ', '1. ')):
                lines = para.split('\n')
                for line in lines:
                    line = line.lstrip('- *1234567890. ')
                    p = self.doc.add_paragraph(style='List Number')
                    p.add_run(line)
                continue

            # Handle tables
            if para.startswith('|'):
                rows = [
                    [cell.strip() for cell in row.strip('|').split('|')]
                    for row in para.split('\n')
                    if '|' in row and not row.strip('| -').isspace()
                ]
                if rows:
                    table = self.doc.add_table(rows=len(rows), cols=len(rows[0]))
                    table.style = 'Table Grid'
                    for i, row in enumerate(rows):
                        for j, cell in enumerate(row):
                            table.cell(i, j).text = cell
                continue

            # Handle regular paragraphs
            self.doc.add_paragraph(para)

    def format_protocol(self, sections):
        """Format complete protocol document"""
        try:
            # Add title page
            self.doc.add_heading('Clinical Trial Protocol', 0)
            self.doc.add_page_break()

            # Add table of contents
            self.doc.add_heading('Table of Contents', 1)
            self.doc.add_paragraph('Contents will be generated automatically')
            self.doc.add_page_break()

            # Process each section
            for section_name, content in sections.items():
                title = section_name.replace('_', ' ').title()
                self.doc.add_heading(title, 1)
                self._process_markdown(content)
                self.doc.add_page_break()

            # Apply post-processing
            self.doc = self.post_processor.post_process_document(self.doc)

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
                # Convert to PDF using libreoffice
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
