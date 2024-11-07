from typing import Dict, List, Optional

# Add these patterns to the existing SynopsisValidator class

DESIGN_PATTERNS = {
    'randomized': [
        'randomized', 'randomisation', 'random allocation', 
        'randomly assigned', 'random assignment'
    ],
    'controlled': [
        'controlled study', 'control group', 'comparator arm',
        'active control', 'placebo control'
    ],
    'blinding': [
        'double-blind', 'single-blind', 'triple-blind',
        'blinded assessment', 'masked'
    ],
    'adaptive': [
        'adaptive design', 'sample size re-estimation',
        'interim analysis', 'adaptive randomization'
    ],
    'crossover': [
        'crossover', 'cross-over', 'treatment switch',
        'sequence assignment'
    ]
}

VALIDITY_MARKERS = {
    'internal_validity': [
        'bias control', 'standardization', 'quality control',
        'monitoring procedures', 'data validation'
    ],
    'external_validity': [
        'generalizability', 'real-world', 'practice setting',
        'population representation', 'implementation'
    ]
}

QUALITY_INDICATORS = {
    'methods': [
        'standardized procedures', 'validated instruments',
        'quality assurance', 'monitoring plan'
    ],
    'endpoints': [
        'primary endpoint', 'secondary endpoints',
        'outcome measures', 'assessment criteria'
    ],
    'analysis': [
        'statistical analysis', 'sample size calculation',
        'power analysis', 'interim analysis'
    ]
}

# Add this method to SynopsisValidator class
def analyze_study_characteristics(self, content: str) -> Dict:
    """
    Enhanced analysis of study characteristics including design features,
    validity considerations, and quality indicators
    """
    content_lower = content.lower()
    characteristics = {
        'design_features': [],
        'validity_considerations': {
            'internal': [],
            'external': []
        },
        'quality_indicators': [],
        'strength_score': 0
    }

    # Analyze design features
    for design_type, patterns in DESIGN_PATTERNS.items():
        if any(pattern in content_lower for pattern in patterns):
            characteristics['design_features'].append(design_type)

    # Analyze validity considerations
    for validity_type, patterns in VALIDITY_MARKERS.items():
        matches = [p for p in patterns if p in content_lower]
        if matches:
            if validity_type == 'internal_validity':
                characteristics['validity_considerations']['internal'].extend(matches)
            else:
                characteristics['validity_considerations']['external'].extend(matches)

    # Analyze quality indicators
    for category, indicators in QUALITY_INDICATORS.items():
        matches = [i for i in indicators if i in content_lower]
        if matches:
            characteristics['quality_indicators'].extend(matches)

    # Calculate strength score (basic version)
    characteristics['strength_score'] = (
        len(characteristics['design_features']) * 2 +
        len(characteristics['validity_considerations']['internal']) +
        len(characteristics['validity_considerations']['external']) +
        len(characteristics['quality_indicators'])
    ) / 10.0  # Normalize to 0-1 scale

    return characteristics

# Add to validate_synopsis method
def validate_synopsis(self, synopsis_content: str) -> Dict:
    """Enhanced synopsis validation"""
    try:
        # Existing validation
        base_validation = super().validate_synopsis(synopsis_content)

        # Additional characteristics analysis
        characteristics = self.analyze_study_characteristics(synopsis_content)

        # Merge results
        enhanced_validation = {
            **base_validation,
            'design_features': characteristics['design_features'],
            'validity_profile': characteristics['validity_considerations'],
            'quality_indicators': characteristics['quality_indicators'],
            'strength_score': characteristics['strength_score'],
            'recommendations': []
        }

        # Generate recommendations
        if not characteristics['design_features']:
            enhanced_validation['recommendations'].append(
                "Consider explicitly stating study design features"
            )
        if not characteristics['validity_considerations']['internal']:
            enhanced_validation['recommendations'].append(
                "Add internal validity considerations"
            )
        if not characteristics['validity_considerations']['external']:
            enhanced_validation['recommendations'].append(
                "Include external validity considerations"
            )

        return enhanced_validation

    except Exception as e:
        logger.error(f"Error in enhanced synopsis validation: {str(e)}")
        return None
