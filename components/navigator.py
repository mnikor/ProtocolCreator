import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_all_sections():
    """Generate all protocol sections with enhanced progress tracking"""
    generator = TemplateSectionGenerator()
    
    # Create progress indicators
    progress = st.sidebar.progress(0)
    status = st.sidebar.empty()
    detailed_status = st.sidebar.empty()

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
    finally:
        st.experimental_rerun()

def render_navigator():
    """Render the section navigator sidebar"""
    # Debug information at the top with enhanced display
    with st.sidebar.expander("🔍 Debug Info", expanded=True):
        st.write({
            "Synopsis Present": st.session_state.get('synopsis_content') is not None,
            "Synopsis Length": len(st.session_state.get('synopsis_content', '')) if st.session_state.get('synopsis_content') else 0,
            "Study Type": st.session_state.get('study_type'),
            "Sections Status": st.session_state.get('sections_status', {}),
            "Current Section": st.session_state.get('current_section')
        })

    # Protocol Generation Section with enhanced styling
    st.sidebar.markdown("## 🚀 Protocol Generation")
    
    if st.session_state.get('synopsis_content') is not None and st.session_state.get('study_type'):
        st.sidebar.markdown("Generate a complete protocol from your synopsis")
        
        # Add enhanced styling
        st.sidebar.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 0.5rem;
                border-radius: 5px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Primary generation button
        if st.sidebar.button(
            "🚀 Generate Complete Protocol",
            help="Generate all protocol sections at once",
            use_container_width=True
        ):
            try:
                with st.spinner("Generating complete protocol..."):
                    generate_all_sections()
            except Exception as e:
                st.error(f"Error generating protocol: {str(e)}")
    else:
        if st.session_state.get('synopsis_content') is None:
            st.sidebar.warning("⚠️ Please upload synopsis first")
        if not st.session_state.get('study_type'):
            st.sidebar.warning("⚠️ Please select study type")

    st.sidebar.markdown("---")

    # Section Navigation
    st.sidebar.header("Protocol Sections")
    
    # Progress tracking
    total_sections = len(st.session_state.sections_status)
    completed_sections = sum(1 for status in st.session_state.sections_status.values() 
                           if status == 'Generated')
    
    # Show overall progress
    progress = completed_sections / total_sections if total_sections > 0 else 0
    st.sidebar.progress(progress, text=f"Progress: {completed_sections}/{total_sections} sections")

    # Enhanced status indicators
    status_indicators = {
        'Not Started': {'icon': '⚪', 'desc': 'Not started yet', 'color': 'gray'},
        'In Progress': {'icon': '🟡', 'desc': 'Generation in progress', 'color': 'yellow'},
        'Generated': {'icon': '🟢', 'desc': 'Generated successfully', 'color': 'green'},
        'Review': {'icon': '🟣', 'desc': 'Ready for review', 'color': 'purple'},
        'Error': {'icon': '🔴', 'desc': 'Error in generation', 'color': 'red'}
    }

    # Section navigation with enhanced status display
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
                logger.info(f"Navigating to section: {section}")
                st.experimental_rerun()

        with col2:
            indicator = status_indicators.get(status, status_indicators['Not Started'])
            st.markdown(
                f"<span style='color: {indicator['color']}'>{indicator['icon']}</span>",
                help=indicator['desc'],
                unsafe_allow_html=True
            )

    # Additional Controls
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Additional Controls")

    # Retry failed sections
    failed_sections = [s for s, status in st.session_state.sections_status.items() 
                      if status in ['Error', 'Not Started']]
    if failed_sections:
        if st.sidebar.button(
            f"🔄 Retry Failed Sections ({len(failed_sections)})",
            help="Retry generating failed sections",
            use_container_width=True
        ):
            try:
                with st.spinner("Retrying failed sections..."):
                    regenerate_failed_sections(failed_sections)
            except Exception as e:
                st.error(f"Error retrying sections: {str(e)}")

def regenerate_failed_sections(failed_sections):
    """Regenerate failed sections with enhanced error handling"""
    generator = TemplateSectionGenerator()
    
    progress = st.sidebar.progress(0)
    status = st.sidebar.empty()
    detailed_status = st.sidebar.empty()

    try:
        total = len(failed_sections)
        start_time = datetime.now()

        for idx, section in enumerate(failed_sections):
            section_start = datetime.now()
            status.info(f"🔄 Regenerating {section.replace('_', ' ').title()}...")
            st.session_state.sections_status[section] = 'In Progress'

            try:
                content = generator.generate_section(
                    section,
                    st.session_state.study_type,
                    st.session_state.synopsis_content,
                    st.session_state.generated_sections
                )

                st.session_state.generated_sections[section] = content
                st.session_state.sections_status[section] = 'Generated'

                section_time = datetime.now() - section_start
                progress.progress((idx + 1) / total)
                detailed_status.success(
                    f"✅ {section.replace('_', ' ').title()} "
                    f"({section_time.total_seconds():.1f}s)"
                )

            except Exception as e:
                logger.error(f"Error regenerating {section}: {str(e)}")
                st.session_state.sections_status[section] = 'Error'
                detailed_status.error(f"❌ {section}: {str(e)}")
                continue

        total_time = datetime.now() - start_time
        regenerated = sum(1 for s in failed_sections 
                         if st.session_state.sections_status[s] == 'Generated')
        
        if regenerated == total:
            status.success(
                f"✅ All sections regenerated successfully! "
                f"({total_time.total_seconds():.1f}s)"
            )
        else:
            status.warning(
                f"⚠️ Regenerated {regenerated}/{total} sections. "
                f"({total_time.total_seconds():.1f}s)"
            )

    except Exception as e:
        logger.error(f"Error in regeneration: {str(e)}")
        status.error(f"❌ Error: {str(e)}")
    finally:
        st.experimental_rerun()
