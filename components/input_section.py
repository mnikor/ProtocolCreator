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
    if 'show_process_button' not in st.session_state:
        st.session_state.show_process_button = False
    
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
            st.session_state.show_process_button = True
            
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
        key="synopsis_text_input",
        on_change=lambda: setattr(st.session_state, 'show_process_button', bool(st.session_state.synopsis_text_input.strip()))
    )
    
    # Process text input if present
    if synopsis_text.strip():
        # Initialize improver for early analysis
        improver = ProtocolImprover()
        validator = SynopsisValidator()
        
        # Analyze content for missing information
        missing_info = improver.analyze_synopsis(synopsis_text)
        
        # Always show missing information analysis
        st.markdown("### 📋 Synopsis Analysis")
        
        # Display missing information prominently
        if missing_info['critical_missing']:
            missing_count = len(missing_info['critical_fields'])
            st.error(f"⚠️ Found {missing_count} missing critical items")
            
            # Group missing fields by category
            st.markdown("#### Required Information")
            col1, col2 = st.columns([1, 2])
            
            missing_fields_inputs = {}
            for field, description in missing_info['critical_fields'].items():
                with col1:
                    st.markdown(f"**{field.replace('_', ' ').title()}**")
                with col2:
                    field_input = st.text_input(
                        label=description,
                        key=f"missing_{field}",
                        help=f"Add details about {field.replace('_', ' ')}"
                    )
                    missing_fields_inputs[field] = field_input
            
            # Show process button if text is present
            if synopsis_text.strip():
                show_process_button = True
                if not all(missing_fields_inputs.values()):
                    st.warning("⚠️ Filling in missing information is recommended but not required")
        else:
            st.success("✅ All critical information appears to be present")
            show_process_button = True
        
        # Always show process button if we have content
        if synopsis_text.strip():
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
