# Default templates for all study types
DEFAULT_TEMPLATES = {
    'title': 'Generate a clear and descriptive title that reflects the study objectives and design.',
    'synopsis': 'Create a comprehensive synopsis summarizing the key aspects of the study.',
    'background': 'Provide relevant background information and study rationale.',
    'objectives': 'Define primary and secondary study objectives.',
    'statistical_analysis': '''
Generate a detailed Statistical Analysis Plan including:

1. Analysis Populations:
   • Define Intent-to-Treat (ITT) population
   • Specify Per-Protocol (PP) population criteria
   • Detail Safety population definitions
   • Specify handling of protocol deviations
   • Define criteria for analysis set assignment

2. Statistical Methods:
   • Specify primary analysis methods and models
   • Define significance levels (e.g., alpha = 0.05)
   • List covariates and stratification factors
   • Detail secondary analysis approaches
   • Specify software packages to be used

3. Missing Data Handling:
   • Define primary imputation methods
   • Specify sensitivity analyses
   • Detail handling of dropouts
   • Define methods for partially missing data
   • Specify documentation requirements

4. Interim Analyses:
   • Define interim analysis timing
   • Specify stopping rules (efficacy/futility)
   • Detail alpha spending approach
   • Describe DSMB review process
   • Specify unblinding procedures

Cross-reference with:
- Endpoints section for outcome measures
- Sample Size section for power calculations
- Study Design for stratification factors
''',
    'study_design': '''
Detail the Study Design including:

1. Study Framework:
   • Specify study phase and type
   • Define number of arms/groups
   • Detail allocation ratio
   • List stratification factors
   • Specify blinding approach

2. Visit Schedule:
   • Define screening period duration
   • Specify treatment period length
   • Detail follow-up requirements
   • Define visit windows
   • List permitted deviations

3. Operational Flow:
   • Detail subject registration process
   • Specify randomization mechanics
   • Define drug dispensing procedures
   • Detail sample handling requirements
   • Specify data collection timing

4. Study Timeline:
   • Define overall study duration
   • Specify recruitment period
   • Detail treatment duration
   • Define follow-up period
   • List key milestone dates

Cross-reference with:
- Population section for eligibility
- Procedures for assessments
- Endpoints for outcome timing
''',
    'safety': '''
Detail Safety Monitoring including:

1. Adverse Event Management:
   • Define AE grading criteria (e.g., CTCAE)
   • Specify reporting timelines
   • Detail causality assessment
   • Define SAE reporting procedures
   • Specify follow-up requirements

2. Safety Review Process:
   • Define DSMB composition and charter
   • Specify safety review frequency
   • Detail stopping rules
   • Define dose modification criteria
   • Specify safety signal detection

3. Laboratory Monitoring:
   • List required safety labs
   • Define testing schedule
   • Specify alert values
   • Detail reporting timelines
   • Define follow-up procedures

4. Risk Management:
   • Detail risk mitigation strategies
   • Define subject withdrawal criteria
   • Specify rescue procedures
   • Detail emergency unblinding
   • Define pregnancy reporting

Cross-reference with:
- Study Design for visit schedule
- Procedures for assessments
- Statistical Analysis for safety analyses
''',
    'population': '''
Define Study Population including:

1. Demographics:
   • Specify age ranges
   • Define gender distribution
   • Detail ethnic considerations
   • Specify geographic location
   • Define language requirements

2. Clinical Characteristics:
   • Detail disease stage/severity
   • Specify required diagnoses
   • Define prior therapy requirements
   • List prohibited medications
   • Specify washout periods

3. Laboratory Requirements:
   • Define required lab values
   • Specify testing windows
   • Detail retesting procedures
   • Define eligibility ranges
   • Specify critical values

4. Screening Procedures:
   • Detail screening assessments
   • Define rescreening policies
   • Specify documentation requirements
   • Detail informed consent process
   • Define screen failure handling

Cross-reference with:
- Study Design for stratification
- Safety for lab monitoring
- Statistical Analysis for populations
''',
    'ethical_considerations': 'Address relevant ethical considerations and compliance requirements.',
    'data_monitoring': '''
Define data monitoring procedures including quality control measures, monitoring frequency, and documentation requirements.
Cross-reference with Statistical Analysis for interim analyses and Safety for DSMB procedures.
'''
}

# Study type specific section templates
SECTION_TEMPLATES = {
    'phase1': {
        'safety': '''
Enhanced Safety Monitoring for Phase 1:
• Specify dose-limiting toxicity criteria
• Define dose escalation rules
• Detail cohort review procedures
• Specify stopping criteria
''',
        'statistical_analysis': '''
Phase 1-Specific Analysis:
• Detail dose-escalation analysis
• Define MTD determination methods
• Specify safety signal detection
• Detail PK/PD analysis approach
'''
    },
    'phase2': {
        'statistical_analysis': '''
Phase 2-Specific Analysis:
• Define response criteria
• Specify interim futility analysis
• Detail predictive probability methods
• Define go/no-go criteria
''',
        'study_design': '''
Phase 2 Design Elements:
• Specify expansion cohort criteria
• Define response assessment timing
• Detail randomization approach
• Specify control group selection
'''
    },
    'phase3': {
        'statistical_analysis': '''
Phase 3-Specific Analysis:
• Detail superiority/non-inferiority margins
• Define subgroup analyses
• Specify multiplicity adjustment
• Detail sensitivity analyses
''',
        'study_design': '''
Phase 3 Design Elements:
• Define stratification factors
• Detail site selection criteria
• Specify quality control measures
• Define adaptive design elements
'''
    }
}

# Section configuration based on study type
CONDITIONAL_SECTIONS = {
    'phase1': {
        'required': [
            'safety',
            'dose_escalation',
            'pharmacokinetics'
        ],
        'optional': ['biomarkers'],
        'excluded': ['efficacy']
    },
    'phase2': {
        'required': [
            'efficacy',
            'safety',
            'statistical_analysis'
        ],
        'optional': ['pharmacodynamics'],
        'excluded': []
    },
    'phase3': {
        'required': [
            'efficacy',
            'safety',
            'statistical_analysis',
            'quality_of_life'
        ],
        'optional': ['health_economics'],
        'excluded': ['dose_escalation']
    }
}
