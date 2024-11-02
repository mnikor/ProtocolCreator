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
            .disabled-button {
                opacity: 0.6;
                cursor: not-allowed;
            }
            </style>
        """, unsafe_allow_html=True)

        # Initialize session state if needed
        if 'generated_sections' not in st.session_state:
            st.session_state.generated_sections = {}
        if 'generation_in_progress' not in st.session_state:
            st.session_state.generation_in_progress = False
        if 'generation_started' not in st.session_state:
            st.session_state.generation_started = False

        # Check connection
        if not check_connection():
            st.sidebar.error("⚠️ Connection issues detected. Please refresh the page.")
            return

        st.sidebar.markdown("## Protocol Development")

        # Show study type if selected
        if study_type := st.session_state.get('study_type'):
            st.sidebar.info(f"📋 Study Type: {study_type.replace('_', ' ').title()}")

        # Section Navigation
        st.sidebar.markdown("### 📑 Protocol Sections")
        
        if study_type:
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
            
            # Section list with status
            for section in sections:
                is_completed = section in st.session_state.get('generated_sections', {})
                icon = "✅" if is_completed else "⏳"
                section_name = section.replace('_', ' ').title()
                st.sidebar.markdown(f"{icon} {section_name}")

            # Generate Protocol button - only show if synopsis exists and not already generated
            if st.session_state.get('synopsis_content'):
                st.sidebar.markdown("### 🚀 Protocol Generation")
                
                # Disable button if sections are already generated or generation is in progress
                button_disabled = (
                    bool(st.session_state.get('generated_sections')) or 
                    st.session_state.generation_in_progress or
                    st.session_state.generation_started
                )
                
                if st.sidebar.button(
                    "Generate Complete Protocol",
                    key="nav_generate_btn",
                    help="Generate all protocol sections from synopsis",
                    use_container_width=True,
                    disabled=button_disabled
                ):
                    try:
                        st.session_state.generation_in_progress = True
                        st.session_state.generation_started = True
                        
                        with st.sidebar.spinner("🔄 Generating protocol..."):
                            generator = TemplateSectionGenerator()
                            
                            # Generate complete protocol
                            result = generator.generate_complete_protocol(
                                study_type=study_type,
                                synopsis_content=st.session_state.synopsis_content
                            )
                            
                            if result and isinstance(result, dict) and "sections" in result:
                                st.session_state.generated_sections = result["sections"]
                                st.sidebar.success("✅ Protocol generated successfully!")
                                st.session_state.generation_in_progress = False
                                st.rerun()
                            else:
                                st.sidebar.error("❌ Failed to generate protocol sections")
                                st.session_state.generation_in_progress = False
                                st.session_state.generation_started = False
                                
                    except Exception as e:
                        logger.error(f"Error in protocol generation: {str(e)}")
                        st.sidebar.error(f"Error: {str(e)}")
                        st.session_state.generation_in_progress = False
                        st.session_state.generation_started = False

            # Download options - only show if sections are generated
            if generated_sections := st.session_state.get('generated_sections'):
                st.sidebar.markdown("---")
                st.sidebar.markdown("### 📥 Download Options")
                
                # Create protocol text with proper formatting
                protocol_text = "\n\n".join(
                    f"## {section.replace('_', ' ').title()}\n\n{content}"
                    for section, content in generated_sections.items()
                )
                
                st.sidebar.download_button(
                    "📄 Download Protocol",
                    protocol_text,
                    file_name="protocol.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                    
    except Exception as e:
        logger.error(f"Error in navigator rendering: {str(e)}")
        st.sidebar.error("An error occurred while rendering the navigator")
