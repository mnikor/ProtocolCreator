import streamlit as st
from datetime import datetime
import logging
import time
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter
from utils.protocol_validator import ProtocolValidator
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
    """Generate all protocol sections with enhanced validation and error handling"""
    max_retries = 3
    retry_count = 0
    start_time = datetime.now()
    
    while retry_count < max_retries:
        try:
            # Initialize generator and progress tracking
            generator = TemplateSectionGenerator()
            progress_placeholder = st.empty()
            progress_bar = progress_placeholder.progress(0)
            status_text = st.empty()
            
            # Get sections for study type
            study_type = st.session_state.study_type
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            required_sections = study_config.get('required_sections', [])
            total_sections = len(required_sections)
            
            # Generate complete protocol with enhanced error handling
            status_text.info("🔄 Generating protocol sections...")
            try:
                result = generator.generate_complete_protocol(
                    study_type=study_type,
                    synopsis_content=st.session_state.synopsis_content
                )
                
                # Update section statuses and progress
                sections = result.get("sections", {})
                validation_results = result.get("validation_results", {})
                generated_count = len(sections)
                
                for section in required_sections:
                    if section in sections:
                        st.session_state.sections_status[section] = 'Generated'
                        progress_bar.progress(generated_count / total_sections)
                    else:
                        st.session_state.sections_status[section] = 'Error'
                
                # Store results
                st.session_state.generated_sections = sections
                st.session_state.validation_results = validation_results
                
                # Display validation summary
                if validation_results:
                    quality_score = validation_results.get('quality_score', 0)
                    st.info(f"Protocol Quality Score: {quality_score:.2f}%")
                    
                    # Show critical issues if any
                    critical_issues = [i for i in validation_results.get("issues", []) 
                                    if i.get("severity") == "critical"]
                    if critical_issues:
                        st.warning("Critical Issues Found:")
                        for issue in critical_issues:
                            st.write(f"- {issue.get('message')}")
                
                # Generation summary
                total_time = datetime.now() - start_time
                if generated_count == total_sections:
                    progress_placeholder.success(
                        f"✅ Protocol generated successfully! ({total_time.total_seconds():.1f}s)"
                    )
                    st.balloons()
                    return True
                else:
                    progress_placeholder.warning(
                        f"⚠️ Generated {generated_count}/{total_sections} sections ({total_time.total_seconds():.1f}s)"
                    )
                    if result.get("generation_errors"):
                        for error in result["generation_errors"]:
                            st.error(f"Generation Error: {error}")
                    return False
                    
            except Exception as e:
                logger.error(f"Error in protocol generation: {str(e)}")
                status_text.error(f"❌ Error: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    st.warning(f"Retrying generation... (Attempt {retry_count}/{max_retries})")
                    time.sleep(2)
                    continue
                return False
                
        except Exception as e:
            logger.error(f"Error in generation setup: {str(e)}")
            st.error(f"❌ Error: {str(e)}")
            return False
            
        # If we reach here with no exceptions, break the retry loop
        break
    
    return False

def render_navigator():
    """Render the section navigator with enhanced UI and validation feedback"""
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

        # Generate button
        if st.sidebar.button(
            "🚀 Generate Complete Protocol",
            help="Generate all protocol sections from your synopsis",
            use_container_width=True,
            key="nav_generate_protocol"
        ):
            with st.spinner("Generating protocol..."):
                if generate_all_sections():
                    st.sidebar.success("✅ Protocol generated successfully!")
                    # Show export options if generation successful
                    st.sidebar.markdown("---")
                    st.sidebar.markdown("### 📥 Export Protocol")
                    export_protocol()
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
                       if status == 'Generated')
        total = len(sections)
        progress = completed / total if total > 0 else 0
        
        # Add quality score if available
        if validation_results := st.session_state.get('validation_results'):
            quality_score = validation_results.get('quality_score', 0)
            st.sidebar.progress(progress, text=f"Progress: {completed}/{total} sections (Quality: {quality_score:.1f}%)")
        else:
            st.sidebar.progress(progress, text=f"Progress: {completed}/{total} sections")

        # Section navigation with enhanced status indicators
        status_indicators = {
            'Not Started': {'icon': '⚪', 'desc': 'Not started yet', 'color': 'gray'},
            'In Progress': {'icon': '🟡', 'desc': 'Generation in progress', 'color': '#FFD700'},
            'Generated': {'icon': '🟢', 'desc': 'Generated successfully', 'color': '#4CAF50'},
            'Error': {'icon': '🔴', 'desc': 'Error in generation', 'color': '#FF0000'},
            'Warning': {'icon': '🟠', 'desc': 'Generated with warnings', 'color': '#FFA500'}
        }

        for section in sections:
            status = st.session_state.sections_status.get(section, 'Not Started')
            
            # Check validation results for this section
            if validation_results := st.session_state.get('validation_results'):
                section_results = validation_results.get(section, {})
                if status == 'Generated' and section_results.get('missing_items'):
                    status = 'Warning'
            
            col1, col2 = st.sidebar.columns([3, 1])
            
            with col1:
                if st.button(
                    section.replace('_', ' ').title(),
                    key=f"nav_{section}",
                    help=f"Edit {section.replace('_', ' ').title()} section",
                    use_container_width=True
                ):
                    st.session_state.current_section = section

            with col2:
                indicator = status_indicators.get(status, status_indicators['Not Started'])
                st.markdown(
                    f"""<div style='text-align: center;'>
                        <span title='{indicator["desc"]}' style='color: {indicator["color"]};
                        font-size: 20px;'>{indicator["icon"]}</span></div>""",
                    unsafe_allow_html=True
                )

def export_protocol():
    """Handle protocol export with enhanced error handling"""
    try:
        formatter = ProtocolFormatter()
        
        # Format selection
        format_option = st.sidebar.radio(
            "Export Format:",
            ["DOCX", "PDF"],
            key="nav_export_format"
        )
        
        if st.sidebar.button("Export Protocol", key="nav_export_button"):
            with st.spinner("Preparing document..."):
                try:
                    if format_option == "PDF":
                        output_file = formatter.save_document("protocol", format='pdf')
                        with open(output_file, "rb") as file:
                            st.sidebar.download_button(
                                "Download Protocol (PDF)",
                                file,
                                file_name="protocol.pdf",
                                mime="application/pdf",
                                key="nav_download_pdf"
                            )
                    else:  # DOCX format
                        output_file = formatter.save_document("protocol", format='docx')
                        with open(output_file, "rb") as file:
                            st.sidebar.download_button(
                                "Download Protocol (DOCX)",
                                file,
                                file_name="protocol.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="nav_download_docx"
                            )
                    st.sidebar.success(f"✅ Protocol exported as {format_option}")
                    
                except ValueError as ve:
                    st.sidebar.warning(str(ve))
                except Exception as e:
                    st.sidebar.error(f"Error exporting protocol: {str(e)}")
                    
    except Exception as e:
        st.sidebar.error(f"Error preparing protocol: {str(e)}")
