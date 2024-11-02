import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.template_section_generator import TemplateSectionGenerator

logger = logging.getLogger(__name__)

def render_editor():
    """Render the protocol editor with enhanced missing information detection"""
    st.markdown("## Protocol Editor")
    
    # Initialize improver
    improver = ProtocolImprover()
    
    # Check prerequisites
    if not st.session_state.get('synopsis_content'):
        st.warning("Please upload a synopsis first")
        return
    if not st.session_state.get('study_type'):
        st.warning("Please select a study type first")
        return
        
    # Initialize session state for user inputs
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = {}
    
    # Display generated sections if available
    if generated_sections := st.session_state.get('generated_sections'):
        # Analyze protocol sections
        analysis_results = improver.analyze_protocol_sections(generated_sections)
        overall_score = analysis_results['overall_quality_score']
        
        # Display overall quality score
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### Protocol Quality Score")
            quality_color = "green" if overall_score >= 8 else "orange" if overall_score >= 6 else "red"
            st.markdown(f"<h2 style='color: {quality_color}'>{overall_score}/10</h2>", unsafe_allow_html=True)
            
        # Display sections with enhanced feedback
        for section_name, content in generated_sections.items():
            section_analysis = analysis_results['section_analyses'][section_name]
            missing_fields = section_analysis['missing_fields']
            recommendations = section_analysis['recommendations']
            
            # Create expander with completion indicator
            completion = section_analysis['completeness_score'] * 100
            completion_color = "green" if completion >= 80 else "orange" if completion >= 60 else "red"
            
            with st.expander(
                f"📝 {section_name.replace('_', ' ').title()} ({completion:.0f}% complete)",
                expanded=False
            ):
                # Display section content
                st.text_area(
                    "Section content",
                    value=content,
                    height=300,
                    disabled=True,
                    key=f"section_{section_name}"
                )
                
                # Display missing information and recommendations
                if missing_fields or recommendations:
                    st.markdown("#### Section Analysis")
                    
                    if missing_fields:
                        st.warning("Missing Information:")
                        for field in missing_fields:
                            field_key = f"{section_name}_{field}"
                            
                            # Check if we already have user input
                            if field_key not in st.session_state.user_inputs:
                                prompt = improver.generate_field_prompt(field, section_name)
                                user_input = st.text_area(prompt, key=field_key)
                                
                                if user_input:
                                    st.session_state.user_inputs[field_key] = user_input
                                    
                    if recommendations:
                        st.info("Recommendations:")
                        for rec in recommendations:
                            st.markdown(f"- {rec}")
                            
                # Show improvement suggestions
                suggestions = improver.get_improvement_suggestions(section_name, section_analysis)
                if suggestions != "No immediate improvements needed.":
                    with st.expander("💡 Improvement Suggestions"):
                        st.markdown(suggestions)
                        
        # Add update button if there are user inputs
        if st.session_state.user_inputs:
            if st.button("Update Protocol with User Inputs", type="primary"):
                try:
                    # Initialize template generator
                    generator = TemplateSectionGenerator()
                    
                    # Update sections with user inputs
                    updated_sections = dict(generated_sections)
                    for field_key, value in st.session_state.user_inputs.items():
                        section_name = field_key.split('_')[0]
                        if section_name in updated_sections:
                            # Replace placeholder with user input
                            field_name = '_'.join(field_key.split('_')[1:])
                            placeholder = f"[PLACEHOLDER: *{field_name}*]"
                            updated_sections[section_name] = updated_sections[section_name].replace(
                                placeholder, value
                            )
                            
                    # Update session state
                    st.session_state.generated_sections = updated_sections
                    st.success("✅ Protocol updated successfully!")
                    st.rerun()
                    
                except Exception as e:
                    logger.error(f"Error updating protocol: {str(e)}")
                    st.error(f"Error updating protocol: {str(e)}")
    else:
        st.info("Use the 'Generate Complete Protocol' button in the sidebar to generate protocol sections.")
