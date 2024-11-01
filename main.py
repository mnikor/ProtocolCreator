import streamlit as st
from components.input_section import render_input_section
from components.navigator import render_navigator
from components.editor import render_editor
from utils.template_manager import TemplateManager

def init_session_state():
    """Initialize session state variables"""
    # Initialize only if not already present
    if 'synopsis_content' not in st.session_state:
        st.session_state.synopsis_content = None
    if 'synopsis_analysis' not in st.session_state:
        st.session_state.synopsis_analysis = None
    if 'detected_phase' not in st.session_state:
        st.session_state.detected_phase = None
    if 'study_type' not in st.session_state:
        st.session_state.study_type = None
    if 'template_manager' not in st.session_state:
        st.session_state.template_manager = TemplateManager()
    if 'sections_status' not in st.session_state:
        st.session_state.sections_status = {
            'background': 'Not Started',
            'objectives': 'Not Started',
            'study_design': 'Not Started',
            'population': 'Not Started',
            'procedures': 'Not Started',
            'statistical_analysis': 'Not Started',  # Updated name
            'safety': 'Not Started'
        }
    if 'generated_sections' not in st.session_state:
        st.session_state.generated_sections = {}

def main():
    # Set page config
    st.set_page_config(
        page_title="Protocol Development Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    init_session_state()

    # Page title
    st.title("Protocol Development Assistant")

    # Debug information
    with st.expander("🔍 Session State Debug", expanded=True):
        st.write({
            "Synopsis Present": st.session_state.get('synopsis_content') is not None,
            "Synopsis Length": len(st.session_state.get('synopsis_content', '')) if st.session_state.get('synopsis_content') else 0,
            "Study Type": st.session_state.get('study_type'),
            "Detected Phase": st.session_state.get('detected_phase'),
            "Generated Sections": list(st.session_state.get('generated_sections', {}).keys()),
            "Sections Status": st.session_state.get('sections_status', {})
        })

    # Main flow
    if not st.session_state.get('synopsis_content'):
        render_input_section()
    else:
        # Show sidebar navigation if study type is selected
        if st.session_state.get('study_type'):
            tab1, tab2 = st.tabs(["Protocol Editor", "Compliance Check"])
            with tab1:
                col1, col2 = st.columns([1, 3])
                with col1:
                    render_navigator()
                with col2:
                    render_editor()
        else:
            # If synopsis is uploaded but study type not selected,
            # render input section to complete the phase selection
            render_input_section()

if __name__ == "__main__":
    main()
