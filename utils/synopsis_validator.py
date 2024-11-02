import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SynopsisValidator:
    def __init__(self):
        """Initialize validator with study type detection patterns"""
        self.study_type_patterns = {
            'phase1': [
                'phase 1', 'phase i', 'first in human', 'dose escalation',
                'safety study', 'tolerability study', 'healthy volunteers'
            ],
            'phase2': [
                'phase 2', 'phase ii', 'proof of concept', 'efficacy study',
                'dose finding', 'dose ranging', 'preliminary efficacy'
            ],
            'phase3': [
                'phase 3', 'phase iii', 'confirmatory', 'pivotal study',
                'registration trial', 'comparative efficacy'
            ],
            'phase4': [
                'phase 4', 'phase iv', 'post-marketing', 'real-world evidence',
                'post-authorization'
            ],
            'observational': [
                'observational study', 'registry study', 'cohort study',
                'case-control', 'prospective observational'
            ],
            'medical_device': [
                'device study', 'medical device', 'feasibility study',
                'device safety', 'device performance'
            ],
            'diagnostic': [
                'diagnostic accuracy', 'screening study', 'sensitivity specificity',
                'diagnostic test', 'biomarker validation'
            ]
        }

    def detect_therapeutic_area(self, content: str) -> Optional[str]:
        """Detect therapeutic area from content using defined patterns"""
        therapeutic_areas = {
            'oncology': ['cancer', 'tumor', 'oncology', 'neoplasm'],
            'cardiology': ['heart', 'cardiac', 'cardiovascular'],
            'neurology': ['brain', 'neural', 'nervous system'],
            'immunology': ['immune', 'autoimmune', 'inflammation'],
            'infectious_disease': ['infection', 'viral', 'bacterial'],
            'metabolism': ['diabetes', 'metabolic', 'endocrine'],
            'respiratory': ['lung', 'respiratory', 'pulmonary'],
            'psychiatry': ['psychiatric', 'mental health', 'behavioral'],
        }
        
        content_lower = content.lower()
        for area, patterns in therapeutic_areas.items():
            if any(pattern in content_lower for pattern in patterns):
                return area
        return None

    def detect_study_type(self, content: str) -> Optional[str]:
        """Detect study type from content using defined patterns"""
        try:
            content_lower = content.lower()
            
            for study_type, patterns in self.study_type_patterns.items():
                if any(pattern in content_lower for pattern in patterns):
                    return study_type
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting study type: {str(e)}")
            return None

    def validate_synopsis(self, synopsis_content: str) -> Dict:
        """Validate synopsis content and detect study type and therapeutic area"""
        try:
            study_type = self.detect_study_type(synopsis_content)
            therapeutic_area = self.detect_therapeutic_area(synopsis_content)
            
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
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error in synopsis validation: {str(e)}")
            return None
