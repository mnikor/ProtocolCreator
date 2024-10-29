import streamlit as st
from utils.gpt_handler import GPTHandler

def render_navigator():
    """Render the section navigator sidebar"""
    st.sidebar.header("Protocol Sections")
    
    # Generate All button
    if st.sidebar.button("Generate All Sections"):
        generate_all_sections()
    
    # Section navigation
    for section, status in st.session_state.sections_status.items():
        col1, col2 = st.sidebar.columns([3, 1])
        
        with col1:
            if st.button(section.replace('_', ' ').title()):
                st.session_state.current_section = section
                
        with col2:
            status_color = {
                'Not Started': '⚪',
                'In Progress': '🟡',
                'Generated': '🟢',
                'Review': '🟣'
            }
            st.write(status_color.get(status, '⚪'))

def generate_all_sections():
    """Generate all protocol sections"""
    if not st.session_state.synopsis_content:
        st.error("Please input synopsis first")
        return
        
    gpt_handler = GPTHandler()
    
    with st.spinner("Generating protocol sections..."):
        try:
            for section in st.session_state.sections_status.keys():
                st.session_state.sections_status[section] = 'In Progress'
                content = gpt_handler.generate_section(
                    section,
                    st.session_state.synopsis_content,
                    st.session_state.generated_sections
                )
                st.session_state.generated_sections[section] = content
                st.session_state.sections_status[section] = 'Generated'
                
            st.success("All sections generated successfully!")
            
        except Exception as e:
            st.error(f"Error generating sections: {str(e)}")
