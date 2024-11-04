import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.gpt_handler import GPTHandler
import time

logger = logging.getLogger(__name__)

def generate_ai_suggestion(field: str, section_name: str) -> str:
    try:
        if not st.session_state.get('synopsis_content'):
            st.error("No synopsis content found")
            return None
            
        if not st.session_state.get('study_type'):
            st.error("Study type not detected")
            return None
        
        # Create GPT handler first to catch initialization errors
        gpt_handler = GPTHandler()
        
        # Show spinner while processing
        with st.spinner("Generating AI suggestion..."):
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
        error_msg = str(e)
        logger.error(f"AI suggestion error: {error_msg}")
        st.error(f"Error generating suggestion: {error_msg}")
        return None

def update_section_content(section_name: str):
    """Update section content with user inputs"""
    try:
        content = st.session_state.generated_sections[section_name]
        for field_key, value in st.session_state.user_inputs.items():
            if field_key.startswith(f"{section_name}_"):
                field = '_'.join(field_key.split('_')[1:-2])
                placeholder = f"[PLACEHOLDER: *{field}*]"
                content = content.replace(placeholder, value)
        
        st.session_state.generated_sections[section_name] = content
        st.success(f"✅ {section_name.title()} updated successfully!")
        st.rerun()
    except Exception as e:
        logger.error(f"Error updating section: {str(e)}")
        st.error(f"Error updating section: {str(e)}")

def render_missing_field_input(field: str, section_name: str, field_key: str):
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown(f"**{field.replace('_', ' ').title()}**")
    
    with col2:
        previous_value = st.session_state.user_inputs.get(field_key, "")
        current_input = st.text_area(
            label=f"Enter information for {field.replace('_', ' ')}:",
            value=previous_value,
            key=field_key,
            height=100
        )
        
        suggest_key = f"suggest_{field_key}"
        if st.button("🤖 Get AI Suggestion", key=suggest_key, help="Generate AI suggestion for this field"):
            try:
                suggestion = generate_ai_suggestion(field, section_name)
                if suggestion:
                    # Update session state
                    st.session_state.user_inputs[field_key] = suggestion
                    st.success("✅ AI suggestion generated!")
                    time.sleep(0.5)  # Small delay to ensure state update
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to generate suggestion: {str(e)}")
                logger.error(f"AI suggestion error: {str(e)}")

def render_missing_information(analysis_results):
    """Render missing information collection interface"""
    missing_count = sum(len(section['missing_fields']) 
                      for section in analysis_results['section_analyses'].values())
    
    if missing_count > 0:
        st.warning(f"Found {missing_count} items that need your attention")
        
        for section_name, analysis in analysis_results['section_analyses'].items():
            if analysis['missing_fields']:
                st.markdown(f"### 📝 {section_name.replace('_', ' ').title()}")
                
                for idx, field in enumerate(analysis['missing_fields']):
                    field_key = f"{section_name}_{field}_{idx}_{int(time.time())}"
                    render_missing_field_input(field, section_name, field_key)
                
                update_key = f"update_{section_name}_{int(time.time())}"
                if st.button(f"Update {section_name.title()}", key=update_key):
                    update_section_content(section_name)
                
                st.markdown("---")
    else:
        st.success("✅ All required information has been provided")

def render_protocol_sections(analysis_results):
    """Render protocol sections with logical grouping"""
    sections = st.session_state.generated_sections
    
    # Reorder sections logically
    section_groups = {
        "Study Overview": ["title", "background", "objectives"],
        "Study Design": ["study_design", "population"],
        "Procedures": ["procedures", "endpoints"],
        "Analysis": ["statistical_analysis"],
        "Safety & Ethics": ["safety", "ethical_considerations"],
        "Monitoring": ["data_monitoring", "completion_criteria"]
    }
    
    # Create tabs for section groups
    tabs = st.tabs([group for group in section_groups.keys() 
                   if any(section in sections for section in section_groups[group])])
    
    for tab, (group_name, group_sections) in zip(tabs, section_groups.items()):
        with tab:
            for section_name in group_sections:
                if section_name in sections:
                    with st.expander(f"📝 {section_name.replace('_', ' ').title()}", expanded=False):
                        content_key = f"content_view_{section_name}_{int(time.time())}"
                        st.text_area(
                            "Section Content",
                            value=sections[section_name],
                            height=200,
                            key=content_key,
                            disabled=True
                        )
                        
                        # Display recommendations
                        recommendations = analysis_results['section_analyses'][section_name].get('recommendations', [])
                        if recommendations:
                            st.markdown("#### 💡 Recommendations")
                            for rec in recommendations:
                                st.info(rec)

def render_editor():
    """Render the protocol editor with enhanced organization"""
    improver = ProtocolImprover()
    
    # Add custom styling
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: 600;
        }
        .stButton > button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Check prerequisites
    if not st.session_state.get('synopsis_content'):
        st.warning("Please upload a synopsis first")
        return
    if not st.session_state.get('study_type'):
        st.warning("Please select a study type first")
        return
        
    # Initialize session state for user inputs
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = {}
    
    # Display generated sections if available
    if generated_sections := st.session_state.get('generated_sections'):
        # Create main tabs
        tab1, tab2 = st.tabs(["🚨 Missing Information", "📄 Protocol Sections"])
        
        analysis_results = improver.analyze_protocol_sections(generated_sections)
        
        with tab1:
            st.markdown("## Required Information")
            render_missing_information(analysis_results)
        
        with tab2:
            st.markdown("## Protocol Content")
            render_protocol_sections(analysis_results)
        
        # Global Update Button
        if st.session_state.user_inputs:
            st.markdown("---")
            st.markdown("### 🔄 Update All Sections")
            update_all_key = f"update_all_{int(time.time())}"
            if st.button("Update Protocol with All Input", type="primary", key=update_all_key):
                try:
                    updated_sections = dict(st.session_state.generated_sections)
                    for field_key, value in st.session_state.user_inputs.items():
                        section_name = field_key.split('_')[0]
                        if section_name in updated_sections:
                            field = '_'.join(field_key.split('_')[1:-2])
                            placeholder = f"[PLACEHOLDER: *{field}*]"
                            updated_sections[section_name] = updated_sections[section_name].replace(
                                placeholder, value
                            )
                    
                    st.session_state.generated_sections = updated_sections
                    st.success("✅ Protocol updated successfully!")
                    st.rerun()
                except Exception as e:
                    logger.error(f"Error updating protocol: {str(e)}")
                    st.error(f"Error updating protocol: {str(e)}")
    else:
        st.info("Use the 'Generate Complete Protocol' button in the sidebar to generate protocol sections.")
