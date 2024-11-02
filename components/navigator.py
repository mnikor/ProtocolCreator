import streamlit as st
import logging
import time
from utils.template_section_generator import TemplateSectionGenerator
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS
from io import BytesIO
from docx import Document

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
    """Create a properly formatted Word document"""
    doc = Document()
    for section, content in generated_sections.items():
        section_title = section.replace('_', ' ').title()
        doc.add_heading(section_title, level=1)
        doc.add_paragraph(content)
        doc.add_paragraph()  # Add spacing between sections
    return doc

def render_navigator():
    """Render the section navigator with simplified UI"""
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
            </style>
        """, unsafe_allow_html=True)

        # Initialize session state
        if 'generated_sections' not in st.session_state:
            st.session_state.generated_sections = {}
        if 'generation_in_progress' not in st.session_state:
            st.session_state.generation_in_progress = False
        if 'section_generation_times' not in st.session_state:
            st.session_state.section_generation_times = {}

        # Check connection
        if not check_connection():
            st.sidebar.error("⚠️ Connection issues detected. Please refresh the page.")
            return

        st.sidebar.markdown("## Protocol Development")

        # Show study type if selected
        study_type = st.session_state.get('study_type')
        if study_type:
            st.sidebar.info(f"📋 Study Type: {study_type.replace('_', ' ').title()}")

        # Section Navigation
        st.sidebar.markdown("### 📑 Protocol Sections")
        
        if study_type:
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            sections = study_config.get('required_sections', [])
            
            # Progress tracking
            completed = sum(1 for section in sections 
                          if section in st.session_state.get('generated_sections', {}))
            total = len(sections)
            progress = completed / total if total > 0 else 0
            
            # Progress section
            with st.sidebar.container():
                st.markdown('<div class="progress-section">', unsafe_allow_html=True)
                st.progress(progress, text=f"Progress: {completed}/{total} sections")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Section list with status
            for section in sections:
                is_completed = section in st.session_state.get('generated_sections', {})
                generation_time = st.session_state.section_generation_times.get(section, 0)
                
                if is_completed:
                    time_info = f"(Generated in {generation_time:.1f}s)" if generation_time > 0 else ""
                    st.sidebar.markdown(f"✅ {section.replace('_', ' ').title()} {time_info}")
                else:
                    st.sidebar.markdown(f"⏳ {section.replace('_', ' ').title()}")

            # Generate Protocol button
            if st.session_state.get('synopsis_content'):
                st.sidebar.markdown("### 🚀 Protocol Generation")
                
                button_disabled = st.session_state.generation_in_progress
                
                if st.sidebar.button(
                    "Generate Complete Protocol",
                    key="nav_generate_btn",
                    help="Generate all protocol sections from synopsis",
                    use_container_width=True,
                    disabled=button_disabled
                ):
                    try:
                        st.session_state.generation_in_progress = True
                        
                        with st.sidebar:
                            progress_placeholder = st.empty()
                            progress_bar = st.progress(0)
                            section_status = st.empty()
                            
                            generator = TemplateSectionGenerator()
                            generated_sections = {}
                            
                            for i, section in enumerate(sections):
                                progress = (i + 1) / len(sections)
                                progress_bar.progress(progress)
                                section_status.markdown(f"🔄 Generating: {section.replace('_', ' ').title()}")
                                
                                try:
                                    start_time = time.time()
                                    section_content = generator.generate_section(
                                        section_name=section,
                                        synopsis_content=st.session_state.synopsis_content,
                                        study_type=study_type
                                    )
                                    generation_time = time.time() - start_time
                                    
                                    if section_content:
                                        generated_sections[section] = section_content
                                        st.session_state.section_generation_times[section] = generation_time
                                        section_status.markdown(f"✅ {section.replace('_', ' ').title()} (Generated in {generation_time:.1f}s)")
                                    
                                except Exception as section_error:
                                    logger.error(f"Error generating section {section}: {str(section_error)}")
                                    section_status.error(f"❌ Error generating {section}")
                                    continue
                            
                            # Store generated sections and reset state
                            st.session_state.generated_sections = generated_sections
                            st.session_state.generation_in_progress = False
                            
                            if generated_sections:
                                st.sidebar.success("✅ Protocol sections generated successfully!")
                            else:
                                st.sidebar.error("❌ Failed to generate any sections")
                            
                            st.rerun()
                                    
                    except Exception as e:
                        logger.error(f"Error in protocol generation: {str(e)}")
                        st.sidebar.error(f"Error: {str(e)}")
                        st.session_state.generation_in_progress = False

            # Download options
            if generated_sections := st.session_state.get('generated_sections'):
                st.sidebar.markdown("---")
                st.sidebar.markdown("### 📥 Download Options")
                
                # Create and save DOCX
                doc_buffer = BytesIO()
                doc = create_docx(generated_sections)
                doc.save(doc_buffer)
                doc_buffer.seek(0)
                
                st.sidebar.download_button(
                    "📄 Download DOCX",
                    doc_buffer,
                    file_name="protocol.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                    
    except Exception as e:
        logger.error(f"Error in navigator rendering: {str(e)}")
        st.sidebar.error("An error occurred while rendering the navigator")
