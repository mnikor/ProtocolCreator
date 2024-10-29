import streamlit as st
import os
from components.input_section import render_input_section
from components.navigator import render_navigator
from components.editor import render_editor
from utils.synopsis_validator import validate_synopsis
from utils.protocol_formatter import ProtocolFormatter

def init_session_state():
    if 'synopsis_content' not in st.session_state:
        st.session_state.synopsis_content = None
    if 'current_section' not in st.session_state:
        st.session_state.current_section = None
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
        # Use sidebar for navigation
        with st.sidebar:
            render_navigator()
        
        # Main content area for editor
        render_editor()
    else:
        # Show input section when no synopsis is available
        render_input_section()

    # Add footer
    st.markdown("---")
    st.markdown("Protocol Development Assistant v1.0")

if __name__ == "__main__":
    main()
