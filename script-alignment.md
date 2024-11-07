# Script Alignment Analysis

## 1. Current State

### Protocol Validator
- Has updated study types (Phase 1-4, SLR, Secondary RWE)
- Includes detailed validity checks
- Missing specific recommendations implementation

### Section Templates
- Only covers Phase 1-3
- Missing newer study types
- Basic template structure

### Enhanced Prompts
- Includes chain-of-thought prompting
- Covers all study types
- Has detailed validity considerations

## Required Updates

### 1. Section Templates (`section_templates.py`)
```python
# Add new study types
SECTION_TEMPLATES.update({
    'phase4': {
        'statistical_analysis': '''
Phase 4-Specific Analysis:
• Define effectiveness measures
• Specify safety monitoring approaches
• Detail real-world evidence collection
• Define utilization analyses
''',
        'study_design': '''
Phase 4 Design Elements:
• Define real-world setting criteria
• Specify practice pattern assessment
• Detail safety surveillance methods
• Define population representation
'''
    },
    'systematic_review': {
        'statistical_analysis': '''
Systematic Review Analysis:
• Define evidence synthesis methods
• Specify heterogeneity assessment
• Detail meta-analysis approach
• Define sensitivity analyses
''',
        'study_design': '''
Systematic Review Design:
• Define search strategy framework
• Specify selection criteria process
• Detail quality assessment methods
• Define data extraction process
'''
    },
    'secondary_rwe': {
        'statistical_analysis': '''
Secondary RWE Analysis:
• Define data validation methods
• Specify missing data approaches
• Detail confounding control
• Define sensitivity analyses
''',
        'study_design': '''
Secondary RWE Design:
• Define data source requirements
• Specify variable definitions
• Detail quality assessment
• Define validation procedures
'''
    }
})

# Update CONDITIONAL_SECTIONS
CONDITIONAL_SECTIONS.update({
    'phase4': {
        'required': [
            'effectiveness',
            'safety',
            'utilization',
            'real_world_evidence'
        ],
        'optional': ['health_economics'],
        'excluded': ['dose_escalation']
    },
    'systematic_review': {
        'required': [
            'search_strategy',
            'selection_criteria',
            'quality_assessment',
            'evidence_synthesis'
        ],
        'optional': ['meta_analysis'],
        'excluded': ['safety', 'efficacy']
    },
    'secondary_rwe': {
        'required': [
            'data_source',
            'variable_definitions',
            'quality_assessment',
            'analysis_plan'
        ],
        'optional': ['sensitivity_analysis'],
        'excluded': ['randomization', 'blinding']
    }
})
```

### 2. Protocol Validator Implementation
```python
def _get_validity_recommendations(self, study_type: str) -> Dict:
    """Implement specific recommendations by study type"""
    recommendations = {
        'phase2': {
            'endpoint_measurement': {
                'message': 'Incomplete endpoint measurement specification',
                'recommendation': '''
                Add detailed endpoint measurement procedures:
                - Standardization methods
                - Quality control measures
                - Central assessment procedures
                - Missing data handling
                '''
            },
            'bias_control_methods': {
                'message': 'Insufficient bias control methods',
                'recommendation': '''
                Specify bias control measures:
                - Independent assessment procedures
                - Standardization methods
                - Quality control measures
                - Documentation requirements
                '''
            }
        },
        # Add similar structures for other study types
    }
    return recommendations.get(study_type, {})
```

## Integration Strategy

1. **Align Validation Rules**
- Ensure validator rules match template requirements
- Add specific checks for new study types
- Implement detailed recommendations

2. **Update Templates**
- Add missing study types
- Enhance validity considerations
- Include chain-of-thought elements

3. **Enhance Prompting System**
- Integrate with validator rules
- Include template-specific guidance
- Add validity checks in prompts

## Quality Control Measures

1. **Cross-Reference Checks**
- Verify consistency between scripts
- Ensure all study types covered
- Validate recommendation alignment

2. **Validation Coverage**
- Check all validity aspects covered
- Ensure appropriate severity levels
- Verify recommendation completeness

## Next Steps

1. Implement updated section templates
2. Complete validity recommendations
3. Add specific checks for each study type
4. Enhance cross-referencing system