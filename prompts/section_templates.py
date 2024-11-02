import logging
from typing import Dict

logger = logging.getLogger(__name__)

SECTION_TEMPLATES = {
    'phase1': {
        'background': '''Generate comprehensive background for Phase 1 study focusing on:
- First-in-human considerations
- Safety profile of compound
- Preliminary pharmacology data
- Relevant preclinical studies''',
        'objectives': '''Generate objectives for Phase 1 study including:
- Primary: Safety and tolerability
- Secondary: PK parameters
- Exploratory: Initial PD markers''',
        'study_design': '''Create detailed Phase 1 design including:
- Study population (healthy volunteers/patients)
- Dose escalation methodology
- Safety monitoring procedures
- Stopping criteria'''
    },
    'phase2': {
        'background': '''Generate background for Phase 2 study emphasizing:
- Disease burden and unmet needs
- Mechanism of action
- Phase 1 safety data
- Preliminary efficacy signals''',
        'objectives': '''Generate Phase 2 objectives including:
- Primary: Efficacy endpoints
- Secondary: Safety continuation
- Exploratory: Biomarkers''',
        'study_design': '''Detail Phase 2 design including:
- Patient population
- Randomization strategy
- Control group rationale
- Dose selection justification'''
    }
}

CONDITIONAL_SECTIONS = {
    'phase1': {
        'required': ['background', 'objectives', 'study_design', 'safety_monitoring'],
        'optional': ['pk_analysis', 'interim_analysis'],
        'excluded': ['efficacy_endpoints']
    },
    'phase2': {
        'required': ['background', 'objectives', 'study_design', 'efficacy_endpoints'],
        'optional': ['pk_analysis', 'interim_analysis'],
        'excluded': ['dose_escalation']
    }
}

# Default templates for sections not covered by specific study types
DEFAULT_TEMPLATES = {
    'background': '''Generate comprehensive study background including:
- Disease/condition overview
- Current treatment landscape
- Rationale for study''',
    'objectives': '''Generate study objectives including:
- Primary objective
- Secondary objectives
- Exploratory objectives''',
    'study_design': '''Create detailed study design including:
- Study type and methodology
- Population characteristics
- Key procedures and assessments'''
}
