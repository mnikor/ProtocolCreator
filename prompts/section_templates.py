import logging
from typing import Dict

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATES = {
    'title': '''
Generate a clear and descriptive study title that includes:

- The study type and phase (if applicable)
- The target population or condition
- The main intervention or focus

**Instructions**:
- Ensure the title is concise and adheres to scientific guidelines
- Avoid including any confidential information
- Use formal, objective language
- If sufficient details are not provided, omit this section

*Ensure the title is clear, aligns with study objectives, and is free of confidential information.*
''',

    'background': '''
Generate a comprehensive Background section focusing on:

1. **Current Understanding**:
   - Describe the current state of knowledge
   - Reference relevant context from the synopsis

2. **Study Rationale**:
   - Explain why this study is needed
   - Highlight any gaps in current knowledge

**Instructions**:
- Use only the information provided
- Present information in a clear, logical manner
- Avoid making unsupported assumptions

*Ensure the background is informative and based solely on provided information.*
''',

    'objectives': '''
Generate clear study objectives including:

1. **Primary Objective**:
   - State the main goal of the study
   - Ensure it is specific and measurable

2. **Secondary Objectives**:
   - List additional study aims
   - Align with overall study purpose

**Instructions**:
- Make objectives specific and measurable
- Base all content on provided information
- Avoid unsupported assumptions

*Ensure all objectives are clear, focused, and supported by the synopsis.*
''',

    'study_design': '''
Describe the overall study design including:

1. **Study Type**:
   - Specify the type of study
   - Include key design elements

2. **Methodology**:
   - Detail the study approach
   - Describe key procedures

**Instructions**:
- Use only provided information
- Present clear, organized content
- Include relevant study parameters

*Ensure the design is appropriate and clearly described.*
''',

    'endpoints': '''
Define study endpoints including:

1. **Primary Endpoint**:
   - Specify main outcome measure
   - Include measurement timing

2. **Secondary Endpoints**:
   - List additional outcomes
   - Define measurement methods

**Instructions**:
- Make endpoints specific and measurable
- Align with study objectives
- Include timing of assessments

*Ensure endpoints are appropriate and well-defined.*
''',

    'synopsis': '''
Generate a concise and comprehensive Synopsis summarizing:

1. **Study Overview**:
   - Study title and type
   - Primary objectives
   - Key design elements

2. **Background**:
   - Disease/condition context
   - Current treatment landscape
   - Study rationale

3. **Methods**:
   - Study design and population
   - Key procedures
   - Primary endpoints

**Instructions**:
- Keep content clear and organized
- Include all critical elements
- Maintain scientific accuracy

*Ensure the synopsis provides a complete study overview.*
''',

    'ethical_considerations': '''
Detail the ethical considerations including:

1. **Regulatory Compliance**:
   - IRB/Ethics committee review
   - Informed consent process
   - Patient rights protection

2. **Data Privacy**:
   - Confidentiality measures
   - Data protection procedures
   - Subject privacy safeguards

**Instructions**:
- Address all key ethical aspects
- Include compliance requirements
- Detail protection measures

*Ensure comprehensive coverage of ethical considerations.*
''',

    'data_monitoring': '''
Describe the data monitoring approach including:

1. **Monitoring Plan**:
   - Data collection oversight
   - Quality control measures
   - Safety monitoring procedures

2. **Committee Structure**:
   - Data monitoring committee
   - Safety review board
   - Reporting procedures

**Instructions**:
- Detail monitoring frequency
- Specify quality measures
- Include safety oversight

*Ensure thorough coverage of monitoring procedures.*
''',

    'completion_criteria': '''
Define study completion criteria including:

1. **Study Endpoints**:
   - Primary completion definition
   - Secondary completion points
   - Follow-up requirements

2. **Discontinuation Criteria**:
   - Individual subject completion
   - Study termination conditions
   - Early stopping rules

**Instructions**:
- Be specific and measurable
- Include all completion scenarios
- Define clear endpoints

*Ensure clear definition of completion criteria.*
''',

    'population': '''
Define the study population including:

1. **Target Population**:
   - Key characteristics
   - Demographics
   - Disease/condition criteria

2. **Selection Criteria**:
   - Inclusion criteria
   - Exclusion criteria
   - Sample size justification

**Instructions**:
- Be specific about eligibility
- Define clear criteria
- Include population size

*Ensure population definition is clear and appropriate.*
''',

    'procedures': '''
Detail study procedures including:

1. **Study Activities**:
   - Screening procedures
   - Treatment/intervention details
   - Follow-up activities

2. **Schedule of Events**:
   - Visit schedule
   - Assessment timing
   - Data collection points

**Instructions**:
- Provide chronological order
- Include all key activities
- Specify timing clearly

*Ensure procedures are comprehensive and well-organized.*
''',

    'statistical_analysis': '''
Describe statistical methodology including:

1. **Analysis Population**:
   - Analysis sets
   - Handling of missing data
   - Population definitions

2. **Statistical Methods**:
   - Primary analysis approach
   - Secondary analyses
   - Interim analyses (if applicable)

**Instructions**:
- Define analysis populations
- Specify statistical tests
- Include power calculations

*Ensure statistical approach is appropriate and comprehensive.*
''',

    'safety': '''
Detail safety monitoring including:

1. **Safety Parameters**:
   - Adverse event monitoring
   - Safety assessments
   - Laboratory evaluations

2. **Safety Oversight**:
   - Safety monitoring board
   - Stopping rules
   - Risk management

**Instructions**:
- Define safety parameters
- Specify monitoring frequency
- Include reporting requirements

*Ensure safety monitoring is thorough and appropriate.*
''',

    'search_strategy': '''
Detail the systematic search strategy including:

1. **Search Parameters**:
   - Databases to be searched
   - Search terms and keywords
   - Time period covered

2. **Search Implementation**:
   - Search string construction
   - Database-specific adaptations
   - Documentation methods

**Instructions**:
- Be comprehensive and systematic
- Include all relevant databases
- Document search process

*Ensure search strategy is reproducible and thorough.*
''',

    'eligibility_criteria': '''
Define study eligibility criteria including:

1. **Inclusion Criteria**:
   - Study types to include
   - Population characteristics
   - Outcome requirements

2. **Exclusion Criteria**:
   - Study types to exclude
   - Quality thresholds
   - Language restrictions

**Instructions**:
- Be specific and clear
- Justify each criterion
- Ensure reproducibility

*Ensure criteria are comprehensive and well-justified.*
''',

    'data_extraction': '''
Detail the data extraction process including:

1. **Extraction Protocol**:
   - Data fields to extract
   - Extraction methods
   - Quality control measures

2. **Documentation**:
   - Data forms/templates
   - Handling of missing data
   - Resolution of discrepancies

**Instructions**:
- Define clear procedures
- Include quality checks
- Specify documentation

*Ensure extraction process is systematic and reliable.*
''',

    'quality_assessment': '''
Describe quality assessment methodology including:

1. **Assessment Tools**:
   - Quality assessment instruments
   - Risk of bias evaluation
   - Grading criteria

2. **Assessment Process**:
   - Reviewer training
   - Independent assessment
   - Consensus procedures

**Instructions**:
- Define assessment criteria
- Detail evaluation process
- Include validation steps

*Ensure quality assessment is rigorous and standardized.*
''',

    'synthesis_methods': '''
Detail data synthesis methodology including:

1. **Analysis Approach**:
   - Synthesis methods
   - Statistical techniques
   - Heterogeneity assessment

2. **Presentation**:
   - Results organization
   - Data presentation
   - Narrative synthesis

**Instructions**:
- Specify analysis methods
- Define synthesis approach
- Include presentation plans

*Ensure synthesis methods are appropriate and well-documented.*
''',

    'results_reporting': '''
Define results reporting approach including:

1. **Reporting Structure**:
   - PRISMA guidelines
   - Results organization
   - Data presentation

2. **Documentation**:
   - Search results
   - Study characteristics
   - Quality assessments

**Instructions**:
- Follow reporting guidelines
- Be comprehensive
- Include all key elements

*Ensure reporting is complete and transparent.*
''',

    'data_source': '''
Detail data source specifications including:

1. **Data Sources**:
   - Database descriptions
   - Time periods covered
   - Data quality metrics

2. **Access Methods**:
   - Data extraction procedures
   - Quality control measures
   - Documentation methods

**Instructions**:
- Specify data sources
- Detail access methods
- Include quality metrics

*Ensure data sources are appropriate and well-documented.*
''',

    'variables': '''
Define study variables including:

1. **Variable Definitions**:
   - Outcome variables
   - Predictor variables
   - Covariates

2. **Measurement**:
   - Data collection methods
   - Variable coding
   - Missing data handling

**Instructions**:
- Define variables clearly
- Specify measurements
- Include coding schemes

*Ensure variables are well-defined and measurable.*
''',

    'limitations': '''
Address study limitations including:

1. **Data Limitations**:
   - Data quality issues
   - Missing information
   - Potential biases

2. **Methodology Limitations**:
   - Design constraints
   - Analysis limitations
   - Generalizability issues

**Instructions**:
- Be transparent
- Address key limitations
- Discuss implications

*Ensure limitations are thoroughly addressed.*
''',

    'survey_design': '''
Detail survey design including:

1. **Survey Structure**:
   - Question types
   - Response formats
   - Survey flow

2. **Implementation**:
   - Administration method
   - Sampling strategy
   - Response handling

**Instructions**:
- Define clear structure
- Specify methodology
- Include validation steps

*Ensure survey design is appropriate and well-planned.*
''',

    'survey_instrument': '''
Describe survey instrument including:

1. **Instrument Development**:
   - Question development
   - Scale selection
   - Validation process

2. **Content Areas**:
   - Key domains
   - Question sequence
   - Response options

**Instructions**:
- Detail instrument development
- Include validation steps
- Specify response formats

*Ensure instrument is valid and reliable.*
''',

    'data_collection': '''
Detail data collection procedures including:

1. **Collection Methods**:
   - Data capture process
   - Quality control measures
   - Timeline management

2. **Documentation**:
   - Data forms
   - Processing procedures
   - Storage methods

**Instructions**:
- Specify procedures
- Include quality checks
- Detail documentation

*Ensure data collection is systematic and well-documented.*
'''
}

