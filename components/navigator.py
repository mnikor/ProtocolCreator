import streamlit as st
import logging
import time
from utils.template_section_generator import TemplateSectionGenerator
from utils.synopsis_validator import SynopsisValidator
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
import os

logger = logging.getLogger(__name__)

def check_connection():
    """Check if application can establish necessary connections"""
    try:
        generator = TemplateSectionGenerator()
        return True
    except Exception as e:
        logger.error(f"Connection check failed: {str(e)}")
        return False

def create_docx(generated_sections):
    try:
        doc = Document()
        
        # Set up basic styles
        styles = doc.styles
        if 'TOC 1' not in styles:
            toc_style = styles.add_style('TOC 1', 1)
            toc_style.base_style = styles['Normal']
            font = toc_style.font
            font.size = Pt(12)
            font.name = 'Calibri'
        
        # Add title
        title = doc.add_heading('Study Protocol', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()
        
        # Add table of contents header
        doc.add_heading('Table of Contents', level=1)
        
        # Add TOC entries as regular paragraphs with indentation
        for section in generated_sections:
            p = doc.add_paragraph(style='TOC 1')
            p.paragraph_format.left_indent = Inches(0.25)
            p.add_run(section.replace('_', ' ').title())
        
        doc.add_page_break()
        
        # Add sections with proper formatting
        for section, content in generated_sections.items():
            # Add section heading
            heading = doc.add_heading(section.replace('_', ' ').title(), level=1)
            
            # Split content into paragraphs
            paragraphs = content.split('\n')
            for para in paragraphs:
                if para.strip():
                    p = doc.add_paragraph()
                    # Handle formatting markers
                    parts = para.split('*')
                    for i, part in enumerate(parts):
                        if part.strip():
                            run = p.add_run(part.strip())
                            run.font.name = 'Calibri'
                            run.font.size = Pt(11)
                            if i % 2:  # Odd indices are italic
                                run.italic = True
            
            # Add spacing between sections
            doc.add_paragraph()
        
        return doc
        
    except Exception as e:
        logger.error(f"Error creating DOCX: {str(e)}")
        raise Exception(f"Failed to create DOCX document: {str(e)}")

def create_pdf(generated_sections):
    try:
        pdf = FPDF()
        pdf.set_margins(20, 20, 20)  # Add margins
        
        # Set document properties
        pdf.set_title('Study Protocol')
        pdf.set_author('Protocol Development Assistant')
        
        # Add custom font for better unicode support
        pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', uni=True)
        pdf.add_font('DejaVu', 'I', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf', uni=True)
        
        # Title page
        pdf.add_page()
        pdf.set_font('DejaVu', 'B', 24)
        pdf.cell(0, 20, 'Study Protocol', align='C', ln=True)
        pdf.ln(20)
        
        # Add date
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 10, f'Generated: {time.strftime("%B %d, %Y")}', align='C', ln=True)
        
        # Table of contents
        pdf.add_page()
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, 'Table of Contents', ln=True)
        pdf.ln(5)
        
        # Track page numbers for TOC
        section_pages = {}
        current_page = pdf.page_no() + 1
        
        # Add TOC entries with page numbers and dots
        pdf.set_font('DejaVu', '', 12)
        for section in generated_sections:
            section_title = section.replace('_', ' ').title()
            section_pages[section] = current_page
            
            # Calculate dots
            title_width = pdf.get_string_width(section_title)
            page_num_width = pdf.get_string_width(str(current_page))
            dots_width = 170 - title_width - page_num_width
            num_dots = int(dots_width / pdf.get_string_width('.'))
            dots = '.' * num_dots
            
            # Print TOC line
            pdf.cell(0, 8, f'{section_title}{dots}{current_page}', ln=True)
            current_page += 1
        
        # Content pages
        for section, content in generated_sections.items():
            pdf.add_page()
            
            # Section heading
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, section.replace('_', ' ').title(), ln=True)
            pdf.ln(5)
            
            # Process content with careful text handling
            pdf.set_font('DejaVu', '', 11)
            
            # Split content into manageable chunks
            paragraphs = content.split('\n')
            for para in paragraphs:
                if para.strip():
                    # Handle italic markers
                    parts = para.split('*')
                    
                    # Calculate total width for proper text wrapping
                    text_width = 170  # Page width minus margins
                    
                    for i, part in enumerate(parts):
                        if part.strip():
                            # Toggle between normal and italic font
                            pdf.set_font('DejaVu', 'I' if i % 2 else '', 11)
                            
                            # Use multi_cell with fixed width for proper text wrapping
                            pdf.multi_cell(
                                w=text_width,
                                h=5,    # Line height
                                txt=part.strip(),
                                align='J'  # Justified text alignment
                            )
                    pdf.ln(3)
                else:
                    pdf.ln(5)
            
            pdf.ln(10)
        
        # Add page numbers
        total_pages = pdf.page_no()
        for page in range(1, total_pages + 1):
            pdf.page = page
            pdf.set_font('DejaVu', '', 10)
            pdf.set_y(-15)
            pdf.cell(0, 10, f'Page {page} of {total_pages}', align='C')
        
        return pdf
        
    except Exception as e:
        logger.error(f"Error creating PDF: {str(e)}")
        raise Exception(f"Failed to create PDF document: {str(e)}")

