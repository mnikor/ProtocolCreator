import streamlit as st
from datetime import datetime
import logging
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS
from config.validation_rules import validate_protocol_quality

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _initialize_sections_status():
    """Initialize or update sections status"""
    if 'sections_status' not in st.session_state:
        st.session_state.sections_status = {}
    
    if 'generated_sections' not in st.session_state:
        st.session_state.generated_sections = {}
        
    # Get sections based on study type
    if study_type := st.session_state.get('study_type'):
        study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
        sections = study_config.get('required_sections', [])
        
        # Update sections status
        for section in sections:
            if section not in st.session_state.sections_status:
                st.session_state.sections_status[section] = 'Not Started'

def generate_all_sections():
    """Generate all protocol sections with enhanced progress tracking"""
    try:
        # Initialize generator and progress tracking
        generator = TemplateSectionGenerator()
        progress_placeholder = st.empty()
        progress_bar = progress_placeholder.progress(0)
        status_text = st.empty()
        sections_status = st.empty()
        
        # Get sections for study type
        study_type = st.session_state.study_type
        study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
        required_sections = study_config.get('required_sections', [])
        total_sections = len(required_sections)
        
        # Initialize tracking
        successful_sections = 0
        generation_errors = []
        start_time = datetime.now()

        # Generate each section
        for idx, section in enumerate(required_sections, 1):
            section_start = datetime.now()
            status_text.info(f"📝 Generating {section.replace('_', ' ').title()}...")
            
            try:
                # Update status to in progress
                st.session_state.sections_status[section] = 'In Progress'
                sections_status.write("Current Status:")
                for sec, status in st.session_state.sections_status.items():
                    sections_status.write(f"{sec}: {status}")
                
                # Generate section content
                content = generator.generate_section(
                    section_name=section,
                    study_type=study_type,
                    synopsis_content=st.session_state.synopsis_content,
                    existing_sections=st.session_state.generated_sections
                )
                
                if content:
                    # Store generated content
                    st.session_state.generated_sections[section] = content
                    st.session_state.sections_status[section] = 'Generated'
                    successful_sections += 1
                    
                    # Update progress
                    progress_bar.progress(idx / total_sections)
                    section_time = datetime.now() - section_start
                    sections_status.success(f"✅ {section.replace('_', ' ').title()} completed ({section_time.total_seconds():.1f}s)")
                else:
                    raise ValueError(f"No content generated for {section}")
                    
            except Exception as e:
                error_msg = f"Error in {section}: {str(e)}"
                logger.error(error_msg)
                generation_errors.append(error_msg)
                st.session_state.sections_status[section] = 'Error'
                sections_status.error(f"❌ {section}: {str(e)}")
                continue

        # Validate complete protocol
        validation_results = validate_protocol_quality(study_type, st.session_state.generated_sections)
        
        # Final status update
        total_time = datetime.now() - start_time
        if successful_sections == total_sections:
            progress_placeholder.success(f"✅ Protocol generated successfully! ({total_time.total_seconds():.1f}s)")
            
            # Show validation results if there are any issues
            if validation_results["missing_elements"]:
                with st.expander("📋 Protocol Quality Check"):
                    st.warning("Some recommended elements are missing:")
                    for missing in validation_results["missing_elements"]:
                        st.write(f"- {missing['category']}: {missing['element']}")
            
            st.balloons()
            return True
        else:
            progress_placeholder.warning(
                f"⚠️ Generated {successful_sections}/{total_sections} sections ({total_time.total_seconds():.1f}s)"
            )
            if generation_errors:
                with st.expander("View Generation Errors"):
                    for error in generation_errors:
                        st.error(error)
            return False

    except Exception as e:
        logger.error(f"Error in protocol generation: {str(e)}")
        st.error(f"❌ Error: {str(e)}")
        return False

def render_navigator():
    """Render the section navigator sidebar"""
    st.sidebar.markdown("## 🚀 Protocol Generation")
    
    # Initialize sections status
    _initialize_sections_status()
    
    # Check prerequisites
    can_generate = (
        st.session_state.get('synopsis_content') is not None and 
        st.session_state.get('study_type') is not None
    )

    if can_generate:
        # Add enhanced styling for the generation button
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

        # Add generation button with unique key
        if st.sidebar.button(
            "🚀 Generate Complete Protocol",
            help="Generate all protocol sections from your synopsis",
            use_container_width=True,
            key="nav_generate_protocol"
        ):
            with st.spinner("Generating protocol..."):
                if generate_all_sections():
                    # If generation successful, show export options
                    st.sidebar.success("✅ Protocol generated successfully!")
                    
                    # Add export format selection with unique key
                    format_option = st.sidebar.radio(
                        "Export Format:",
                        ["DOCX", "PDF"],
                        key="navigator_export_format"
                    )
                    
                    if st.sidebar.button("Export Protocol", key="nav_export_button"):
                        try:
                            formatter = ProtocolFormatter()
                            doc = formatter.format_protocol(st.session_state.generated_sections)
                            
                            if format_option == "PDF":
                                output_file = formatter.save_document("protocol", format='pdf')
                                with open(output_file, "rb") as file:
                                    st.sidebar.download_button(
                                        label="Download Protocol (PDF)",
                                        data=file,
                                        file_name="protocol.pdf",
                                        mime="application/pdf",
                                        key="nav_download_pdf"
                                    )
                            else:  # DOCX format
                                output_file = formatter.save_document("protocol", format='docx')
                                with open(output_file, "rb") as file:
                                    st.sidebar.download_button(
                                        label="Download Protocol (DOCX)",
                                        data=file,
                                        file_name="protocol.docx",
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        key="nav_download_docx"
                                    )
                        except Exception as e:
                            st.sidebar.error(f"Error exporting protocol: {str(e)}")
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
        
        # Show overall progress
        completed = sum(1 for status in st.session_state.sections_status.values() 
                       if status == 'Generated')
        total = len(sections)
        progress = completed / total if total > 0 else 0
        st.sidebar.progress(progress, text=f"Progress: {completed}/{total} sections")

        # Section navigation with status indicators
        status_indicators = {
            'Not Started': {'icon': '⚪', 'desc': 'Not started yet', 'color': 'gray'},
            'In Progress': {'icon': '🟡', 'desc': 'Generation in progress', 'color': '#FFD700'},
            'Generated': {'icon': '🟢', 'desc': 'Generated successfully', 'color': '#4CAF50'},
            'Error': {'icon': '🔴', 'desc': 'Error in generation', 'color': '#FF0000'}
        }

        for section in sections:
            status = st.session_state.sections_status.get(section, 'Not Started')
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
