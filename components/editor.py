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
        // Generate AI suggestion (Ctrl+G)
        if (e.ctrlKey && e.key === 'g') {
            e.preventDefault();
            document.querySelector('button[data-testid*="suggest"]').click();
        }
        
        // Update section (Ctrl+U)
        if (e.ctrlKey && e.key === 'u') {
            e.preventDefault();
            document.querySelector('button[data-testid*="update"]').click();
        }
        
        // Clear field (Ctrl+X)
        if (e.ctrlKey && e.key === 'x') {
            e.preventDefault();
            let activeField = document.activeElement;
            if (activeField.tagName === 'TEXTAREA') {
                activeField.value = '';
                activeField.dispatchEvent(new Event('input'));
            }
        }
        
        // Toggle details (Ctrl+D)
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

def update_section_content(section_name: str, field: str, new_content: str):
    """Update protocol section content"""
    try:
        if section_name in st.session_state.generated_sections:
            current_content = st.session_state.generated_sections[section_name]
            updated_content = f"{current_content}\n\n{field.replace('_', ' ').title()}: {new_content}"
            st.session_state.generated_sections[section_name] = updated_content
            
            # Mark section as updated
            if 'updated_sections' not in st.session_state:
                st.session_state.updated_sections = set()
            st.session_state.updated_sections.add(f"{section_name}_{field}")
            
            # Force state update and progress recalculation
            st.rerun()
    except Exception as e:
        logger.error(f"Error updating section content: {str(e)}")
        raise

def generate_ai_suggestion(field: str, section_name: str) -> str:
    """Generate AI suggestion for field content"""
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
        
        # Store suggestion in session state
        if suggestion:
            if 'ai_suggestions' not in st.session_state:
                st.session_state.ai_suggestions = {}
            st.session_state.ai_suggestions[f"{section_name}_{field}"] = suggestion
            
        return suggestion
        
    except Exception as e:
        logger.error(f"AI suggestion error: {str(e)}")
        return None

def render_editor():
    """Render the protocol editor interface"""
    try:
        if not st.session_state.get('generated_sections'):
            return

        # Add keyboard shortcuts
        render_keyboard_shortcuts()
        add_shortcut_handlers()

        # Initialize handlers
        improver = ProtocolImprover()
        missing_info_handler = MissingInformationHandler()
            
        # Initialize session state for editor
        if 'editor_states' not in st.session_state:
            st.session_state.editor_states = {}
        if 'updated_sections' not in st.session_state:
            st.session_state.updated_sections = set()
        if 'ai_suggestions' not in st.session_state:
            st.session_state.ai_suggestions = {}

        # Define preferred section order based on standard protocol structure
        ordered_sections = [
            # Administrative
            'title',
            'synopsis',
            
            # Background & Objectives
            'background',
            'objectives',
            
            # Core Study Design
            'study_design',
            'population',
            'procedures',
            'endpoints',
            
            # Statistical Considerations
            'statistical_analysis',
            'sample_size',
            
            # Safety & Monitoring
            'safety',
            'data_monitoring',
            
            # Data Management
            'data_collection',
            'data_quality',
            
            # Additional Considerations
            'ethical_considerations',
            'completion_criteria',
            
            # Supplementary Sections
            'references',
            'appendices'
        ]

        # Filter and sort sections based on study type
        generated_sections = dict(st.session_state.generated_sections)
        sections_to_display = [s for s in ordered_sections if s in generated_sections]
        remaining_sections = [s for s in generated_sections if s not in ordered_sections]
        sections_to_display.extend(remaining_sections)

        # Display Protocol Sections with improved organization
        st.markdown("## 📄 Protocol Sections")
        
        # Get analysis results for all sections
        analysis_results = improver.analyze_protocol_sections(generated_sections)['section_analyses']
        
        # Calculate overall completion progress
        total_sections = len(sections_to_display)
        completed_sections = 0

        # Count completed sections
        for section in sections_to_display:
            section_analysis = analysis_results[section]
            # Section is complete if it has no missing fields or all fields have been updated
            missing_fields = [
                field for field in section_analysis['missing_fields']
                if f"{section}_{field}" not in st.session_state.get('updated_sections', set())
            ]
            if not missing_fields:
                completed_sections += 1

        progress = completed_sections / total_sections if total_sections > 0 else 0
        st.progress(progress, text=f"Protocol Completion: {progress*100:.1f}%")

        # Display sections with category-based icons
        for section_name in sections_to_display:
            icon = "📝"
            if section_name in ['title', 'synopsis']: icon = "📋"
            elif section_name in ['background', 'objectives']: icon = "🎯"
            elif section_name in ['study_design', 'population', 'endpoints']: icon = "🔬"
            elif section_name in ['statistical_analysis', 'sample_size']: icon = "📊"
            elif section_name in ['safety', 'data_monitoring']: icon = "⚕️"
            elif section_name in ['ethical_considerations']: icon = "⚖️"
            elif section_name in ['data_collection', 'data_quality']: icon = "💾"
            elif section_name in ['references', 'appendices']: icon = "📚"
            
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

        # Display Missing Information Section with severity indicators
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
                        field_info = missing_info_handler._get_field_prompt(field, section_name)
                        
                        # Show field header with severity badge
                        severity = field_info['severity']
                        severity_badge = {
                            'critical': '🔴 CRITICAL',
                            'major': '🟡 MAJOR',
                            'minor': '🟢 MINOR'
                        }.get(severity, '⚪️ UNKNOWN')
                        
                        st.markdown(f"#### {field.replace('_', ' ').title()} {severity_badge}")
                        
                        # Show field details in collapsible section
                        with st.expander("🔍 Field Details", expanded=False):
                            st.markdown(field_info['message'])
                            
                            if section_name in ['statistical_analysis', 'study_design', 'safety', 'population']:
                                st.info('''
                                This field requires specific attention based on section requirements:
                                1. Content must be detailed and comprehensive
                                2. Must follow regulatory guidelines
                                3. Should cross-reference related sections
                                4. Include all required sub-components
                                ''')
                        
                        # Field input with improved layout
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            # Show previous AI suggestion if available
                            suggestion_key = f"{section_name}_{field}"
                            if suggestion_key in st.session_state.get('ai_suggestions', {}):
                                with st.expander("💡 Previous AI Suggestion", expanded=False):
                                    st.markdown(st.session_state.ai_suggestions[suggestion_key])
                            
                            current_value = st.text_area(
                                label=f"Enter {field.replace('_', ' ')}:",
                                value=st.session_state.editor_states.get(field_key, ""),
                                key=field_key,
                                height=100,
                                help=f"Provide details for {field.replace('_', ' ')}"
                            )
                        
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
