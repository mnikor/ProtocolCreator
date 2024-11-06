# Default templates for all study types
DEFAULT_TEMPLATES = {
    'title': 'Generate a clear and descriptive title that reflects the study objectives and design.',
    'synopsis': 'Create a comprehensive synopsis summarizing the key aspects of the study.',
    'background': 'Provide relevant background information and study rationale.',
    'objectives': 'Define primary and secondary study objectives.',
    'data_source': 'Describe the data sources and their characteristics.',
    'variables': 'Define study variables and their measurements.',
    'statistical_analysis': 'Detail the statistical analysis approach.',
    'limitations': 'Discuss potential study limitations and mitigation strategies.',
    'ethical_considerations': 'Address relevant ethical considerations and compliance requirements.'
}

# Study type specific section templates
SECTION_TEMPLATES = {
    'secondary_rwe': {
        'data_source': '''
Describe the database(s) or data source(s) to be used, including:
- Database characteristics and coverage
- Time period of data collection
- Population represented
- Data quality and validation
''',
        'variables': '''
Define study variables including:
- Primary outcomes
- Secondary outcomes
- Covariates and confounders
- Data definitions and coding
''',
        'statistical_analysis': '''
Detail the statistical analysis plan:
- Primary analysis methods
- Handling of missing data
- Sensitivity analyses
- Subgroup analyses
'''
    }
}

# Section configuration based on study type
CONDITIONAL_SECTIONS = {
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
            'data_monitoring',  # Remove as not typically needed for secondary analysis
            'completion_criteria',  # Remove as timing is usually predefined
            'endpoints'  # Typically covered under variables/outcomes
        ]
    }
}
