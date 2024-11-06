# Previous content remains the same until CONDITIONAL_SECTIONS definition
# Adding only the CONDITIONAL_SECTIONS update for brevity

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
            'objectives',
            'data_source',
            'variables',
            'statistical_analysis',
            'limitations',
            'ethical_considerations'
        ],
        'optional': ['sensitivity_analysis', 'subgroup_analysis'],
        'excluded': [
            'safety',
            'procedures',
            'data_monitoring',
            'completion_criteria'
        ]
    },
    'patient_survey': {
        'required': [
            'title',
            'synopsis',
            'background',
            'objectives',
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
