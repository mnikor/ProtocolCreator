import streamlit as st
import logging
from utils.synopsis_validator import SynopsisValidator
from utils.file_processor import process_file_content
from utils.protocol_improver import ProtocolImprover

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
            
            # Validate content length
            if len(synopsis_content.strip()) < 50:
                st.warning("⚠️ Synopsis content seems too short. Please ensure all content is included.")
            else:
                st.success("✅ File uploaded successfully!")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            synopsis_content = ""
    
    # Synopsis text input
    synopsis_content = st.text_area(
        "Or enter your synopsis text",
        value=st.session_state.get('synopsis_input', ''),
        height=300,
        help="Paste your study synopsis here or use the file uploader above.",
        key="synopsis_input"
    )
    
    # Validate content and show confirm button
    if synopsis_content.strip():
        # Initialize improver for early analysis
        improver = ProtocolImprover()
        validator = SynopsisValidator()
        
        # Analyze content for missing information
        missing_info = improver.analyze_synopsis(synopsis_content)
        
        if missing_info['critical_missing']:
            st.error("⚠️ Critical Information Missing")
            
            # Display missing fields with input collection
            st.markdown("### Required Information")
            for field, description in missing_info['critical_fields'].items():
                st.text_input(
                    f"{field.replace('_', ' ').title()}",
                    key=f"missing_{field}",
                    help=description
                )
            
            # Only show process button if all critical fields are filled
            all_fields_filled = all(
                st.session_state.get(f"missing_{field}")
                for field in missing_info['critical_fields']
            )
            
            if not all_fields_filled:
                st.warning("Please fill in all required fields before proceeding")
                return
        
        # Show confirm button only if critical info is provided
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
                    
                    # Store full content
                    synopsis_content = synopsis_content.strip()
                    
                    # Add missing information from user inputs
                    if missing_info['critical_missing']:
                        for field in missing_info['critical_fields']:
                            field_value = st.session_state.get(f"missing_{field}")
                            if field_value:
                                synopsis_content += f"\n{field.replace('_', ' ').title()}: {field_value}"
                    
                    # Validate synopsis
                    validation_result = validator.validate_synopsis(synopsis_content)
                    
                    if validation_result and validation_result.get('study_type'):
                        study_type = validation_result['study_type']
                        # Display detected study type
                        st.info(f"📋 Detected Study Type: {study_type.replace('_', ' ').title()}")
                        
                        # Store synopsis and study type
                        st.session_state.synopsis_content = synopsis_content
                        st.session_state.study_type = study_type
                        
                        st.success("✅ Synopsis processed successfully!")
                        st.rerun()  # Refresh to show editor
                    else:
                        st.error("❌ Could not detect study type. Please check synopsis content.")
                        
            except Exception as e:
                logger.error(f"Error processing synopsis: {str(e)}")
                st.error(f"Error processing synopsis: {str(e)}")
