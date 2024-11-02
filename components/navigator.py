import streamlit as st
import logging
from utils.template_section_generator import TemplateSectionGenerator
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS

logger = logging.getLogger(__name__)

def check_connection():
    """Check if application can establish necessary connections"""
    try:
        generator = TemplateSectionGenerator()
        return True
    except Exception as e:
        logger.error(f"Connection check failed: {str(e)}")
        return False

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
            </style>
        """, unsafe_allow_html=True)
        
        # Initialize session state if needed
        if 'generated_sections' not in st.session_state:
            st.session_state.generated_sections = {}
        if 'validation_results' not in st.session_state:
            st.session_state.validation_results = None
        
        # Check connection
        if not check_connection():
            st.sidebar.error("⚠️ Connection issues detected. Please refresh the page.")
            return
        
        st.sidebar.markdown("## Protocol Development")
        
        # Generate Protocol button - only show if synopsis exists
        if st.session_state.get('synopsis_content'):
            st.sidebar.markdown("### 🚀 Protocol Generation")
            
            if st.sidebar.button(
                "Generate Complete Protocol",
                key="nav_generate_btn",
                help="Generate all protocol sections from synopsis",
                use_container_width=True
            ):
                try:
                    with st.sidebar.spinner("🔄 Generating protocol..."):
                        generator = TemplateSectionGenerator()
                        
                        # Generate complete protocol
                        result = generator.generate_complete_protocol(
                            study_type=st.session_state.study_type,
                            synopsis_content=st.session_state.synopsis_content
                        )
                        
                        if result and isinstance(result, dict):
                            # Store generated sections and validation results
                            if "sections" in result:
                                st.session_state.generated_sections = result["sections"]
                            if "validation_results" in result:
                                st.session_state.validation_results = result["validation_results"]
                                
                            st.sidebar.success("✅ Protocol generated successfully!")
                            st.rerun()
                        else:
                            st.sidebar.error("❌ Failed to generate protocol sections")
                            
                except Exception as e:
                    logger.error(f"Error in protocol generation: {str(e)}")
                    st.sidebar.error(f"Error: {str(e)}")

        # Section Navigation
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📑 Protocol Sections")
        
        if study_type := st.session_state.get('study_type'):
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            sections = study_config.get('required_sections', [])
            
            # Progress tracking
            completed = sum(1 for section, content in st.session_state.get('generated_sections', {}).items() 
                          if content and content.strip())
            total = len(sections)
            progress = completed / total if total > 0 else 0
            
            # Progress section
            with st.sidebar.container():
                st.markdown('<div class="progress-section">', unsafe_allow_html=True)
                st.progress(progress, text=f"Progress: {completed}/{total} sections")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Section list
            for section in sections:
                is_completed = section in st.session_state.get('generated_sections', {})
                icon = "✅" if is_completed else "⏳"
                section_name = section.replace('_', ' ').title()
                st.sidebar.markdown(f"{icon} {section_name}")
            
            # Download options - only show if sections are generated
            if generated_sections := st.session_state.get('generated_sections'):
                st.sidebar.markdown("---")
                st.sidebar.markdown("### 📥 Download Options")
                
                # Create protocol text with proper formatting
                protocol_text = "\n\n".join(
                    f"## {section.replace('_', ' ').title()}\n\n{content}"
                    for section, content in generated_sections.items()
                )
                
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    st.download_button(
                        "📄 DOCX",
                        protocol_text,
                        file_name="protocol.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="nav_download_docx"
                    )
                with col2:
                    st.download_button(
                        "📑 PDF",
                        protocol_text,
                        file_name="protocol.pdf",
                        mime="application/pdf",
                        key="nav_download_pdf"
                    )
                    
    except Exception as e:
        logger.error(f"Error in navigator rendering: {str(e)}")
        st.sidebar.error("An error occurred while rendering the navigator")
