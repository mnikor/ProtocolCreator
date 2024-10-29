import streamlit as st
import os
import json
from components.input_section import render_input_section
from components.navigator import render_navigator
from components.editor import render_editor
from components.compliance_checker import render_compliance_checker
from utils.synopsis_validator import validate_synopsis
from utils.protocol_formatter import ProtocolFormatter
from utils.template_manager import TemplateManager

def init_session_state():
    if 'synopsis_content' not in st.session_state:
        st.session_state.synopsis_content = None
    if 'current_section' not in st.session_state:
        st.session_state.current_section = None
    if 'study_type' not in st.session_state:
        st.session_state.study_type = None
    if 'sections_status' not in st.session_state:
        st.session_state.sections_status = {
            'background': 'Not Started',
            'objectives': 'Not Started',
            'study_design': 'Not Started',
            'population': 'Not Started',
            'procedures': 'Not Started',
            'statistical': 'Not Started',
            'safety': 'Not Started',
            'references': 'Not Started'
        }
    if 'generated_sections' not in st.session_state:
        st.session_state.generated_sections = {}
    if 'template_manager' not in st.session_state:
        st.session_state.template_manager = TemplateManager()

def main():
    st.set_page_config(
        page_title="Protocol Development Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    st.title("Protocol Development Assistant")

    # Only show navigator if synopsis is available
    if st.session_state.synopsis_content is not None:
        # Template selection in sidebar
        with st.sidebar:
            if st.session_state.study_type is None:
                st.subheader("Select Study Type")
                template_types = st.session_state.template_manager.get_template_types()
                selected_type = st.selectbox(
                    "Study Type",
                    template_types,
                    format_func=lambda x: st.session_state.template_manager.get_template(x)['name']
                )
                if st.button("Confirm Study Type"):
                    st.session_state.study_type = selected_type
                    st.experimental_rerun()
            
            if st.session_state.study_type:
                render_navigator()

        # Main content area
        if st.session_state.study_type:
            tab1, tab2 = st.tabs(["Protocol Editor", "Compliance Check"])
            
            with tab1:
                render_editor()
            with tab2:
                render_compliance_checker()
        else:
            st.info("Please select a study type to begin")
    else:
        # Show input section when no synopsis is available
        render_input_section()

    # Add footer
    st.markdown("---")
    st.markdown("Protocol Development Assistant v1.0")

if __name__ == "__main__":
    main()
