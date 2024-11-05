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
'''
}

SECTION_TEMPLATES = {
    # Phase 1 Clinical Trial
    'phase1': {
        'title': '''
Generate a clear and descriptive study title for the Phase 1 clinical trial that includes:

- The investigational compound or intervention
- The study phase (Phase 1)
- The study population or condition

**Instructions**:

- Ensure the title is concise and adheres to regulatory guidelines.
- Avoid including any confidential or proprietary information.
- Use formal, objective language appropriate for a scientific document.
- If sufficient details are not provided, omit this section.

*Ensure the title is clear, aligns with the study objectives, and is free of confidential information.*
''',
        # ... rest of the phase1 templates ...
    },
    # ... rest of the SECTION_TEMPLATES content ...
}

CONDITIONAL_SECTIONS = {
    'phase1': {
        'required': [
            'title',  # Add title first
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
            'title',  # Add title first
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
            'title',  # Add title first
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
            'title',  # Add title first
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
