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
- Stopping criteria''',
        'population': '''Generate population section including:
- Inclusion criteria
- Exclusion criteria
- Sample size justification''',
        'procedures': '''Detail study procedures including:
- Screening procedures
- Treatment procedures
- Follow-up procedures
- Safety monitoring''',
        'statistical_analysis': '''Describe statistical methods including:
- Primary analysis methods
- Secondary analyses
- Sample size calculation
- Interim analyses''',
        'safety': '''Detail safety considerations including:
- Adverse event monitoring
- Safety parameters
- Risk mitigation
- Stopping rules''',
        'endpoints': '''Define study endpoints including:
- Primary endpoints
- Secondary endpoints
- Safety endpoints
- Exploratory endpoints'''
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
- Dose selection justification''',
        'population': '''Generate population section including:
- Target patient population
- Inclusion/exclusion criteria
- Sample size calculation
- Recruitment strategy''',
        'procedures': '''Detail study procedures including:
- Screening assessments
- Treatment administration
- Safety monitoring
- Efficacy assessments''',
        'statistical_analysis': '''Describe statistical methods including:
- Primary efficacy analysis
- Secondary analyses
- Interim analyses
- Power calculations''',
        'safety': '''Detail safety monitoring including:
- Adverse event reporting
- Safety parameters
- Risk management
- Data monitoring''',
        'endpoints': '''Define study endpoints including:
- Primary efficacy endpoints
- Secondary endpoints
- Safety endpoints
- Exploratory endpoints'''
    }
}

CONDITIONAL_SECTIONS = {
    'phase1': {
        'required': ['background', 'objectives', 'study_design', 'population', 'procedures', 'statistical_analysis', 'safety', 'endpoints'],
        'optional': ['pk_analysis', 'interim_analysis'],
        'excluded': ['efficacy_endpoints']
    },
    'phase2': {
        'required': ['background', 'objectives', 'study_design', 'population', 'procedures', 'statistical_analysis', 'safety', 'endpoints'],
        'optional': ['pk_analysis', 'interim_analysis'],
        'excluded': []
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
- Key procedures and assessments''',
    'population': '''Generate population section including:
- Target population
- Inclusion/exclusion criteria
- Sample size justification''',
    'procedures': '''Detail study procedures including:
- Study assessments
- Treatment procedures
- Follow-up procedures''',
    'statistical_analysis': '''Describe statistical methods including:
- Analysis populations
- Primary analyses
- Secondary analyses''',
    'safety': '''Detail safety considerations including:
- Safety monitoring
- Adverse event reporting
- Risk management''',
    'endpoints': '''Define study endpoints including:
- Primary endpoints
- Secondary endpoints
- Safety endpoints'''
}
