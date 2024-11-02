import streamlit as st
import logging
import time
from utils.template_section_generator import TemplateSectionGenerator
from utils.synopsis_validator import SynopsisValidator
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS
from io import BytesIO
from docx import Document
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

def create_pdf(generated_sections):
    """Create a properly formatted PDF with enhanced styling and formatting"""
    pdf = FPDF()
    
    # Set document properties
    pdf.set_title('Study Protocol')
    pdf.set_author('Protocol Development Assistant')
    
    # Add fonts - DejaVu supports unicode characters
    pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', uni=True)
    pdf.add_font('DejaVu', 'I', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf', uni=True)
    
    # Title page
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 24)
    pdf.cell(0, 20, 'Study Protocol', ln=True, align='C')
    pdf.ln(20)
    
    # Add date
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(0, 10, f'Generated: {time.strftime("%B %d, %Y")}', ln=True, align='C')
    pdf.ln(30)
    
    # Table of contents page
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(0, 20, 'Table of Contents', ln=True)
    pdf.ln(10)
    
    # Add sections to table of contents
    pdf.set_font('DejaVu', '', 12)
    page_numbers = {}
    current_page = pdf.page_no() + 1  # Start counting from next page
    
    for section in generated_sections:
        section_title = section.replace('_', ' ').title()
        page_numbers[section] = current_page
        pdf.cell(0, 10, f'{section_title}....{current_page}', ln=True)
        
        # Estimate pages needed for content (rough estimation)
        content_length = len(generated_sections[section])
        current_page += max(1, content_length // 2000)  # Assume ~2000 chars per page
    
    # Content pages
    for section, content in generated_sections.items():
        pdf.add_page()
        
        # Section heading
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 15, section.replace('_', ' ').title(), ln=True)
        pdf.ln(5)
        
        # Process content paragraphs with enhanced formatting
        pdf.set_font('DejaVu', '', 11)
        paragraphs = content.split('\n')
        
        for para in paragraphs:
            if para.strip():
                # Split by italic markers
                parts = para.split('*')
                x_start = pdf.get_x()
                
                for i, part in enumerate(parts):
                    if part.strip():
                        # Handle font changes
                        pdf.set_font('DejaVu', 'I' if i % 2 == 1 else '', 11)
                        
                        # Calculate text height and check for page break
                        text_height = pdf.get_string_height(part.strip())
                        if pdf.get_y() + text_height > pdf.page_break_trigger:
                            pdf.add_page()
                        
                        # Multi-line text support
                        pdf.multi_cell(0, 5, part.strip())
                        
                        # Reset position for next part if not last part
                        if i < len(parts) - 1:
                            pdf.set_xy(x_start, pdf.get_y())
                
                pdf.ln(3)
            else:
                pdf.ln(5)
        
        pdf.ln(10)
    
    # Add page numbers
    for i in range(1, pdf.page_no() + 1):
        pdf.page = i
        pdf.set_font('DejaVu', '', 10)
        pdf.set_y(-15)
        pdf.cell(0, 10, f'Page {i}', align='C')
    
    return pdf

