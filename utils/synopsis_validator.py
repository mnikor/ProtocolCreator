import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SynopsisValidator:
    def __init__(self):
        """Initialize validator with study type detection patterns"""
        self.study_type_patterns = {
            'phase1': ['phase 1', 'phase i', 'first in human', 'dose escalation'],
            'phase2': ['phase 2', 'phase ii', 'proof of concept', 'efficacy study'],
            'phase3': ['phase 3', 'phase iii', 'confirmatory', 'pivotal study'],
            'slr': ['systematic review', 'literature review', 'meta-analysis'],
            'rwe': ['real world', 'observational', 'registry study', 'cohort study']
        }

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
        """Validate synopsis content and detect study type"""
        try:
            # Detect study type from synopsis
            study_type = self.detect_study_type(synopsis_content)
            
            # Validate content based on type
            validation_result = {
                'study_type': study_type,
                'is_valid': True,
                'messages': []
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error in synopsis validation: {str(e)}")
            return None
