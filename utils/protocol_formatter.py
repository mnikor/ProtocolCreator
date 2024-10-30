from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import logging

logger = logging.getLogger(__name__)

class ProtocolFormatter:
    def __init__(self):
        self.doc = Document()
        self.setup_document()
        self.content_for_pdf = []  # Store content for PDF generation

    def setup_document(self):
        """Setup document styles"""
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

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
        text = text.replace('\\', '').strip()
        text = re.sub(r'# (\w+)\s+# \1', r'# \1', text)
        text = re.sub(r'\\\#', '#', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        return text

    def add_section(self, title, content):
        """Add a section to both Word and PDF content"""
        content = self.clean_text(content)

        # Add to Word document
        self.doc.add_heading(title.strip('#').strip(), level=1)
        self.content_for_pdf.append(('heading1', title.strip('#').strip()))

        paragraphs = content.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Handle headings
            if para.startswith('##'):
                text = para.lstrip('#').strip()
                self.doc.add_heading(text, level=2)
                self.content_for_pdf.append(('heading2', text))
                continue

            # Handle bullet points
            if para.startswith('- '):
                for line in para.split('\n'):
                    if line.strip():
                        self.doc.add_paragraph(line.strip('- ').strip(), style='List Bullet')
                        self.content_for_pdf.append(('bullet', line.strip('- ').strip()))
                continue

            # Handle numbered lists
            if re.match(r'^\d+\.', para):
                for line in para.split('\n'):
                    if line.strip():
                        self.doc.add_paragraph(line.strip(), style='List Number')
                        self.content_for_pdf.append(('number', line.strip()))
                continue

            # Regular paragraph
            self.doc.add_paragraph(para)
            self.content_for_pdf.append(('para', para))

    def format_protocol(self, sections):
        """Format protocol document"""
        section_order = [
            'background',
            'objectives',
            'study_design',
            'population',
            'procedures',
            'statistical',
            'safety'
        ]

        for section_name in section_order:
            if section_name in sections:
                self.add_section(
                    section_name.replace('_', ' ').title(),
                    sections[section_name]
                )

        return self.doc

    def save_document(self, filename, format='docx'):
        """Save document in specified format"""
        try:
            # Save DOCX
            docx_filename = filename if filename.endswith('.docx') else f"{filename}.docx"
            self.doc.save(docx_filename)

            # Generate PDF if requested
            if format.lower() == 'pdf':
                pdf_filename = filename if filename.endswith('.pdf') else f"{filename}.pdf"
                self._generate_pdf(pdf_filename)
                return pdf_filename

            return docx_filename

        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise

    def _generate_pdf(self, filename):
        """Generate PDF using reportlab"""
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Add custom styles
            styles.add(ParagraphStyle(
                name='Heading1',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=12
            ))
            styles.add(ParagraphStyle(
                name='Heading2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=6
            ))

            for content_type, content in self.content_for_pdf:
                if content_type == 'heading1':
                    story.append(Paragraph(content, styles['Heading1']))
                    story.append(Spacer(1, 12))
                elif content_type == 'heading2':
                    story.append(Paragraph(content, styles['Heading2']))
                    story.append(Spacer(1, 6))
                elif content_type == 'bullet':
                    story.append(Paragraph(f"• {content}", styles['Normal']))
                elif content_type == 'number':
                    story.append(Paragraph(content, styles['Normal']))
                else:
                    story.append(Paragraph(content, styles['Normal']))
                    story.append(Spacer(1, 6))

            doc.build(story)

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise