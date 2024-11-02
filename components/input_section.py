import streamlit as st
import logging
from utils.synopsis_validator import SynopsisValidator
from utils.file_processor import process_file_content
from utils.protocol_improver import ProtocolImprover

logger = logging.getLogger(__name__)

def render_input_section():
    st.markdown("## Protocol Development")
    st.markdown("Please upload your study synopsis or enter text below.")
    
    # Initialize session state for synopsis input if not exists
    if 'synopsis_input' not in st.session_state:
        st.session_state.synopsis_input = ''
    
    # Add file uploader
    uploaded_file = st.file_uploader(
        "Upload Synopsis File (Optional)",
        type=["txt", "docx", "pdf"],
        help="Upload your synopsis document (supported formats: TXT, DOCX, PDF)",
        key="synopsis_file"
    )
    
    # Process uploaded file if present
    if uploaded_file:
        try:
            synopsis_content = process_file_content(uploaded_file)
            st.session_state.synopsis_input = synopsis_content
            
            # Validate content length
            if len(synopsis_content.strip()) < 50:
                st.warning("⚠️ Synopsis content seems too short. Please ensure all content is included.")
            else:
                st.success("✅ File uploaded successfully!")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    # Synopsis text input - always show this
    synopsis_text = st.text_area(
        "Enter your synopsis text",
        value=st.session_state.synopsis_input,
        height=300,
        help="Enter your study synopsis here or use the file uploader above.",
        key="synopsis_text_input"
    )
    
    # Process text input if present (regardless of file upload)
    if synopsis_text.strip():
        # Initialize improver for early analysis
        improver = ProtocolImprover()
        validator = SynopsisValidator()
        
        # Analyze content for missing information
        missing_info = improver.analyze_synopsis(synopsis_text)
        
        if missing_info['critical_missing']:
            st.error("⚠️ Critical Information Missing")
            
            # Display missing fields with input collection
            st.markdown("### Required Information")
            missing_fields_inputs = {}
            for field, description in missing_info['critical_fields'].items():
                field_input = st.text_input(
                    f"{field.replace('_', ' ').title()}",
                    key=f"missing_{field}",
                    help=description
                )
                missing_fields_inputs[field] = field_input
            
            # Show process button if all critical fields are filled
            if all(missing_fields_inputs.values()):
                show_process_button = True
            else:
                st.warning("Please fill in all required fields before proceeding")
                show_process_button = False
        else:
            show_process_button = True
        
        # Show process button if conditions are met
        if show_process_button:
            if st.button(
                "Process Synopsis",
                type="primary",
                use_container_width=True,
                help="Click to process your synopsis and begin protocol development"
            ):
                try:
                    with st.spinner("Processing synopsis..."):
                        # Combine synopsis text with any missing field inputs
                        final_synopsis = synopsis_text
                        if missing_info['critical_missing']:
                            for field, value in missing_fields_inputs.items():
                                if value:
                                    final_synopsis += f"\n{field.replace('_', ' ').title()}: {value}"
                        
                        # Validate synopsis
                        validation_result = validator.validate_synopsis(final_synopsis)
                        
                        if validation_result and validation_result.get('study_type'):
                            study_type = validation_result['study_type']
                            st.info(f"📋 Detected Study Type: {study_type.replace('_', ' ').title()}")
                            
                            # Store synopsis and study type
                            st.session_state.synopsis_content = final_synopsis
                            st.session_state.study_type = study_type
                            
                            st.success("✅ Synopsis processed successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Could not detect study type. Please check synopsis content.")
                            
                except Exception as e:
                    logger.error(f"Error processing synopsis: {str(e)}")
                    st.error(f"Error processing synopsis: {str(e)}")