SECTION_TEMPLATES = {
    'phase1': {
        'title': '''
Generate a clear and descriptive study title for the Phase 1 clinical trial that includes:

- The investigational compound or intervention
- The study phase (Phase 1)
- The study population or condition

**Instructions**:
- Ensure the title is concise and adheres to regulatory guidelines
- Avoid including any confidential information
- Use formal, objective language
- If sufficient details are not provided, omit this section

*Ensure the title is clear, aligns with study objectives, and is free of confidential information.*
''',
    },
}

CONDITIONAL_SECTIONS = {
    'phase1': {
        'required': [
            'title',
            'synopsis',
            'background',
            'objectives',
            'study_design',
            'population',
            'procedures',
            'statistical_analysis',
            'safety',
            'endpoints',
            'ethical_considerations',
            'data_monitoring',
            'completion_criteria'
        ],
        'optional': ['pk_analysis', 'interim_analysis'],
        'excluded': ['efficacy_endpoints']
    },
    'systematic_review': {
        'required': [
            'title',
            'synopsis',
            'background',
            'search_strategy',
            'eligibility_criteria',
            'data_extraction',
            'quality_assessment',
            'synthesis_methods',
            'results_reporting',
            'ethical_considerations'
        ],
        'optional': ['meta_analysis', 'risk_of_bias'],
        'excluded': ['safety', 'procedures']
    },
    'secondary_rwe': {
        'required': [
            'title',
            'synopsis',
            'background',
            'data_source',
            'variables',
            'statistical_analysis',
            'limitations',
            'ethical_considerations',
            'data_monitoring'
        ],
        'optional': ['sensitivity_analysis', 'subgroup_analysis'],
        'excluded': ['safety', 'procedures']
    },
    'patient_survey': {
        'required': [
            'title',
            'synopsis',
            'background',
            'survey_design',
            'population',
            'survey_instrument',
            'data_collection',
            'statistical_analysis',
            'ethical_considerations'
        ],
        'optional': ['pilot_testing', 'cognitive_debriefing'],
        'excluded': ['safety', 'procedures']
    }
}
