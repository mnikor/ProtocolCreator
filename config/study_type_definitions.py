"""Study type definitions and configurations"""

from typing import Dict, List

# Comprehensive study configurations
COMPREHENSIVE_STUDY_CONFIGS = {
    "phase1": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures",
            "procedures": "procedures"
        }
    },
    "phase2": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures",
            "procedures": "procedures"
        }
    },
    "phase3": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures",
            "procedures": "procedures"
        }
    }
}
