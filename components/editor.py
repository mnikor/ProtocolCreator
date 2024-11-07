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
            for section in sections:
                if section in sections_to_display:
                    ordered_sections.append(section)
        
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
        
        # Display missing information sections
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
                    for issue in analysis['issues']:
                        severity_icon = {
                            'critical': '🔴',
                            'major': '🟡',
                            'minor': '🟢'
                        }.get(issue['severity'], '⚪️')
                        
                        with st.expander(f"{severity_icon} {issue['message']}", expanded=False):
                            st.markdown(f"**Suggestion:** {issue['suggestion']}")
                            
                            # Add AI suggestion button
                            if st.button("🤖 Get AI Suggestion", key=f"suggest_{section_name}_{issue['type']}"):
                                with st.spinner("Generating suggestion..."):
                                    gpt_handler = GPTHandler()
                                    prompt = f"""Given this issue in the {section_name.replace('_', ' ')} section:
                                    {issue['message']}
                                    
                                    Generate specific content to address this issue. The content should be:
                                    1. Technically accurate
                                    2. Specific and detailed
                                    3. Written in clear language
                                    4. Compliant with protocol standards
                                    
                                    Study Type: {st.session_state.get('study_type', 'clinical study')}"""
                                    
                                    suggestion = gpt_handler.generate_content(
                                        prompt,
                                        "Generate concise, specific protocol content in clear technical language."
                                    )
                                    if suggestion:
                                        st.markdown("### Suggested Content:")
                                        st.markdown(suggestion)
                                        
                                        if st.button("📝 Apply Suggestion", key=f"apply_{section_name}_{issue['type']}"):
                                            current_content = st.session_state.generated_sections[section_name]
                                            updated_content = current_content + "\n\n" + suggestion
                                            st.session_state.generated_sections[section_name] = updated_content
                                            st.success("✅ Content updated!")
                                            st.rerun()
        
        # Display generated sections
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
                    
    except Exception as e:
        logger.error(f"Error in editor: {str(e)}")
        st.error(f"An error occurred: {str(e)}")