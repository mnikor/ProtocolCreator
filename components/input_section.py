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
    """Display synopsis validation results"""
    with st.spinner("Validating synopsis..."):
        try:
            validation_results = validate_synopsis(content)
            
            if validation_results['is_valid']:
                st.success("Synopsis structure validated successfully!")
            else:
                st.warning("Synopsis validation found some issues:")
                for section in validation_results['missing_sections']:
                    st.warning(f"Missing section: {section}")
            
            if 'detailed_analysis' in validation_results:
                analysis_dict = validation_results['detailed_analysis']
                
                # Display Study Type and Design
                st.subheader("Study Type and Design")
                study_design = analysis_dict[0].get('study_type_and_design', {})
                st.write(f"Primary Classification: {study_design.get('primary_classification', '')}")
                st.write(f"Design Type: {study_design.get('design_type', '')}")
                st.write(f"Phase: {study_design.get('phase', '')}")
                st.write("Key Features:")
                for feature in study_design.get('key_features', []):
                    st.write(f"• {feature}")
                
                # Display Critical Parameters
                st.subheader("Critical Parameters")
                params = analysis_dict[0].get('critical_parameters', {})
                st.write(f"Population: {params.get('population', '')}")
                st.write(f"Intervention: {params.get('intervention', '')}")
                st.write(f"Control/Comparator: {params.get('control_comparator', '')}")
                st.write(f"Primary Endpoint: {params.get('primary_endpoint', '')}")
                st.write("Secondary Endpoints:")
                for endpoint in params.get('secondary_endpoints', []):
                    st.write(f"• {endpoint}")
                
                # Display Required Sections
                st.subheader("Required Sections")
                for section in analysis_dict[0].get('required_protocol_sections', []):
                    st.write(f"• {section}")
                
                # Display Missing Information
                if analysis_dict[0].get('missing_information'):
                    st.subheader("Missing Information")
                    for item in analysis_dict[0].get('missing_information', []):
                        st.write(f"• {item}")
                
        except Exception as e:
            st.error(f"Error during validation: {str(e)}")
