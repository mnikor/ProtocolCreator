import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.gpt_handler import GPTHandler

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
    
    # Add custom styling
    st.markdown("""
        <style>
        .suggestion-button {
            background-color: #7c4dff !important;
            color: white !important;
            padding: 0.5rem !important;
            margin-top: 0.5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
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
        st.markdown("## 🚨 Missing Information")
        st.markdown("Please provide the following required information:")
        
        # Analyze protocol sections
        analysis_results = improver.analyze_protocol_sections(generated_sections)
        missing_count = sum(len(section['missing_fields']) 
                          for section in analysis_results['section_analyses'].values())
        
        if missing_count > 0:
            st.warning(f"Found {missing_count} items that need your attention")
            
            # Group missing fields by section
            for section_name, analysis in analysis_results['section_analyses'].items():
                if analysis['missing_fields']:
                    st.markdown(f"### 📝 {section_name.replace('_', ' ').title()}")
                    
                    for field in analysis['missing_fields']:
                        field_key = f"{section_name}_{field}"
                        col1, col2 = st.columns([2, 3])
                        
                        with col1:
                            st.markdown(f"**{field.replace('_', ' ').title()}**")
                        
                        with col2:
                            # Add input field with previous value
                            previous_value = st.session_state.user_inputs.get(field_key, "")
                            st.text_area(
                                label=f"Enter information for {field.replace('_', ' ')}:",
                                value=previous_value,
                                key=field_key,
                                height=100
                            )
                            
                            # Add AI suggestion button
                            if st.button(f"🤖 Get AI Suggestion", key=f"suggest_{field_key}", help="Generate AI suggestion for this field"):
                                with st.spinner("Generating suggestion..."):
                                    # Get suggestion from GPT
                                    prompt = f'''Based on this synopsis:
{st.session_state.synopsis_content}

Generate specific content for the {field.replace('_', ' ')} field in the {section_name} section.
Focus on providing detailed, relevant information that matches the study context.
Format any key points with *italic* markers.'''

                                    try:
                                        gpt_handler = GPTHandler()
                                        suggestion = gpt_handler.generate_content(prompt)
                                        
                                        # Store suggestion in session state
                                        st.session_state.user_inputs[field_key] = suggestion
                                        st.success("✅ Suggestion generated!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error generating suggestion: {str(e)}")
                    
                    # Add update button for each section
                    if st.button(f"Update {section_name.title()}", key=f"update_{section_name}"):
                        update_section_content(section_name)
                    
                    st.markdown("---")
        else:
            st.success("✅ All required information has been provided")
        
        # Show protocol sections after missing information
        st.markdown("## 📄 Protocol Sections")
        for section_name, content in generated_sections.items():
            with st.expander(f"📝 {section_name.replace('_', ' ').title()}", expanded=False):
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
