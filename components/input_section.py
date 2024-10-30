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
    """Display synopsis validation results in a structured format"""
    with st.spinner("Validating synopsis..."):
        try:
            validation_results = validate_synopsis(content)
            
            # Create expandable sections for validation results
            with st.expander("Synopsis Validation Results", expanded=True):
                # Overall Status
                if validation_results['is_valid']:
                    st.success("✅ Synopsis structure validated successfully!")
                else:
                    st.warning("⚠️ Synopsis validation found some issues")
                
                # Display Study Information
                if 'detailed_analysis' in validation_results:
                    analysis = validation_results['detailed_analysis']
                    
                    # Study Type and Design
                    st.subheader("Study Type and Design")
                    if isinstance(analysis.get('study_type_and_design'), dict):
                        study_design = analysis['study_type_and_design']
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Primary Classification:**")
                            st.markdown(f"_{study_design.get('primary_classification', 'Not specified')}_")
                            st.markdown("**Design Type:**")
                            st.markdown(f"_{study_design.get('design_type', 'Not specified')}_")
                        with col2:
                            st.markdown("**Phase:**")
                            st.markdown(f"_{study_design.get('phase', 'Not specified')}_")
                            if study_design.get('key_features'):
                                st.markdown("**Key Features:**")
                                for feature in study_design.get('key_features', []):
                                    st.markdown(f"• {feature}")
                    
                    # Critical Parameters
                    st.subheader("Critical Parameters")
                    if isinstance(analysis.get('critical_parameters'), dict):
                        params = analysis['critical_parameters']
                        cols = st.columns(2)
                        with cols[0]:
                            st.markdown("**Population:**")
                            st.markdown(f"_{params.get('population', 'Not specified')}_")
                            st.markdown("**Intervention:**")
                            st.markdown(f"_{params.get('intervention', 'Not specified')}_")
                        with cols[1]:
                            st.markdown("**Control/Comparator:**")
                            st.markdown(f"_{params.get('control_comparator', 'Not specified')}_")
                            st.markdown("**Primary Endpoint:**")
                            st.markdown(f"_{params.get('primary_endpoint', 'Not specified')}_")
                        
                        if params.get('secondary_endpoints'):
                            st.markdown("**Secondary Endpoints:**")
                            for endpoint in params.get('secondary_endpoints', []):
                                st.markdown(f"• {endpoint}")
                
                # Missing Sections and Information
                if validation_results.get('missing_sections') or validation_results.get('feedback'):
                    st.subheader("Issues and Recommendations")
                    
                    # Display missing sections
                    if validation_results.get('missing_sections'):
                        st.markdown("**Missing Required Sections:**")
                        for section in validation_results['missing_sections']:
                            with st.container():
                                st.warning(f"📝 {section['section'].title()}")
                                if section.get('suggested_content'):
                                    st.markdown("Suggested content:")
                                    for suggestion in section['suggested_content']:
                                        st.markdown(f"• {suggestion}")
                                if section.get('guidelines'):
                                    st.markdown("_Relevant guidelines: " + ", ".join(section['guidelines']) + "_")
                    
                    # Display detailed feedback
                    if validation_results.get('feedback'):
                        st.markdown("**Detailed Recommendations:**")
                        for item in validation_results['feedback']:
                            with st.container():
                                if item['type'] == 'content_guidance':
                                    st.info(f"💡 {item['message']}")
                                    if item.get('impact'):
                                        st.markdown(f"_Impact: {item['impact']}_")
                                elif item['type'] == 'template_requirement':
                                    st.warning(f"📋 {item['message']}")
                                    if item.get('example_content'):
                                        st.markdown("Example content:")
                                        for example in item['example_content']:
                                            st.markdown(f"• {example}")
                
        except Exception as e:
            st.error(f"Error during validation: {str(e)}")
            st.info("Please check your synopsis content and try again.")
