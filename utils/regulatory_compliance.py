import re
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegulatoryCompliance:
    def __init__(self):
        # ICH E6(R2) GCP Requirements
        self.ich_e6_requirements = {
            'background': {
                'required_elements': [
                    'rationale',
                    'background_information',
                    'risk_benefit_assessment'
                ],
                'keywords': [
                    'background',
                    'rationale',
                    'risk',
                    'benefit',
                    'previous findings'
                ]
            },
            'objectives': {
                'required_elements': [
                    'primary_objective',
                    'primary_endpoint',
                    'secondary_objectives'
                ],
                'keywords': [
                    'objective',
                    'endpoint',
                    'measure',
                    'assessment'
                ]
            },
            'study_design': {
                'required_elements': [
                    'study_type',
                    'design_description',
                    'randomization',
                    'blinding',
                    'treatment_groups'
                ],
                'keywords': [
                    'design',
                    'randomization',
                    'blinding',
                    'control',
                    'treatment'
                ]
            }
        }

        # Phase-specific requirements
        self.phase_requirements = {
            'phase1': {
                'safety_focus': True,
                'required_sections': [
                    'safety_parameters',
                    'dose_escalation',
                    'stopping_rules'
                ],
                'minimum_monitoring': 'intensive'
            },
            'phase2': {
                'efficacy_focus': True,
                'required_sections': [
                    'efficacy_parameters',
                    'dose_selection',
                    'population_selection'
                ],
                'minimum_monitoring': 'regular'
            },
            'phase3': {
                'confirmatory_focus': True,
                'required_sections': [
                    'primary_analysis',
                    'superiority_noninferiority',
                    'safety_monitoring'
                ],
                'minimum_monitoring': 'standard'
            }
        }

    def check_compliance(self, protocol_sections: Dict, study_phase: str) -> Dict:
        """
        Check protocol compliance against ICH guidelines and phase-specific requirements
        """
        compliance_report = {
            'overall_compliance': True,
            'missing_elements': [],
            'warnings': [],
            'suggestions': [],
            'section_compliance': {}
        }

        try:
            # Check ICH E6 compliance
            for section, content in protocol_sections.items():
                if section in self.ich_e6_requirements:
                    section_compliance = self._check_section_compliance(
                        section, 
                        content, 
                        self.ich_e6_requirements[section]
                    )
                    compliance_report['section_compliance'][section] = section_compliance
                    
                    if not section_compliance['compliant']:
                        compliance_report['overall_compliance'] = False
                        compliance_report['missing_elements'].extend(
                            section_compliance['missing_elements']
                        )

            # Check phase-specific requirements
            phase_compliance = self._check_phase_requirements(
                protocol_sections,
                study_phase
            )
            compliance_report['phase_compliance'] = phase_compliance

            if not phase_compliance['compliant']:
                compliance_report['overall_compliance'] = False
                compliance_report['missing_elements'].extend(
                    phase_compliance['missing_elements']
                )

            # Generate suggestions for improvement
            compliance_report['suggestions'] = self._generate_suggestions(
                compliance_report,
                study_phase
            )

            return compliance_report

        except Exception as e:
            logger.error(f"Error in compliance checking: {str(e)}")
            raise

    def _check_section_compliance(
        self,
        section: str,
        content: str,
        requirements: Dict
    ) -> Dict:
        """
        Check individual section compliance
        """
        section_report = {
            'compliant': True,
            'missing_elements': [],
            'keyword_coverage': 0.0
        }

        # Check required elements
        for element in requirements['required_elements']:
            if not self._check_element_presence(content, element):
                section_report['compliant'] = False
                section_report['missing_elements'].append({
                    'element': element,
                    'section': section,
                    'requirement': 'ICH E6(R2)'
                })

        # Check keyword coverage
        found_keywords = sum(
            1 for keyword in requirements['keywords']
            if self._check_element_presence(content, keyword)
        )
        section_report['keyword_coverage'] = (
            found_keywords / len(requirements['keywords'])
        )

        return section_report

    def _check_phase_requirements(
        self,
        protocol_sections: Dict,
        study_phase: str
    ) -> Dict:
        """
        Check phase-specific requirements
        """
        phase_report = {
            'compliant': True,
            'missing_elements': [],
            'phase_specific_warnings': []
        }

        phase_reqs = self.phase_requirements.get(study_phase)
        if not phase_reqs:
            phase_report['phase_specific_warnings'].append(
                f"Unknown study phase: {study_phase}"
            )
            return phase_report

        # Check required sections for phase
        for required_section in phase_reqs['required_sections']:
            found = False
            for section, content in protocol_sections.items():
                if self._check_element_presence(content, required_section):
                    found = True
                    break

            if not found:
                phase_report['compliant'] = False
                phase_report['missing_elements'].append({
                    'element': required_section,
                    'phase': study_phase,
                    'requirement': f"{study_phase.upper()} specific requirement"
                })

        return phase_report

    def _check_element_presence(self, content: str, element: str) -> bool:
        """
        Check if an element is present in the content
        """
        element_pattern = element.replace('_', ' ').lower()
        content_lower = content.lower()
        return bool(re.search(rf'\b{element_pattern}\b', content_lower))

    def _generate_suggestions(
        self,
        compliance_report: Dict,
        study_phase: str
    ) -> List[str]:
        """
        Generate improvement suggestions based on compliance findings
        """
        suggestions = []

        # Suggestions for missing elements
        for missing in compliance_report['missing_elements']:
            element = missing['element'].replace('_', ' ')
            suggestions.append(
                f"Add {element} to {missing.get('section', 'protocol')} section "
                f"to comply with {missing['requirement']}"
            )

        # Phase-specific suggestions
        phase_reqs = self.phase_requirements.get(study_phase, {})
        if phase_reqs:
            if phase_reqs.get('safety_focus'):
                suggestions.append(
                    "Ensure comprehensive safety monitoring and "
                    "dose escalation procedures"
                )
            if phase_reqs.get('efficacy_focus'):
                suggestions.append(
                    "Include detailed efficacy assessments and "
                    "dose-response evaluations"
                )
            if phase_reqs.get('confirmatory_focus'):
                suggestions.append(
                    "Ensure robust statistical analysis plan and "
                    "adequate power calculations"
                )

        return suggestions

    def get_ich_guidelines(self) -> Dict:
        """
        Get ICH guideline requirements
        """
        return self.ich_e6_requirements

    def get_phase_requirements(self, phase: str) -> Optional[Dict]:
        """
        Get phase-specific requirements
        """
        return self.phase_requirements.get(phase)
