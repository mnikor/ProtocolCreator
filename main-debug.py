def init_session_state():
    """Initialize session state variables"""
    # Debug mode
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = True
        
    if 'synopsis_content' not in st.session_state:
        st.session_state.synopsis_content = None
        
    if 'current_section' not in st.session_state:
        st.session_state.current_section = None
        
    if 'study_type' not in st.session_state:
        st.session_state.study_type = None
        
    if 'template_manager' not in st.session_state:
        st.session_state.template_manager = TemplateManager()
        
    if 'generated_sections' not in st.session_state:
        st.session_state.generated_sections = {}
        
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

def main():
    st.set_page_config(
        page_title="Protocol Development Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    st.title("Protocol Development Assistant")
    
    # Debug information at the top
    if st.session_state.debug_mode:
        with st.expander("Debug Information", expanded=False):
            st.write({
                "synopsis_content": bool(st.session_state.get('synopsis_content')),
                "study_type": st.session_state.get('study_type'),
                "sections_status": st.session_state.get('sections_status'),
                "current_section": st.session_state.get('current_section')
            })
    
    # Main application flow
    if st.session_state.synopsis_content is None:
        render_input_section()
    else:
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
            
            render_navigator()
        
        # Main content area
        tab1, tab2 = st.tabs(["Protocol Editor", "Compliance Check"])
        with tab1:
            render_editor()
        with tab2:
            render_compliance_checker()
            
    # Add footer
    st.markdown("---")
    st.markdown("Protocol Development Assistant v1.0")