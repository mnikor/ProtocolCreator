import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.template_section_generator import TemplateSectionGenerator

logger = logging.getLogger(__name__)

def update_section_content(section_name: str):
    """Update section content with user inputs"""
    try:
        content = st.session_state.generated_sections[section_name]
        for field_key, value in st.session_state.user_inputs.items():
            if field_key.startswith(f"{section_name}_"):
                field = field_key.replace(f"{section_name}_", "")
                placeholder = f"[PLACEHOLDER: *{field}*]"
                content = content.replace(placeholder, value)
        
        st.session_state.generated_sections[section_name] = content
        st.success(f"✅ {section_name.title()} updated successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error updating section: {str(e)}")

def render_editor():
    """Render the protocol editor with enhanced missing information detection"""
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
        # Add prominent missing information summary at the top
        st.markdown("## 📋 Protocol Review")
        
        # Analyze protocol sections
        analysis_results = improver.analyze_protocol_sections(generated_sections)
        
        # Quality metrics in columns
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Protocol Quality Score", f"{analysis_results['overall_quality_score']}/10")
        with col2:
            missing_count = sum(len(section['missing_fields']) 
                              for section in analysis_results['section_analyses'].values())
            if missing_count > 0:
                st.error(f"⚠️ {missing_count} items need attention")
            else:
                st.success("✅ All required information provided")
        
        # Display missing information prominently
        missing_info = False
        for section_name, analysis in analysis_results['section_analyses'].items():
            if analysis['missing_fields']:
                if not missing_info:
                    st.markdown("### ❗ Required Information")
                    missing_info = True
                
                with st.expander(f"📝 {section_name.replace('_', ' ').title()}", expanded=True):
                    for field in analysis['missing_fields']:
                        field_key = f"{section_name}_{field}"
                        st.markdown(f"**{field.replace('_', ' ').title()}**")
                        
                        # Add input field with previous value
                        previous_value = st.session_state.user_inputs.get(field_key, "")
                        user_input = st.text_area(
                            "Enter missing information:",
                            value=previous_value,
                            key=field_key,
                            help=f"Add details about {field.replace('_', ' ')}"
                        )
                        
                        if user_input:
                            st.session_state.user_inputs[field_key] = user_input
                            
                    if st.button(f"Update {section_name}", key=f"update_{section_name}"):
                        update_section_content(section_name)
        
        # Display all sections with content
        st.markdown("## 📄 Protocol Sections")
        for section_name, content in generated_sections.items():
            with st.expander(f"📝 {section_name.replace('_', ' ').title()}", expanded=False):
                # Display section content
                st.text_area(
                    "Section Content",
                    value=content,
                    height=200,
                    key=f"content_{section_name}",
                    disabled=True
                )
                
                # Display recommendations if any
                recommendations = analysis_results['section_analyses'][section_name].get('recommendations', [])
                if recommendations:
                    st.markdown("#### 💡 Recommendations")
                    for rec in recommendations:
                        st.info(rec)
        
        # Global Update Button
        if st.session_state.user_inputs:
            st.markdown("---")
            st.markdown("### 🔄 Update All Sections")
            if st.button("Update Protocol with All Input", type="primary"):
                try:
                    updated_sections = dict(generated_sections)
                    for field_key, value in st.session_state.user_inputs.items():
                        section_name = field_key.split('_')[0]
                        if section_name in updated_sections:
                            field = '_'.join(field_key.split('_')[1:])
                            placeholder = f"[PLACEHOLDER: *{field}*]"
                            updated_sections[section_name] = updated_sections[section_name].replace(
                                placeholder, value
                            )
                    
                    st.session_state.generated_sections = updated_sections
                    st.success("✅ Protocol updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating protocol: {str(e)}")
    else:
        st.info("Use the 'Generate Complete Protocol' button in the sidebar to generate protocol sections.")
