import logging
from typing import Dict

logger = logging.getLogger(__name__)

SECTION_TEMPLATES = {
    'phase1': {
        'title': '''Generate a clear and descriptive study title for Phase 1 clinical trial including:
        - Study compound
        - Study phase
        - Study population or condition''',
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
        - Exploratory endpoints''',
        'ethical_considerations': '''Address ethical aspects including:
        - Adherence to Good Clinical Practice (GCP)
        - Informed consent process
        - Data privacy protection
        - Participant rights and safety''',
        'data_monitoring': '''Detail data quality and monitoring plan including:
        - Data collection and entry procedures
        - Quality assurance measures
        - Frequency and scope of monitoring visits''',
        'completion_criteria': '''Define completion and withdrawal criteria, covering:
        - Participant discontinuation criteria
        - Withdrawal procedures
        - Criteria for study termination'''
    },
    'phase2': {
        'title': '''Generate a clear and descriptive study title for Phase 2 clinical trial including:
        - Study compound
        - Study phase
        - Study population or condition''',
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
        - Exploratory endpoints''',
        'ethical_considerations': '''Address ethical aspects including:
        - Adherence to Good Clinical Practice (GCP)
        - Informed consent process
        - Data privacy protection
        - Participant rights and safety''',
        'data_monitoring': '''Detail data quality and monitoring plan including:
        - Data collection and entry procedures
        - Quality assurance measures
        - Frequency and scope of monitoring visits''',
        'completion_criteria': '''Define completion and withdrawal criteria, covering:
        - Participant discontinuation criteria
        - Withdrawal procedures
        - Criteria for study termination'''
    },
    'systematic_review': {
        'title': '''Generate a descriptive title for the systematic review including:
        - Focus on disease or treatment type
        - Scope of review (e.g., real-world evidence, clinical trials)
        - Population or key parameters''',
        'search_strategy': '''Detail comprehensive search strategy including:
        - Databases to be searched
        - Search terms and combinations
        - Search date ranges
        - Grey literature sources''',
        'eligibility_criteria': '''Define clear inclusion/exclusion criteria:
        - PICOS framework application
        - Study design criteria
        - Publication types
        - Language restrictions''',
        'data_extraction': '''Describe data extraction process:
        - Data extraction form design
        - Independent reviewer process
        - Quality control measures
        - Data management procedures''',
        'quality_assessment': '''Detail quality assessment methodology:
        - Risk of bias assessment tools
        - Quality scoring criteria
        - Inter-rater reliability
        - Handling discrepancies''',
        'synthesis_methods': '''Outline synthesis methodology:
        - Meta-analysis approach if applicable
        - Heterogeneity assessment
        - Subgroup analyses
        - Sensitivity analyses''',
        'results_reporting': '''Define reporting structure:
        - PRISMA flow diagram
        - Summary tables format
        - Forest plots if applicable
        - Publication bias assessment'''
    },
    'secondary_rwe': {
        'title': '''Generate a descriptive title for the secondary real-world evidence (RWE) study including:
        - Study focus (e.g., effectiveness, safety)
        - Population or disease condition
        - Data source characteristics''',
        'data_source': '''Describe data sources including:
        - Database characteristics
        - Time period covered
        - Data quality assessment
        - Relevant variables available''',
        'variables': '''Detail study variables including:
        - Exposure definitions
        - Outcome measures
        - Covariates and confounders
        - Coding systems used''',
        'statistical_analysis': '''Outline analysis approach:
        - Primary analysis methods
        - Propensity score matching
        - Sensitivity analyses
        - Missing data handling''',
        'limitations': '''Address study limitations:
        - Data quality issues
        - Selection bias considerations
        - Confounding factors
        - Generalizability''',
        'ethical_considerations': '''Address ethical considerations including:
        - Compliance with data privacy regulations
        - Informed consent (if applicable)
        - Anonymization and data security''',
        'data_monitoring': '''Outline data quality and monitoring strategy including:
        - Quality assurance measures
        - Consistency checks across sites or databases
        - Monitoring intervals and audit procedures''',
    },
    'patient_survey': {
        'title': '''Generate a descriptive title for the patient survey study including:
        - Survey focus (e.g., quality of life, treatment experience)
        - Target population
        - Context (e.g., specific condition or treatment phase)''',
        'survey_design': '''Detail survey methodology including:
        - Survey type and format
        - Administration method
        - Timing of assessments
        - Response validation methods''',
        'survey_instrument': '''Describe survey instruments:
        - Questionnaire development/validation
        - Question types and scales
        - Reliability and validity
        - Pilot testing results''',
        'data_collection': '''Outline data collection process:
        - Data collection methods
        - Quality control measures
        - Missing data handling
        - Data security measures''',
        'ethical_considerations': '''Address ethical aspects:
        - Informed consent process
        - Data privacy protection
        - Participant burden
        - Compensation details'''
    }
}

CONDITIONAL_SECTIONS = {
    'phase1': {
        'required': ['title', 'background', 'objectives', 'study_design', 'population', 'procedures', 'statistical_analysis', 'safety', 'endpoints', 'ethical_considerations', 'data_monitoring', 'completion_criteria'],
        'optional': ['pk_analysis', 'interim_analysis'],
        'excluded': ['efficacy_endpoints']
    },
    'phase2': {
        'required': ['title', 'background', 'objectives', 'study_design', 'population', 'procedures', 'statistical_analysis', 'safety', 'endpoints', 'ethical_considerations', 'data_monitoring', 'completion_criteria'],
        'optional': ['pk_analysis', 'interim_analysis'],
        'excluded': []
    },
    'systematic_review': {
        'required': ['title', 'search_strategy', 'eligibility_criteria', 'data_extraction', 'quality_assessment', 'synthesis_methods', 'results_reporting', 'ethical_considerations'],
        'optional': ['meta_analysis', 'risk_of_bias'],
        'excluded': ['safety', 'procedures']
    },
    'secondary_rwe': {
        'required': ['title', 'data_source', 'variables', 'statistical_analysis', 'limitations', 'ethical_considerations', 'data_monitoring'],
        'optional': ['sensitivity_analysis', 'subgroup_analysis'],
        'excluded': ['safety', 'procedures']
    },
    'patient_survey': {
        'required': ['title', 'survey_design', 'population', 'survey_instrument', 'data_collection', 'statistical_analysis', 'ethical_considerations'],
        'optional': ['pilot_testing', 'cognitive_debriefing'],
        'excluded': ['safety', 'procedures']
    }
}

# Default templates for sections not covered by specific study types
DEFAULT_TEMPLATES = {
    'title': '''Generate a descriptive study title based on:
    - Study focus
    - Phase or type of study
    - Key condition or population''',
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
