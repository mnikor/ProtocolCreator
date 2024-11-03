import streamlit as st
import logging
from utils.template_section_generator import TemplateSectionGenerator
from utils.pdf_generator import ProtocolPDFGenerator
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import time
import re

logger = logging.getLogger(__name__)

def render_navigator():
    '''Render the protocol navigation interface'''
    try:
        # Initialize session state
        if 'synopsis_content' not in st.session_state:
            st.session_state.synopsis_content = None
        if 'study_type' not in st.session_state:
            st.session_state.study_type = None
        if 'generated_sections' not in st.session_state:
            st.session_state.generated_sections = {}
            
        # Show study information in sidebar
        if st.session_state.synopsis_content and st.session_state.study_type:
            st.sidebar.markdown("### 📋 Study Information")
            st.sidebar.info(f"Study Type: {st.session_state.study_type.replace('_', ' ').title()}")
            
            # Show generation progress
            if not st.session_state.generated_sections:
                st.sidebar.markdown("### 🚀 Generate Protocol")
                if st.sidebar.button("Generate Complete Protocol", type="primary", use_container_width=True):
                    with st.spinner("Generating protocol sections..."):
                        try:
                            # Get required sections for study type
                            from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS
                            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(st.session_state.study_type, {})
                            required_sections = study_config.get('required_sections', [])
                            
                            # Show progress for each section
                            progress_text = st.sidebar.empty()
                            progress_bar = st.sidebar.progress(0)
                            
                            # Generate protocol sections
                            generator = TemplateSectionGenerator()
                            result = {"sections": {}}
                            
                            for idx, section_name in enumerate(required_sections):
                                progress_text.text(f"Generating {section_name.replace('_', ' ').title()}...")
                                progress = (idx + 1) / len(required_sections)
                                progress_bar.progress(progress)
                                
                                section_content = generator.generate_section(
                                    section_name=section_name,
                                    synopsis_content=st.session_state.synopsis_content,
                                    study_type=st.session_state.study_type
                                )
                                if section_content:
                                    result["sections"][section_name] = section_content
                            
                            st.session_state.generated_sections = result["sections"]
                            progress_bar.empty()
                            progress_text.empty()
                            st.success("✅ Protocol sections generated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating protocol: {str(e)}")
            else:
                st.sidebar.markdown("### 📝 Generated Sections")
                for section in st.session_state.generated_sections.keys():
                    st.sidebar.markdown(f"✓ {section.replace('_', ' ').title()}")
        
            # Add download options if sections are generated
            if generated_sections := st.session_state.get('generated_sections'):
                st.sidebar.markdown('### 📥 Download Protocol')
                
                try:
                    # Generate both formats with progress indication
                    with st.spinner("Preparing documents..."):
                        # Generate DOCX
                        docx_bytes = generate_docx(generated_sections)
                        
                        # Generate PDF with improved styling
                        pdf_generator = ProtocolPDFGenerator()
                        pdf_bytes = pdf_generator.generate_pdf(generated_sections)
                    
                    # Add download buttons in columns
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
    '''Generate DOCX document with enhanced formatting'''
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
    
    # Add table of contents
    doc.add_heading('Table of Contents', level=1)
    for section_name in sections.keys():
        toc_para = doc.add_paragraph()
        toc_para.add_run(f'• {section_name.replace("_", " ").title()}')
    
    doc.add_page_break()
    
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
            for part in parts[1:]:
                # Find end of mermaid section
                diagram_end = part.find('```')
                if diagram_end != -1:
                    # Add diagram as text box
                    diagram_code = part[:diagram_end].strip()
                    diagram_para = doc.add_paragraph()
                    diagram_para.add_run('Study Flow Diagram:').bold = True
                    box_para = doc.add_paragraph()
                    box_para.add_run(diagram_code)
                    
                    # Add remaining text
                    remaining_text = part[diagram_end + 3:].strip()
                    if remaining_text:
                        add_text_with_formatting(doc, remaining_text)
        else:
            # No diagram, just add text content
            add_text_with_formatting(doc, content)
            
        # Add page break between sections
        doc.add_page_break()
    
    # Save document
    doc.save(docx_bytes)
    docx_bytes.seek(0)
    return docx_bytes

def add_text_with_formatting(doc, text):
    '''Add text to document with enhanced formatting'''
    # Handle HTML tables
    if '<table' in text:
        # Convert HTML tables to Word tables
        parts = text.split('<table')
        for i, part in enumerate(parts):
            if i == 0:
                if part.strip():
                    add_paragraphs_with_formatting(doc, part)
                continue
                
            table_end = part.find('</table>')
            if table_end != -1:
                table_html = '<table' + part[:table_end + 8]
                remaining_text = part[table_end + 8:]
                
                # Convert HTML table to Word table
                rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)
                if rows:
                    # Count columns from first row
                    first_row_cells = re.findall(r'<t[hd]>(.*?)</t[hd]>', rows[0])
                    table = doc.add_table(rows=len(rows), cols=len(first_row_cells))
                    table.style = 'Table Grid'
                    
                    # Fill table
                    for i, row in enumerate(rows):
                        cells = re.findall(r'<t[hd]>(.*?)</t[hd]>', row)
                        for j, cell_content in enumerate(cells):
                            # Clean and format cell content
                            clean_content = cell_content.strip()
                            table.cell(i, j).text = clean_content
                            
                            # Apply header formatting
                            if i == 0:
                                table.cell(i, j).paragraphs[0].runs[0].bold = True
                
                # Add remaining text
                if remaining_text.strip():
                    add_paragraphs_with_formatting(doc, remaining_text)
    else:
        add_paragraphs_with_formatting(doc, text)

def add_paragraphs_with_formatting(doc, text):
    '''Add paragraphs with italic formatting'''
    for para in text.split('\n'):
        if para.strip():
            p = doc.add_paragraph()
            parts = para.split('*')
            for i, part in enumerate(parts):
                if part.strip():
                    run = p.add_run(part.strip())
                    if i % 2:  # Odd indices are italic
                        run.italic = True
                        run.font.size = Pt(11)  # Set font size for italic text
                    else:
                        run.font.size = Pt(11)  # Set font size for regular text