def render_navigator():
    """Render the section navigator with improved generation tracking"""
    try:
        # Add custom styling
        st.markdown("""
            <style>
            .section-status {
                font-size: 0.9em;
                color: #666;
                margin-top: 5px;
            }
            .progress-section {
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1rem;
            }
            .stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                height: 3em;
                border-radius: 10px;
                margin: 0.5em 0;
                width: 100%;
            }
            .disabled-button {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .download-buttons {
                display: flex;
                gap: 10px;
            }
            .download-buttons > div {
                flex: 1;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Initialize session state for progress tracking
        if 'generation_in_progress' not in st.session_state:
            st.session_state.generation_in_progress = False
            
        # Check connection
        if not check_connection():
            st.sidebar.error("⚠️ Connection issues detected. Please refresh the page.")
            return
            
        st.sidebar.markdown("## Protocol Development")
        
        # Study type detection and analysis
        if synopsis_content := st.session_state.get('synopsis_content'):
            validator = SynopsisValidator()
            validation_result = validator.validate_synopsis(synopsis_content)
            
            if validation_result:
                if study_type := validation_result.get('study_type'):
                    st.sidebar.success(f"📋 Study Type: {study_type.replace('_', ' ').title()}")
                    if study_type in ['phase1', 'phase2', 'phase3', 'phase4']:
                        st.sidebar.info(f"🔬 Clinical Trial Phase: {study_type[-1]}")
                else:
                    st.sidebar.warning("⚠️ Could not detect study type")
                    
                if therapeutic_area := validation_result.get('therapeutic_area'):
                    st.sidebar.info(f"🏥 Therapeutic Area: {therapeutic_area.replace('_', ' ').title()}")
                    
            # Section Navigation
            study_type = st.session_state.get('study_type')
            if study_type:
                st.sidebar.markdown("### 📑 Protocol Sections")
                
                study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
                sections = study_config.get('required_sections', [])
                
                # Progress tracking
                completed = sum(1 for section in sections 
                              if st.session_state.section_status.get(section, {}).get('status') == 'completed')
                total = len(sections)
                progress = completed / total if total > 0 else 0
                
                # Progress section
                with st.sidebar.container():
                    st.markdown('<div class="progress-section">', unsafe_allow_html=True)
                    st.progress(progress, text=f"Progress: {completed}/{total} sections")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Generate Protocol button
                if not st.session_state.generation_in_progress:
                    if st.sidebar.button(
                        "Generate Complete Protocol",
                        key="generate_btn",
                        use_container_width=True
                    ):
                        st.session_state.generation_in_progress = True
                        progress_bar = st.sidebar.progress(0)
                        status_area = st.sidebar.empty()
                        
                        try:
                            generator = TemplateSectionGenerator()
                            sections = study_config.get('required_sections', [])
                            
                            generated_sections = {}
                            for idx, section in enumerate(sections):
                                progress = (idx + 1) / len(sections)
                                progress_bar.progress(progress)
                                status_area.info(f"Generating {section.replace('_', ' ').title()}...")
                                
                                try:
                                    content = generator.generate_section(
                                        section_name=section,
                                        synopsis_content=synopsis_content,
                                        study_type=study_type
                                    )
                                    if content:
                                        generated_sections[section] = content
                                        st.session_state.section_status[section] = {
                                            'status': 'completed',
                                            'timestamp': time.strftime('%H:%M:%S')
                                        }
                                except Exception as e:
                                    logger.error(f"Error generating {section}: {str(e)}")
                                    st.session_state.section_status[section] = {
                                        'status': 'failed',
                                        'error': str(e)
                                    }
                                    continue
                            
                            st.session_state.generated_sections = generated_sections
                            st.session_state.generation_in_progress = False
                            st.rerun()
                            
                        except Exception as e:
                            logger.error(f"Error in protocol generation: {str(e)}")
                            st.session_state.generation_in_progress = False
                            st.sidebar.error(f"Error: {str(e)}")
                
                # Section navigation and download options
                if generated_sections := st.session_state.get('generated_sections'):
                    # Display sections
                    st.sidebar.markdown("### 📑 Generated Sections")
                    for section in sections:
                        if content := generated_sections.get(section):
                            with st.sidebar.expander(f"📝 {section.replace('_', ' ').title()}"):
                                st.text_area(
                                    "Content",
                                    value=content,
                                    height=150,
                                    disabled=True,
                                    key=f"nav_{section}"
                                )
                    
                    # Download options
                    st.sidebar.markdown("### 📥 Download Protocol")
                    
                    try:
                        # Create document bytes
                        docx_bytes = BytesIO()
                        pdf_bytes = BytesIO()
                        
                        # Generate DOCX
                        doc = create_docx(generated_sections)
                        doc.save(docx_bytes)
                        docx_bytes.seek(0)
                        
                        # Generate PDF
                        pdf = create_pdf(generated_sections)
                        pdf.output(pdf_bytes)
                        pdf_bytes.seek(0)
                        
                        # Add download buttons
                        col1, col2 = st.sidebar.columns(2)
                        
                        with col1:
                            st.download_button(
                                label="📄 Download DOCX",
                                data=docx_bytes,
                                file_name="protocol.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
                        
                        with col2:
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_bytes,
                                file_name="protocol.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Document creation error: {error_msg}")
                        st.sidebar.error(f"Error creating documents: {error_msg}")
                        
    except Exception as e:
        logger.error(f"Error in navigator rendering: {str(e)}")
        st.sidebar.error("An error occurred while rendering the navigator")
