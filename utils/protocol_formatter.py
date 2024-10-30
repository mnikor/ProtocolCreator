import logging
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from bs4 import BeautifulSoup
import re
import os
from weasyprint import HTML
from htmldocx import HtmlToDocx
import graphviz

logger = logging.getLogger(__name__)

class ProtocolFormatter:
    def __init__(self):
        self.html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 1in;
                    color: #333;
                }

                /* Headings */
                h1 {
                    font-size: 24px;
                    text-align: center;
                    margin: 24px 0;
                    color: #000;
                    page-break-before: always;
                }
                h1:first-of-type {
                    page-break-before: avoid;
                }
                h2 {
                    font-size: 16px;
                    margin: 20px 0 10px 0;
                    color: #000;
                }
                h3 {
                    font-size: 14px;
                    margin: 16px 0 8px 0;
                    color: #222;
                }

                /* Paragraphs */
                p {
                    font-size: 11px;
                    margin: 6px 0;
                    text-align: justify;
                }

                /* Tables */
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                    font-size: 10px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                    vertical-align: top;
                }
                th {
                    background-color: #f2f2f2;
                    font-weight: bold;
                    text-align: center;
                }

                /* Lists */
                ul, ol {
                    margin: 6px 0 6px 20px;
                    padding-left: 20px;
                }
                li {
                    font-size: 11px;
                    margin: 4px 0;
                    padding-left: 4px;
                }

                /* Images */
                img {
                    max-width: 100%;
                    height: auto;
                    margin: 10px auto;
                    display: block;
                }

                /* Page breaks */
                .page-break {
                    page-break-after: always;
                }

                /* Special sections */
                .cover-page {
                    text-align: center;
                    margin-top: 3in;
                }
                .cover-page h1 {
                    font-size: 28px;
                    margin-bottom: 48px;
                }

                /* Tables of contents */
                .toc {
                    margin: 20px 0;
                }
                .toc a {
                    text-decoration: none;
                    color: #000;
                }
                .toc-entry {
                    margin: 4px 0;
                    display: flex;
                    justify-content: space-between;
                }
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        self.content_sections = []

    def clean_text(self, text):
        """Clean text content"""
        if not isinstance(text, str):
            return ""

        # Remove escape characters
        text = text.replace('\\', '')

        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)

        # Fix multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Fix spacing around lists
        text = re.sub(r'(?<=\w)\n(?=[1-9]\.|\-|\*)', '\n\n', text)

        return text.strip()

    def convert_markdown_to_html(self, content):
        """Convert markdown content to HTML"""
        html_parts = []
        content = self.clean_text(content)

        paragraphs = content.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Handle different content types
            if para.startswith('|'):  # Table
                html_parts.append(self._convert_table(para))
            elif para.startswith('#'):  # Heading
                html_parts.append(self._convert_heading(para))
            elif para.startswith(('- ', '* ')):  # Bullet list
                html_parts.append(self._convert_list(para, ordered=False))
            elif re.match(r'^\d+\.', para):  # Numbered list
                html_parts.append(self._convert_list(para, ordered=True))
            elif '```mermaid' in para:  # Mermaid diagram
                html_parts.append(self._convert_mermaid(para))
            else:  # Normal paragraph
                html_parts.append(f"<p>{para}</p>")

        return '\n'.join(html_parts)

    def _convert_table(self, table_text):
        """Convert markdown table to HTML table"""
        rows = [row.strip('|').split('|') for row in table_text.split('\n') 
               if '|' in row and not row.strip('| -').isspace()]

        if not rows:
            return ''

        html = ['<table>']

        # Add header
        html.append('<thead>')
        html.append('<tr>')
        for cell in rows[0]:
            html.append(f'<th>{cell.strip()}</th>')
        html.append('</tr>')
        html.append('</thead>')

        # Add body
        html.append('<tbody>')
        for row in rows[2:]:  # Skip header and separator
            html.append('<tr>')
            for cell in row:
                html.append(f'<td>{cell.strip()}</td>')
            html.append('</tr>')
        html.append('</tbody>')
        html.append('</table>')

        return '\n'.join(html)

    def _convert_list(self, list_text, ordered=False):
        """Convert markdown list to HTML list"""
        items = list_text.split('\n')
        tag = 'ol' if ordered else 'ul'

        html = [f'<{tag}>']
        for item in items:
            if ordered:
                item = re.sub(r'^\d+\.\s*', '', item)
            else:
                item = item.lstrip('- *')
            html.append(f'<li>{item.strip()}</li>')
        html.append(f'</{tag}>')

        return '\n'.join(html)

    def _convert_heading(self, heading_text):
        """Convert markdown heading to HTML heading"""
        level = len(heading_text.split()[0].strip('#'))
        text = heading_text.lstrip('#').strip()
        return f'<h{min(level+1, 6)}>{text}</h{min(level+1, 6)}>'

    def _convert_mermaid(self, mermaid_text):
        """Convert Mermaid diagram to SVG and embed in HTML"""
        try:
            # Extract Mermaid code
            mermaid_code = re.search(r'```mermaid\n(.*?)\n```', mermaid_text, re.DOTALL)
            if not mermaid_code:
                return ''

            # Generate SVG using graphviz
            dot = graphviz.Source(mermaid_code.group(1))
            svg_filename = 'temp_diagram'
            dot.render(svg_filename, format='svg')

            # Read SVG content
            with open(f'{svg_filename}.svg', 'r') as f:
                svg_content = f.read()

            # Clean up
            os.remove(f'{svg_filename}')
            os.remove(f'{svg_filename}.svg')

            return svg_content

        except Exception as e:
            logger.error(f"Error converting Mermaid diagram: {str(e)}")
            return ''

    def add_cover_page(self):
        """Add cover page to document"""
        cover = """
        <div class="cover-page">
            <h1>Clinical Trial Protocol</h1>
            <p class="protocol-id">{protocol_id}</p>
            <p class="protocol-title">{title}</p>
            <p class="date">{date}</p>
        </div>
        <div class="page-break"></div>
        """.format(
            protocol_id="Protocol ID: XXX-XXX",
            title="Study Title",
            date="Date: YYYY-MM-DD"
        )
        self.content_sections.insert(0, cover)

    def add_toc(self):
        """Add table of contents"""
        toc = ['<div class="toc"><h2>Table of Contents</h2>']
        for section in self.content_sections:
            soup = BeautifulSoup(section, 'html.parser')
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                level = int(heading.name[1])
                toc.append(
                    f'<div class="toc-entry" style="margin-left: {(level-1)*20}px">'
                    f'<span>{heading.text}</span>'
                    f'</div>'
                )
        toc.append('</div><div class="page-break"></div>')
        self.content_sections.insert(1, '\n'.join(toc))

    def format_protocol(self, sections):
        """Format complete protocol document"""
        try:
            # Add cover page
            self.add_cover_page()

            # Process each section
            for section_name, content in sections.items():
                title = section_name.replace('_', ' ').title()
                html_content = f'<h1>{title}</h1>\n'
                html_content += self.convert_markdown_to_html(content)
                self.content_sections.append(html_content)

            # Add table of contents
            self.add_toc()

            # Combine all sections
            complete_html = self.html_template.format(
                content='\n'.join(self.content_sections)
            )

            return complete_html

        except Exception as e:
            logger.error(f"Error formatting protocol: {str(e)}")
            raise

    def save_document(self, html_content, output_file, format='docx'):
        """Save document in specified format"""
        try:
            if format.lower() == 'pdf':
                HTML(string=html_content).write_pdf(
                    f"{output_file}.pdf",
                    stylesheets=[]
                )
                return f"{output_file}.pdf"
            else:
                converter = HtmlToDocx()
                doc = converter.parse_html_string(html_content)
                doc.save(f"{output_file}.docx")
                return f"{output_file}.docx"
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise