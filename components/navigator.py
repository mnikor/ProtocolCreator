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
    
    # Get current study type's required sections
    if study_type := st.session_state.get('study_type'):
        study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
        required_sections = study_config.get('required_sections', [])
        
        # Initialize status for required sections
        for section in required_sections:
            if section not in st.session_state.sections_status:
                st.session_state.sections_status[section] = 'Not Started'

def generate_all_sections():
    """Generate all protocol sections"""
    try:
        with st.spinner("🔄 Generating protocol..."):
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
                # Update section statuses
                sections = result["sections"]
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                for section in required_sections:
                    if section in sections:
                        st.session_state.sections_status[section] = f'Generated at {timestamp}'
                    else:
                        st.session_state.sections_status[section] = 'Failed'
                
                # Store results in session state
                st.session_state.generated_sections = sections
                
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
            # Add button styling
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

            # Generate button
            generate_button = st.sidebar.button(
                "🚀 Generate Complete Protocol",
                help="Generate all protocol sections from your synopsis",
                use_container_width=True,
                key="nav_generate_button"
            )

            if generate_button:
                logger.info("Generate protocol button clicked")
                generate_all_sections()

            # Display download option if protocol is generated
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

        else:
            if not st.session_state.get('synopsis_content'):
                st.sidebar.warning("⚠️ Please upload a synopsis first")
            if not st.session_state.get('study_type'):
                st.sidebar.warning("⚠️ Please select a study type")

        # Section Navigation
        st.sidebar.markdown("---")
        st.sidebar.header("📑 Protocol Sections")
        
        # Show section navigation
        if study_type := st.session_state.get('study_type'):
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            sections = study_config.get('required_sections', [])
            
            # Overall progress
            completed = sum(1 for status in st.session_state.sections_status.values() 
                          if 'Generated' in status)
            total = len(sections)
            progress = completed / total if total > 0 else 0
            
            # Progress bar
            st.sidebar.progress(progress, f"Progress: {completed}/{total} sections")

            # Section buttons with unique keys
            for section in sections:
                status = st.session_state.sections_status.get(section, 'Not Started')
                status_color = "🟢" if "Generated" in status else "⚪️"
                button_text = f"{status_color} {section.replace('_', ' ').title()}"
                
                if st.sidebar.button(
                    button_text,
                    key=f"nav_section_btn_{section}",
                    help=f"Status: {status}"
                ):
                    logger.info(f"Selected section: {section}")
                    st.session_state.current_section = section
                    
    except Exception as e:
        logger.error(f"Error in navigator rendering: {str(e)}")
        st.sidebar.error("An error occurred while rendering the navigator")
