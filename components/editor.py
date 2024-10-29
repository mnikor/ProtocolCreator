import streamlit as st
from utils.gpt_handler import GPTHandler
from utils.protocol_formatter import ProtocolFormatter

def render_editor():
    """Render the protocol editor interface"""
    st.header("Protocol Editor")
    
    if st.session_state.current_section:
        edit_section(st.session_state.current_section)
    else:
        st.info("Select a section from the navigator to begin editing")

def edit_section(section_name):
    """Edit individual protocol section"""
    st.subheader(section_name.replace('_', ' ').title())
    
    # Generate button if section not yet generated
    if section_name not in st.session_state.generated_sections:
        if st.button("Generate Section"):
            generate_section(section_name)
            
    # Edit interface
    if section_name in st.session_state.generated_sections:
        content = st.text_area(
            "Edit Content",
            value=st.session_state.generated_sections[section_name],
            height=400
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Save Changes"):
                st.session_state.generated_sections[section_name] = content
                st.success("Changes saved!")
                
        with col2:
            if st.button("Regenerate"):
                generate_section(section_name)
                
    # Export options
    if st.session_state.generated_sections:
        st.subheader("Export Options")
        if st.button("Export Protocol"):
            export_protocol()

def generate_section(section_name):
    """Generate individual protocol section"""
    with st.spinner("Generating section..."):
        try:
            gpt_handler = GPTHandler()
            content = gpt_handler.generate_section(
                section_name,
                st.session_state.synopsis_content,
                st.session_state.generated_sections
            )
            st.session_state.generated_sections[section_name] = content
            st.session_state.sections_status[section_name] = 'Generated'
            st.success("Section generated successfully!")
            
        except Exception as e:
            st.error(f"Error generating section: {str(e)}")

def export_protocol():
    """Export complete protocol document"""
    try:
        formatter = ProtocolFormatter()
        doc = formatter.format_protocol(st.session_state.generated_sections)
        
        # Save temporarily and provide download link
        doc.save("protocol.docx")
        
        with open("protocol.docx", "rb") as file:
            st.download_button(
                label="Download Protocol",
                data=file,
                file_name="protocol.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
    except Exception as e:
        st.error(f"Error exporting protocol: {str(e)}")
