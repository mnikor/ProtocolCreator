import streamlit as st
import logging
from utils.template_section_generator import TemplateSectionGenerator
from utils.pdf_generator import ProtocolPDFGenerator
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import time

logger = logging.getLogger(__name__)

def render_navigator():
    '''Render the protocol navigation interface'''
    try:
        # Add download options if sections are generated
        if generated_sections := st.session_state.get('generated_sections'):
            st.sidebar.markdown('### 📥 Download Protocol')
            
            try:
                # Generate DOCX
                docx_bytes = generate_docx(generated_sections)
                
                # Generate PDF
                pdf_bytes = generate_pdf(generated_sections)
                
                # Add download buttons
                col1, col2 = st.sidebar.columns(2)
                
                with col1:
                    st.download_button(
                        label='📄 DOCX',
                        data=docx_bytes,
                        file_name='protocol.docx',
                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        use_container_width=True
                    )
                
                with col2:
                    st.download_button(
                        label='📑 PDF',
                        data=pdf_bytes,
                        file_name='protocol.pdf',
                        mime='application/pdf',
                        use_container_width=True
                    )
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f'Error creating documents: {error_msg}')
                st.sidebar.error(f'Error creating documents: {error_msg}')
    
    except Exception as e:
        logger.error(f'Error in navigator: {str(e)}')
        st.error(f'An error occurred while rendering the navigator: {str(e)}')

def generate_docx(sections):
    '''Generate DOCX document'''
    docx_bytes = BytesIO()
    
    # Generate DOCX
    doc = Document()
    
    # Add title
    title = doc.add_heading('Study Protocol', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add date
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_para.add_run(f'Generated: {time.strftime("%B %d, %Y")}')
    
    # Add sections
    for section_name, content in sections.items():
        # Add section heading
        doc.add_heading(section_name.replace('_', ' ').title(), level=1)
        
        # Process content parts
        if '```mermaid' in content:
            parts = content.split('```mermaid')
            
            # Add first part (text before mermaid diagram)
            if parts[0].strip():
                add_text_with_formatting(doc, parts[0])
            
            # Process mermaid diagrams and remaining text
            for i, part in enumerate(parts[1:], 1):
                # Find end of mermaid section
                diagram_end = part.find('```')
                if diagram_end != -1:
                    # Add diagram as text
                    diagram_code = part[:diagram_end].strip()
                    diagram_para = doc.add_paragraph()
                    diagram_para.add_run('Study Flow Diagram:').bold = True
                    doc.add_paragraph(diagram_code)
                    
                    # Add remaining text
                    remaining_text = part[diagram_end + 3:].strip()
                    if remaining_text:
                        add_text_with_formatting(doc, remaining_text)
        else:
            # No diagram, just add text content
            add_text_with_formatting(doc, content)
    
    # Save document
    doc.save(docx_bytes)
    docx_bytes.seek(0)
    return docx_bytes

def generate_pdf(sections):
    '''Generate PDF document'''
    try:
        pdf_generator = ProtocolPDFGenerator()
        return pdf_generator.generate_pdf(sections)
    except Exception as e:
        logger.error(f'Error generating PDF: {str(e)}')
        raise

def add_text_with_formatting(doc, text):
    '''Add text to document with proper formatting'''
    for para in text.split('\n'):
        if para.strip():
            p = doc.add_paragraph()
            parts = para.split('*')
            for i, part in enumerate(parts):
                if part.strip():
                    run = p.add_run(part.strip())
                    if i % 2:  # Odd indices are italic
                        run.italic = True
