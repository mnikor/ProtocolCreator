import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.gpt_handler import GPTHandler
from utils.missing_information_handler import MissingInformationHandler

logger = logging.getLogger(__name__)

# Define strict section order based on protocol standards
SECTION_ORDER = [
    'title',
    'synopsis',
    'background',
    'objectives',
    'study_design',
    'population',
    'procedures',
    'statistical_analysis',
    'safety',
    'endpoints',
    'ethical_considerations',
    'data_monitoring',
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

def generate_unique_key(section_name: str, field: str, prefix: str = "") -> str:
    """Generate a unique key for streamlit widgets"""
    return f"{prefix}_{section_name}_{field}_{id(field)}"

def generate_ai_suggestion(field: str, section_name: str) -> str:
    """Generate AI suggestion with improved error handling and caching"""
    try:
        # Initialize session state for suggestions if not exists
        if 'ai_suggestions' not in st.session_state:
            st.session_state.ai_suggestions = {}
            
        # Check if suggestion already exists
        suggestion_key = f"{section_name}_{field}"
        if suggestion_key in st.session_state.ai_suggestions:
            return st.session_state.ai_suggestions[suggestion_key]
        
        # Get context from session state
        synopsis = st.session_state.get('synopsis_content', '')
        current_content = st.session_state.generated_sections.get(section_name, '')
        study_type = st.session_state.get('study_type', '')
        
        # Enhanced prompt with study type context and validation requirements
        prompt = f'''Based on this synopsis:
{synopsis}

And current {section_name} section content:
{current_content}

Generate specific content for the {field.replace('_', ' ')} field.
Study type: {study_type}

Consider the following:
1. Study type-specific requirements
2. Quality control measures
3. Validation requirements
4. Regulatory compliance

Focus on:
1. Required elements for {study_type}
2. Consistency with existing content
3. Clear, technical language
4. Concrete details from synopsis'''

        gpt_handler = GPTHandler()
        suggestion = gpt_handler.generate_content(
            prompt=prompt,
            system_message='''You are a protocol development assistant specializing in clinical study protocols.
Generate specific, focused protocol content using clear, direct language.
Ensure all content aligns with study type requirements and regulatory standards.
Include appropriate quality control measures and validation requirements.'''
        )
        
        # Cache valid suggestion
        if suggestion:
            st.session_state.ai_suggestions[suggestion_key] = suggestion
            
        return suggestion
        
    except Exception as e:
        logger.error(f"Error generating AI suggestion: {str(e)}")
        return None

def update_section_content(section_name: str, field: str, value: str):
    """Update section content with error handling"""
    try:
        if not section_name or not field or not value:
            logger.warning("Missing required parameters for update_section_content")
            return
            
        if section_name not in st.session_state.generated_sections:
            logger.warning(f"Section {section_name} not found in generated sections")
            return
            
        current_content = st.session_state.generated_sections[section_name]
        field_title = field.replace('_', ' ').title()
        
        # Add or update field content
        field_pattern = f"{field_title}:"
        lines = current_content.split('\n')
        updated_lines = []
        content_updated = False
        
        for line in lines:
            if line.startswith(field_pattern) and not content_updated:
                updated_lines.append(f"{field_title}: {value}")
                content_updated = True
            else:
                updated_lines.append(line)
                
        if not content_updated:
            updated_lines.append(f"\n{field_title}: {value}")
            
        # Update content and session state
        st.session_state.generated_sections[section_name] = '\n'.join(updated_lines)
        
        # Track update in session state
        if 'updated_sections' not in st.session_state:
            st.session_state.updated_sections = set()
        st.session_state.updated_sections.add(f"{section_name}_{field}")
        
        # Clear cached suggestion
        if 'ai_suggestions' in st.session_state:
            suggestion_key = f"{section_name}_{field}"
            st.session_state.ai_suggestions.pop(suggestion_key, None)
        
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
    """Render protocol editor with improved section ordering"""
    try:
        if not st.session_state.get('generated_sections'):
            logger.debug("No generated sections available")
            return
            
        # Initialize handlers
        improver = ProtocolImprover()
        
        # Order sections according to SECTION_ORDER
        available_sections = set(st.session_state.generated_sections.keys())
        ordered_sections = [s for s in SECTION_ORDER if s in available_sections]
        remaining_sections = sorted(list(available_sections - set(ordered_sections)))
        ordered_sections.extend(remaining_sections)
        
        # Initialize session state for suggestions
        if 'ai_suggestions' not in st.session_state:
            st.session_state.ai_suggestions = {}
        
        # Analyze sections
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
        
        # Display progress
        st.markdown("### 📊 Protocol Development Progress")
        st.progress(progress, text=f"Completion: {progress*100:.1f}%")
        
        # Display Protocol Assessment first
        if analysis_results:
            st.markdown("### 🔍 Protocol Assessment")
            for section_name in ordered_sections:
                if section_name in analysis_results:
                    analysis = analysis_results[section_name]
                    
                    # Section header with severity indicators
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
                    
                    # Display issues with improved input handling
                    for idx, issue in enumerate(analysis['issues']):
                        severity_icon = {
                            'critical': '🔴',
                            'major': '🟡',
                            'minor': '🟢'
                        }.get(issue['severity'], '⚪️')
                        
                        with st.expander(f"{severity_icon} {issue['message']}", expanded=False):
                            st.markdown(f"**Suggestion:** {issue['suggestion']}")
                            
                            # Input area with unique keys
                            field_key = generate_unique_key(section_name, issue['type'], "input")
                            user_input = st.text_area(
                                "Content",
                                key=field_key,
                                height=100,
                                help="Enter content or use AI suggestion below",
                                label_visibility="collapsed"
                            )
                            
                            # Action buttons with unique keys
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(
                                    "📝 Update Section",
                                    key=generate_unique_key(section_name, issue['type'], "update"),
                                    help="Update section with entered content"
                                ):
                                    if user_input.strip():
                                        update_section_content(section_name, issue['type'], user_input)
                                        st.success("✅ Content updated!")
                                        st.rerun()
                            
                            with col2:
                                if st.button(
                                    "🤖 Get AI Suggestion",
                                    key=generate_unique_key(section_name, issue['type'], "suggest"),
                                    help="Generate AI suggestion for this field"
                                ):
                                    with st.spinner("Generating suggestion..."):
                                        suggestion = generate_ai_suggestion(
                                            field=issue['type'],
                                            section_name=section_name
                                        )
                                        if suggestion:
                                            st.markdown("##### Suggested Content:")
                                            st.markdown(suggestion)
                                            if st.button(
                                                "📝 Apply Suggestion",
                                                key=generate_unique_key(section_name, issue['type'], "apply"),
                                                help="Update section with AI suggestion"
                                            ):
                                                update_section_content(section_name, issue['type'], suggestion)
                                                st.success("✅ Content updated!")
                                                st.rerun()
        
        # Display protocol sections
        st.markdown("### 📄 Protocol Sections")
        for section_name in ordered_sections:
            with st.expander(f"📄 {section_name.replace('_', ' ').title()}", expanded=False):
                st.markdown(st.session_state.generated_sections[section_name])
                    
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