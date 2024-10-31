import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator, STUDY_TYPE_CONFIG
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def _get_sections_for_study_type(study_type):
    """Get the appropriate sections for the given study type"""
    study_type_key = _normalize_study_type(study_type)
    if study_type_key in STUDY_TYPE_CONFIG:
        return STUDY_TYPE_CONFIG[study_type_key]["required_sections"]
    return STUDY_TYPE_CONFIG["Clinical Trial"]["required_sections"]

def _normalize_study_type(study_type):
    """Normalize study type string to match config keys"""
    study_type = study_type.lower() if study_type else ""
    if any(phase in study_type for phase in ["phase1", "phase 1", "phase2", "phase 2", "phase3", "phase 3"]):
        return "Clinical Trial"
    elif any(term in study_type for term in ["systematic", "literature review", "slr"]):
        return "Systematic Literature Review"
    elif "meta" in study_type:
        return "Meta-analysis"
    elif any(term in study_type for term in ["real world", "rwe"]):
        return "Real World Evidence"
    elif "consensus" in study_type:
        return "Consensus Method"
    return "Clinical Trial"

def _format_section_name(section_name):
    """Format section name for display"""
    return section_name.replace('_', ' ').title()

def _initialize_sections_status():
    """Initialize or update sections status"""
    if 'sections_status' not in st.session_state:
        st.session_state.sections_status = {}
    
    study_type = st.session_state.get('study_type')
    if study_type:
        sections = _get_sections_for_study_type(study_type)
        for section in sections:
            if section not in st.session_state.sections_status:
                st.session_state.sections_status[section] = 'Not Started'

def generate_all_sections():
    """Generate all protocol sections with enhanced progress tracking"""
    if not st.session_state.get('synopsis_content'):
        st.error("⚠️ Please upload a synopsis first")
        return False
    if not st.session_state.get('study_type'):
        st.error("⚠️ Please select a study type first")
        return False

    try:
        # Initialize generator
        generator = TemplateSectionGenerator()
        
        # Create progress indicators
        progress = st.progress(0)
        status = st.empty()
        detailed_status = st.empty()

        # Get sections for study type
        study_type = st.session_state.study_type
        sections = _get_sections_for_study_type(study_type)
        total_sections = len(sections)
        
        # Initialize tracking
        if 'generated_sections' not in st.session_state:
            st.session_state.generated_sections = {}

        successful_sections = 0
        start_time = datetime.now()

        # Generate each section
        for idx, section in enumerate(sections, 1):
            section_start = datetime.now()
            status.info(f"📝 Generating {_format_section_name(section)}...")
            st.session_state.sections_status[section] = 'In Progress'

            try:
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
                    progress.progress(idx / total_sections)
                    section_time = datetime.now() - section_start
                    detailed_status.success(
                        f"✅ {_format_section_name(section)} "
                        f"({section_time.total_seconds():.1f}s)"
                    )
                else:
                    raise ValueError(f"No content generated for {section}")

            except Exception as e:
                logger.error(f"Error generating {section}: {str(e)}")
                st.session_state.sections_status[section] = 'Error'
                detailed_status.error(f"❌ {_format_section_name(section)}: {str(e)}")
                continue

        # Final status
        total_time = datetime.now() - start_time
        if successful_sections == total_sections:
            status.success(f"✅ Protocol generated successfully! ({total_time.total_seconds():.1f}s)")
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
        st.error(f"❌ Error: {str(e)}")
        return False

def render_navigator():
    """Render the section navigator sidebar"""
    st.sidebar.markdown("## 🚀 Protocol Generation")
    
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

        if st.sidebar.button(
            "🚀 Generate Complete Protocol",
            help="Generate all protocol sections from your synopsis",
            use_container_width=True
        ):
            generate_all_sections()
    else:
        if not st.session_state.get('synopsis_content'):
            st.sidebar.warning("⚠️ Please upload a synopsis first")
        if not st.session_state.get('study_type'):
            st.sidebar.warning("⚠️ Please select a study type")

    st.sidebar.markdown("---")

    # Section Navigation
    st.sidebar.header("📑 Protocol Sections")
    
    # Initialize sections status
    _initialize_sections_status()
    
    if st.session_state.get('study_type'):
        sections = _get_sections_for_study_type(st.session_state.get('study_type'))
        
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
                    _format_section_name(section),
                    key=f"nav_{section}",
                    help=f"Edit {_format_section_name(section)} section",
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
