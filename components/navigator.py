import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator

def render_navigator():
    """Render the section navigator sidebar"""
    # Debug information at the top
    st.sidebar.write("Debug Session State:", {
        "synopsis_content": st.session_state.get('synopsis_content', 'None'),
        "study_type": st.session_state.get('study_type', 'None'),
        "sections_status": st.session_state.get('sections_status', {}),
        "current_section": st.session_state.get('current_section', 'None')
    })

    st.sidebar.header("Protocol Sections")

    # Status indicators with tooltips
    status_indicators = {
        'Not Started': {'icon': '⚪', 'desc': 'Not started yet'},
        'In Progress': {'icon': '🟡', 'desc': 'Generation in progress'},
        'Generated': {'icon': '🟢', 'desc': 'Generated successfully'},
        'Review': {'icon': '🟣', 'desc': 'Ready for review'},
        'Error': {'icon': '🔴', 'desc': 'Error in generation'}
    }

    # Section selection
    st.sidebar.markdown("### Navigate Sections")

    for section, status in st.session_state.sections_status.items():
        col1, col2 = st.sidebar.columns([3, 1])

        # Make the section name clickable
        with col1:
            if st.button(
                section.replace('_', ' ').title(),
                key=f"nav_{section}",
                help=f"Click to edit {section} section"
            ):
                st.session_state.current_section = section
                st.experimental_rerun()

        # Show status indicator
        with col2:
            indicator = status_indicators.get(status, status_indicators['Not Started'])
            st.write(f"{indicator['icon']} ", help=indicator['desc'])

    st.sidebar.markdown("---")

    # Generation controls in sidebar
    st.sidebar.markdown("### Generation Controls")

    # Only show generation buttons if we have synopsis and study type
    if st.session_state.get('synopsis_content') and st.session_state.get('study_type'):
        if st.sidebar.button("🚀 Generate All Sections", 
                           help="Generate all protocol sections at once",
                           use_container_width=True):
            generate_all_sections()

        # Option to regenerate failed sections
        failed_sections = [s for s, status in st.session_state.sections_status.items() 
                         if status in ['Error', 'Not Started']]
        if failed_sections:
            if st.sidebar.button("🔄 Retry Failed Sections",
                               help="Retry generating failed sections",
                               use_container_width=True):
                regenerate_failed_sections(failed_sections)
    else:
        if not st.session_state.get('synopsis_content'):
            st.sidebar.warning("⚠️ Upload synopsis first")
        if not st.session_state.get('study_type'):
            st.sidebar.warning("⚠️ Select study type first")

def generate_all_sections():
    """Generate all protocol sections"""
    generator = TemplateSectionGenerator()

    progress = st.sidebar.progress(0)
    status = st.sidebar.empty()

    try:
        sections = list(st.session_state.sections_status.keys())
        total_sections = len(sections)

        for idx, section in enumerate(sections):
            status.text(f"Generating {section.replace('_', ' ').title()}...")
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

            except Exception as e:
                st.session_state.sections_status[section] = 'Error'
                st.sidebar.error(f"Error in {section}: {str(e)}")
                continue

            progress.progress((idx + 1) / total_sections)

        # Final status update
        generated = sum(1 for s in st.session_state.sections_status.values() if s == 'Generated')
        if generated == total_sections:
            status.success("✅ All sections generated!")
        else:
            status.warning(f"⚠️ Generated {generated}/{total_sections} sections")

    except Exception as e:
        status.error(f"❌ Error: {str(e)}")
    finally:
        st.experimental_rerun()

def regenerate_failed_sections(failed_sections):
    """Regenerate only the failed sections"""
    generator = TemplateSectionGenerator()

    progress = st.sidebar.progress(0)
    status = st.sidebar.empty()

    try:
        total = len(failed_sections)
        for idx, section in enumerate(failed_sections):
            status.text(f"Regenerating {section.replace('_', ' ').title()}...")
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

            except Exception as e:
                st.session_state.sections_status[section] = 'Error'
                st.sidebar.error(f"Error in {section}: {str(e)}")
                continue

            progress.progress((idx + 1) / total)

        status.success("✅ Retry complete!")

    except Exception as e:
        status.error(f"❌ Error: {str(e)}")
    finally:
        st.experimental_rerun()
