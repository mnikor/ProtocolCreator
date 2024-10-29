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
                    
            st.subheader("Detailed Analysis")
            st.json(validation_results['detailed_analysis'])
            
        except Exception as e:
            st.error(f"Error during validation: {str(e)}")
