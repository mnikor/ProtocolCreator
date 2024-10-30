from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from fpdf import FPDF
import re
import html
from bs4 import BeautifulSoup
import logging
import io
import os
from PIL import Image
import graphviz
from datetime import datetime

logger = logging.getLogger(__name__)

class ProtocolFormatter:
    def __init__(self):
        self.doc = Document()
        self.setup_document()
        self.content_for_pdf = []

    def setup_document(self):
        # Set up document styles
        style = self.doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(11)
        
        # Set margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
        
        # Add title page
        title = self.doc.add_heading('Clinical Trial Protocol', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_mermaid_diagram(self, mermaid_code):
        '''Convert Mermaid code to SVG and add to document'''
        try:
            if not mermaid_code or not isinstance(mermaid_code, str):
                logger.warning("Invalid or empty Mermaid code")
                return

            # Convert Mermaid to DOT format using graphviz
            dot = graphviz.Source(mermaid_code)
            
            # Save as temporary SVG
            svg_path = "temp_diagram.svg"
            dot.render(svg_path, format='svg')
            
            # Add to document
            self.doc.add_picture(svg_path)
            
            # Clean up temporary files
            if os.path.exists(svg_path):
                os.remove(svg_path)
            if os.path.exists(svg_path + '.svg'):
                os.remove(svg_path + '.svg')
                
        except Exception as e:
            logger.error(f"Error adding Mermaid diagram: {str(e)}")

    def markdown_to_html_table(self, markdown_table):
        """Convert markdown table to HTML"""
        try:
            lines = [line.strip() for line in markdown_table.split('\n') if line.strip()]
            if len(lines) < 3:
                return None

            # Process header
            header = [cell.strip() for cell in lines[0].strip('|').split('|')]

            # Skip separator line
            data_rows = []
            for line in lines[2:]:  # Skip header and separator
                if not all(c in '|-' for c in line):  # Skip separator rows
                    row = [cell.strip() for cell in line.strip('|').split('|')]
                    data_rows.append(row)

            # Create HTML table
            html_table = ['<table style="width:100%; border-collapse: collapse; margin: 10px 0;">']

            # Add header
            html_table.append('<thead>')
            html_table.append('<tr>')
            for cell in header:
                html_table.append(f'<th style="background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;">{html.escape(cell)}</th>')
            html_table.append('</tr>')
            html_table.append('</thead>')

            # Add body
            html_table.append('<tbody>')
            for row in data_rows:
                html_table.append('<tr>')
                for cell in row:
                    html_table.append(f'<td style="border: 1px solid #ddd; padding: 8px;">{html.escape(cell)}</td>')
                html_table.append('</tr>')
            html_table.append('</tbody>')
            html_table.append('</table>')

            return '\n'.join(html_table)

        except Exception as e:
            logger.error(f"Error converting table to HTML: {str(e)}")
            return None

    def insert_html_table(self, html_table):
        """Insert HTML table into Word document"""
        try:
            # Parse HTML
            soup = BeautifulSoup(html_table, 'html.parser')

            # Create Word table
            rows = soup.find_all('tr')
            if not rows:
                return None
            
            cols = len(rows[0].find_all(['th', 'td']))
            if cols == 0:
                return None

            table = self.doc.add_table(rows=len(rows), cols=cols)
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            # Process rows
            for i, row in enumerate(rows):
                cells = row.find_all(['th', 'td'])
                for j, cell in enumerate(cells):
                    # Get cell and paragraph
                    word_cell = table.cell(i, j)
                    paragraph = word_cell.paragraphs[0]

                    # Set cell text
                    run = paragraph.add_run(cell.get_text())

                    # Format header cells
                    if cell.name == 'th':
                        run.bold = True
                        word_cell._tc.get_or_add_tcPr().append(parse_xml(f'''
                            <w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" 
                                  w:fill="F2F2F2"/>
                        '''))

                    # Set alignment
                    paragraph.alignment = WD_TABLE_ALIGNMENT.LEFT

            # Add spacing after table
            self.doc.add_paragraph()
            return table

        except Exception as e:
            logger.error(f"Error inserting HTML table: {str(e)}")
            return None

    def clean_text(self, text):
        """Clean text content"""
        if not isinstance(text, str):
            return ""
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Clean markdown-style headers
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        
        return text.strip()

    def add_section(self, title, content):
        """Add formatted section to document"""
        start_time = datetime.now()
        try:
            # Clean content
            content = self.clean_text(content)

            # Add section title
            self.doc.add_heading(title.strip('#').strip(), level=1)
            
            # Store for PDF
            self.content_for_pdf.append(('heading1', title.strip('#').strip()))

            # Process Mermaid diagrams
            mermaid_matches = re.finditer(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
            for match in mermaid_matches:
                mermaid_code = match.group(1)
                self.add_mermaid_diagram(mermaid_code)
                content = content.replace(match.group(0), '')  # Remove Mermaid code

            # Process content by paragraphs
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if not para.strip():
                    continue

                # Handle tables
                if '|' in para and '-|-' in para:
                    html_table = self.markdown_to_html_table(para)
                    if html_table:
                        self.insert_html_table(html_table)
                    continue

                # Handle lists
                if para.strip().startswith(('- ', '* ', '1. ')):
                    lines = para.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith(('- ', '* ')):
                            p = self.doc.add_paragraph(line[2:], style='List Bullet')
                            self.content_for_pdf.append(('bullet', line[2:]))
                        elif re.match(r'^\d+\.\s', line):
                            p = self.doc.add_paragraph(line, style='List Number')
                            self.content_for_pdf.append(('number', line))
                    continue

                # Regular paragraph
                self.doc.add_paragraph(para)
                self.content_for_pdf.append(('paragraph', para))

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Generated section {title} in {duration:.2f} seconds")

        except Exception as e:
            logger.error(f"Error generating section {title}: {str(e)}")
            raise

    def format_protocol(self, sections):
        """Format complete protocol"""
        try:
            total_start_time = datetime.now()
            for section_name, content in sections.items():
                if content:
                    title = section_name.replace('_', ' ').title()
                    self.add_section(title, content)
            total_end_time = datetime.now()
            total_duration = (total_end_time - total_start_time).total_seconds()
            logger.info(f"Total protocol formatting time: {total_duration:.2f} seconds")
            return self.doc
        except Exception as e:
            logger.error(f"Error formatting protocol: {str(e)}")
            raise

    def save_document(self, fname, format='docx'):
        """Save document in specified format"""
        try:
            if not fname:
                raise ValueError('"fname" parameter is required')
                
            if format.lower() == 'pdf':
                return self._generate_pdf(fname)
            else:
                return self._generate_docx(fname)
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise

    def _generate_docx(self, filename):
        """Generate DOCX document"""
        try:
            start_time = datetime.now()
            output_file = f"{filename}.docx"
            self.doc.save(output_file)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Generated DOCX document in {duration:.2f} seconds: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error generating DOCX: {str(e)}")
            raise

    def _generate_pdf(self, filename):
        """Generate PDF using FPDF"""
        try:
            start_time = datetime.now()
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # Set up fonts
            pdf.add_font('Arial', '', None, uni=True)
            pdf.set_font('Arial', '', 11)

            # Process content
            for content_type, content in self.content_for_pdf:
                if content_type == 'heading1':
                    pdf.set_font('Arial', 'B', 16)
                    pdf.ln(10)
                    pdf.cell(0, 10, content, ln=True)
                    pdf.set_font('Arial', '', 11)
                elif content_type == 'heading2':
                    pdf.set_font('Arial', 'B', 14)
                    pdf.ln(5)
                    pdf.cell(0, 10, content, ln=True)
                    pdf.set_font('Arial', '', 11)
                elif content_type == 'bullet':
                    pdf.cell(10, 10, '•', ln=0)
                    pdf.multi_cell(0, 10, content)
                elif content_type == 'number':
                    pdf.multi_cell(0, 10, content)
                else:
                    pdf.multi_cell(0, 10, content)
                    pdf.ln(5)

            output_file = f"{filename}.pdf"
            pdf.output(output_file)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Generated PDF document in {duration:.2f} seconds: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
