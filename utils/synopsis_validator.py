from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Study design patterns and indicators
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

class SynopsisValidator:
    def __init__(self):
        """Initialize validator with design patterns and indicators"""
        self.design_patterns = DESIGN_PATTERNS
        self.validity_markers = VALIDITY_MARKERS
        self.quality_indicators = QUALITY_INDICATORS

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
        for design_type, patterns in self.design_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                characteristics['design_features'].append(design_type)

        # Analyze validity considerations
        for validity_type, patterns in self.validity_markers.items():
            matches = [p for p in patterns if p in content_lower]
            if matches:
                if validity_type == 'internal_validity':
                    characteristics['validity_considerations']['internal'].extend(matches)
                else:
                    characteristics['validity_considerations']['external'].extend(matches)

        # Analyze quality indicators
        for category, indicators in self.quality_indicators.items():
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

    def validate_synopsis(self, synopsis_content: str) -> Dict:
        """Enhanced synopsis validation"""
        try:
            # Get study characteristics
            characteristics = self.analyze_study_characteristics(synopsis_content)
            
            # Basic validation results
            validation_results = {
                'study_type': self._detect_study_type(synopsis_content),
                'therapeutic_area': self._detect_therapeutic_area(synopsis_content),
                'design_features': characteristics['design_features'],
                'validity_profile': characteristics['validity_considerations'],
                'quality_indicators': characteristics['quality_indicators'],
                'strength_score': characteristics['strength_score'],
                'recommendations': []
            }

            # Generate recommendations
            if not characteristics['design_features']:
                validation_results['recommendations'].append(
                    "Consider explicitly stating study design features"
                )
            if not characteristics['validity_considerations']['internal']:
                validation_results['recommendations'].append(
                    "Add internal validity considerations"
                )
            if not characteristics['validity_considerations']['external']:
                validation_results['recommendations'].append(
                    "Include external validity considerations"
                )

            return validation_results

        except Exception as e:
            logger.error(f"Error in enhanced synopsis validation: {str(e)}")
            return None

    def _detect_study_type(self, content: str) -> Optional[str]:
        """Detect study type from synopsis content"""
        content_lower = content.lower()
        
        # Phase detection patterns
        phase_patterns = {
            'phase1': ['phase 1', 'phase i', 'first-in-human', 'dose escalation'],
            'phase2': ['phase 2', 'phase ii', 'proof of concept', 'efficacy study'],
            'phase3': ['phase 3', 'phase iii', 'confirmatory study', 'pivotal study'],
            'phase4': ['phase 4', 'phase iv', 'post-marketing', 'real-world evidence']
        }
        
        # Special study type patterns
        special_patterns = {
            'observational': ['observational study', 'cohort study', 'case-control'],
            'systematic_review': ['systematic review', 'meta-analysis', 'literature review'],
            'secondary_rwe': ['secondary analysis', 'database study', 'claims analysis'],
            'patient_survey': ['patient survey', 'questionnaire study', 'patient-reported']
        }
        
        # Check phase patterns first
        for phase, patterns in phase_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                return phase
                
        # Then check special study types
        for study_type, patterns in special_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                return study_type
                
        return None

    def _detect_therapeutic_area(self, content: str) -> Optional[str]:
        """Detect therapeutic area from synopsis content"""
        content_lower = content.lower()
        
        therapeutic_areas = {
            'oncology': ['cancer', 'tumor', 'oncology', 'neoplasm'],
            'cardiology': ['cardiac', 'heart', 'cardiovascular', 'hypertension'],
            'neurology': ['neural', 'brain', 'neurological', 'cognitive'],
            'immunology': ['immune', 'autoimmune', 'inflammation'],
            'infectious_disease': ['infection', 'viral', 'bacterial', 'pathogen'],
            'psychiatry': ['psychiatric', 'mental health', 'depression', 'anxiety'],
            'endocrinology': ['hormone', 'diabetes', 'thyroid', 'metabolic'],
            'respiratory': ['lung', 'respiratory', 'asthma', 'copd'],
            'gastroenterology': ['gastro', 'digestive', 'liver', 'intestinal']
        }
        
        for area, patterns in therapeutic_areas.items():
            if any(pattern in content_lower for pattern in patterns):
                return area
                
        return None