def create_docx(generated_sections):
    """Create a properly formatted Word document with italic placeholders"""
    doc = Document()
    
    # Add title page
    doc.add_heading('Study Protocol', 0)
    doc.add_paragraph()
    
    # Add each section
    for section, content in generated_sections.items():
        # Add section heading
        doc.add_heading(section.replace('_', ' ').title(), level=1)
        
        # Process content paragraphs
        paragraphs = content.split('\n')
        for para in paragraphs:
            if para.strip():
                p = doc.add_paragraph()
                # Split paragraph by italic markers
                parts = para.split('*')
                for i, part in enumerate(parts):
                    if part.strip():
                        # Alternate between normal and italic text
                        run = p.add_run(part.strip())
                        if i % 2 == 1:  # Odd indices are italic
                            run.italic = True
        
        # Add spacing between sections
        doc.add_paragraph()
    
    return doc

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

        # Initialize session state
        if 'generated_sections' not in st.session_state:
            st.session_state.generated_sections = {}
        if 'section_status' not in st.session_state:
            st.session_state.section_status = {}
        if 'generation_in_progress' not in st.session_state:
            st.session_state.generation_in_progress = False

        # Check connection
        if not check_connection():
            st.sidebar.error("⚠️ Connection issues detected. Please refresh the page.")
            return

        st.sidebar.markdown("## Protocol Development")

        # Study type detection and analysis
        if synopsis_content := st.session_state.get('synopsis_content'):
            # Study Type Detection Section
            st.sidebar.markdown("### 🔍 Study Analysis")
            
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

            # Section Navigation with detailed status
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
                st.sidebar.markdown("### 🚀 Protocol Generation")
                button_disabled = st.session_state.generation_in_progress
                
                if st.sidebar.button(
                    "Generate Complete Protocol",
                    key="nav_generate_btn",
                    help="Generate all protocol sections from synopsis",
                    disabled=button_disabled,
                    use_container_width=True
                ):
                    try:
                        st.session_state.generation_in_progress = True
                        progress_placeholder = st.sidebar.empty()
                        progress_bar = st.sidebar.progress(0)
                        status_area = st.sidebar.empty()
                        
                        # Initialize generator
                        generator = TemplateSectionGenerator()
                        study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
                        sections = study_config.get('required_sections', [])
                        
                        generated_sections = {}
                        for idx, section in enumerate(sections):
                            # Update progress
                            progress = (idx + 1) / len(sections)
                            progress_bar.progress(progress)
                            status_area.info(f"Generating {section.replace('_', ' ').title()}...")
                            
                            try:
                                # Generate section
                                start_time = time.time()
                                content = generator.generate_section(
                                    section_name=section,
                                    synopsis_content=synopsis_content,
                                    study_type=study_type
                                )
                                generation_time = time.time() - start_time
                                
                                if content:
                                    generated_sections[section] = content
                                    st.session_state.section_status[section] = {
                                        'status': 'completed',
                                        'time': generation_time,
                                        'timestamp': time.strftime('%H:%M:%S')
                                    }
                                    status_area.success(f"✅ {section.replace('_', ' ').title()} (Generated in {generation_time:.1f}s)")
                            except Exception as e:
                                st.session_state.section_status[section] = {
                                    'status': 'failed',
                                    'error': str(e)
                                }
                                status_area.error(f"❌ Failed to generate {section}")
                                logger.error(f"Error generating {section}: {str(e)}")
                                continue
                        
                        # Store generated sections and reset state
                        st.session_state.generated_sections = generated_sections
                        st.session_state.generation_in_progress = False
                        
                        # Final status update
                        if generated_sections:
                            st.success("✅ Protocol generation completed!")
                            st.rerun()
                        else:
                            st.error("❌ No sections were generated successfully")
                            
                    except Exception as e:
                        logger.error(f"Error in protocol generation: {str(e)}")
                        st.sidebar.error(f"Error: {str(e)}")
                        st.session_state.generation_in_progress = False

                # Section navigation and content display
                st.sidebar.markdown("### 📑 Generated Sections")
                for section, content in st.session_state.get('generated_sections', {}).items():
                    with st.sidebar.expander(f"📝 {section.replace('_', ' ').title()}"):
                        st.text_area(
                            "Content",
                            value=content,
                            height=150,
                            disabled=True,
                            key=f"nav_{section}"
                        )

                # Download options
                if generated_sections := st.session_state.get('generated_sections'):
                    st.sidebar.markdown("### 📥 Download Protocol")
                    
                    try:
                        # Create DOCX document
                        doc = create_docx(generated_sections)
                        doc_bytes = BytesIO()
                        doc.save(doc_bytes)
                        doc_bytes.seek(0)
                        
                        # Create PDF document
                        pdf = create_pdf(generated_sections)
                        pdf_bytes = BytesIO()
                        pdf.output(pdf_bytes)
                        pdf_bytes.seek(0)
                        
                        # Add download buttons in a row
                        st.sidebar.markdown('<div class="download-buttons">', unsafe_allow_html=True)
                        
                        # DOCX download button
                        col1, col2 = st.sidebar.columns(2)
                        with col1:
                            st.download_button(
                                label="📄 Download DOCX",
                                data=doc_bytes,
                                file_name="protocol.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                help="Download protocol as Word document"
                            )
                        
                        # PDF download button
                        with col2:
                            st.download_button(
                                label="📑 Download PDF",
                                data=pdf_bytes,
                                file_name="protocol.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                help="Download protocol as PDF document"
                            )
                            
                        st.sidebar.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        logger.error(f"Error creating documents: {str(e)}")
                        st.sidebar.error("Error creating documents for download")
                    
    except Exception as e:
        logger.error(f"Error in navigator rendering: {str(e)}")
        st.sidebar.error("An error occurred while rendering the navigator")