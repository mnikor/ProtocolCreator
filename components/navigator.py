import streamlit as st
from datetime import datetime
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

def _initialize_sections_status():
    """Initialize sections status in session state"""
    if 'sections_status' not in st.session_state:
        st.session_state.sections_status = {}
    
    if study_type := st.session_state.get('study_type'):
        study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
        required_sections = study_config.get('required_sections', [])
        
        for section in required_sections:
            if section not in st.session_state.sections_status:
                st.session_state.sections_status[section] = 'Not Started'

def generate_all_sections():
    """Generate all protocol sections"""
    try:
        if not st.session_state.get('synopsis_content'):
            st.error("Please upload a synopsis first")
            return False
            
        if not st.session_state.get('study_type'):
            st.error("Study type not detected")
            return False
            
        with st.spinner("🔄 Generating protocol..."):
            generator = TemplateSectionGenerator()
            study_type = st.session_state.study_type
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            required_sections = study_config.get('required_sections', [])
            
            result = generator.generate_complete_protocol(
                study_type=study_type,
                synopsis_content=st.session_state.synopsis_content
            )
            
            if result and result.get("sections"):
                sections = result["sections"]
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                for section in required_sections:
                    if section in sections:
                        st.session_state.sections_status[section] = f'Generated at {timestamp}'
                    else:
                        st.session_state.sections_status[section] = 'Failed'
                
                st.session_state.generated_sections = sections
                st.session_state.validation_results = result.get("validation_results", {})
                st.success("✅ Protocol generated successfully!")
                return True
            else:
                st.error("❌ Failed to generate protocol sections")
                return False
                
    except Exception as e:
        logger.error(f"Error in protocol generation: {str(e)}")
        st.error(f"Error: {str(e)}")
        return False

def render_navigator():
    """Render the section navigator with simplified UI"""
    try:
        # Add custom styling
        st.markdown("""
            <style>
            .stDebug {
                display: none !important;
            }
            .element-container div[data-testid="stDebugElement"] {
                display: none !important;
            }
            .section-button {
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0;
                transition: all 0.3s ease;
            }
            .section-button:hover {
                background-color: #e0e2e6;
                transform: translateX(5px);
            }
            .main-content {
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }
            .section-header {
                color: #2c3e50;
                font-size: 1.8rem;
                margin-bottom: 1rem;
            }
            .stButton > button {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 0.75rem;
                border-radius: 10px;
                margin: 10px 0;
                width: 100%;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Check connection and initialize
        if not check_connection():
            st.sidebar.error("⚠️ Connection issues detected. Please refresh the page.")
            return
            
        st.sidebar.markdown("## 🚀 Protocol Generation")
        _initialize_sections_status()
        
        # Generate button
        generate_button = st.sidebar.button(
            "🚀 Generate Complete Protocol",
            help="Generate all protocol sections from synopsis",
            use_container_width=True,
            key="nav_generate_button"
        )

        if generate_button:
            generate_all_sections()

        # Download option
        if st.session_state.get('generated_sections'):
            st.sidebar.markdown("### Download Protocol")
            protocol_text = "\n\n".join(st.session_state.generated_sections.values())
            st.sidebar.download_button(
                "⬇️ Download Protocol",
                protocol_text,
                file_name="protocol.txt",
                mime="text/plain",
                key="nav_download_protocol"
            )

        # Section Navigation
        st.sidebar.markdown("---")
        st.sidebar.markdown('<p class="section-header">📑 Protocol Sections</p>', unsafe_allow_html=True)
        
        if study_type := st.session_state.get('study_type'):
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            sections = study_config.get('required_sections', [])
            
            # Progress bar
            completed = sum(1 for status in st.session_state.sections_status.values() 
                          if 'Generated' in status)
            total = len(sections)
            progress = completed / total if total > 0 else 0
            st.sidebar.progress(progress, f"Progress: {completed}/{total} sections")

            # Section buttons
            for section in sections:
                status = st.session_state.sections_status.get(section, 'Not Started')
                status_color = "🟢" if "Generated" in status else "⚪️"
                button_text = f"{status_color} {section.replace('_', ' ').title()}"
                
                st.sidebar.markdown(
                    f'<div class="section-button">{button_text}</div>',
                    unsafe_allow_html=True
                )
                
    except Exception as e:
        logger.error(f"Error in navigator rendering: {str(e)}")
        st.sidebar.error("An error occurred while rendering the navigator")
