import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter
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
    with st.expander("Debug Information", expanded=True):
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
        
        if st.button("Generate Complete Protocol", type='primary', use_container_width=True):
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
        
        # Overall score
        overall_score = sum(r['score'] for r in validation_results.values()) / len(validation_results)
        st.metric(
            "Overall Quality Score",
            f"{overall_score:.2%}",
            f"{(overall_score-0.8)*100:.1f}% from target" if overall_score < 0.8 else "Meets target"
        )
        
        # Bar chart of dimension scores
        scores_data = {
            dim.replace('_', ' ').title(): results['score'] 
            for dim, results in validation_results.items()
        }
        st.bar_chart(data=scores_data, use_container_width=True)
        
        # Detailed Assessment
        st.markdown("### Detailed Assessment")
        for dimension, results in validation_results.items():
            st.markdown(f"#### {dimension.replace('_', ' ').title()}")
            st.progress(results['score'])
            
            if results["missing_items"]:
                st.warning("Missing Items:")
                for item in results["missing_items"]:
                    st.write(f"- {item}")
                    
            if results["recommendations"]:
                st.info("Recommendations:")
                for rec in results["recommendations"]:
                    st.write(f"- {rec}")
    
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
            key="editor_export_format"
        )
        
        if st.button("Export Protocol", key="editor_export_button"):
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
                            key="editor_download_pdf"
                        )
                else:  # DOCX format
                    output_file = formatter.save_document("protocol", format='docx')
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="Download Protocol (DOCX)",
                            data=file,
                            file_name="protocol.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="editor_download_docx"
                        )
                        
                st.success(f"Protocol exported successfully as {format_option}!")
                
            except Exception as e:
                st.error(f"Error exporting protocol: {str(e)}")
