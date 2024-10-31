import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator, STUDY_TYPE_CONFIG
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def _get_sections_for_study_type(study_type):
    """Get the appropriate sections for the given study type"""
    # Check if study type exists in configuration
    study_type_key = _normalize_study_type(study_type)
    if study_type_key in STUDY_TYPE_CONFIG:
        return STUDY_TYPE_CONFIG[study_type_key]["required_sections"]
    return STUDY_TYPE_CONFIG["Clinical Trial"]["required_sections"]

def _normalize_study_type(study_type):
    """Normalize study type string to match config keys"""
    study_type = study_type.lower() if study_type else ""
    if "phase1" in study_type or "phase 1" in study_type:
        return "Clinical Trial"
    elif "phase2" in study_type or "phase 2" in study_type:
        return "Clinical Trial"
    elif "phase3" in study_type or "phase 3" in study_type:
        return "Clinical Trial"
    elif "systematic" in study_type or "literature review" in study_type or study_type == "slr":
        return "Systematic Literature Review"
    elif "meta" in study_type:
        return "Meta-analysis"
    elif "real world" in study_type or "rwe" in study_type:
        return "Real World Evidence"
    elif "consensus" in study_type:
        return "Consensus Method"
    return "Clinical Trial"

def _format_section_name(section_name):
    """Format section name for display"""
    return section_name.replace('_', ' ').title()

def _initialize_sections_status(sections):
    """Initialize or update sections status"""
    if 'sections_status' not in st.session_state:
        st.session_state.sections_status = {}
    
    # Update existing status dict with any new sections
    for section in sections:
        if section not in st.session_state.sections_status:
            st.session_state.sections_status[section] = 'Not Started'

def generate_all_sections():
    """Generate all protocol sections with enhanced progress tracking"""
    if not st.session_state.get('synopsis_content'):
        st.sidebar.error("⚠️ Please upload a synopsis first")
        return False
    if not st.session_state.get('study_type'):
        st.sidebar.error("⚠️ Please select a study type first")
        return False

    try:
        # Initialize the generator
        generator = TemplateSectionGenerator()
        if not generator:
            raise ValueError("Failed to initialize TemplateSectionGenerator")

        # Create progress indicators
        progress = st.sidebar.progress(0)
        status = st.sidebar.empty()
        detailed_status = st.sidebar.empty()

        # Get appropriate sections for study type
        study_type = st.session_state.study_type
        sections = _get_sections_for_study_type(study_type)
        total_sections = len(sections)
        
        # Initialize sections status
        _initialize_sections_status(sections)
        
        # Initialize generated sections if not exists
        if 'generated_sections' not in st.session_state:
            st.session_state.generated_sections = {}

        # Track generation progress
        successful_sections = 0
        start_time = datetime.now()

        for idx, section in enumerate(sections, 1):
            section_start = datetime.now()
            status.info(f"📝 Generating {_format_section_name(section)}...")
            st.session_state.sections_status[section] = 'In Progress'

            try:
                content = generator.generate_section(
                    section_name=section,
                    study_type=study_type,
                    synopsis_content=st.session_state.synopsis_content,
                    existing_sections=st.session_state.generated_sections
                )

                if content and isinstance(content, str):
                    # Store generated content
                    st.session_state.generated_sections[section] = content
                    st.session_state.sections_status[section] = 'Generated'
                    successful_sections += 1

                    # Update progress
                    section_time = datetime.now() - section_start
                    progress.progress(idx / total_sections)
                    detailed_status.success(
                        f"✅ {_format_section_name(section)} "
                        f"({section_time.total_seconds():.1f}s)"
                    )
                else:
                    raise ValueError(f"Invalid content generated for {section}")

            except Exception as e:
                logger.error(f"Error generating {section}: {str(e)}")
                st.session_state.sections_status[section] = 'Error'
                detailed_status.error(f"❌ {_format_section_name(section)}: {str(e)}")
                continue

        # Final status update
        total_time = datetime.now() - start_time
        if successful_sections == total_sections:
            status.success(
                f"✅ Protocol generated successfully! "
                f"({total_time.total_seconds():.1f}s)"
            )
            st.balloons()
            return True
        else:
            status.warning(
                f"⚠️ Generated {successful_sections}/{total_sections} sections. "
                f"({total_time.total_seconds():.1f}s)"
            )
            return False

    except Exception as e:
        logger.error(f"Error in protocol generation: {str(e)}")
        status.error(f"❌ Error: {str(e)}")
        return False

def render_navigator():
    """Render the section navigator sidebar"""
    # Protocol Generation Section
    st.sidebar.markdown("## 🚀 Protocol Generation")
    
    # Check prerequisites
    can_generate = (
        st.session_state.get('synopsis_content') is not None and 
        st.session_state.get('study_type') is not None
    )

    if can_generate:
        # Protocol Generation Button with enhanced styling
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

        if st.sidebar.button(
            "🚀 Generate Complete Protocol",
            help="Generate all protocol sections from your synopsis",
            use_container_width=True,
            key='generate_complete_protocol'
        ):
            if generate_all_sections():
                st.session_state.generation_complete = True
    else:
        if not st.session_state.get('synopsis_content'):
            st.sidebar.warning("⚠️ Please upload a synopsis first")
        if not st.session_state.get('study_type'):
            st.sidebar.warning("⚠️ Please select a study type")

    st.sidebar.markdown("---")

    # Section Navigation
    st.sidebar.header("📑 Protocol Sections")

    # Get sections for current study type
    if st.session_state.get('study_type'):
        sections = _get_sections_for_study_type(st.session_state.get('study_type'))
        _initialize_sections_status(sections)
        
        # Progress tracking
        total_sections = len(sections)
        completed_sections = sum(1 for status in st.session_state.sections_status.values() 
                               if status == 'Generated')
        
        # Show overall progress
        progress = completed_sections / total_sections if total_sections > 0 else 0
        st.sidebar.progress(progress, text=f"Progress: {completed_sections}/{total_sections} sections")

        # Status indicators with tooltips
        status_indicators = {
            'Not Started': {'icon': '⚪', 'desc': 'Not started yet', 'color': 'gray'},
            'In Progress': {'icon': '🟡', 'desc': 'Generation in progress', 'color': '#FFD700'},
            'Generated': {'icon': '🟢', 'desc': 'Generated successfully', 'color': '#4CAF50'},
            'Error': {'icon': '🔴', 'desc': 'Error in generation', 'color': '#FF0000'}
        }

        # Section navigation with status indicators
        for section in sections:
            status = st.session_state.sections_status.get(section, 'Not Started')
            col1, col2 = st.sidebar.columns([3, 1])
            
            with col1:
                if st.button(
                    _format_section_name(section),
                    key=f"nav_{section}",
                    help=f"Click to edit {_format_section_name(section)} section",
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
