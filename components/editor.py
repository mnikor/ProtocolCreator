import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.gpt_handler import GPTHandler
from utils.missing_information_handler import MissingInformationHandler

logger = logging.getLogger(__name__)

def update_section_content(section_name: str, field: str, new_content: str):
    '''Update protocol section content'''
    if section_name in st.session_state.generated_sections:
        current_content = st.session_state.generated_sections[section_name]
        updated_content = f"{current_content}\n\n{field.replace('_', ' ').title()}: {new_content}"
        st.session_state.generated_sections[section_name] = updated_content
        
        # Mark section as updated
        if 'updated_sections' not in st.session_state:
            st.session_state.updated_sections = set()
        st.session_state.updated_sections.add(f"{section_name}_{field}")

def generate_ai_suggestion(field: str, section_name: str) -> str:
    try:
        # Get previously generated content for context
        previous_content = st.session_state.generated_sections.get(section_name, "")
        
        context = f'''Based on this synopsis for a {st.session_state.study_type.replace('_', ' ')} study:
{st.session_state.synopsis_content}

Current section content:
{previous_content}

Generate specific content for the {field.replace('_', ' ')} field in the {section_name} section.
Ensure the suggestion:
1. Does not duplicate existing information
2. Maintains consistency with current content
3. Complements existing details
4. Adds relevant new information
5. Integrates smoothly with current text

Requirements:
- Content must be specific to {st.session_state.study_type.replace('_', ' ')} studies
- Follow standard protocol writing guidelines
- Include specific details and measurements
- Use appropriate scientific terminology
- Format key points with *italic* markers
- Be concise but comprehensive'''

        gpt_handler = GPTHandler()
        suggestion = gpt_handler.generate_content(
            prompt=context,
            system_message="You are a protocol development expert. Generate focused content that complements existing information without duplication."
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

        # Initialize handlers
        improver = ProtocolImprover()
        missing_info_handler = MissingInformationHandler()
            
        # Initialize session state for editor
        if 'editor_states' not in st.session_state:
            st.session_state.editor_states = {}
            
        if 'suggestion_states' not in st.session_state:
            st.session_state.suggestion_states = {}
            
        if 'updated_sections' not in st.session_state:
            st.session_state.updated_sections = set()

        # Define preferred section order based on standard protocol structure
        ordered_sections = [
            # Administrative Information
            'title',
            'synopsis',
            
            # Introduction
            'background',
            'objectives',
            
            # Study Methods
            'study_design',
            'population',
            'procedures',
            
            # Clinical Trial Specific
            'safety',
            'endpoints',
            
            # Data Collection & Analysis
            'data_source',
            'variables',
            'statistical_analysis',
            
            # Research Methodology
            'search_strategy',
            'eligibility_criteria',
            'data_extraction',
            'quality_assessment',
            'synthesis_methods',
            
            # Survey/Questionnaire Specific
            'survey_design',
            'survey_instrument',
            'data_collection',
            
            # Study Governance
            'ethical_considerations',
            'data_monitoring',
            'completion_criteria',
            
            # Discussion
            'limitations',
            'results_reporting'
        ]

        # Filter and sort sections based on study type
        generated_sections = dict(st.session_state.generated_sections)
        sections_to_display = [s for s in ordered_sections if s in generated_sections]
        remaining_sections = [s for s in generated_sections if s not in ordered_sections]
        sections_to_display.extend(remaining_sections)

        # Display Protocol Sections with improved organization
        st.markdown("## 📄 Protocol Sections")
        
        # Get analysis results for all sections
        analysis_results = {}
        for section_name, content in generated_sections.items():
            analysis_results[section_name] = missing_info_handler.analyze_section_completeness(section_name, content)
        
        # Calculate completion progress considering updated sections
        total_sections = len(sections_to_display)
        completed_sections = sum(1 for section in sections_to_display 
                               if not any(f"{section}_{field}" not in st.session_state.get('updated_sections', set())
                                        for field in analysis_results[section]['missing_fields']))
        
        progress = completed_sections / total_sections if total_sections > 0 else 0
        st.progress(progress, text=f"Protocol Completion: {progress*100:.1f}%")

        # Group sections by category
        for section_name in sections_to_display:
            icon = "📝"
            if section_name in ['title', 'synopsis']: icon = "📋"
            elif section_name in ['background', 'objectives']: icon = "🎯"
            elif section_name in ['data_source', 'variables', 'statistical_analysis']: icon = "📊"
            elif section_name in ['ethical_considerations', 'data_monitoring']: icon = "⚖️"
            elif section_name in ['limitations', 'results_reporting']: icon = "💭"
            
            with st.expander(f"{icon} {section_name.replace('_', ' ').title()}", expanded=False):
                # Show update indicator if section has been updated
                if any(f"{section_name}_" in update for update in st.session_state.get('updated_sections', set())):
                    st.info("✏️ This section has been updated")
                
                st.text_area(
                    "Section Content",
                    value=generated_sections[section_name],
                    height=200,
                    key=f"content_view_{section_name}",
                    disabled=True
                )

        # Display Missing Information Section with improved organization
        st.markdown("## 🚨 Required Information")
        
        missing_count = 0
        for section_name in sections_to_display:
            if section_name in analysis_results:
                analysis = analysis_results[section_name]
                # Filter out updated fields
                current_fields = [
                    field for field in analysis['missing_fields']
                    if f"{section_name}_{field}" not in st.session_state.get('updated_sections', set())
                ]
                missing_count += len(current_fields)
                
                if current_fields:  # Only show if there are non-updated fields
                    st.markdown(f"### {section_name.replace('_', ' ').title()}")
                    
                    for idx, field in enumerate(current_fields):
                        field_key = f"{section_name}_{field}_{idx}"
                        
                        # Initialize field state if needed
                        if field_key not in st.session_state.editor_states:
                            st.session_state.editor_states[field_key] = ""
                        
                        # Field input with improved layout
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            current_value = st.text_area(
                                label=f"Enter {field.replace('_', ' ')}:",
                                value=st.session_state.editor_states[field_key],
                                key=field_key,
                                height=100,
                                help=f"Provide details for {field.replace('_', ' ')}"
                            )
                            st.session_state.editor_states[field_key] = current_value
                        
                        with col2:
                            # AI Suggestion button
                            if st.button("🤖 Get AI Suggestion", key=f"suggest_{field_key}"):
                                with st.spinner("Generating suggestion..."):
                                    suggestion = generate_ai_suggestion(field, section_name)
                                    if suggestion:
                                        st.session_state.editor_states[field_key] = suggestion
                                        st.success("✅ Suggestion generated!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to generate suggestion")
                            
                            # Update Section button
                            if st.button("📝 Update Section", key=f"update_{field_key}"):
                                if current_value.strip():
                                    update_section_content(
                                        section_name=section_name,
                                        field=field,
                                        new_content=current_value
                                    )
                                    st.success("✅ Updated!")
                                    st.session_state.editor_states[field_key] = ""
                                    st.rerun()

        if missing_count == 0:
            st.success("✅ All required information has been provided")
        else:
            st.warning(f"Found {missing_count} items that need attention")

    except Exception as e:
        logger.error(f"Error in editor: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
