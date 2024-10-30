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
    """Display synopsis validation results with enhanced formatting"""
    with st.spinner('Validating synopsis...'):
        try:
            validation_results = validate_synopsis(content)
            
            if not isinstance(validation_results, dict):
                st.error('Invalid validation results format')
                return
                
            # Create columns for better organization
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader('Validation Status')
                if validation_results.get('is_valid'):
                    st.success('✅ Synopsis structure validated successfully!')
                else:
                    st.warning('⚠️ Synopsis validation found some issues')
                
                # Display missing sections with guidelines
                if validation_results.get('missing_sections'):
                    st.subheader('Missing Sections')
                    for section in validation_results['missing_sections']:
                        if isinstance(section, dict):
                            with st.expander(f"📝 {section.get('section', '').title()}"):
                                st.warning(f"This section is required according to {', '.join(section.get('guidelines', []))}")
                                if section.get('suggested_content'):
                                    st.markdown("**Suggested content:**")
                                    for suggestion in section['suggested_content']:
                                        st.markdown(f"• {suggestion}")
            
            with col2:
                # Display detailed analysis
                analysis = validation_results.get('detailed_analysis')
                if isinstance(analysis, dict):
                    st.subheader('Study Analysis')
                    
                    # Study Type and Design
                    with st.expander('🔍 Study Type and Design', expanded=True):
                        study_design = analysis.get('study_type_and_design', {})
                        if isinstance(study_design, dict):
                            st.markdown(f"**Primary Classification:** {study_design.get('primary_classification', 'Not specified')}")
                            st.markdown(f"**Design Type:** {study_design.get('design_type', 'Not specified')}")
                            st.markdown(f"**Phase:** {study_design.get('phase', 'Not specified')}")
                            if study_design.get('key_features'):
                                st.markdown("**Key Features:**")
                                for feature in study_design['key_features']:
                                    if isinstance(feature, str):
                                        st.markdown(f"• {feature}")
                    
                    # Critical Parameters
                    with st.expander('📊 Critical Parameters', expanded=True):
                        params = analysis.get('critical_parameters', {})
                        if isinstance(params, dict):
                            st.markdown(f"**Population:** {params.get('population', 'Not specified')}")
                            st.markdown(f"**Intervention:** {params.get('intervention', 'Not specified')}")
                            st.markdown(f"**Control/Comparator:** {params.get('control_comparator', 'Not specified')}")
                            st.markdown(f"**Primary Endpoint:** {params.get('primary_endpoint', 'Not specified')}")
                            if params.get('secondary_endpoints'):
                                st.markdown("**Secondary Endpoints:**")
                                for endpoint in params['secondary_endpoints']:
                                    if isinstance(endpoint, str):
                                        st.markdown(f"• {endpoint}")
            
            # Display feedback and recommendations
            if validation_results.get('feedback'):
                st.subheader('💡 Recommendations')
                for item in validation_results['feedback']:
                    if isinstance(item, dict):
                        if item.get('type') == 'content_guidance':
                            st.info(item.get('message'))
                            if item.get('impact'):
                                st.caption(f"Impact: {item['impact']}")
                        elif item.get('type') == 'template_requirement':
                            st.warning(item.get('message'))
                            if item.get('example_content'):
                                with st.expander("View suggested content"):
                                    for example in item['example_content']:
                                        st.markdown(f"• {example}")
                
        except Exception as e:
            st.error(f'Error during validation: {str(e)}')
            st.info('Please check your synopsis content and try again.')
