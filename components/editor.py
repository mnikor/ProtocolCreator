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
    timestamp = int(time.time())
    if st.button("Generate Complete Protocol", type='primary', key=f"gen_protocol_{timestamp}", use_container_width=True):
        try:
            with st.spinner("Generating protocol..."):
                generator = TemplateSectionGenerator()
                logger.info(f"Starting protocol generation for study type: {st.session_state.study_type}")
                
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
            st.error(f"Error: {str(e)}")
    
    # Display validation results if available
    if validation_results := st.session_state.get('validation_results'):
        # Use unique key for quality assessment
        render_quality_assessment(validation_results, key_suffix=f"main_{timestamp}")
        
        # Show improvement button if there are any issues to address
        has_missing_items = any(
            len(r.get('missing_items', [])) > 0
            for r in validation_results.values()
            if isinstance(r, dict)
        )
        has_recommendations = any(
            len(r.get('recommendations', [])) > 0
            for r in validation_results.values()
            if isinstance(r, dict)
        )
        
        if has_missing_items or has_recommendations:
            st.markdown("### 🔄 Protocol Improvement")
            if st.button("Apply Recommendations & Regenerate", key=f"improve_protocol_{timestamp}"):
                with st.spinner("Improving protocol..."):
                    try:
                        # Store original versions
                        if 'original_sections' not in st.session_state:
                            st.session_state.original_sections = st.session_state.generated_sections.copy()
                            st.session_state.original_validation = st.session_state.validation_results.copy()
                        
                        # Initialize improver
                        generator = TemplateSectionGenerator()
                        improver = ProtocolImprover(generator.gpt_handler)
                        
                        # Show progress
                        progress_container = st.container()
                        with progress_container:
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Improve each section
                            improved_sections = {}
                            total_sections = len(st.session_state.original_sections)
                            
                            for idx, (section_name, content) in enumerate(st.session_state.original_sections.items()):
                                progress = (idx + 1) / total_sections
                                progress_bar.progress(progress, f"Improving section {idx + 1} of {total_sections}")
                                status_text.text(f"Processing: {section_name}")
                                
                                improved_content = improver.improve_section(
                                    section_name=section_name,
                                    content=content,
                                    issues=st.session_state.validation_results.get(section_name, {})
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
                        
                    except Exception as e:
                        st.error(f"Error improving protocol: {str(e)}")
                        logger.error(f"Protocol improvement error: {str(e)}")
    
    # Comparison and Download Section
    if st.session_state.get('show_comparison'):
        st.markdown("## Protocol Comparison")
        
        # Quality score comparison
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Original Version")
            st.metric(
                "Original Score",
                f"{st.session_state.original_validation.get('overall_score', 0)/10:.1f}/10"
            )
            
        with col2:
            st.markdown("### Improved Version")
            st.metric(
                "Improved Score",
                f"{st.session_state.validation_results.get('overall_score', 0)/10:.1f}/10"
            )
        
        # Show section-by-section comparison
        st.markdown("### Section Changes")
        comp_timestamp = int(time.time())
        for section_name in st.session_state.original_sections.keys():
            with st.expander(f"📑 {section_name.replace('_', ' ').title()}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Original Version**")
                    st.text_area(
                        label="Original content",
                        value=st.session_state.original_sections[section_name],
                        height=300,
                        key=f"orig_{section_name}_{comp_timestamp}",
                        disabled=True
                    )
                with col2:
                    st.markdown("**Improved Version**")
                    st.text_area(
                        label="Improved content",
                        value=st.session_state.generated_sections[section_name],
                        height=300,
                        key=f"impr_{section_name}_{comp_timestamp}",
                        disabled=True
                    )

    # Download section - separated from state checks
    if st.session_state.get('generated_sections'):
        st.markdown("### Download Protocol Versions")
        
        # Create container for download buttons
        download_container = st.container()
        with download_container:
            col1, col2 = st.columns(2)
            
            # Original version download
            with col1:
                if st.session_state.get('original_sections'):
                    original_text = "\n\n".join(st.session_state.original_sections.values())
                    st.download_button(
                        "⬇️ Download Original Version",
                        original_text,
                        file_name="original_protocol.txt",
                        mime="text/plain",
                        key=f"download_original_{timestamp}"
                    )
                
            # Improved version download
            with col2:
                improved_text = "\n\n".join(st.session_state.generated_sections.values())
                st.download_button(
                    "⬇️ Download Improved Version",
                    improved_text,
                    file_name="improved_protocol.txt",
                    mime="text/plain",
                    key=f"download_improved_{timestamp}"
                )
        
        # Keep assessment visible with unique key
        if st.session_state.get('validation_results'):
            st.markdown("### Final Quality Assessment")
            render_quality_assessment(st.session_state.validation_results, key_suffix=f"final_{timestamp}")
    
    # Hide comparison option
    if st.session_state.get('show_comparison'):
        if st.button("Hide Comparison", key=f"hide_comparison_{timestamp}"):
            del st.session_state.show_comparison
