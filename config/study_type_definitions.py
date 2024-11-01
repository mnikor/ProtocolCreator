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
            "methods": "procedures"
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
            "methods": "procedures"
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
            "methods": "procedures"
        }
    },
    "rwe": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "data_sources",
            "population",
            "variables",
            "statistical_analysis",
            "limitations"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "methods": "study_design",
            "data": "data_sources",
            "outcomes": "variables"
        }
    },
    "slr": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "methods",
            "search_strategy",
            "data_extraction",
            "quality_assessment",
            "data_synthesis"
        ],
        "section_aliases": {
            "methodology": "methods",
            "extraction": "data_extraction",
            "synthesis": "data_synthesis",
            "search": "search_strategy"
        }
    },
    "meta": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "methods",
            "search_strategy",
            "data_extraction",
            "statistical_analysis",
            "quality_assessment"
        ],
        "section_aliases": {
            "methodology": "methods",
            "extraction": "data_extraction",
            "statistical": "statistical_analysis",
            "search": "search_strategy"
        }
    },
    "observational": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "population",
            "variables",
            "data_collection",
            "statistical_analysis",
            "limitations"
        ],
        "section_aliases": {
            "methods": "study_design",
            "outcomes": "variables",
            "statistical": "statistical_analysis",
            "data": "data_collection"
        }
    }
}
