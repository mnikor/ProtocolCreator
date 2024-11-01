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
    """Generate the complete protocol"""
    progress_placeholder = st.empty()
    progress_bar = progress_placeholder.progress(0)
    status_text = st.empty()
    sections_status = st.empty()
    
    try:
        sections = generator.get_required_sections(st.session_state.study_type)
        total_sections = len(sections)
        completed = 0
        
        result = generator.generate_complete_protocol(
            study_type=st.session_state.study_type,
            synopsis_content=st.session_state.synopsis_content
        )
        
        # Store generated sections
        st.session_state.generated_sections = result["sections"]
        st.session_state.validation_results = result["validation_results"]
        
        if len(result["sections"]) == total_sections:
            progress_placeholder.success("✅ Protocol generation completed!")
            st.balloons()
            return True
        else:
            progress_placeholder.warning(f"⚠️ Generated {len(result['sections'])}/{total_sections} sections")
            return False
            
    except Exception as e:
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
        
        if st.button("Generate Complete Protocol", type='primary', key=f"gen_protocol_{int(time.time())}", use_container_width=True):
            try:
                with st.spinner("Generating protocol..."):
                    generator = TemplateSectionGenerator()
                    if generate_complete_protocol(generator):
                        st.success("Protocol generation completed successfully!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        if st.session_state.get('synopsis_content') is None:
            st.warning("⚠️ Please upload a synopsis first")
        if not st.session_state.get('study_type'):
            st.warning("⚠️ Please select a study type")
    
    st.markdown("---")
    
    # Quality Assessment Display
    if validation_results := st.session_state.get('validation_results'):
        st.markdown("## 📊 Protocol Quality Assessment")
        
        # Quality metrics in clear columns
        col1, col2 = st.columns([2, 1])
        with col1:
            st.metric(
                "Overall Quality Score",
                f"{validation_results.get('overall_score', 0):.1f}%",
                f"{(validation_results.get('overall_score', 0)/100-0.8)*100:.1f}% from target"
            )
            
            # Bar chart of dimension scores
            scores_data = {}
            for dim, results in validation_results.items():
                if isinstance(results, dict) and 'score' in results:
                    scores_data[dim.replace('_', ' ').title()] = results['score']
            st.bar_chart(scores_data)
            
        with col2:
            st.markdown("### Quick Summary")
            total_issues = sum(
                len(r.get('missing_items', [])) 
                for r in validation_results.values() 
                if isinstance(r, dict)
            )
            if total_issues > 0:
                st.warning(f"Found {total_issues} items needing attention")
            else:
                st.success("Protocol meets all quality criteria")
        
        # Protocol Improvement Section
        st.markdown("### 🔄 Protocol Improvement")
        current_time = int(time.time())
        if st.button("Apply Recommendations & Regenerate", key=f'improve_button_{current_time}'):
            with st.spinner("Improving protocol..."):
                try:
                    # Store original versions
                    original_sections = st.session_state.generated_sections.copy()
                    original_validation = st.session_state.validation_results.copy()
                    
                    # Improvement logic
                    generator = TemplateSectionGenerator()
                    improver = ProtocolImprover(generator.gpt_handler)
                    improved_sections = {}
                    
                    # Create tabs for comparison
                    tab1, tab2 = st.tabs(["Quality Comparison", "Content Changes"])
                    
                    # Show progress
                    progress_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    # Improve each section
                    for idx, (section_name, content) in enumerate(original_sections.items()):
                        progress_text.text(f"Improving section: {section_name}")
                        progress_bar.progress((idx + 1) / len(original_sections))
                        
                        try:
                            improved_content = improver.improve_section(
                                section_name=section_name,
                                content=content,
                                issues=validation_results.get(section_name, {})
                            )
                            improved_sections[section_name] = improved_content
                        except Exception as e:
                            logger.error(f"Error improving section {section_name}: {str(e)}")
                            improved_sections[section_name] = content
                    
                    # Validate improved version
                    new_validation = generator.validator.validate_protocol(
                        improved_sections,
                        st.session_state.study_type
                    )
                    
                    with tab1:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### Original Score")
                            st.metric(
                                "Quality Score",
                                f"{original_validation.get('overall_score', 0):.1f}%"
                            )
                        with col2:
                            st.markdown("#### New Score")
                            st.metric(
                                "Quality Score",
                                f"{new_validation.get('overall_score', 0):.1f}%"
                            )
                            
                    with tab2:
                        for section_name in original_sections.keys():
                            section_time = int(time.time())
                            with st.expander(f"📑 {section_name.replace('_', ' ').title()}", expanded=False):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("**Original Version**")
                                    st.text_area(
                                        "Original content",
                                        original_sections[section_name],
                                        height=200,
                                        disabled=True,
                                        key=f"orig_{section_name}_{section_time}"
                                    )
                                with col2:
                                    st.markdown("**Improved Version**")
                                    st.text_area(
                                        "Improved content",
                                        improved_sections[section_name],
                                        height=200,
                                        disabled=True,
                                        key=f"impr_{section_name}_{section_time}"
                                    )
                    
                    # Update protocol with improvements
                    st.session_state.generated_sections = improved_sections
                    st.session_state.validation_results = new_validation
                    
                    progress_text.empty()
                    progress_bar.empty()
                    st.success("✅ Protocol improved successfully!")
                    
                    # Option to revert changes
                    if st.button("↩️ Revert to Original Version", key=f"revert_{current_time}"):
                        st.session_state.generated_sections = original_sections
                        st.session_state.validation_results = original_validation
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"Error improving protocol: {str(e)}")
                    logger.error(f"Protocol improvement error: {str(e)}")
    
    # Show current section content if any
    if st.session_state.get('current_section'):
        st.markdown("---")
        section = st.session_state.current_section
        st.subheader(f"Editing: {section.replace('_', ' ').title()}")
        
        current_time = int(time.time())
        if section in st.session_state.generated_sections:
            content = st.text_area(
                "Section Content",
                value=st.session_state.generated_sections[section],
                height=400,
                key=f"edit_{section}_{current_time}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Changes", key=f"save_{section}_{current_time}"):
                    st.session_state.generated_sections[section] = content
                    st.success("Changes saved!")
            with col2:
                if st.button("🔄 Regenerate", key=f"regen_{section}_{current_time}"):
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
        current_time = int(time.time())
        
        format_option = st.radio(
            "Export Format:",
            ["DOCX", "PDF"],
            key=f"editor_export_format_{current_time}"
        )
        
        if st.button("Export Protocol", key=f"editor_export_button_{current_time}"):
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
                            mime="application/pdf",
                            key=f"editor_download_pdf_{current_time}"
                        )
                else:  # DOCX format
                    output_file = formatter.save_document("protocol", format='docx')
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="Download Protocol (DOCX)",
                            data=file,
                            file_name="protocol.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"editor_download_docx_{current_time}"
                        )
                        
                st.success(f"✅ Protocol exported successfully as {format_option}!")
                
            except Exception as e:
                st.error(f"Error exporting protocol: {str(e)}")
