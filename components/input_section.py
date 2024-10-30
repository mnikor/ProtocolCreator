import streamlit as st
from utils.file_processor import read_file_content
from utils.gpt_handler import GPTHandler
from utils.synopsis_validator import validate_synopsis

def render_input_section():
    """Render the synopsis input section"""
    st.header("Synopsis Input")

    uploaded_file = st.file_uploader(
        "Upload Synopsis",
        type=["pdf", "docx", "txt"],
        help="Upload your synopsis document"
    )

    if uploaded_file:
        try:
            # Process file
            content = read_file_content(uploaded_file)
            if content:
                st.success(f"✅ Successfully processed {uploaded_file.name}")

                # Initial GPT Analysis
                with st.spinner("Analyzing synopsis..."):
                    gpt_handler = GPTHandler()
                    analysis_results, detected_phase = gpt_handler.analyze_synopsis(content)

                    # Store results in session state
                    st.session_state.synopsis_content = content
                    st.session_state.synopsis_analysis = analysis_results
                    st.session_state.detected_phase = detected_phase

                # Display Analysis Results
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Study Design")
                    design_info = analysis_results.get('study_type_and_design', {})
                    st.write(f"**Type:** {design_info.get('primary_classification', 'Not specified')}")
                    st.write(f"**Design:** {design_info.get('design_type', 'Not specified')}")
                    st.write(f"**Phase:** {design_info.get('phase', 'Not specified')}")

                    if design_info.get('key_features'):
                        st.write("**Key Features:**")
                        for feature in design_info['key_features']:
                            st.write(f"- {feature}")

                with col2:
                    st.subheader("Critical Parameters")
                    params = analysis_results.get('critical_parameters', {})
                    st.write(f"**Population:** {params.get('population', 'Not specified')}")
                    st.write(f"**Intervention:** {params.get('intervention', 'Not specified')}")
                    st.write(f"**Control:** {params.get('control_comparator', 'Not specified')}")
                    st.write(f"**Primary Endpoint:** {params.get('primary_endpoint', 'Not specified')}")

                # Show validation status
                st.subheader("Validation Status")
                missing_info = analysis_results.get('missing_information', [])
                if missing_info:
                    st.warning("⚠️ Potential Issues Identified:")
                    for issue in missing_info:
                        st.write(f"- {issue}")
                else:
                    st.success("✅ No major issues identified")

                # Confirm Study Phase
                st.subheader("Confirm Study Phase")
                detected_text = f"Detected Phase: {detected_phase.replace('phase', 'Phase ')}"
                st.info(f"👉 {detected_text}")

                phase_options = {
                    'phase1': 'Phase 1',
                    'phase2': 'Phase 2',
                    'phase3': 'Phase 3'
                }

                selected_phase = st.selectbox(
                    "Confirm or modify study phase:",
                    options=list(phase_options.keys()),
                    format_func=lambda x: phase_options[x],
                    index=list(phase_options.keys()).index(detected_phase) if detected_phase in phase_options else 0,
                    key='phase_selection'
                )

                if st.button("Confirm and Continue", key='confirm_phase'):
                    st.session_state.study_type = selected_phase
                    st.success("✅ Study phase confirmed. You can now proceed with protocol generation.")
                    st.rerun()

        except Exception as e:
            st.error(f"Error processing synopsis: {str(e)}")
            st.error("Please make sure your synopsis file is properly formatted and try again.")

    # Debug information
    with st.expander("Debug Information", expanded=False):
        synopsis_content = st.session_state.get('synopsis_content')
        st.json({
            "Synopsis Present": synopsis_content is not None,
            "Synopsis Length": len(synopsis_content) if synopsis_content else 0,
            "Study Type": st.session_state.get('study_type'),
            "Analysis Results": st.session_state.get('synopsis_analysis'),
            "Detected Phase": st.session_state.get('detected_phase')
        })
