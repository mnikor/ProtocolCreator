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

[Rest of the file content remains the same...]
