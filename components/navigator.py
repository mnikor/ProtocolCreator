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
        
        # Use section name as key to prevent duplications
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
            
            # Generate complete protocol
            result = generator.generate_complete_protocol(
                study_type=study_type,
                synopsis_content=st.session_state.synopsis_content
            )
            
            if result and result.get("sections"):
                sections = result["sections"]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Update section statuses
                for section in required_sections:
                    if section in sections and sections[section].strip():
                        st.session_state.sections_status[section] = f'Generated at {timestamp}'
                    else:
                        st.session_state.sections_status[section] = 'Failed'
                
                # Store results in session state
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
                cursor: pointer;
            }
            .section-button:hover {
                background-color: #e0e2e6;
                transform: translateX(5px);
            }
            .section-status {
                font-size: 0.8em;
                color: #666;
                margin-top: 5px;
            }
            .stButton > button {
                background-color: #4CAF50 !important;
                color: white !important;
                font-weight: bold !important;
                padding: 0.75rem !important;
                border-radius: 10px !important;
                margin: 10px 0 !important;
                width: 100% !important;
            }
            .stProgress > div > div > div {
                background-color: #4CAF50 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Check connection and initialize
        if not check_connection():
            st.sidebar.error("⚠️ Connection issues detected. Please refresh the page.")
            return
            
        st.sidebar.markdown("## 🚀 Protocol Generation")
        _initialize_sections_status()
        
        # Generate Protocol button - only show if synopsis exists
        if st.session_state.get('synopsis_content'):
            generate_button = st.sidebar.button(
                "🚀 Generate Complete Protocol",
                help="Generate all protocol sections from synopsis",
                use_container_width=True,
                key="nav_generate_protocol"
            )

            if generate_button:
                if generate_all_sections():
                    st.rerun()  # Refresh UI after successful generation

        # Download options - only show if sections are generated
        if generated_sections := st.session_state.get('generated_sections'):
            st.sidebar.markdown("### 📥 Download Protocol")
            protocol_text = "\n\n".join(generated_sections.values())
            
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.download_button(
                    "📄 Download TXT",
                    protocol_text,
                    file_name="protocol.txt",
                    mime="text/plain",
                    key="download_txt"
                )
            with col2:
                st.download_button(
                    "📑 Download DOCX",
                    protocol_text,
                    file_name="protocol.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="download_docx"
                )

        # Section Navigation
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📑 Protocol Sections")
        
        if study_type := st.session_state.get('study_type'):
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            sections = study_config.get('required_sections', [])
            
            # Calculate and display progress
            completed = sum(1 for status in st.session_state.sections_status.values() 
                          if 'Generated' in status)
            total = len(sections)
            progress = completed / total if total > 0 else 0
            
            # Progress bar with percentage
            progress_text = f"Progress: {completed}/{total} sections ({progress*100:.1f}%)"
            st.sidebar.progress(progress, text=progress_text)

            # Section list with status indicators
            for section in sections:
                status = st.session_state.sections_status.get(section, 'Not Started')
                
                # Status indicator
                if 'Generated' in status:
                    icon = "🟢"  # Green circle for generated
                elif 'Failed' in status:
                    icon = "🔴"  # Red circle for failed
                else:
                    icon = "⚪️"  # White circle for not started
                
                # Section name with status
                section_name = section.replace('_', ' ').title()
                st.sidebar.markdown(
                    f"""
                    <div class="section-button">
                        {icon} {section_name}
                        <div class="section-status">{status}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
    except Exception as e:
        logger.error(f"Error in navigator rendering: {str(e)}")
        st.sidebar.error("An error occurred while rendering the navigator")
