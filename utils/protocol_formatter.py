# protocol_formatter.py

import os
import logging
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

logger = logging.getLogger(__name__)

class ProtocolFormatter:
    def __init__(self):
        self.doc = Document()
        self.setup_document()
        self.setup_custom_styles()

        # Track section numbers and content hashes to avoid duplication
        self.section_numbers = {}
        self.content_hashes = set()

        # Define canonical section names and their numbers
        self.section_structure = {
            "title": {"number": "1", "title": "Protocol Title"},
            "background": {"number": "2", "title": "Background"},
            "objectives": {"number": "3", "title": "Objectives"},
            "study_design": {"number": "4", "title": "Study Design"},
            "population": {"number": "5", "title": "Study Population"},
            "procedures": {"number": "6", "title": "Study Procedures"},
            "statistical": {"number": "7", "title": "Statistical Analysis"},
            "safety": {"number": "8", "title": "Safety"}
        }

    def setup_document(self):
        """Initialize document settings"""
        # Set margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

    def setup_custom_styles(self):
        # Your existing style setup code...
        pass

    def _clean_content(self, content):
        """Clean and deduplicate content"""
        if not content:
            return ""

        # Split into paragraphs
        paragraphs = content.split('\n\n')
        cleaned_paragraphs = []
        seen_content = set()
        current_section = None

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Clean up section headings
            if re.match(r'^#+\s+|^\d+\.[\d\.]*\s+|^[A-Z][A-Z\s]+$', para):
                # Remove existing numbers and hashes
                cleaned_para = re.sub(r'^#+\s+|^\d+\.[\d\.]*\s+', '', para)
                # Store as current section
                current_section = cleaned_para.strip().lower()
                cleaned_paragraphs.append(cleaned_para)
            else:
                # Hash content (ignoring numbers) to detect duplicates
                content_hash = re.sub(r'\d+', '', para.lower())
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    cleaned_paragraphs.append(para)

        return '\n\n'.join(cleaned_paragraphs)

    def _format_section(self, section_name, content, parent_number):
        """Format a single section with proper numbering"""
        if not content:
            return

        section_info = self.section_structure.get(section_name)
        if not section_info:
            return

        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        subsection_number = 1
        current_level = 1

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if it's a heading
            if re.match(r'^#+\s+|^\d+\.[\d\.]*\s+|^[A-Z][A-Z\s]+$', para):
                # Clean up the heading text
                heading_text = re.sub(r'^#+\s+|^\d+\.[\d\.]*\s+', '', para)

                # Determine heading level
                if current_level == 1:
                    self.doc.add_heading(
                        f"{parent_number} {heading_text}",
                        level=1
                    )
                else:
                    self.doc.add_heading(
                        f"{parent_number}.{subsection_number} {heading_text}",
                        level=2
                    )
                    subsection_number += 1

            # Handle bullet points and numbered lists
            elif para.startswith('•') or para.startswith('-'):
                p = self.doc.add_paragraph(style='List Bullet')
                p.text = para.lstrip('•- ')
            elif re.match(r'^\d+\.\s', para):
                p = self.doc.add_paragraph(style='List Number')
                p.text = para
            else:
                # Regular paragraph
                p = self.doc.add_paragraph()
                p.text = para

    def format_protocol(self, sections):
        """Format complete protocol with proper structure"""
        try:
            # Add title page
            self.doc.add_heading("Clinical Trial Protocol", 0)
            self.doc.add_page_break()

            # Add table of contents
            self.doc.add_heading("Table of Contents", 1)
            self.doc.add_paragraph()  # Placeholder for TOC
            self.doc.add_page_break()

            # Process sections in order
            for section_name, section_info in self.section_structure.items():
                if section_name in sections:
                    # Clean and deduplicate content
                    content = self._clean_content(sections[section_name])

                    if content:
                        # Format section with proper numbering
                        self._format_section(
                            section_name,
                            content,
                            section_info["number"]
                        )

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

                # Save as DOCX first
                self.doc.save(docx_path)

                # Convert to PDF
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