import logging
from typing import Dict

logger = logging.getLogger(__name__)

SECTION_TEMPLATES = {
    # General Instructions
    "general_instructions": """
When generating each section, consider the specific type and phase of the study as provided in the synopsis (e.g., Phase 1 clinical trial, Phase 2b, systematic review, secondary Real World Evidence (RWE) study, patient survey, disease registry, etc.).

Ensure that the content is tailored to the objectives, design, methodologies, and regulatory requirements appropriate for that specific study type.

Include sections only when relevant based on the provided information and the study type. Do not create sections or subsections solely to state that they are not applicable.

Avoid including any disallowed content, and ensure all information is based solely on the provided synopsis without making unsupported assumptions or fabricating data.

Use formal, objective language appropriate for a scientific document, and ensure compliance with ethical and regulatory standards throughout.
""",

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

        'synopsis': '''
Generate a concise and comprehensive Synopsis for the Phase 1 clinical trial, summarizing the key elements based on the provided information.

The Synopsis should include:

1. **Study Title**:
   - Provide the full title of the study as generated or provided.

2. **Study Type and Phase**:
   - Indicate that this is a Phase 1 clinical trial.

3. **Background and Rationale**:
   - Briefly describe the background and the rationale for the study, focusing on first-in-human considerations, safety profile, and preclinical data.

4. **Objectives**:
   - Summarize the primary and secondary objectives of the study.

5. **Study Design**:
   - Outline the overall study design, including key features such as dose escalation methodology, safety monitoring, and stopping criteria.

6. **Population**:
   - Describe the target population, including key inclusion and exclusion criteria.

7. **Interventions**:
   - Summarize the investigational compound, dosing regimen, and administration route.

8. **Endpoints/Outcome Measures**:
   - List the primary and secondary endpoints.

9. **Statistical Methods**:
   - Briefly mention the primary statistical methods to be used for data analysis.

10. **Ethical Considerations**:
    - Note any key ethical considerations, such as informed consent procedures and data confidentiality measures.

**Instructions**:

- **Conciseness**: Keep the Synopsis concise, ideally within 1-2 pages.
- **Clarity**: Use clear and precise language to ensure that the summary is easily understood.
- **Consistency**: Ensure that the information in the Synopsis aligns with the detailed sections of the protocol.
- **Relevance**: Include only the elements relevant to the Phase 1 study and based on the information provided.
- **Compliance**: Avoid including any disallowed content or confidential information.
- **Accuracy**: Base the Synopsis solely on the information provided without making unsupported assumptions.

*Ensure that the Synopsis provides a clear and comprehensive overview of the study, facilitating understanding for readers.*
''',

        'background': '''
Generate a comprehensive Background section for the Phase 1 study, focusing on:

1. **First-in-Human Considerations**:
   - Discuss the significance of introducing the investigational compound to humans.
   - Reference any relevant preclinical studies that support human testing.

2. **Safety Profile of the Compound**:
   - Summarize known safety data from preclinical studies.

3. **Preliminary Pharmacology Data**:
   - Include pharmacokinetic and pharmacodynamic data from preclinical research.

**Instructions**:

- Use only the information provided; do not fabricate data or references.
- Avoid making unsupported assumptions.
- Present the information in a clear and logical manner, using appropriate headings.

*Ensure the background is informative, based solely on the provided information, and adheres to ethical and regulatory standards.*
'''
    }
}

# Add DEFAULT_TEMPLATES dictionary after SECTION_TEMPLATES
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
    'phase2': {
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
        'excluded': []
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
