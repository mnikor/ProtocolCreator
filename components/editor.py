import streamlit as st
import time
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter
from utils.protocol_improver import ProtocolImprover
from utils.protocol_quality_ui import render_quality_assessment
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_complete_protocol(generator):
    '''Generate the complete protocol with enhanced error handling'''
    try:
        logger.info("Starting protocol generation")
        sections = generator.get_required_sections(st.session_state.study_type)
        total_sections = len(sections)
        
        # Show initial progress
        st.info("🔄 Generating protocol...")
        
        result = generator.generate_complete_protocol(
            study_type=st.session_state.study_type,
            synopsis_content=st.session_state.synopsis_content
        )
        
        if not result or "sections" not in result:
            logger.error("No sections generated")
            st.error("Failed to generate protocol sections")
            return False
            
        # Store results in session state
        st.session_state.generated_sections = result["sections"]
        st.session_state.validation_results = result["validation_results"]
        
        if len(result["sections"]) == total_sections:
            logger.info("Protocol generation completed successfully")
            return True
        else:
            logger.warning(f"Incomplete protocol generation: {len(result['sections'])}/{total_sections}")
            return False
            
    except Exception as e:
        logger.error(f"Error in protocol generation: {str(e)}")
        st.error(f"Error: {str(e)}")
        return False

def render_editor():
    """Render the protocol editor interface"""
    st.header("Protocol Editor")
    
    # Debug information
    with st.expander("Debug Information", expanded=False):
        st.write({
            "Synopsis Content Present": st.session_state.get('synopsis_content') is not None,
            "Synopsis Content Length": len(st.session_state.get('synopsis_content', '')) if st.session_state.get('synopsis_content') else 0,
            "Study Type": st.session_state.get('study_type', 'Not Selected'),
            "Current Section": st.session_state.get('current_section', 'None'),
            "Generated Sections": list(st.session_state.get('generated_sections', {}).keys())
        })
    
    # Generate Protocol button at the top with enhanced styling
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
        
        if st.button("Generate Complete Protocol", type='primary', key="gen_protocol", use_container_width=True):
            logger.info("Generate button clicked")
            try:
                with st.spinner("Generating protocol..."):
                    generator = TemplateSectionGenerator()
                    logger.info(f"Starting protocol generation for study type: {st.session_state.study_type}")
                    
                    # Show progress status
                    progress_placeholder = st.empty()
                    progress_bar = progress_placeholder.progress(0)
                    status_text = st.empty()
                    
                    if generate_complete_protocol(generator):
                        st.success("Protocol generation completed successfully!")
                        st.session_state.show_quality_assessment = True
                        st.rerun()  # Force refresh to show new content
                    else:
                        st.error("Protocol generation failed. Please check the logs for details.")
            except Exception as e:
                logger.error(f"Error in protocol generation: {str(e)}")
                st.error(f"Error: {str(e)}")
    else:
        if st.session_state.get('synopsis_content') is None:
            st.warning("⚠️ Please upload a synopsis first")
        if not st.session_state.get('study_type'):
            st.warning("⚠️ Please select a study type")
    
    # Quality Assessment Display
    if validation_results := st.session_state.get('validation_results'):
        render_quality_assessment(validation_results)
        
        # Protocol Improvement Section
        st.markdown("### 🔄 Protocol Improvement")
        if st.button("Apply Recommendations & Regenerate", key='improve_protocol'):
            with st.spinner("Improving protocol..."):
                try:
                    generator = TemplateSectionGenerator()
                    improver = ProtocolImprover(generator.gpt_handler)
                    for section_name, content in st.session_state.generated_sections.items():
                        improved_content = improver.improve_section(
                            section_name=section_name,
                            content=content,
                            issues=validation_results.get(section_name, {})
                        )
                        st.session_state.generated_sections[section_name] = improved_content
                    st.success("Protocol improved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error improving protocol: {str(e)}")
    
    # Show current section content if any
    if st.session_state.get('current_section'):
        st.markdown("---")
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
                if st.button("💾 Save Changes", key=f"save_{section}"):
                    st.session_state.generated_sections[section] = content
                    st.success("Changes saved!")
            with col2:
                if st.button("🔄 Regenerate", key=f"regen_{section}"):
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
    
    # Export functionality at the bottom
    if st.session_state.get('generated_sections'):
        st.markdown("---")
        st.subheader("Export Protocol")
        format_option = st.radio(
            "Export Format:",
            ["DOCX", "PDF"],
            key="export_format"
        )
        
        if st.button("Export Protocol", key="export_protocol"):
            try:
                formatter = ProtocolFormatter()
                doc = formatter.format_protocol(st.session_state.generated_sections)
                
                if format_option == "PDF":
                    output_file = formatter.save_document("protocol", format='pdf')
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="Download Protocol (PDF)",
                            data=file,
                            file_name="protocol.pdf",
                            mime="application/pdf"
                        )
                else:  # DOCX format
                    output_file = formatter.save_document("protocol", format='docx')
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="Download Protocol (DOCX)",
                            data=file,
                            file_name="protocol.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                st.success(f"✅ Protocol exported successfully as {format_option}!")
            except Exception as e:
                st.error(f"Error exporting protocol: {str(e)}")
