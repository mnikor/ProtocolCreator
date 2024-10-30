import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_complete_protocol(generator):
    """Generate complete protocol using the template generator"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    sections_status = st.empty()
    
    total_sections = len(st.session_state.sections_status)
    completed = 0
    
    # Track generation progress
    for section_name in st.session_state.sections_status.keys():
        try:
            status_text.info(f"📝 Generating {section_name.replace('_', ' ').title()}...")
            st.session_state.sections_status[section_name] = 'In Progress'
            
            # Generate section content
            content = generator.generate_section(
                section_name,
                st.session_state.study_type,
                st.session_state.synopsis_content,
                st.session_state.generated_sections
            )
            
            # Update status
            st.session_state.generated_sections[section_name] = content
            st.session_state.sections_status[section_name] = 'Generated'
            completed += 1
            
            # Update progress
            progress_bar.progress(completed / total_sections)
            sections_status.success(f"✅ {section_name.replace('_', ' ').title()} completed")
            
        except Exception as e:
            logger.error(f"Error generating {section_name}: {str(e)}")
            st.session_state.sections_status[section_name] = 'Error'
            sections_status.error(f"❌ Error in {section_name}: {str(e)}")
            continue
    
    # Final status update
    if completed == total_sections:
        st.success("✅ Protocol generation completed successfully!")
        st.balloons()
    else:
        st.warning(f"⚠️ Generated {completed}/{total_sections} sections. Some sections need attention.")

def render_editor():
    """Render the protocol editor interface"""
    st.header("Protocol Editor")
    
    # Generate Protocol Button at the top
    st.markdown("## Generate Protocol")
    st.markdown("Click the button below to generate a complete protocol from your synopsis")
    
    if st.button('🔄 Generate Complete Protocol', type='primary', use_container_width=True):
        try:
            with st.spinner("Generating protocol..."):
                generator = TemplateSectionGenerator()
                generate_complete_protocol(generator)
        except Exception as e:
            st.error(f"Error generating protocol: {str(e)}")
    
    st.markdown("---")  # Add separator
    
    # Section editing interface
    if st.session_state.get('current_section'):
        edit_section(st.session_state.current_section)
    else:
        st.info("👈 Select a section from the navigator to begin editing")

def edit_section(section_name):
    """Edit individual protocol section"""
    st.subheader(section_name.replace('_', ' ').title())
    
    # Section status indicator with detailed information
    status = st.session_state.sections_status.get(section_name, 'Not Started')
    status_colors = {
        'Not Started': 'blue',
        'In Progress': 'orange',
        'Generated': 'green',
        'Error': 'red'
    }
    st.markdown(f"**Status:** :{status_colors.get(status, 'gray')}[{status}]")
    
    if section_name in st.session_state.generated_sections:
        content = st.text_area(
            "Edit Content",
            value=st.session_state.generated_sections[section_name],
            height=400,
            key=f"edit_{section_name}"
        )
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if st.button("💾 Save Changes", use_container_width=True):
                try:
                    st.session_state.generated_sections[section_name] = content
                    st.success("✅ Changes saved successfully!")
                except Exception as e:
                    logger.error(f"Error saving changes: {str(e)}")
                    st.error(f"❌ Error saving changes: {str(e)}")
        
        with col2:
            if st.button("🔄 Regenerate Section", use_container_width=True):
                try:
                    with st.spinner(f"Regenerating {section_name.replace('_', ' ').title()}..."):
                        generator = TemplateSectionGenerator()
                        new_content = generator.generate_section(
                            section_name,
                            st.session_state.study_type,
                            st.session_state.synopsis_content,
                            st.session_state.generated_sections
                        )
                        st.session_state.generated_sections[section_name] = new_content
                        st.session_state.sections_status[section_name] = 'Generated'
                        st.success("✅ Section regenerated successfully!")
                        st.experimental_rerun()
                except Exception as e:
                    logger.error(f"Error regenerating section: {str(e)}")
                    st.error(f"❌ Error regenerating section: {str(e)}")
        
        with col3:
            if st.button("🔍 Review", use_container_width=True):
                st.session_state.sections_status[section_name] = 'Review'
                st.info("Section marked for review")
    else:
        st.warning("Section not yet generated. Use the generate button above to create content.")

def export_protocol():
    """Export complete protocol document"""
    try:
        with st.spinner("Creating protocol document..."):
            formatter = ProtocolFormatter()
            doc = formatter.format_protocol(st.session_state.generated_sections)
            
            # Save temporarily
            doc.save("protocol.docx")
            
            # Provide download
            with open("protocol.docx", "rb") as file:
                st.download_button(
                    label="📥 Download Protocol",
                    data=file,
                    file_name="protocol.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            st.success("✅ Protocol exported successfully!")
            
    except Exception as e:
        logger.error(f"Error exporting protocol: {str(e)}")
        st.error(f"❌ Error exporting protocol: {str(e)}")
