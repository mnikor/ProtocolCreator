import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.gpt_handler import GPTHandler

logger = logging.getLogger(__name__)

def update_section_content(section_name: str, field: str, new_content: str):
    '''Update protocol section content'''
    if section_name in st.session_state.generated_sections:
        current_content = st.session_state.generated_sections[section_name]
        updated_content = f"{current_content}\n\n{field.replace('_', ' ').title()}: {new_content}"
        st.session_state.generated_sections[section_name] = updated_content

def generate_ai_suggestion(field: str, section_name: str) -> str:
    '''Generate AI suggestion for missing field'''
    try:
        if not st.session_state.get('synopsis_content'):
            st.error("No synopsis content found")
            return None

        if not st.session_state.get('study_type'):
            st.error("Study type not detected")
            return None

        gpt_handler = GPTHandler()
        context = f'''Based on this synopsis:
{st.session_state.synopsis_content}

Generate specific content for the {field.replace('_', ' ')} field in the {section_name} section.
This is for a {st.session_state.study_type} study.

Requirements:
- Be specific and detailed
- Match the study context and type
- Format key points with *italic* markers
- Be concise but comprehensive'''

        suggestion = gpt_handler.generate_content(
            prompt=context,
            system_message="You are a protocol development expert. Generate focused, scientific content."
        )
        
        return suggestion if suggestion else None

    except Exception as e:
        logger.error(f"AI suggestion error: {str(e)}")
        return None

def render_editor():
    '''Render the protocol editor interface'''
    try:
        if not st.session_state.get('generated_sections'):
            return

        # Initialize session state for editor
        if 'editor_states' not in st.session_state:
            st.session_state.editor_states = {}
            
        if 'suggestion_states' not in st.session_state:
            st.session_state.suggestion_states = {}

        # Define preferred section order
        ordered_sections = [
            'title',                  # Basic Information
            'synopsis',               # Overview
            'background',             # Context
            'objectives',             # Goals
            'study_design',           # Design
            'population',             # Participants
            'procedures',             # Clinical Trial Specific
            'endpoints',
            'safety',
            'search_strategy',        # Research Methodology
            'eligibility_criteria',
            'data_extraction',
            'quality_assessment',
            'synthesis_methods',
            'survey_design',          # Survey/Questionnaire Specific
            'survey_instrument',
            'data_collection',
            'data_source',            # Data Analysis
            'variables',
            'statistical_analysis',
            'ethical_considerations',  # Governance
            'data_monitoring',
            'completion_criteria',
            'results_reporting',      # Reporting
            'limitations'
        ]

        # Filter and sort sections
        generated_sections = dict(st.session_state.generated_sections)
        sections_to_display = [s for s in ordered_sections if s in generated_sections]
        remaining_sections = [s for s in generated_sections if s not in ordered_sections]
        sections_to_display.extend(remaining_sections)

        # Display Protocol Sections
        st.markdown("## 📄 Generated Protocol Sections")
        
        for section_name in sections_to_display:
            content = generated_sections[section_name]
            with st.expander(f"📝 {section_name.replace('_', ' ').title()}", expanded=False):
                st.text_area(
                    "Section Content",
                    value=content,
                    height=200,
                    key=f"content_view_{section_name}",
                    disabled=True
                )

        # Analyze Protocol Content
        improver = ProtocolImprover()
        analysis_results = improver.analyze_protocol_sections(generated_sections)
        missing_count = sum(len(section['missing_fields']) 
                          for section in analysis_results['section_analyses'].values())

        # Display Missing Information Section
        st.markdown("## 🚨 Missing Information")
        if missing_count > 0:
            st.warning(f"Found {missing_count} items that need your attention")

            for section_name in sections_to_display:
                if section_name in analysis_results['section_analyses']:
                    analysis = analysis_results['section_analyses'][section_name]
                    if analysis['missing_fields']:
                        st.markdown(f"### 📝 {section_name.replace('_', ' ').title()}")

                        for idx, field in enumerate(analysis['missing_fields']):
                            field_key = f"{section_name}_{field}_{idx}"
                            
                            # Initialize field state if needed
                            if field_key not in st.session_state.editor_states:
                                st.session_state.editor_states[field_key] = ""
                            
                            # Field input with proper state management
                            current_value = st.text_area(
                                label=f"Enter information for {field.replace('_', ' ')}:",
                                value=st.session_state.editor_states[field_key],
                                key=field_key,
                                height=100,
                                help=f"Enter details for {field.replace('_', ' ')}"
                            )
                            
                            # Store value in session state
                            if current_value != st.session_state.editor_states[field_key]:
                                st.session_state.editor_states[field_key] = current_value

                            # Action buttons with improved state management
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                suggestion_key = f"suggest_{field_key}"
                                if st.button("🤖 Get AI Suggestion", key=suggestion_key):
                                    with st.spinner("Generating suggestion..."):
                                        suggestion = generate_ai_suggestion(field, section_name)
                                        if suggestion:
                                            st.session_state.editor_states[field_key] = suggestion
                                            st.success("✅ AI suggestion generated!")
                                            st.session_state.suggestion_states[suggestion_key] = True
                                        else:
                                            st.error("Failed to generate suggestion")

                            with col2:
                                update_key = f"update_{field_key}"
                                if st.button("📝 Update Section", key=update_key):
                                    if current_value.strip():
                                        update_section_content(
                                            section_name=section_name,
                                            field=field,
                                            new_content=current_value
                                        )
                                        st.success("✅ Section updated!")
                                        st.session_state.editor_states[field_key] = ""  # Clear input after update
                                    else:
                                        st.warning("Please enter content before updating.")
        else:
            st.success("✅ All required information has been provided")

    except Exception as e:
        logger.error(f"Error in editor: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
