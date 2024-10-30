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
        self.content_for_pdf = []
        self.setup_custom_styles()
        self.setup_document()

    def setup_custom_styles(self):
        """Set up custom document styles"""
        styles = {
            'CustomTitle': {'name': 'Protocol Title', 'size': 24, 'bold': True, 'align': 'CENTER'},
            'CustomHeading1': {'name': 'Section Title', 'size': 16, 'bold': True},
            'CustomHeading2': {'name': 'Subsection Title', 'size': 14, 'bold': True},
            'CustomHeading3': {'name': 'Sub-subsection Title', 'size': 12, 'bold': True},
            'BodyText': {'name': 'Body Text', 'size': 11},
            'TableText': {'name': 'Table Text', 'size': 10},
            'TableHeader': {'name': 'Table Header', 'size': 10, 'bold': True},
            'Caption': {'name': 'Figure Caption', 'size': 10, 'italic': True},
            'Reference': {'name': 'Reference Text', 'size': 10},
            'ListBullet': {'name': 'List Bullet', 'size': 11},
            'ListNumber': {'name': 'List Number', 'size': 11}
        }

        for style_name, props in styles.items():
            if style_name not in self.doc.styles:
                style = self.doc.styles.add_style(style_name, 1)
                font = style.font
                font.name = 'Arial'
                font.size = Pt(props['size'])
                font.bold = props.get('bold', False)
                font.italic = props.get('italic', False)
                
                para_format = style.paragraph_format
                para_format.space_before = Pt(6)
                para_format.space_after = Pt(6)
                para_format.line_spacing = 1.15
                
                if props.get('align') == 'CENTER':
                    para_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def setup_document(self):
        """Initialize document settings"""
        # Set margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Add title page using custom style
        title = self.doc.add_paragraph('Clinical Trial Protocol')
        title.style = self.doc.styles['CustomTitle']

    def add_mermaid_diagram(self, mermaid_code):
        """Convert Mermaid code to SVG and add to document"""
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

    def format_protocol(self, sections):
        """Format complete protocol with timing information"""
        try:
            start_time = datetime.now()
            for section_name, content in sections.items():
                if content:
                    title = section_name.replace('_', ' ').title()
                    section_start_time = datetime.now()
                    self.add_section(title, content)
                    section_duration = (datetime.now() - section_start_time).total_seconds()
                    logger.info(f"Formatted section {title} in {section_duration:.2f} seconds")
            
            total_duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Total protocol formatting time: {total_duration:.2f} seconds")
            return self.doc
            
        except Exception as e:
            logger.error(f"Error formatting protocol: {str(e)}")
            raise

    def add_section(self, title, content):
        """Add formatted section with timing information"""
        start_time = datetime.now()
        try:
            # Clean content
            content = self.clean_text(content)
            
            # Add section title using custom style
            heading = self.doc.add_paragraph(title)
            heading.style = self.doc.styles['CustomHeading1']
            self.content_for_pdf.append(('heading1', title))

            # Process content
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if not para.strip():
                    continue

                # Process different content types with appropriate styling
                if '```mermaid' in para:
                    mermaid_match = re.search(r'```mermaid\n(.*?)\n```', para, re.DOTALL)
                    if mermaid_match:
                        self.add_mermaid_diagram(mermaid_match.group(1))
                    continue

                # Handle lists with custom styles
                if re.match(r'^\s*[-*]\s', para):
                    items = [line.strip('- *').strip() for line in para.split('\n') if line.strip()]
                    for item in items:
                        p = self.doc.add_paragraph(style='ListBullet')
                        p.add_run(item)
                    continue

                if re.match(r'^\s*\d+\.\s', para):
                    items = [line.strip().split('. ', 1)[1] for line in para.split('\n') if re.match(r'^\s*\d+\.\s', line)]
                    for item in items:
                        p = self.doc.add_paragraph(style='ListNumber')
                        p.add_run(item)
                    continue

                # Regular paragraphs with body text style
                p = self.doc.add_paragraph(para.strip(), style='BodyText')
                self.content_for_pdf.append(('paragraph', para))

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Generated section {title} in {duration:.2f} seconds")

        except Exception as e:
            logger.error(f"Error generating section {title}: {str(e)}")
            raise

    def _generate_docx(self, filename):
        """Generate DOCX document with timing"""
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
        """Generate PDF with timing"""
        try:
            start_time = datetime.now()
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Add fonts
            pdf.add_font('Arial', '', None, uni=True)
            pdf.set_font('Arial', '', 11)
            
            # Process content with custom styles
            for content_type, content in self.content_for_pdf:
                if content_type == 'heading1':
                    pdf.set_font('Arial', 'B', 16)
                    pdf.ln(10)
                    pdf.cell(0, 10, content, ln=True)
                    pdf.set_font('Arial', '', 11)
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

    def save_document(self, fname, format='docx'):
        """Save document in specified format"""
        try:
            if not fname:
                raise ValueError("Filename is required")

            if format.lower() == 'pdf':
                return self._generate_pdf(fname)
            else:
                return self._generate_docx(fname)

        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise

    def clean_text(self, text):
        """Clean text content"""
        if not isinstance(text, str):
            return ""
        
        # Remove escape characters and clean formatting
        text = text.replace('\\', '')
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'#{1,6}\s*', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
