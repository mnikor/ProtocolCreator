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
        if 'synopsis_content' not in st.session_state:
            st.error("No synopsis content found")
            return None
            
        if 'study_type' not in st.session_state:
            st.error("Study type not detected")
            return None
        
        # Create GPT handler
        gpt_handler = GPTHandler()
        
        # Build prompt
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
        
        if suggestion:
            return suggestion
        else:
            st.error("Failed to generate suggestion - no content returned")
            return None
            
    except Exception as e:
        logger.error(f"AI suggestion error: {str(e)}")
        st.error(f"Error generating suggestion: {str(e)}")
        return None

def render_editor():
    '''Render the protocol editor interface'''
    try:
        if not st.session_state.get('generated_sections'):
            return
            
        # Initialize session state
        if 'editor_states' not in st.session_state:
            st.session_state.editor_states = {}
            
        # Show generated sections first
        st.markdown("## 📄 Generated Protocol Sections")
        
        # Get all generated sections and sort them
        all_sections = list(st.session_state.generated_sections.keys())
        
        # Define preferred section order (add any new sections at the appropriate position)
        ordered_sections = [
            'title',
            'background',
            'objectives',
            'study_design',
            'population',
            'search_strategy',       # For systematic reviews
            'eligibility_criteria',  # For systematic reviews
            'data_extraction',       # For systematic reviews
            'quality_assessment',    # For systematic reviews
            'synthesis_methods',     # For systematic reviews
            'survey_design',         # For patient surveys
            'survey_instrument',     # For patient surveys
            'data_collection',       # For patient surveys
            'data_source',          # For secondary RWE
            'variables',            # For secondary RWE
            'procedures',
            'statistical_analysis',
            'safety',
            'endpoints',
            'ethical_considerations',
            'data_monitoring',
            'completion_criteria',
            'results_reporting',     # For systematic reviews
            'limitations'            # For secondary RWE
        ]
        
        # Filter ordered sections to only show those that exist in generated_sections
        sections_to_display = [section for section in ordered_sections 
                             if section in st.session_state.generated_sections]
        
        # Add any sections that might be in generated_sections but not in ordered_sections
        remaining_sections = [section for section in all_sections 
                            if section not in ordered_sections]
        sections_to_display.extend(remaining_sections)
        
        # Display sections in the determined order
        for section_name in sections_to_display:
            content = st.session_state.generated_sections[section_name]
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
            for section_name in sections_to_display:  # Use same order as display
                if section_name in analysis_results['section_analyses']:
                    analysis = analysis_results['section_analyses'][section_name]
                    if analysis['missing_fields']:
                        st.markdown(f"### 📝 {section_name.replace('_', ' ').title()}")
                        
                        for idx, field in enumerate(analysis['missing_fields']):
                            field_key = f"{section_name}_{field}_{idx}"
                            
                            # Initialize state for this field if not exists
                            if field_key not in st.session_state.editor_states:
                                st.session_state.editor_states[field_key] = ""
                                
                            # Add input field with proper state management
                            current_value = st.text_area(
                                label=f"Enter information for {field.replace('_', ' ')}:",
                                value=st.session_state.editor_states[field_key],
                                key=field_key,
                                height=100,
                                help=f"Enter details for {field.replace('_', ' ')}"
                            )

                            # Store value back in session state immediately
                            st.session_state.editor_states[field_key] = current_value

                            # Add buttons in columns whenever there's content
                            col1, col2 = st.columns(2)

                            # AI Suggestion button in first column
                            with col1:
                                if st.button("🤖 Get AI Suggestion", key=f"suggest_{field_key}"):
                                    try:
                                        with st.spinner("Generating suggestion..."):
                                            suggestion = generate_ai_suggestion(field, section_name)
                                            if suggestion:
                                                st.session_state.editor_states[field_key] = suggestion
                                                st.success("✅ AI suggestion generated!")
                                                st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")

                            # Show Update Section button whenever there's content (manual or AI)
                            with col2:
                                if current_value.strip():  # Show button for any non-empty content
                                    if st.button("📝 Update Section", key=f"update_{field_key}"):
                                        try:
                                            update_section_content(
                                                section_name=section_name,
                                                field=field,
                                                new_content=current_value
                                            )
                                            st.success("✅ Section updated!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
        else:
            st.success("✅ All required information has been provided")
            
    except Exception as e:
        logger.error(f"Error in editor: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
