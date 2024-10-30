def render_input_section():
    """Render the synopsis input section"""
    st.header("Synopsis Input")
    
    # Choose input method
    input_method = st.radio(
        "Choose input method:",
        ["File Upload", "Text Input"],
        label_visibility="collapsed"
    )
    
    if input_method == "File Upload":
        uploaded_file = st.file_uploader(
            "Upload Synopsis",
            type=["pdf", "docx", "txt"],
            help="Upload your synopsis document (PDF, DOCX, or TXT)"
        )
        
        if uploaded_file is not None:
            try:
                # Process uploaded file
                content = read_file_content(uploaded_file)
                if content:
                    # Store in session state
                    st.session_state.synopsis_content = content
                    st.success(f"✅ Successfully processed {uploaded_file.name}")
                    
                    # Debug info
                    with st.expander("Debug Information", expanded=True):
                        st.write({
                            "Synopsis Content Length": len(content),
                            "Synopsis Content Type": type(content),
                            "First 100 chars": content[:100] + "..."
                        })
                    
                    try:
                        # Validate synopsis
                        validation_results = validate_synopsis(content)
                        display_validation_results(validation_results)
                    except Exception as e:
                        st.error(f"Error validating synopsis: {str(e)}")
                        
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    else:
        # Text input method
        synopsis_text = st.text_area(
            "Enter Synopsis Text",
            height=300,
            help="Paste your synopsis text here"
        )
        
        if synopsis_text:
            if st.button("Process Synopsis"):
                # Store in session state
                st.session_state.synopsis_content = synopsis_text
                st.success("✅ Synopsis processed successfully")
                
                try:
                    # Validate synopsis
                    validation_results = validate_synopsis(synopsis_text)
                    display_validation_results(validation_results)
                except Exception as e:
                    st.error(f"Error validating synopsis: {str(e)}")

    # Always show debug info at the bottom
    with st.expander("Session State Debug", expanded=False):
        st.write({
            "Synopsis Present": st.session_state.get('synopsis_content') is not None,
            "Synopsis Length": len(st.session_state.get('synopsis_content', '')) if st.session_state.get('synopsis_content') else 0,
            "Study Type": st.session_state.get('study_type', 'Not Selected')
        })

def display_validation_results(validation_results):
    """Display validation results in a structured way"""
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