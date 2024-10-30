import streamlit as st
from utils.file_processor import read_file_content
from utils.synopsis_validator import validate_synopsis

def render_input_section():
    """Render the synopsis input section"""
    st.header("Synopsis Input")
    
    input_method = st.radio(
        "Choose input method:",
        ["File Upload", "Text Input"]
    )
    
    if input_method == "File Upload":
        uploaded_file = st.file_uploader(
            "Upload Synopsis",
            type=['pdf', 'docx', 'txt']
        )
        
        if uploaded_file:
            try:
                content = read_file_content(uploaded_file)
                st.session_state.synopsis_content = content
                display_validation_results(content)
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                
    else:
        synopsis_text = st.text_area(
            "Paste Synopsis Text",
            height=400
        )
        
        if synopsis_text:
            st.session_state.synopsis_content = synopsis_text
            display_validation_results(synopsis_text)

def display_validation_results(content):
    """Display synopsis validation results with robust type checking"""
    with st.spinner('Validating synopsis...'):
        try:
            validation_results = validate_synopsis(content)
            
            # Basic validation results display
            if isinstance(validation_results, dict):
                if validation_results.get('is_valid'):
                    st.success('Synopsis structure validated successfully!')
                else:
                    st.warning('Synopsis validation found some issues:')
                
                # Display missing sections
                missing_sections = validation_results.get('missing_sections', [])
                if missing_sections:
                    for section in missing_sections:
                        if isinstance(section, dict):
                            st.warning(f"Missing section: {section.get('section', '')}")
                        elif isinstance(section, str):
                            st.warning(f"Missing section: {section}")
                
                # Display analysis if available
                analysis = validation_results.get('detailed_analysis')
                if isinstance(analysis, dict):
                    _display_analysis_section(analysis)
            else:
                st.error('Invalid validation results format')
                
        except Exception as e:
            st.error(f'Error during validation: {str(e)}')
            st.info('Please check your synopsis content and try again.')

def _display_analysis_section(analysis):
    """Helper function to display analysis section"""
    if not isinstance(analysis, dict):
        return
        
    # Study Type and Design
    st.subheader('Study Type and Design')
    study_design = analysis.get('study_type_and_design', {})
    if isinstance(study_design, dict):
        st.write(f"Primary Classification: {study_design.get('primary_classification', 'Not specified')}")
        st.write(f"Design Type: {study_design.get('design_type', 'Not specified')}")
        st.write(f"Phase: {study_design.get('phase', 'Not specified')}")
        st.write('Key Features:')
        for feature in study_design.get('key_features', []):
            if isinstance(feature, str):
                st.write(f"• {feature}")
    
    # Critical Parameters
    st.subheader('Critical Parameters')
    params = analysis.get('critical_parameters', {})
    if isinstance(params, dict):
        st.write(f"Population: {params.get('population', 'Not specified')}")
        st.write(f"Intervention: {params.get('intervention', 'Not specified')}")
        st.write(f"Control/Comparator: {params.get('control_comparator', 'Not specified')}")
        st.write(f"Primary Endpoint: {params.get('primary_endpoint', 'Not specified')}")
        st.write('Secondary Endpoints:')
        for endpoint in params.get('secondary_endpoints', []):
            if isinstance(endpoint, str):
                st.write(f"• {endpoint}")
