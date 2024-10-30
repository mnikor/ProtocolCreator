import streamlit as st
from utils.file_processor import read_file_content
from utils.synopsis_validator import validate_synopsis
import logging

logger = logging.getLogger(__name__)

def render_input_section():
    """Render the synopsis input section"""
    st.header("Synopsis Input")

    # Choose input method
    st.subheader("Choose input method:")
    input_method = st.radio(
        "Input Method",
        ["File Upload", "Text Input"],
        label_visibility="collapsed"
    )

    synopsis_content = None

    if input_method == "File Upload":
        uploaded_file = st.file_uploader(
            "Upload Synopsis",
            type=["pdf", "docx", "txt"],
            help="Upload your synopsis document (PDF, DOCX, or TXT)"
        )

        if uploaded_file:
            try:
                # Process uploaded file
                synopsis_content = read_file_content(uploaded_file)
                if synopsis_content:
                    st.success(f"✅ Successfully processed {uploaded_file.name}")

                    # Store in session state
                    st.session_state.synopsis_content = synopsis_content

                    # Validate synopsis
                    try:
                        validation_results = validate_synopsis(synopsis_content)

                        # Display validation results
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("Validation Status")
                            if validation_results['is_valid']:
                                st.success("✅ Synopsis structure is valid")
                            else:
                                st.warning("⚠️ Synopsis needs attention")

                            if validation_results.get('missing_sections'):
                                st.warning("Missing Sections:")
                                for section in validation_results['missing_sections']:
                                    st.write(f"- {section.get('section', '')}")

                        with col2:
                            st.subheader("Study Analysis")
                            if 'detailed_analysis' in validation_results:
                                analysis = validation_results['detailed_analysis']

                                st.write("**Study Design:**")
                                design = analysis.get('study_type_and_design', {})
                                st.write(f"- Type: {design.get('primary_classification', 'Not specified')}")
                                st.write(f"- Design: {design.get('design_type', 'Not specified')}")
                                st.write(f"- Phase: {design.get('phase', 'Not specified')}")

                                st.write("**Critical Parameters:**")
                                params = analysis.get('critical_parameters', {})
                                st.write(f"- Population: {params.get('population', 'Not specified')}")
                                st.write(f"- Intervention: {params.get('intervention', 'Not specified')}")
                                st.write(f"- Control: {params.get('control_comparator', 'Not specified')}")
                                st.write(f"- Primary Endpoint: {params.get('primary_endpoint', 'Not specified')}")

                    except Exception as e:
                        logger.error(f"Error validating synopsis: {str(e)}")
                        st.error(f"Error during validation: {str(e)}")

            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                st.error(f"Error processing file: {str(e)}")

    else:  # Text Input
        synopsis_content = st.text_area(
            "Enter Synopsis Text",
            height=300,
            help="Paste your synopsis text here"
        )

        if synopsis_content:
            if st.button("Validate Synopsis"):
                st.session_state.synopsis_content = synopsis_content
                try:
                    validation_results = validate_synopsis(synopsis_content)
                    # Display validation results (similar to file upload)
                    if validation_results['is_valid']:
                        st.success("✅ Synopsis structure is valid")
                    else:
                        st.warning("⚠️ Synopsis needs attention")
                except Exception as e:
                    st.error(f"Error validating synopsis: {str(e)}")

    # Debug information
    with st.expander("Debug Information", expanded=False):
        st.write({
            "synopsis_content": bool(st.session_state.get('synopsis_content')),
            "study_type": st.session_state.get('study_type'),
            "sections_status": st.session_state.get('sections_status'),
            "current_section": st.session_state.get('current_section')
        })

    # Show next steps if synopsis is uploaded
    if st.session_state.get('synopsis_content'):
        st.success("✅ Synopsis uploaded successfully!")
        st.info("👈 Please select a study type in the sidebar to continue")