import streamlit as st
import os
import json
import logging
from components.input_section import render_input_section
from components.navigator import render_navigator
from components.editor import render_editor
from components.compliance_checker import render_compliance_checker
from utils.synopsis_validator import validate_synopsis
from utils.protocol_formatter import ProtocolFormatter
from utils.template_manager import TemplateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_info():
    """Generate comprehensive debug information"""
    debug_data = {
        "Application State": {
            "synopsis_content": bool(st.session_state.get('synopsis_content')),
            "study_type": st.session_state.get('study_type'),
            "current_section": st.session_state.get('current_section')
        },
        "Progress Tracking": {
            "sections_status": st.session_state.get('sections_status', {}),
            "total_sections": len(st.session_state.get('sections_status', {})),
            "completed_sections": sum(1 for status in st.session_state.get('sections_status', {}).values() 
                                   if status == 'Generated')
        },
        "Generation Status": {
            "generated_sections": list(st.session_state.get('generated_sections', {}).keys()),
            "pending_sections": [section for section, status in st.session_state.get('sections_status', {}).items() 
                               if status != 'Generated']
        },
        "Template Info": {
            "selected_template": st.session_state.get('study_type'),
            "available_templates": st.session_state.template_manager.get_template_types() 
                                 if hasattr(st.session_state, 'template_manager') else []
        }
    }
    
    if st.session_state.get('synopsis_content'):
        try:
            validation_results = validate_synopsis(st.session_state.synopsis_content)
            debug_data["Validation Results"] = {
                "is_valid": validation_results.get('is_valid', False),
                "missing_sections": [section.get('section') for section in validation_results.get('missing_sections', [])],
                "template_validation": validation_results.get('template_validation', {})
            }
        except Exception as e:
            logger.error(f"Error in synopsis validation: {str(e)}")
            debug_data["Validation Results"] = {"error": str(e)}
    
    return debug_data

def init_session_state():
    """Initialize and track session state variables"""
    logger.info("Initializing session state")
    
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = True
    
    # Track core application state
    if 'synopsis_content' not in st.session_state:
        logger.debug("Initializing synopsis_content")
        st.session_state.synopsis_content = None
    
    if 'current_section' not in st.session_state:
        logger.debug("Initializing current_section")
        st.session_state.current_section = None
    
    if 'study_type' not in st.session_state:
        logger.debug("Initializing study_type")
        st.session_state.study_type = None
    
    # Track section status with timestamps
    if 'sections_status' not in st.session_state:
        logger.debug("Initializing sections_status")
        st.session_state.sections_status = {
            'background': 'Not Started',
            'objectives': 'Not Started',
            'study_design': 'Not Started',
            'population': 'Not Started',
            'procedures': 'Not Started',
            'statistical': 'Not Started',
            'safety': 'Not Started',
            'references': 'Not Started'
        }
    
    # Track generated content
    if 'generated_sections' not in st.session_state:
        logger.debug("Initializing generated_sections")
        st.session_state.generated_sections = {}
    
    # Initialize template manager
    if 'template_manager' not in st.session_state:
        logger.debug("Initializing template_manager")
        st.session_state.template_manager = TemplateManager()
    
    # Track operation history
    if 'operation_history' not in st.session_state:
        logger.debug("Initializing operation_history")
        st.session_state.operation_history = []

def main():
    st.set_page_config(
        page_title="Protocol Development Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    logger.info("Starting Protocol Development Assistant")
    init_session_state()
    
    st.title("Protocol Development Assistant")
    
    # Enhanced debug information display
    if st.session_state.debug_mode:
        with st.expander("🔍 Debug Information", expanded=False):
            debug_data = debug_info()
            
            # Display each debug section in organized tabs
            debug_tabs = st.tabs([
                "Application State", 
                "Progress Tracking", 
                "Generation Status", 
                "Template Info",
                "Validation Results"
            ])
            
            with debug_tabs[0]:
                st.json(debug_data["Application State"])
            
            with debug_tabs[1]:
                st.json(debug_data["Progress Tracking"])
            
            with debug_tabs[2]:
                st.json(debug_data["Generation Status"])
            
            with debug_tabs[3]:
                st.json(debug_data["Template Info"])
            
            with debug_tabs[4]:
                if "Validation Results" in debug_data:
                    st.json(debug_data["Validation Results"])
                else:
                    st.info("No validation results available")
    
    # Main application flow with enhanced logging
    if st.session_state.synopsis_content is None:
        logger.info("No synopsis available, showing input section")
        render_input_section()
    else:
        # Template selection in sidebar
        with st.sidebar:
            if st.session_state.study_type is None:
                logger.info("Study type not selected, showing template selection")
                st.subheader("Select Study Type")
                template_types = st.session_state.template_manager.get_template_types()
                selected_type = st.selectbox(
                    "Study Type",
                    template_types,
                    format_func=lambda x: st.session_state.template_manager.get_template(x)['name']
                )
                if st.button("Confirm Study Type"):
                    logger.info(f"Study type selected: {selected_type}")
                    st.session_state.study_type = selected_type
                    st.session_state.operation_history.append({
                        "action": "study_type_selected",
                        "type": selected_type,
                        "timestamp": str(pd.Timestamp.now())
                    })
                    st.experimental_rerun()
            
            if st.session_state.study_type:
                render_navigator()
        
        # Main content area with progress tracking
        if st.session_state.study_type:
            tab1, tab2 = st.tabs(["Protocol Editor", "Compliance Check"])
            
            with tab1:
                render_editor()
            with tab2:
                render_compliance_checker()
        else:
            st.info("Please select a study type to begin")
    
    # Add footer with version tracking
    st.markdown("---")
    st.markdown("Protocol Development Assistant v1.0")
    
    logger.info("Application render complete")

if __name__ == "__main__":
    main()
