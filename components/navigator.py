import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_all_sections():
    """Generate all protocol sections with enhanced progress tracking"""
    if not st.session_state.get('synopsis_content'):
        st.error("Please upload a synopsis first")
        return
    if not st.session_state.get('study_type'):
        st.error("Please select a study type first")
        return

    # Initialize the generator
    generator = TemplateSectionGenerator()

    # Create progress indicators
    progress = st.progress(0)
    status = st.empty()
    detailed_status = st.empty()

    try:
        sections = list(st.session_state.sections_status.keys())
        total_sections = len(sections)
        start_time = datetime.now()

        for idx, section in enumerate(sections):
            section_start = datetime.now()
            status.info(f"📝 Generating {section.replace('_', ' ').title()}...")
            st.session_state.sections_status[section] = 'In Progress'

            try:
                # Generate section content
                content = generator.generate_section(
                    section,
                    st.session_state.study_type,
                    st.session_state.synopsis_content,
                    st.session_state.generated_sections
                )

                # Update session state
                st.session_state.generated_sections[section] = content
                st.session_state.sections_status[section] = 'Generated'

                # Update progress
                section_time = datetime.now() - section_start
                progress.progress((idx + 1) / total_sections)
                detailed_status.success(
                    f"✅ {section.replace('_', ' ').title()} "
                    f"({section_time.total_seconds():.1f}s)"
                )

            except Exception as e:
                logger.error(f"Error generating {section}: {str(e)}")
                st.session_state.sections_status[section] = 'Error'
                detailed_status.error(f"❌ {section}: {str(e)}")
                continue

        # Final status update
        total_time = datetime.now() - start_time
        generated = sum(1 for s in st.session_state.sections_status.values() if s == 'Generated')

        if generated == total_sections:
            status.success(
                f"✅ Protocol generated successfully! "
                f"({total_time.total_seconds():.1f}s)"
            )
            st.balloons()
        else:
            status.warning(
                f"⚠️ Generated {generated}/{total_sections} sections. "
                f"({total_time.total_seconds():.1f}s)"
            )

    except Exception as e:
        logger.error(f"Error in protocol generation: {str(e)}")
        status.error(f"❌ Error: {str(e)}")

def render_navigator():
    """Render the section navigator sidebar"""
    # Protocol Generation Section at the top
    st.sidebar.markdown("## 🚀 Protocol Generation")

    # Check prerequisites
    can_generate = (
        st.session_state.get('synopsis_content') is not None and 
        st.session_state.get('study_type') is not None
    )

    if can_generate:
        # Protocol Generation Button with improved styling
        st.sidebar.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 1rem;
                border-radius: 10px;
                margin: 20px 0;
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
            generate_all_sections()
    else:
        if not st.session_state.get('synopsis_content'):
            st.sidebar.warning("⚠️ Please upload a synopsis first")
        if not st.session_state.get('study_type'):
            st.sidebar.warning("⚠️ Please select a study type")

    st.sidebar.markdown("---")

    # Section Navigation
    st.sidebar.header("📑 Protocol Sections")

    # Progress tracking
    total_sections = len(st.session_state.sections_status)
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

    # Section navigation with improved styling
    for section, status in st.session_state.sections_status.items():
        col1, col2 = st.sidebar.columns([3, 1])
        
        with col1:
            if st.button(
                section.replace('_', ' ').title(),
                key=f"nav_{section}",
                help=f"Click to edit {section} section",
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

    # Retry failed sections option
    failed_sections = [s for s, status in st.session_state.sections_status.items() 
                      if status in ['Error', 'Not Started']]
    if failed_sections and can_generate:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔄 Retry Failed Sections")
        if st.sidebar.button(
            f"Retry {len(failed_sections)} Failed Section(s)",
            help="Retry generating failed sections",
            use_container_width=True,
            key='retry_failed'
        ):
            for section in failed_sections:
                try:
                    generator = TemplateSectionGenerator()
                    content = generator.generate_section(
                        section,
                        st.session_state.study_type,
                        st.session_state.synopsis_content,
                        st.session_state.generated_sections
                    )
                    st.session_state.generated_sections[section] = content
                    st.session_state.sections_status[section] = 'Generated'
                except Exception as e:
                    logger.error(f"Error regenerating {section}: {str(e)}")
                    st.session_state.sections_status[section] = 'Error'
                    continue
