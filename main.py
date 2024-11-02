import streamlit as st
from components.navigator import render_navigator
from components.editor import render_editor
from components.input_section import render_input_section

def main():
    st.set_page_config(
        page_title="Protocol Development Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add styling to hide debug elements and improve UI
    st.markdown("""
        <style>
        .stDebug {
            display: none !important;
        }
        .element-container div[data-testid="stDebugElement"] {
            display: none !important;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            padding: 0.75rem;
            border-radius: 10px;
            margin: 10px 0;
            width: 100%;
        }
        .main-content {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        .section-header {
            color: #2c3e50;
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'study_type' not in st.session_state:
        st.session_state.study_type = None
    if 'synopsis_content' not in st.session_state:
        st.session_state.synopsis_content = None
    if 'generated_sections' not in st.session_state:
        st.session_state.generated_sections = {}

    # Render components
    render_navigator()
    
    # Main content area
    with st.container():
        st.title("Protocol Development Assistant")
        
        if not st.session_state.synopsis_content:
            render_input_section()
        else:
            render_editor()

if __name__ == "__main__":
    main()
