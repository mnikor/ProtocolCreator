import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.gpt_handler import GPTHandler
from utils.missing_information_handler import MissingInformationHandler

logger = logging.getLogger(__name__)

# Keyboard shortcut definitions
SHORTCUTS = {
    "generate_ai": {"key": "ctrl+g", "description": "Generate AI suggestion"},
    "update_section": {"key": "ctrl+u", "description": "Update section content"},
    "clear_field": {"key": "ctrl+x", "description": "Clear field content"},
    "toggle_details": {"key": "ctrl+d", "description": "Toggle field details"}
}

def calculate_progress(sections_to_display, analysis_results, updated_sections):
    """Calculate overall completion progress"""
    total_sections = len(sections_to_display)
    completed_sections = 0
    
    for section in sections_to_display:
        section_analysis = analysis_results.get(section, {})
        missing_fields = section_analysis.get('missing_fields', [])
        
        # Section is complete if all fields are updated
        is_complete = all(
            f"{section}_{field}" in updated_sections 
            for field in missing_fields
        )
        if is_complete or not missing_fields:
            completed_sections += 1
            
    return completed_sections / total_sections if total_sections > 0 else 0

def generate_ai_suggestion(field: str, section_name: str) -> str:
    try:
        # Get synopsis and current content
        synopsis = st.session_state.get('synopsis_content', '')
        current_content = st.session_state.generated_sections.get(section_name, '')
        
        # Get specific field requirements
        field_requirements = {
            'primary_objective': 'Define the main goal of the study',
            'secondary_objectives': 'List key secondary goals',
            'statistical_methods': 'Specify analysis methods',
            'safety_parameters': 'Define safety monitoring criteria',
            'endpoints': 'Define primary and secondary endpoints',
            'population': 'Specify inclusion/exclusion criteria',
            'study_design': 'Detail study design and methodology',
            'procedures': 'Outline study procedures and assessments',
            'timeline': 'Define study timeline and milestones',
            'data_monitoring': 'Specify data monitoring procedures',
            'ethical_considerations': 'Address ethical aspects and compliance'
        }
        
        field_requirement = field_requirements.get(field, f"Provide content for {field}")
        
        prompt = f'''Based on this synopsis:
{synopsis}

And current {section_name} section content:
{current_content}

Generate specific content for the {field.replace('_', ' ')} field.
Requirement: {field_requirement}

Guidelines:
1. Use specific information from the synopsis and current content
2. Do not duplicate existing content
3. Address the specific missing requirement
4. Use concrete details (drug names, doses, etc.) from synopsis
5. Focus only on {field.replace('_', ' ')}

Study Type: {st.session_state.get('study_type', 'clinical study')}'''
        
        gpt_handler = GPTHandler()
        suggestion = gpt_handler.generate_content(
            prompt=prompt,
            system_message="Generate specific, focused protocol content using available study information. Avoid generic text."
        )
        return suggestion
    except Exception as e:
        logger.error(f"Error generating AI suggestion: {str(e)}")
        return None

def update_section_content(section_name: str, field: str, value: str):
    """Update section content with new field value"""
    try:
        if section_name not in st.session_state.generated_sections:
            return
            
        current_content = st.session_state.generated_sections[section_name]
        field_title = field.replace('_', ' ').title()
        updated_content = f"{current_content}\n\n{field_title}: {value}"
        
        st.session_state.generated_sections[section_name] = updated_content
        
        # Track updated fields
        if 'updated_sections' not in st.session_state:
            st.session_state.updated_sections = set()
        st.session_state.updated_sections.add(f"{section_name}_{field}")
        
    except Exception as e:
        logger.error(f"Error updating section content: {str(e)}")

def render_keyboard_shortcuts():
    """Display available keyboard shortcuts"""
    with st.expander("⌨️ Keyboard Shortcuts", expanded=False):
        st.markdown("""
        | Action | Shortcut | Description |
        |--------|----------|-------------|""")
        for action, details in SHORTCUTS.items():
            st.markdown(f"| {action.replace('_', ' ').title()} | `{details['key']}` | {details['description']} |")

