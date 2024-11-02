import streamlit as st
import logging
import time
from datetime import datetime
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
    if st.button("Generate Complete Protocol", type='primary', key=f"gen_protocol_{int(time.time())}", use_container_width=True):
        try:
            # Clear previous results
            if 'generated_sections' in st.session_state:
                del st.session_state.generated_sections
            if 'validation_results' in st.session_state:
                del st.session_state.validation_results
            if 'show_comparison' in st.session_state:
                del st.session_state.show_comparison
                
            # Initialize progress tracking
            progress_container = st.container()
            progress_text = progress_container.empty()
            progress_bar = progress_container.progress(0)
            progress_text.text("Initializing protocol generation...")
            
            # Initialize generator
            generator = TemplateSectionGenerator()
            logger.info(f"Starting protocol generation for study type: {st.session_state.study_type}")
            
            # Generate complete protocol
            result = generator.generate_complete_protocol(
                study_type=st.session_state.study_type,
                synopsis_content=st.session_state.synopsis_content
            )
            
            if not result or not result.get("sections"):
                raise ValueError("Failed to generate protocol sections")
                
            # Update session state with results
            st.session_state.generated_sections = result["sections"]
            st.session_state.validation_results = result["validation_results"]
            
            # Clear progress indicators
            progress_text.empty()
            progress_bar.empty()
            
            st.success("✅ Protocol generated successfully!")
            st.rerun()  # Force refresh to show new content
            
        except Exception as e:
            logger.error(f"Error in protocol generation: {str(e)}")
            st.error(f"Error generating protocol: {str(e)}")
    
    # Display validation results and improvement options
    if validation_results := st.session_state.get('validation_results'):
        st.markdown("### Protocol Quality Assessment")
        render_quality_assessment(validation_results)
        
        # Show improvement button if there are recommendations
        has_recommendations = any(
            len(r.get('recommendations', [])) > 0
            for r in validation_results.values()
            if isinstance(r, dict)
        )
        
        if has_recommendations:
            st.markdown("### 🔄 Protocol Improvement")
            if st.button("Apply Recommendations & Regenerate", key=f"improve_protocol_{int(time.time())}"):
                try:
                    # Store original versions
                    st.session_state.original_sections = st.session_state.generated_sections.copy()
                    st.session_state.original_validation = validation_results.copy()
                    
                    # Initialize improver
                    generator = TemplateSectionGenerator()
                    improver = ProtocolImprover(generator.gpt_handler)
                    
                    # Show progress
                    with st.spinner("Improving protocol..."):
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
                        
                        # Update state with improvements
                        st.session_state.generated_sections = improved_sections
                        st.session_state.validation_results = new_validation
                        st.session_state.show_comparison = True
                        
                        st.success("✅ Protocol improved successfully!")
                        st.rerun()
                        
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
                    mime="text/plain",
                    key=f"download_original_{int(time.time())}"
                )
            
            with col2:
                improved_text = "\n\n".join(st.session_state.generated_sections.values())
                st.download_button(
                    "⬇️ Download Improved Version",
                    improved_text,
                    file_name="improved_protocol.txt",
                    mime="text/plain",
                    key=f"download_improved_{int(time.time())}"
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
                            key=f"orig_{section_name}_{int(time.time())}",
                            disabled=True
                        )
                    with col2:
                        st.markdown("**Improved Version**")
                        st.text_area(
                            "Improved content",
                            st.session_state.generated_sections[section_name],
                            height=300,
                            key=f"impr_{section_name}_{int(time.time())}",
                            disabled=True
                        )
