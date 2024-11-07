import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.gpt_handler import GPTHandler
from utils.missing_information_handler import MissingInformationHandler

logger = logging.getLogger(__name__)

# Define preferred section order
SECTION_ORDER = [
    'title',
    'synopsis',
    'background',
    'objectives',
    'study_design',
    'population',
    'procedures',
    'endpoints',
    'statistical_analysis',
    'safety',
    'data_monitoring',
    'ethical_considerations',
    'completion_criteria'
]

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
        
        # Get field requirements with improved prompts
        field_requirements = {
            'primary_objective': 'Define clear, measurable primary objective',
            'secondary_objectives': 'List specific secondary objectives',
            'statistical_methods': 'Detail statistical analysis approach',
            'safety_parameters': 'Specify safety monitoring criteria',
            'endpoints': 'Define measurable study endpoints',
            'population': 'Detail inclusion/exclusion criteria',
            'study_design': 'Specify study methodology',
            'procedures': 'List study procedures chronologically',
            'timeline': 'Define study milestones',
            'data_monitoring': 'Outline monitoring approach',
            'ethical_considerations': 'Address key ethical aspects'
        }
        
        field_requirement = field_requirements.get(field, f"Provide content for {field}")
        
        # Enhanced prompt with study type context
        prompt = f'''Based on this synopsis:
{synopsis}

And current {section_name} section content:
{current_content}

Generate specific content for the {field.replace('_', ' ')} field.
Requirement: {field_requirement}

Guidelines:
1. Use specific information from the synopsis
2. Avoid duplicating existing content
3. Address the specific requirement
4. Use concrete details from synopsis
5. Focus only on {field.replace('_', ' ')}
6. Ensure consistency with study type: {st.session_state.get('study_type', 'clinical study')}
7. Use clear, concise language
8. Include measurable criteria where applicable'''
        
        gpt_handler = GPTHandler()
        suggestion = gpt_handler.generate_content(
            prompt=prompt,
            system_message="Generate specific, focused protocol content using available study information. Use clear, direct language."
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
        
        # Check if field already exists in content
        field_pattern = f"{field_title}:"
        if field_pattern in current_content:
            # Replace existing content
            lines = current_content.split('\n')
            updated_lines = []
            found = False
            for line in lines:
                if line.startswith(field_pattern) and not found:
                    updated_lines.append(f"{field_title}: {value}")
                    found = True
                else:
                    updated_lines.append(line)
            updated_content = '\n'.join(updated_lines)
        else:
            # Add new content
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
        
        # Get sections and order them
        available_sections = set(st.session_state.generated_sections.keys())
        ordered_sections = [s for s in SECTION_ORDER if s in available_sections]
        remaining_sections = list(available_sections - set(ordered_sections))
        ordered_sections.extend(sorted(remaining_sections))
        
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
        
        # Show progress bar prominently at top
        st.markdown("### 📊 Protocol Development Progress")
        st.progress(progress, text=f"Completion: {progress*100:.1f}%")
        
        # Display protocol assessment
        if analysis_results:
            st.markdown("### 🔍 Protocol Assessment")
            
            for section_name in ordered_sections:
                if section_name in analysis_results:
                    analysis = analysis_results[section_name]
                    
                    # Create section header with severity indicators
                    header_cols = st.columns([3, 1, 1, 1])
                    with header_cols[0]:
                        st.markdown(f"#### {section_name.replace('_', ' ').title()}")
                    with header_cols[1]:
                        if analysis['severity_counts']['critical']:
                            st.error(f"🔴 Critical: {analysis['severity_counts']['critical']}")
                    with header_cols[2]:
                        if analysis['severity_counts']['major']:
                            st.warning(f"🟡 Major: {analysis['severity_counts']['major']}")
                    with header_cols[3]:
                        if analysis['severity_counts']['minor']:
                            st.info(f"🟢 Minor: {analysis['severity_counts']['minor']}")
                    
                    # Show issues with improved layout
                    for idx, issue in enumerate(analysis['issues']):
                        severity_icon = {
                            'critical': '🔴',
                            'major': '🟡',
                            'minor': '🟢'
                        }.get(issue['severity'], '⚪️')
                        
                        with st.expander(f"{severity_icon} {issue['message']}", expanded=False):
                            st.markdown(f"**Suggestion:** {issue['suggestion']}")
                            
                            # Input area with clear layout
                            st.markdown("---")
                            st.markdown("##### Enter Content:")
                            
                            # Unique keys for each field
                            field_key = f"input_{section_name}_{issue['type']}_{idx}"
                            user_input = st.text_area(
                                "",
                                key=field_key,
                                height=100,
                                help="Enter content or use AI suggestion below"
                            )
                            
                            # Action buttons in columns
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("📝 Update Section", key=f"update_{field_key}"):
                                    if user_input.strip():
                                        update_section_content(section_name, issue['type'], user_input)
                                        st.success("✅ Content updated!")
                                        st.rerun()
                            
                            with col2:
                                suggestion_key = f"suggest_{section_name}_{issue['type']}_{idx}"
                                if st.button("🤖 Get AI Suggestion", key=suggestion_key):
                                    with st.spinner("Generating suggestion..."):
                                        suggestion = generate_ai_suggestion(
                                            field=issue['type'],
                                            section_name=section_name
                                        )
                                        if suggestion:
                                            st.markdown("##### Suggested Content:")
                                            st.markdown(suggestion)
                                            st.markdown("---")
                                            if st.button("📝 Apply Suggestion", key=f"apply_{suggestion_key}"):
                                                update_section_content(section_name, issue['type'], suggestion)
                                                st.success("✅ Content updated!")
                                                st.rerun()
        
        # Display protocol sections
        st.markdown("### 📄 Protocol Sections")
        for section_name in ordered_sections:
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