def render_editor():
    '''Render the protocol editor interface with improved section ordering'''
    try:
        if not st.session_state.get('generated_sections'):
            return
            
        # Initialize handlers
        improver = ProtocolImprover()
        missing_info_handler = MissingInformationHandler()
        
        # Get sections to display
        sections_to_display = list(st.session_state.generated_sections.keys())
        
        # Define preferred section order with categories
        section_categories = {
            "Administrative": ['title', 'synopsis'],
            "Background": ['background', 'objectives'],
            "Core Study Design": ['study_design', 'population', 'procedures', 'endpoints'],
            "Statistical": ['statistical_analysis', 'sample_size'],
            "Safety": ['safety', 'data_monitoring'],
            "Data Management": ['data_collection', 'data_quality'],
            "Additional": ['ethical_considerations', 'completion_criteria']
        }
        
        # Create ordered list based on categories
        ordered_sections = []
        for category, sections in section_categories.items():
            category_sections = [s for s in sections if s in sections_to_display]
            ordered_sections.extend(category_sections)
        
        # Add any remaining sections at the end
        remaining_sections = [s for s in sections_to_display if s not in ordered_sections]
        ordered_sections.extend(remaining_sections)
        
        # Analyze all sections
        analysis_results = {}
        for section in ordered_sections:
            content = st.session_state.generated_sections[section]
            analysis = improver.validate_section(
                section,
                content,
                st.session_state.get('study_type')
            )
            if analysis['issues']:
                analysis_results[section] = analysis
                
        # Calculate progress
        progress = calculate_progress(
            ordered_sections,
            analysis_results,
            st.session_state.get('updated_sections', set())
        )
        
        # Show progress bar
        st.progress(progress, text=f"Protocol Completion: {progress*100:.1f}%")
        
        # Display protocol assessment
        if analysis_results:
            st.markdown("### Protocol Assessment")
            
            for section_name in ordered_sections:
                if section_name in analysis_results:
                    analysis = analysis_results[section_name]
                    st.markdown(f"#### {section_name.replace('_', ' ').title()}")
                    
                    # Show severity counts
                    cols = st.columns(3)
                    with cols[0]:
                        if analysis['severity_counts']['critical']:
                            st.error(f"🔴 Critical Issues: {analysis['severity_counts']['critical']}")
                    with cols[1]:
                        if analysis['severity_counts']['major']:
                            st.warning(f"🟡 Major Issues: {analysis['severity_counts']['major']}")
                    with cols[2]:
                        if analysis['severity_counts']['minor']:
                            st.info(f"🟢 Minor Issues: {analysis['severity_counts']['minor']}")
                    
                    # Show detailed issues
                    for idx, issue in enumerate(analysis['issues']):
                        severity_icon = {
                            'critical': '🔴',
                            'major': '🟡',
                            'minor': '🟢'
                        }.get(issue['severity'], '⚪️')
                        
                        with st.expander(f"{severity_icon} {issue['message']}", expanded=False):
                            st.markdown(f"**Suggestion:** {issue['suggestion']}")
                            
                            # Add text input field
                            field_key = f"input_{section_name}_{issue['type']}_{idx}"
                            user_input = st.text_area(
                                "Enter content:",
                                key=field_key,
                                help="Enter your content or use AI suggestion below"
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                # Add update button for manual input
                                if st.button("📝 Update Section", key=f"update_{field_key}"):
                                    if user_input.strip():
                                        update_section_content(section_name, issue['type'], user_input)
                                        st.success("✅ Content updated!")
                                        st.rerun()
                            
                            with col2:
                                # AI suggestion button
                                if st.button("🤖 Get AI Suggestion", key=f"suggest_{section_name}_{issue['type']}_{idx}"):
                                    with st.spinner("Generating suggestion..."):
                                        suggestion = generate_ai_suggestion(
                                            field=issue['type'],
                                            section_name=section_name
                                        )
                                        if suggestion:
                                            st.markdown("### Suggested Content:")
                                            st.markdown(suggestion)
                                            
                                            if st.button("📝 Apply Suggestion", key=f"apply_{section_name}_{issue['type']}_{idx}"):
                                                update_section_content(section_name, issue['type'], suggestion)
                                                st.success("✅ Content updated!")
                                                st.rerun()
        
        # Display protocol sections
        st.markdown("### Protocol Sections")
        
        # Group sections by category
        for category, category_sections in section_categories.items():
            relevant_sections = [s for s in category_sections if s in ordered_sections]
            if relevant_sections:
                st.markdown(f"#### {category}")
                for section_name in relevant_sections:
                    with st.expander(f"📄 {section_name.replace('_', ' ').title()}", expanded=False):
                        st.markdown(st.session_state.generated_sections[section_name])
        
        # Display any remaining sections
        remaining = [s for s in ordered_sections if not any(s in sections for sections in section_categories.values())]
        if remaining:
            st.markdown("#### Other Sections")
            for section_name in remaining:
                with st.expander(f"📄 {section_name.replace('_', ' ').title()}", expanded=False):
                    st.markdown(st.session_state.generated_sections[section_name])
                    
        render_keyboard_shortcuts()
                    
    except Exception as e:
        logger.error(f"Error in editor: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

def add_shortcut_handlers():
    """Add JavaScript handlers for keyboard shortcuts"""
    shortcut_js = """
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'g') {
            e.preventDefault();
            document.querySelector('button[data-testid*="suggest"]').click();
        }
        if (e.ctrlKey && e.key === 'u') {
            e.preventDefault();
            document.querySelector('button[data-testid*="update"]').click();
        }
        if (e.ctrlKey && e.key === 'x') {
            e.preventDefault();
            let activeField = document.activeElement;
            if (activeField.tagName === 'TEXTAREA') {
                activeField.value = '';
                activeField.dispatchEvent(new Event('input'));
            }
        }
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            let detailsExpander = document.querySelector('button[aria-label*="About"]');
            if (detailsExpander) {
                detailsExpander.click();
            }
        }
    });
    </script>
    """
    st.markdown(shortcut_js, unsafe_allow_html=True)
