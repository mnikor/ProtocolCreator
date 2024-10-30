import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_complete_protocol(generator):
    """Generate the complete protocol"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    sections_status = st.empty()
    total_sections = len(st.session_state.sections_status)
    completed = 0
    
    try:
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
            
    except Exception as e:
        logger.error(f"Error in protocol generation: {str(e)}")
        st.error(f"❌ Error generating protocol: {str(e)}")

def render_editor():
    """Render the protocol editor interface"""
    st.header("Protocol Editor")
    
    # Debug information with enhanced display
    with st.expander("Debug Information", expanded=True):
        st.write({
            "Synopsis Content Present": st.session_state.get('synopsis_content') is not None,
            "Synopsis Content Length": len(st.session_state.get('synopsis_content', '')) if st.session_state.get('synopsis_content') else 0,
            "Study Type": st.session_state.get('study_type', 'Not Selected'),
            "Current Section": st.session_state.get('current_section', 'None'),
            "Generated Sections": list(st.session_state.get('generated_sections', {}).keys())
        })
    
    # Generate Protocol button at the very top with enhanced styling
    if st.session_state.get('synopsis_content') is not None and st.session_state.get('study_type'):
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 1rem;
                border-radius: 10px;
                margin: 20px 0;
                width: 100%;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🚀 Generate Complete Protocol")
        st.markdown("Click below to generate all protocol sections from your synopsis")
        
        if st.button("Generate Complete Protocol", type='primary', use_container_width=True):
            try:
                with st.spinner("Generating protocol..."):
                    generator = TemplateSectionGenerator()
                    generate_complete_protocol(generator)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        if st.session_state.get('synopsis_content') is None:
            st.warning("⚠️ Please upload a synopsis first")
        if not st.session_state.get('study_type'):
            st.warning("⚠️ Please select a study type")
    
    st.markdown("---")  # Add separator
    
    # Show current section content if any
    if st.session_state.get('current_section'):
        section = st.session_state.current_section
        st.subheader(f"Editing: {section.replace('_', ' ').title()}")
        
        if section in st.session_state.generated_sections:
            content = st.text_area(
                "Section Content",
                value=st.session_state.generated_sections[section],
                height=400,
                key=f"edit_{section}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Changes"):
                    st.session_state.generated_sections[section] = content
                    st.success("Changes saved!")
            with col2:
                if st.button("🔄 Regenerate"):
                    try:
                        generator = TemplateSectionGenerator()
                        new_content = generator.generate_section(
                            section,
                            st.session_state.study_type,
                            st.session_state.synopsis_content,
                            st.session_state.generated_sections
                        )
                        st.session_state.generated_sections[section] = new_content
                        st.success(f"Regenerated {section}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error regenerating section: {str(e)}")
        else:
            st.info("Section not yet generated. Use the generate button above to create content.")
    else:
        st.info("👈 Select a section from the sidebar to begin editing")

    # Export functionality with improved options
    if st.session_state.get('generated_sections'):
        st.markdown("---")
        if st.button("Export Protocol"):
            try:
                formatter = ProtocolFormatter()
                doc = formatter.format_protocol(st.session_state.generated_sections)
                
                # Add export format selection
                format_option = st.radio("Export Format:", ["DOCX", "PDF"])
                
                if format_option == "PDF":
                    output_file = formatter.save_document("protocol", format='pdf')
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="Download Protocol (PDF)",
                            data=file,
                            file_name="protocol.pdf",
                            mime="application/pdf"
                        )
                else:
                    output_file = formatter.save_document("protocol", format='docx')
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="Download Protocol (DOCX)",
                            data=file,
                            file_name="protocol.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        
                st.success(f"Protocol exported successfully as {format_option}!")
                
            except Exception as e:
                st.error(f"Error exporting protocol: {str(e)}")
