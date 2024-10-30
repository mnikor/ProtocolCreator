import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter

def render_editor():
    """Render the protocol editor interface"""
    st.header("Protocol Editor")
    
    # Add Generate Complete Protocol button at the top
    if st.button("🔄 Generate Complete Protocol", key="generate_complete"):
        generate_complete_protocol()
    
    if st.session_state.current_section:
        edit_section(st.session_state.current_section)
    else:
        st.info("Select a section from the navigator to begin editing")

def generate_complete_protocol():
    """Generate all protocol sections in sequence"""
    generator = TemplateSectionGenerator()
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_container = st.empty()
    
    total_sections = len(st.session_state.sections_status)
    completed = 0
    
    try:
        for section_name in st.session_state.sections_status.keys():
            # Update progress
            status_container.info(f"Generating {section_name.replace('_', ' ').title()} section...")
            st.session_state.sections_status[section_name] = 'In Progress'
            
            try:
                # Generate section content
                content = generator.generate_section(
                    section_name,
                    st.session_state.study_type,
                    st.session_state.synopsis_content,
                    st.session_state.generated_sections
                )
                
                # Update session state
                st.session_state.generated_sections[section_name] = content
                st.session_state.sections_status[section_name] = 'Generated'
                
                # Update progress
                completed += 1
                progress_bar.progress(completed / total_sections)
                
            except Exception as e:
                st.error(f"Error generating {section_name} section: {str(e)}")
                st.session_state.sections_status[section_name] = 'Not Started'
                continue
        
        # Final status update
        if completed == total_sections:
            status_container.success("✅ Protocol generation completed successfully!")
        else:
            status_container.warning(f"⚠️ Protocol generation completed with {total_sections - completed} failed sections")
            
    except Exception as e:
        status_container.error(f"❌ Error during protocol generation: {str(e)}")

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
    """Generate individual protocol section using templates"""
    with st.spinner("Generating section..."):
        try:
            generator = TemplateSectionGenerator()
            content = generator.generate_section(
                section_name,
                st.session_state.study_type,
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
