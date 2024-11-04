import streamlit as st
import logging
from utils.protocol_improver import ProtocolImprover
from utils.gpt_handler import GPTHandler
import time
import os

logger = logging.getLogger(__name__)

def generate_ai_suggestion(field: str, section_name: str) -> str:
    try:
        # 1. Check API Key first
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("OpenAI API key not found in environment")
            st.error("⚠️ OpenAI API key not found. Please check your environment configuration.")
            return None
            
        # 2. Check synopsis content
        synopsis_content = st.session_state.get('synopsis_content')
        if not synopsis_content:
            logger.error("No synopsis content found in session state")
            st.error("⚠️ No synopsis content found. Please generate a protocol first.")
            return None
            
        # 3. Check study type
        study_type = st.session_state.get('study_type')
        if not study_type:
            logger.error("No study type found in session state")
            st.error("⚠️ Study type not detected. Please ensure synopsis is properly processed.")
            return None
            
        # If all checks pass, proceed with suggestion generation
        logger.info(f"All prerequisite checks passed for field: {field} in section: {section_name}")
        logger.info(f"Study type: {study_type}")
        logger.info("Synopsis content length: " + str(len(synopsis_content)))
        
        # Get section analysis results
        improver = ProtocolImprover()
        analysis_results = improver.analyze_protocol_sections(st.session_state.generated_sections)
        section_analysis = analysis_results['section_analyses'].get(section_name, {})
        recommendations = section_analysis.get('recommendations', [])
        
        # Create GPT handler with clear error handling
        try:
            gpt_handler = GPTHandler()
        except Exception as e:
            logger.error(f"Failed to initialize GPT handler: {str(e)}")
            st.error(f"⚠️ Error initializing AI: {str(e)}")
            return None
        
        logger.info(f"Starting suggestion generation for {field} in {section_name}")
        
        # Build comprehensive prompt
        context = f'''Based on this synopsis:
{synopsis_content}

Generate specific content for the {field.replace('_', ' ')} field in the {section_name} section.
This is for a {study_type} study.

Section Context:
- Current Section: {section_name.replace('_', ' ').title()}
- Field to Complete: {field.replace('_', ' ')}'''

        if recommendations:
            context += "\n\nConsider these recommendations:"
            for rec in recommendations:
                context += f"\n- {rec}"

        context += '''

Requirements:
- Be specific and detailed
- Match the study context and type
- Format key points with *italic* markers
- Be concise but comprehensive
- Address any recommendations provided'''

        logger.info("Sending prompt to GPT")
        try:
            suggestion = gpt_handler.generate_content(
                prompt=context,
                system_message="You are a protocol development expert. Generate focused, scientific content."
            )
            
            if suggestion:
                logger.info("Successfully generated suggestion")
                return suggestion
            else:
                logger.error("Empty suggestion returned from GPT")
                st.error("⚠️ Failed to generate suggestion - no content returned")
                return None
                
        except Exception as e:
            logger.error(f"Error during GPT content generation: {str(e)}")
            st.error(f"⚠️ Error generating suggestion: {str(e)}")
            return None
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"AI suggestion error: {error_msg}")
        st.error(f"⚠️ Error in suggestion process: {error_msg}")
        return None

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
            st.write("Debug Information:")
            st.write(f"- API Key present: {bool(os.environ.get('OPENAI_API_KEY'))}")
            st.write(f"- Synopsis content present: {bool(st.session_state.get('synopsis_content'))}")
            st.write(f"- Study type present: {bool(st.session_state.get('study_type'))}")
            
            try:
                with st.spinner("Generating AI suggestion..."):
                    suggestion = generate_ai_suggestion(field, section_name)
                    if suggestion:
                        st.session_state.user_inputs[field_key] = suggestion
                        st.success("✅ AI suggestion generated!")
                        st.rerun()
                    else:
                        st.error("Failed to generate suggestion - see errors above")
                        
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error in AI suggestion flow: {error_msg}")
                st.error(f"Error generating suggestion: {error_msg}")

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

def render_missing_information(analysis_results):
    """Render missing information collection interface"""
    missing_count = sum(len(section['missing_fields']) 
                      for section in analysis_results['section_analyses'].values())
    
    if missing_count > 0:
        st.warning(f"Found {missing_count} items that need your attention")
        
        # Organize sections in logical order
        section_order = [
            "title", "background", "objectives",
            "study_design", "population", "procedures",
            "endpoints", "statistical_analysis", "safety",
            "ethical_considerations", "data_monitoring"
        ]
        
        for section_name in section_order:
            if section_name in analysis_results['section_analyses']:
                analysis = analysis_results['section_analyses'][section_name]
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
        "Study Design": ["study_design", "population", "procedures"],
        "Endpoints & Analysis": ["endpoints", "statistical_analysis"],
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
                            height=300,
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
        .recommendation-box {
            border: 1px solid #ffa600;
            border-radius: 4px;
            padding: 10px;
            margin: 5px 0;
            background-color: #fff8e6;
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
