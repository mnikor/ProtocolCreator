import streamlit as st
import logging
from utils.synopsis_validator import SynopsisValidator
from utils.file_processor import process_file_content
from utils.protocol_improver import ProtocolImprover

logger = logging.getLogger(__name__)

def render_input_section():
    st.markdown("## Protocol Development")
    st.markdown("Please upload your study synopsis or enter text below.")
    
    # Initialize session state
    if 'synopsis_input' not in st.session_state:
        st.session_state.synopsis_input = ''
    if 'show_process_button' not in st.session_state:
        st.session_state.show_process_button = False
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Synopsis text input - always show this
        synopsis_text = st.text_area(
            "Enter your synopsis text",
            value=st.session_state.synopsis_input,
            height=300,
            help="Enter your study synopsis here",
            key="synopsis_text_input"
        )
    
    with col2:
        # File uploader in second column
        uploaded_file = st.file_uploader(
            "Or upload file",
            type=["txt", "docx", "pdf"],
            help="Upload synopsis (TXT, DOCX, PDF)"
        )
        
        # Process uploaded file if present
        if uploaded_file:
            try:
                synopsis_content = process_file_content(uploaded_file)
                st.session_state.synopsis_input = synopsis_content
                synopsis_text = synopsis_content  # Update text area
                if len(synopsis_content.strip()) < 50:
                    st.warning("⚠️ Synopsis seems too short")
                else:
                    st.success("✅ File uploaded!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Analyze synopsis immediately if text is present
    if synopsis_text.strip():
        st.markdown("---")
        st.markdown("### 📋 Synopsis Analysis")
        
        with st.spinner("Analyzing synopsis..."):
            improver = ProtocolImprover()
            validator = SynopsisValidator()
            
            # Validate study type first
            validation_result = validator.validate_synopsis(synopsis_text)
            if validation_result and validation_result.get('study_type'):
                study_type = validation_result['study_type']
                st.success(f"📋 Detected Study Type: {study_type.replace('_', ' ').title()}")
                
                # Show therapeutic area if detected
                if therapeutic_area := validation_result.get('therapeutic_area'):
                    st.info(f"🏥 Therapeutic Area: {therapeutic_area.replace('_', ' ').title()}")
                
                # Analyze missing information with study type context
                missing_info = improver.analyze_synopsis(
                    synopsis_text,
                    study_type=study_type
                )
                
                if missing_info['critical_missing']:
                    missing_count = len(missing_info['critical_fields'])
                    st.error(f"⚠️ Found {missing_count} missing critical items")
                    
                    # Study type specific guidance
                    if missing_info['study_type_specific']:
                        st.info(f"ℹ️ Showing requirements specific to {study_type.replace('_', ' ').title()} studies")
                    
                    # Input fields with improved layout
                    st.markdown("#### Required Information")
                    for field, prompt in missing_info['critical_fields'].items():
                        with st.expander(f"📝 {field.replace('_', ' ').title()}"):
                            st.markdown(f"**{prompt}**")
                            user_input = st.text_area(
                                label="Enter details",
                                key=f"missing_{field}",
                                height=100,
                                help=f"Provide information about {field.replace('_', ' ')}"
                            )
                    
                    st.warning("⚠️ Adding missing information is recommended but not required")
                else:
                    st.success("✅ All critical information appears to be present")
                
                # Show process button prominently
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button(
                        "🚀 Process Synopsis and Generate Protocol",
                        type="primary",
                        use_container_width=True,
                        help="Begin protocol development"
                    ):
                        try:
                            # Combine synopsis text with any missing field inputs
                            final_synopsis = synopsis_text
                            if missing_info['critical_missing']:
                                for field in missing_info['critical_fields']:
                                    if value := st.session_state.get(f"missing_{field}"):
                                        final_synopsis += f"\n{field.replace('_', ' ').title()}: {value}"
                            
                            # Store synopsis and study type
                            st.session_state.synopsis_content = final_synopsis
                            st.session_state.study_type = study_type
                            
                            st.success("✅ Synopsis processed successfully!")
                            st.rerun()
                            
                        except Exception as e:
                            logger.error(f"Error processing synopsis: {str(e)}")
                            st.error(f"Error: {str(e)}")
            else:
                st.error("❌ Please ensure synopsis content is complete enough to detect study type")
