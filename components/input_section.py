import streamlit as st
import logging
from utils.synopsis_validator import SynopsisValidator
from utils.file_processor import process_file_content

logger = logging.getLogger(__name__)

def render_input_section():
    st.markdown("## Protocol Development")
    st.markdown("Please upload your study synopsis to begin.")
    
    # Add file uploader
    uploaded_file = st.file_uploader(
        "Upload Synopsis File",
        type=["txt", "docx", "pdf"],
        help="Upload your synopsis document (supported formats: TXT, DOCX, PDF)",
        key="synopsis_file"
    )
    
    # Process uploaded file
    if uploaded_file:
        try:
            synopsis_content = process_file_content(uploaded_file)
            st.session_state.synopsis_input = synopsis_content
            st.success("✅ File uploaded successfully!")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            synopsis_content = ""
    
    # Synopsis text input
    synopsis_content = st.text_area(
        "Or enter your synopsis text",
        value=st.session_state.get('synopsis_input', ''),
        height=300,
        help="Paste your study synopsis here or use the file uploader above. The system will automatically detect the study type.",
        key="synopsis_input"
    )
    
    # Confirm button
    if synopsis_content.strip():
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
