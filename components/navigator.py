import streamlit as st
from datetime import datetime
import logging
import time
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter
from utils.protocol_validator import ProtocolValidator
from utils.protocol_quality_ui import render_quality_assessment
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
    
    # Get current study type's required sections
    if study_type := st.session_state.get('study_type'):
        study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
        required_sections = study_config.get('required_sections', [])
        
        # Initialize status for required sections
        for section in required_sections:
            if section not in st.session_state.sections_status:
                st.session_state.sections_status[section] = 'Not Started'

def generate_all_sections():
    """Generate all protocol sections with enhanced validation and progress tracking"""
    try:
        with st.spinner("Generating protocol..."):
            # Initialize generator
            generator = TemplateSectionGenerator()
            
            # Get sections for study type
            study_type = st.session_state.study_type
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            required_sections = study_config.get('required_sections', [])
            
            logger.info(f"Starting generation for study type: {study_type}")
            
            # Generate complete protocol
            result = generator.generate_complete_protocol(
                study_type=study_type,
                synopsis_content=st.session_state.synopsis_content
            )
            
            if result and result.get("sections"):
                # Update section statuses and progress
                sections = result["sections"]
                validation_results = result["validation_results"]
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                for section in required_sections:
                    if section in sections:
                        st.session_state.sections_status[section] = f'Generated at {timestamp}'
                    else:
                        st.session_state.sections_status[section] = 'Failed'
                
                # Store results in session state
                st.session_state.generated_sections = sections
                st.session_state.validation_results = validation_results
                
                st.success("✅ Protocol generated successfully!")
                return True
            else:
                st.error("Failed to generate protocol sections")
                if result.get("generation_errors"):
                    for error in result["generation_errors"]:
                        st.error(f"• {error}")
                return False
                
    except Exception as e:
        logger.error(f"Error in protocol generation: {str(e)}")
        st.error(f"Error: {str(e)}")
        return False

def render_navigator():
    """Render the section navigator with enhanced UI and validation feedback"""
    try:
        # Check connection status first
        if not check_connection():
            st.sidebar.error("⚠️ Connection issues detected. Please refresh the page.")
            return
            
        st.sidebar.markdown("## 🚀 Protocol Generation")
        
        # Initialize sections status
        _initialize_sections_status()
        
        # Check prerequisites
        can_generate = (
            st.session_state.get('synopsis_content') is not None and 
            st.session_state.get('study_type') is not None
        )

        if can_generate:
            # Add enhanced button styling
            st.sidebar.markdown("""
                <style>
                div.stButton > button:first-child {
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

            # Generate button with proper styling
            generate_button = st.sidebar.button(
                "🚀 Generate Complete Protocol",
                help="Generate all protocol sections from your synopsis",
                use_container_width=True,
                key="nav_generate"
            )

            if generate_button:
                logger.info("Generate protocol button clicked")
                generate_all_sections()

        else:
            if not st.session_state.get('synopsis_content'):
                st.sidebar.warning("⚠️ Please upload a synopsis first")
            if not st.session_state.get('study_type'):
                st.sidebar.warning("⚠️ Please select a study type")

        # Section Navigation
        st.sidebar.markdown("---")
        st.sidebar.header("📑 Protocol Sections")
        
        # Show section navigation with validation status
        if study_type := st.session_state.get('study_type'):
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            sections = study_config.get('required_sections', [])
            
            # Overall progress with validation score
            completed = sum(1 for status in st.session_state.sections_status.values() 
                          if 'Generated' in status)
            total = len(sections)
            progress = completed / total if total > 0 else 0
            
            # Add quality score if available
            progress_container = st.sidebar.container()
            with progress_container:
                if validation_results := st.session_state.get('validation_results'):
                    quality_score = validation_results.get('overall_score', 0)
                    st.progress(
                        progress,
                        f"Progress: {completed}/{total} sections (Quality: {quality_score/10:.1f}/10)"
                    )
                else:
                    st.progress(progress, f"Progress: {completed}/{total} sections")

            # Section buttons
            for idx, section in enumerate(sections):
                status = st.session_state.sections_status.get(section, 'Not Started')
                status_color = "🟢" if "Generated" in status else "⚪️"
                button_text = f"{status_color} {section.replace('_', ' ').title()}"
                
                if st.sidebar.button(
                    button_text,
                    key=f"nav_section_{section}",
                    help=f"Status: {status}"
                ):
                    logger.info(f"Selected section: {section}")
                    st.session_state.current_section = section
                    
    except Exception as e:
        logger.error(f"Error in navigator rendering: {str(e)}")
        st.sidebar.error("An error occurred while rendering the navigator")
