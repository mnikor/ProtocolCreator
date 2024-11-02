import streamlit as st
import logging
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_quality_ui import render_quality_assessment
from utils.protocol_improver import ProtocolImprover

logger = logging.getLogger(__name__)

def render_editor():
    st.markdown("## Protocol Development")
    
    # Check if we have synopsis content and study type
    if not st.session_state.get('synopsis_content'):
        st.warning("Please upload a synopsis first")
        return
    if not st.session_state.get('study_type'):
        st.warning("Please select a study type first")
        return
        
    # Generate button with proper styling
    st.markdown('''
        <style>
        div.stButton > button:first-child {
            background-color: #4CAF50;
            color: white;
            height: 3em;
            width: 100%;
            font-size: 20px;
            font-weight: bold;
            border-radius: 10px;
            margin: 1em 0;
        }
        </style>
    ''', unsafe_allow_html=True)
    
    # Main generate button
    if st.button("Generate Complete Protocol", type='primary', key="gen_protocol", use_container_width=True):
        try:
            with st.spinner("Generating protocol..."):
                # Initialize generator
                generator = TemplateSectionGenerator()
                
                # Generate complete protocol
                result = generator.generate_complete_protocol(
                    study_type=st.session_state.study_type,
                    synopsis_content=st.session_state.synopsis_content
                )
                
                if result and result.get("sections"):
                    st.session_state.generated_sections = result["sections"]
                    st.session_state.validation_results = result["validation_results"]
                    st.success("✅ Protocol generated successfully!")
                else:
                    st.error("Failed to generate protocol sections")
                    
        except Exception as e:
            logger.error(f"Error in protocol generation: {str(e)}")
            st.error(f"Error generating protocol: {str(e)}")
    
    # Display validation results and improvement options
    if validation_results := st.session_state.get('validation_results'):
        st.markdown("### Protocol Quality Assessment")
        render_quality_assessment(validation_results)
        
        # Show improvement button if there are recommendations or missing items
        has_improvements_needed = any(
            (isinstance(r, dict) and 
             (r.get('recommendations', []) or r.get('missing_items', [])))
            for r in validation_results.values()
            if isinstance(r, dict) and r != validation_results.get('overall_score')
        )
        
        if has_improvements_needed:
            st.markdown("### 🔄 Protocol Improvement")
            if st.button("Apply Recommendations & Regenerate", key="improve_protocol"):
                try:
                    with st.spinner("Improving protocol..."):
                        # Store original versions
                        st.session_state.original_sections = st.session_state.generated_sections.copy()
                        st.session_state.original_validation = validation_results.copy()
                        
                        # Initialize improver
                        generator = TemplateSectionGenerator()
                        improver = ProtocolImprover(generator.gpt_handler)
                        
                        # Improve sections
                        improved_sections = {}
                        for section_name, content in st.session_state.generated_sections.items():
                            improved_content = improver.improve_section(
                                section_name=section_name,
                                content=content,
                                issues=validation_results.get(section_name, {})
                            )
                            improved_sections[section_name] = improved_content
                        
                        # Get new validation
                        new_validation = generator.validator.validate_protocol(
                            improved_sections,
                            st.session_state.study_type
                        )
                        
                        # Update state
                        st.session_state.generated_sections = improved_sections
                        st.session_state.validation_results = new_validation
                        st.session_state.show_comparison = True
                        
                        st.success("✅ Protocol improved successfully!")
                        
                except Exception as e:
                    st.error(f"Error improving protocol: {str(e)}")
        
        # Show comparison if available
        if st.session_state.get('show_comparison'):
            st.markdown("### Protocol Versions Comparison")
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                original_text = "\n\n".join(st.session_state.original_sections.values())
                st.download_button(
                    "⬇️ Download Original Version",
                    original_text,
                    file_name="original_protocol.txt",
                    mime="text/plain"
                )
            
            with col2:
                improved_text = "\n\n".join(st.session_state.generated_sections.values())
                st.download_button(
                    "⬇️ Download Improved Version",
                    improved_text,
                    file_name="improved_protocol.txt",
                    mime="text/plain"
                )
            
            # Section-by-section comparison
            st.markdown("### Section Changes")
            for section_name in st.session_state.original_sections.keys():
                with st.expander(f"📝 {section_name.replace('_', ' ').title()}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original Version**")
                        st.text_area(
                            "Original content",
                            st.session_state.original_sections[section_name],
                            height=300,
                            disabled=True
                        )
                    with col2:
                        st.markdown("**Improved Version**")
                        st.text_area(
                            "Improved content",
                            st.session_state.generated_sections[section_name],
                            height=300,
                            disabled=True
                        )
