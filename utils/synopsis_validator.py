import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SynopsisValidator:
    def __init__(self):
        """Initialize validator with study type detection patterns"""
        self.study_type_patterns = {
            'phase1': [
                'phase 1', 'phase i', 'first in human', 'dose escalation',
                'safety study', 'tolerability study', 'healthy volunteers',
                'initial human', 'single ascending dose', 'multiple ascending dose'
            ],
            'phase2': [
                'phase 2', 'phase ii', 'proof of concept', 'efficacy study',
                'dose finding', 'dose ranging', 'preliminary efficacy',
                'therapeutic exploratory', 'treatment efficacy'
            ],
            'phase3': [
                'phase 3', 'phase iii', 'confirmatory', 'pivotal study',
                'registration trial', 'comparative efficacy', 'confirmatory study',
                'therapeutic confirmatory', 'randomized controlled'
            ],
            'phase4': [
                'phase 4', 'phase iv', 'post-marketing', 'real-world evidence',
                'post-authorization', 'surveillance study', 'pragmatic trial',
                'registry based', 'effectiveness study'
            ],
            'observational': [
                'observational study', 'registry study', 'cohort study',
                'case-control', 'prospective observational', 'retrospective analysis',
                'longitudinal study', 'epidemiological study', 'natural history',
                'real-world data', 'population-based'
            ],
            'medical_device': [
                'device study', 'medical device', 'feasibility study',
                'device safety', 'device performance', 'usability study',
                'device validation', 'device verification', 'device testing',
                'implant study', 'device trial'
            ],
            'diagnostic': [
                'diagnostic accuracy', 'screening study', 'sensitivity specificity',
                'diagnostic test', 'biomarker validation', 'diagnostic performance',
                'diagnostic evaluation', 'test validation', 'assay validation',
                'diagnostic precision', 'reference standard'
            ],
            'systematic_review': [
                'systematic review', 'systematic literature review', 'slr',
                'meta analysis', 'meta-analysis', 'evidence synthesis',
                'systematic search', 'prisma', 'literature synthesis',
                'literature review', 'evidence review', 'systematic search',
                'search strategy', 'prisma statement', 'evidence synthesis',
                'meta-analyses', 'review protocol', 'systematic methodology',
                'review registration', 'search criteria', 'database search',
                'study selection', 'data synthesis', 'quality appraisal'
            ],
            'secondary_rwe': [
                'secondary analysis', 'real world evidence', 'rwe study',
                'database study', 'claims analysis', 'electronic health records',
                'retrospective database', 'healthcare database', 'real-world data',
                'secondary rwe', 'administrative data'
            ],
            'patient_survey': [
                'patient survey', 'questionnaire study', 'patient reported outcome',
                'survey research', 'patient experience', 'quality of life survey',
                'patient preference', 'patient satisfaction', 'patient perspective',
                'patient feedback', 'pro study', 'patient-reported'
            ]
        }

    def detect_study_type(self, content: str) -> Optional[str]:
        try:
            content_lower = content.lower()
            
            # First check for clinical trial phases
            phase_patterns = {
                'phase1': self.study_type_patterns['phase1'],
                'phase2': self.study_type_patterns['phase2'],
                'phase3': self.study_type_patterns['phase3'],
                'phase4': self.study_type_patterns['phase4']
            }
            
            # Check for phase indicators first
            for phase, patterns in phase_patterns.items():
                if any(pattern in content_lower for pattern in patterns):
                    return phase
                    
            # Then check other study types
            for study_type, patterns in self.study_type_patterns.items():
                if study_type not in ['phase1', 'phase2', 'phase3', 'phase4']:
                    if any(pattern in content_lower for pattern in patterns):
                        return study_type
            
            return None
                
        except Exception as e:
            logger.error(f"Error detecting study type: {str(e)}")
            return None

    def detect_therapeutic_area(self, content: str) -> Optional[str]:
        """Detect therapeutic area from content using defined patterns"""
        therapeutic_areas = {
            'oncology': ['cancer', 'tumor', 'oncology', 'neoplasm', 'malignancy', 'carcinoma'],
            'cardiology': ['heart', 'cardiac', 'cardiovascular', 'hypertension', 'vascular'],
            'neurology': ['brain', 'neural', 'nervous system', 'neurodegenerative', 'cognitive'],
            'immunology': ['immune', 'autoimmune', 'inflammation', 'rheumatic', 'allergy'],
            'infectious_disease': ['infection', 'viral', 'bacterial', 'pathogen', 'antimicrobial'],
            'metabolism': ['diabetes', 'metabolic', 'endocrine', 'obesity', 'lipid'],
            'respiratory': ['lung', 'respiratory', 'pulmonary', 'asthma', 'copd'],
            'psychiatry': ['psychiatric', 'mental health', 'behavioral', 'depression', 'anxiety'],
            'pediatrics': ['pediatric', 'children', 'juvenile', 'infant', 'adolescent'],
            'geriatrics': ['elderly', 'geriatric', 'aging', 'older adults'],
            'rare_disease': ['rare disease', 'orphan disease', 'genetic disorder']
        }
        
        content_lower = content.lower()
        for area, patterns in therapeutic_areas.items():
            if any(pattern in content_lower for pattern in patterns):
                return area
        return None

    def validate_synopsis(self, synopsis_content: str) -> Dict:
        """Validate synopsis content and detect study type and therapeutic area"""
        try:
            study_type = self.detect_study_type(synopsis_content)
            therapeutic_area = self.detect_therapeutic_area(synopsis_content)
            
            # Additional SLR validation
            content_lower = synopsis_content.lower()
            slr_indicators = [
                'search strategy', 'inclusion criteria',
                'exclusion criteria', 'quality assessment',
                'data extraction', 'prisma'
            ]
            
            has_slr_indicators = any(indicator in content_lower 
                                   for indicator in slr_indicators)
            
            # Override study type if strong SLR indicators present
            if has_slr_indicators and study_type not in ['systematic_review', 'secondary_rwe']:
                study_type = 'systematic_review'
                
            validation_result = {
                'study_type': study_type,
                'therapeutic_area': therapeutic_area,
                'is_valid': True,
                'messages': []
            }
            
            # Add validation messages
            if not study_type:
                validation_result['messages'].append('Could not detect study type')
                validation_result['is_valid'] = False
            if not therapeutic_area:
                validation_result['messages'].append('Could not detect therapeutic area')
            
            # Add study phase validation for clinical trials
            if study_type and study_type.startswith('phase'):
                validation_result['study_phase'] = study_type[-1]
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error in synopsis validation: {str(e)}")
            return None
