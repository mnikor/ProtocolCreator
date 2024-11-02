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
    
    # Rest of the editor functionality...
    [Previous editor code continues...]
