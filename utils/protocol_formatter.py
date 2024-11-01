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

    def format_protocol(self, sections):
        """Format complete protocol document with post-processing"""
        try:
            # Combine all sections first
            combined_content = self._combine_sections(sections)
            
            # Post-process the combined content
            processed_content = self._post_process_content(combined_content)
            
            # Format into document
            self._format_into_document(processed_content)
            
            return self.doc
            
        except Exception as e:
            logger.error(f"Error formatting protocol: {str(e)}")
            raise

    def _combine_sections(self, sections):
        """Combine all sections with proper numbering"""
        combined = []
        section_number = 1
        
        for section_name, content in sections.items():
            # Add section heading with number
            heading = f"{section_number}. {section_name.replace('_', ' ').title()}"
            combined.append(heading)
            
            # Process subsections
            subsections = content.split('\n\n')
            subsection_number = 1
            for subsection in subsections:
                if subsection.strip():
                    # Check if it's a subsection heading
                    if ':' in subsection and len(subsection.split(':')[0]) < 50:
                        # Add subsection number
                        sub_heading = f"{section_number}.{subsection_number}. {subsection.split(':')[0]}"
                        combined.append(sub_heading)
                        combined.append(':'.join(subsection.split(':')[1:]))
                        subsection_number += 1
                    else:
                        combined.append(subsection)
                        
            section_number += 1
            combined.append('')  # Add separator
            
        return '\n\n'.join(combined)

    def _post_process_content(self, content):
        """Clean up and format content"""
        # Clean up formatting
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)
        
        # Fix list numbering
        content = re.sub(r'^\d+\.\s*', '', content, flags=re.MULTILINE)
        
        return content

    def _format_into_document(self, content):
        """Format content into document with proper styles"""
        # Add title page
        title = self.doc.add_paragraph('Clinical Trial Protocol')
        title.style = self.doc.styles['CustomTitle']
        
        # Add content with proper styles
        current_section = None
        for paragraph in content.split('\n\n'):
            if not paragraph.strip():
                continue
                
            # Detect heading levels
            if re.match(r'^\d+\.\s', paragraph):
                # Main section heading
                p = self.doc.add_paragraph(paragraph)
                p.style = self.doc.styles['CustomHeading1']
            elif re.match(r'^\d+\.\d+\.\s', paragraph):
                # Subsection heading
                p = self.doc.add_paragraph(paragraph)
                p.style = self.doc.styles['CustomHeading2']
            else:
                # Regular content
                p = self.doc.add_paragraph(paragraph)
                p.style = self.doc.styles['BodyText']

    def save_document(self, filename, format='docx'):
        """Save document in specified format"""
        try:
            if format.lower() == 'pdf':
                docx_path = f"{filename}.docx"
                pdf_path = f"{filename}.pdf"
                
                # Save as DOCX first
                self.doc.save(docx_path)
                
                # Convert to PDF using libreoffice
                os.system(f"libreoffice --headless --convert-to pdf {docx_path}")
                
                # Check if conversion was successful
                if os.path.exists(pdf_path):
                    os.remove(docx_path)  # Clean up DOCX
                    return pdf_path
                else:
                    raise Exception("PDF conversion failed")
                    
            else:  # DOCX format
                docx_path = f"{filename}.docx"
                self.doc.save(docx_path)
                return docx_path
                
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise
