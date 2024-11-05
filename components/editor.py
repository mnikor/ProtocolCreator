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
    try:
        if 'synopsis_content' not in st.session_state:
            st.error("No synopsis content found")
            return None

        if 'study_type' not in st.session_state:
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

        # Define preferred section order
        ordered_sections = [
            'title',                     # Basic Information
            'synopsis',                  # Overview
            'background',                # Context
            'objectives',                # Goals
            'study_design',              # Design
            'population',                # Participants
            
            # Clinical Trial Specific
            'procedures',
            'endpoints', 
            'safety',
            
            # Research Methodology
            'search_strategy',           # For systematic reviews
            'eligibility_criteria',
            'data_extraction',
            'quality_assessment',
            'synthesis_methods',
            
            # Survey/Questionnaire Specific
            'survey_design',
            'survey_instrument',
            'data_collection',
            
            # Data Analysis
            'data_source',               # For RWE studies
            'variables',
            'statistical_analysis',
            
            # Governance
            'ethical_considerations',
            'data_monitoring',
            'completion_criteria',
            
            # Reporting
            'results_reporting',
            'limitations'
        ]

        # Get all generated sections
        all_sections = list(st.session_state.generated_sections.keys())

        # Filter and sort sections
        sections_to_display = [section for section in ordered_sections 
                             if section in st.session_state.generated_sections]
        remaining_sections = [section for section in all_sections 
                            if section not in ordered_sections]
        sections_to_display.extend(remaining_sections)

        # Display Protocol Sections
        st.markdown("## 📄 Generated Protocol Sections")
        
        for section_name in sections_to_display:
            content = st.session_state.generated_sections[section_name]
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
        analysis_results = improver.analyze_protocol_sections(st.session_state.generated_sections)
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
                            
                            # Initialize field state
                            if field_key not in st.session_state.editor_states:
                                st.session_state.editor_states[field_key] = ""

                            # Field input
                            current_value = st.text_area(
                                label=f"Enter information for {field.replace('_', ' ')}:",
                                value=st.session_state.editor_states[field_key],
                                key=field_key,
                                height=100,
                                help=f"Enter details for {field.replace('_', ' ')}"
                            )
                            st.session_state.editor_states[field_key] = current_value

                            # Action buttons
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("🤖 Get AI Suggestion", key=f"suggest_{field_key}"):
                                    suggestion = generate_ai_suggestion(field, section_name)
                                    if suggestion:
                                        st.session_state.editor_states[field_key] = suggestion
                                        st.success("✅ AI suggestion generated!")
                                        st.rerun()

                            with col2:
                                if st.button("📝 Update Section", key=f"update_{field_key}"):
                                    if current_value.strip():
                                        update_section_content(
                                            section_name=section_name,
                                            field=field,
                                            new_content=current_value
                                        )
                                        st.success("✅ Section updated!")
                                        st.rerun()
                                    else:
                                        st.warning("Please enter content before updating.")
        else:
            st.success("✅ All required information has been provided")

    except Exception as e:
        logger.error(f"Error in editor: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
