import streamlit as st
import logging

logger = logging.getLogger(__name__)

def render_editor():
    st.markdown("## Protocol Editor")
    
    # Check prerequisites
    if not st.session_state.get('synopsis_content'):
        st.warning("Please upload a synopsis first")
        return
    if not st.session_state.get('study_type'):
        st.warning("Please select a study type first")
        return
    
    # Display generated sections if available
    if generated_sections := st.session_state.get('generated_sections'):
        for section_name, content in generated_sections.items():
            with st.expander(f"📝 {section_name.replace('_', ' ').title()}", expanded=False):
                st.text_area(
                    "Section content",
                    value=content,
                    height=300,
                    disabled=True,
                    key=f"section_{section_name}"
                )
    else:
        st.info("Use the 'Generate Complete Protocol' button in the sidebar to generate protocol sections.")
