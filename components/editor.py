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

def render_keyboard_shortcuts():
    """Display available keyboard shortcuts"""
    with st.expander("⌨️ Keyboard Shortcuts", expanded=False):
        st.markdown("""
        | Action | Shortcut | Description |
        |--------|----------|-------------|""")
        for action, details in SHORTCUTS.items():
            st.markdown(f"| {action.replace('_', ' ').title()} | `{details['key']}` | {details['description']} |")

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

def render_editor():
    '''Render the protocol editor interface'''
    try:
        if not st.session_state.get('generated_sections'):
            return
            
        # Initialize handlers
        improver = ProtocolImprover()
        missing_info_handler = MissingInformationHandler()
        
        # Get sections to display
        sections_to_display = list(st.session_state.generated_sections.keys())
        
        # Define preferred section order
        section_order = [
            # Administrative
            'title', 'synopsis',
            # Background
            'background', 'objectives',
            # Core Study Design
            'study_design', 'population', 'procedures', 'endpoints',
            # Statistical
            'statistical_analysis', 'sample_size',
            # Safety
            'safety', 'data_monitoring',
            # Data Management
            'data_collection', 'data_quality',
            # Additional
            'ethical_considerations', 'completion_criteria'
        ]
        
        # Sort sections according to defined order
        sections_to_display.sort(key=lambda x: section_order.index(x) if x in section_order else len(section_order))
        
        # Analyze all sections
        analysis_results = {}
        for section in sections_to_display:
            analysis = missing_info_handler.analyze_section_completeness(
                section,
                st.session_state.generated_sections[section]
            )
            if analysis['missing_fields']:
                analysis_results[section] = analysis
                
        # Calculate progress
        progress = calculate_progress(
            sections_to_display,
            analysis_results,
            st.session_state.get('updated_sections', set())
        )
        
        # Show progress bar
        st.progress(progress, text=f"Protocol Completion: {progress*100:.1f}%")
        
        # Display missing information sections
        if analysis_results:
            st.markdown("### Missing Information")
            st.markdown("Please provide the following information to complete the protocol:")
            
            for section_name in sections_to_display:
                if section_name in analysis_results:
                    analysis = analysis_results[section_name]
                    if analysis['missing_fields']:
                        st.markdown(f"#### {section_name.replace('_', ' ').title()}")
                        
                        # Handle each missing field
                        for idx, field in enumerate(analysis['missing_fields']):
                            field_key = f"{section_name}_{field}_{idx}"
                            
                            # Initialize field state if needed
                            if field_key not in st.session_state:
                                st.session_state[field_key] = ""
                            
                            # Field input with improved layout
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                current_value = st.text_area(
                                    label=f"Enter {field.replace('_', ' ')}:",
                                    value=st.session_state[field_key],
                                    key=field_key + "_input",
                                    height=100,
                                    help=f"Provide details for {field.replace('_', ' ')}"
                                )
                                st.session_state[field_key] = current_value
                            
                            with col2:
                                # AI Suggestion button
                                if st.button("🤖 Get AI Suggestion", key=f"suggest_{field_key}"):
                                    with st.spinner("Generating suggestion..."):
                                        gpt_handler = GPTHandler()
                                        prompt = f"""Generate specific content for the {field.replace('_', ' ')} 
                                        in the {section_name.replace('_', ' ')} section. Focus on:
                                        1. Technical accuracy
                                        2. Specific details
                                        3. Clear language
                                        4. Protocol standards
                                        Context: This is for a {st.session_state.get('study_type', 'clinical')} study."""
                                        
                                        suggestion = gpt_handler.generate_content(
                                            prompt,
                                            "Generate concise, specific content in clear technical language."
                                        )
                                        if suggestion:
                                            st.session_state[field_key] = suggestion
                                            st.success("✅ Suggestion generated!")
                                            st.rerun()
                                
                                # Update Section button
                                if st.button("📝 Update Section", key=f"update_{field_key}"):
                                    if current_value.strip():
                                        section_content = st.session_state.generated_sections[section_name]
                                        updated_content = f"{section_content}\n\n{field.replace('_', ' ').title()}: {current_value}"
                                        st.session_state.generated_sections[section_name] = updated_content
                                        
                                        # Mark as updated
                                        if 'updated_sections' not in st.session_state:
                                            st.session_state.updated_sections = set()
                                        st.session_state.updated_sections.add(f"{section_name}_{field}")
                                        
                                        st.success("✅ Section updated!")
                                        st.session_state[field_key] = ""
                                        st.rerun()
        
        # Display generated sections
        st.markdown("### Generated Protocol Sections")
        for section_name in sections_to_display:
            with st.expander(f"📄 {section_name.replace('_', ' ').title()}", expanded=False):
                st.markdown(st.session_state.generated_sections[section_name])
                
    except Exception as e:
        logger.error(f"Error in editor: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
