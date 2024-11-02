import streamlit as st
import logging
from utils.synopsis_validator import SynopsisValidator

logger = logging.getLogger(__name__)

def render_input_section():
    """Render the synopsis input section"""
    st.markdown("## Protocol Development")
    st.markdown("Please upload your study synopsis to begin.")
    
    # Synopsis text input
    synopsis_content = st.text_area(
        "Enter your synopsis text",
        height=300,
        help="Paste your study synopsis here. The system will automatically detect the study type.",
        key="synopsis_input"
    )
    
    # Confirm button
    confirm_button = st.button(
        "Process Synopsis",
        type="primary",
        use_container_width=True,
        help="Click to process your synopsis and begin protocol development"
    )
    
    if confirm_button:
        try:
            with st.spinner("Processing synopsis..."):
                # Initialize synopsis validator
                validator = SynopsisValidator()
                
                # Validate synopsis
                validation_result = validator.validate_synopsis(
                    synopsis_content=synopsis_content
                )
                
                if validation_result and validation_result.get('study_type'):
                    # Store both synopsis and detected study type
                    st.session_state.synopsis_content = synopsis_content
                    st.session_state.study_type = validation_result['study_type']
                    st.success("✅ Synopsis processed successfully!")
                    st.rerun()  # Refresh to show editor
                else:
                    st.error("❌ Could not process synopsis. Please check content and try again.")
                    
        except Exception as e:
            logger.error(f"Error processing synopsis: {str(e)}")
            st.error(f"Error processing synopsis: {str(e)}")
