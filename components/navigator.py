import streamlit as st
import logging
from utils.template_section_generator import TemplateSectionGenerator
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
                    # Generate DOCX
                    with st.spinner("Preparing document..."):
                        docx_bytes = generate_docx(generated_sections)
                    
                    # Add download button
                    st.sidebar.download_button(
                        label='📄 Download DOCX',
                        data=docx_bytes,
                        file_name='protocol.docx',
                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        use_container_width=True
                    )
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f'Error creating document: {error_msg}')
                    st.sidebar.error(f'Error creating document: {error_msg}')
    
    except Exception as e:
        logger.error(f'Error in navigator: {str(e)}')
        st.error(f'An error occurred while rendering the navigator: {str(e)}')

def generate_docx(sections):
    '''Generate DOCX document with enhanced formatting'''
    docx_bytes = BytesIO()
    doc = Document()
    
    # Add title with proper encoding
    title = doc.add_heading('Study Protocol', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add date with proper encoding
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_para.add_run(time.strftime("%B %d, %Y"))
    
    # Add table of contents
    doc.add_heading('Table of Contents', level=1)
    for section_name in sections.keys():
        toc_para = doc.add_paragraph()
        toc_para.add_run(f'• {section_name.replace("_", " ").title()}')
    
    doc.add_page_break()
    
    # Add sections with proper encoding
    for section_name, content in sections.items():
        # Add section heading
        doc.add_heading(section_name.replace('_', ' ').title(), level=1)
        
        # Process content with proper encoding
        add_text_with_formatting(doc, content)
        doc.add_page_break()
    
    # Save document
    doc.save(docx_bytes)
    docx_bytes.seek(0)
    return docx_bytes.getvalue()

def add_text_with_formatting(doc, text):
    '''Add text to document with proper encoding'''
    try:
        # Convert text to string if it's bytes
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        
        # Replace special characters with ASCII equivalents
        replacements = {
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '•': '-',
            '–': '-',
            '—': '-',
            '…': '...',
            '°': ' degrees ',
            '±': '+/-',
            '×': 'x',
            '÷': '/',
            '≥': '>=',
            '≤': '<=',
            '≈': '~',
            '≠': '!='
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Handle HTML tables
        if '<table' in text:
            parts = text.split('<table')
            
            # Add text before first table
            if parts[0].strip():
                add_paragraphs_with_formatting(doc, parts[0])
            
            # Process each table
            for part in parts[1:]:
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
                                clean_content = cell_content.strip()
                                # Replace special characters in table cells
                                for old, new in replacements.items():
                                    clean_content = clean_content.replace(old, new)
                                table.cell(i, j).text = clean_content
                                if i == 0:
                                    table.cell(i, j).paragraphs[0].runs[0].bold = True
                    
                    # Add remaining text
                    if remaining_text.strip():
                        add_paragraphs_with_formatting(doc, remaining_text)
        else:
            add_paragraphs_with_formatting(doc, text)
    except Exception as e:
        logger.error(f"Error in add_text_with_formatting: {str(e)}")
        raise

def add_paragraphs_with_formatting(doc, text):
    '''Add paragraphs with proper encoding'''
    try:
        # Convert text to string if it's bytes
        if isinstance(text, bytes):
            text = text.decode('utf-8')
            
        # Split into paragraphs
        for para in text.split('\n'):
            if para.strip():
                p = doc.add_paragraph()
                # Handle italic formatting
                parts = para.split('*')
                for i, part in enumerate(parts):
                    if part.strip():
                        run = p.add_run(part.strip())
                        if i % 2:  # Odd indices are italic
                            run.italic = True
                        run.font.size = Pt(11)
    except Exception as e:
        logger.error(f"Error in add_paragraphs_with_formatting: {str(e)}")
        raise
