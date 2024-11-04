import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.gpt_handler import GPTHandler

logger = logging.getLogger(__name__)

def update_section_content(section_name: str, field: str, new_content: str):
    '''Update protocol section content'''
    if section_name in st.session_state.generated_sections:
        current_content = st.session_state.generated_sections[section_name]
        # Replace or append the field content
        updated_content = f"{current_content}\n\n{field.replace('_', ' ').title()}: {new_content}"
        st.session_state.generated_sections[section_name] = updated_content

def generate_ai_suggestion(field: str, section_name: str) -> str:
    try:
        synopsis_content = st.session_state.get('synopsis_content')
        study_type = st.session_state.get('study_type')
        
        if not synopsis_content or not study_type:
            st.error("⚠️ Missing required context. Please ensure protocol is generated first.")
            return None
            
        # Create GPT handler
        gpt_handler = GPTHandler()
        
        # Build prompt
        context = f'''Based on this synopsis:
{synopsis_content}

Generate specific content for the {field.replace('_', ' ')} field in the {section_name} section.
This is for a {study_type} study.

Requirements:
- Be specific and detailed
- Match the study context and type
- Format key points with *italic* markers
- Be concise but comprehensive'''

        # Generate suggestion
        suggestion = gpt_handler.generate_content(
            prompt=context,
            system_message="You are a protocol development expert. Generate focused, scientific content."
        )
        
        return suggestion
            
    except Exception as e:
        logger.error(f"AI suggestion error: {str(e)}")
        st.error(f"Error generating suggestion: {str(e)}")
        return None

def render_editor():
    '''Render the protocol editor interface'''
    try:
        if not st.session_state.get('generated_sections'):
            return
            
        # Initialize all session state variables first
        if 'editor_states' not in st.session_state:
            st.session_state.editor_states = {}
            
        # Show generated sections first
        st.markdown("## 📄 Generated Protocol Sections")
        for section_name, content in st.session_state.generated_sections.items():
            with st.expander(f"📝 {section_name.replace('_', ' ').title()}", expanded=False):
                content_key = f"content_view_{section_name}"
                st.text_area(
                    "Section Content",
                    value=content,
                    height=200,
                    key=content_key,
                    disabled=True
                )
        
        # Initialize improver
        improver = ProtocolImprover()
        
        # Analyze protocol sections
        analysis_results = improver.analyze_protocol_sections(st.session_state.generated_sections)
        missing_count = sum(len(section['missing_fields']) 
                          for section in analysis_results['section_analyses'].values())
        
        # Show missing information section after generated sections
        st.markdown("## 🚨 Missing Information")
        if missing_count > 0:
            st.warning(f"Found {missing_count} items that need your attention")
            
            # Group missing fields by section
            for section_name, analysis in analysis_results['section_analyses'].items():
                if analysis['missing_fields']:
                    st.markdown(f"### 📝 {section_name.replace('_', ' ').title()}")
                    
                    for idx, field in enumerate(analysis['missing_fields']):
                        field_key = f"{section_name}_{field}_{idx}"
                        
                        # Initialize state for this field if not exists
                        if field_key not in st.session_state.editor_states:
                            st.session_state.editor_states[field_key] = ""
                            
                        # Add input field
                        current_value = st.text_area(
                            label=f"Enter information for {field.replace('_', ' ')}:",
                            value=st.session_state.editor_states[field_key],
                            key=field_key,
                            height=100
                        )
                        
                        # Store value back in session state
                        st.session_state.editor_states[field_key] = current_value
                        
                        # Add buttons in columns
                        col1, col2 = st.columns(2)
                        
                        # AI Suggestion button in first column
                        with col1:
                            if st.button("🤖 Get AI Suggestion", key=f"suggest_{field_key}"):
                                with st.spinner("Generating suggestion..."):
                                    suggestion = generate_ai_suggestion(field, section_name)
                                    if suggestion:
                                        st.session_state.editor_states[field_key] = suggestion
                                        st.success("✅ AI suggestion generated!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to generate suggestion")
                        
                        # Show Update Section button whenever there's content
                        with col2:
                            if current_value.strip():  # Show button if there's any content
                                if st.button("📝 Update Section", key=f"update_{field_key}"):
                                    update_section_content(
                                        section_name=section_name,
                                        field=field,
                                        new_content=current_value
                                    )
                                    st.success("✅ Section updated!")
                                    st.rerun()
        else:
            st.success("✅ All required information has been provided")
            
    except Exception as e:
        logger.error(f"Error in editor: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
