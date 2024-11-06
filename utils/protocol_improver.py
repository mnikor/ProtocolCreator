import logging
import re
from typing import Dict, Optional, List
from .missing_information_handler import MissingInformationHandler
from .gpt_handler import GPTHandler

logger = logging.getLogger(__name__)

class ProtocolImprover:
    def __init__(self):
        """Initialize improver with handlers"""
        self.missing_info_handler = MissingInformationHandler()
        self.gpt_handler = GPTHandler()
        
    def analyze_synopsis(self, content: str, study_type: str = None) -> Dict:
        '''Analyze synopsis content with study type specific validation'''
        content_lower = content.lower()
        
        # Get study-specific required fields
        required_fields = self._get_study_type_requirements(study_type)
        
        missing_fields = {}
        for field, patterns in required_fields.items():
            found = any(pattern in content_lower for pattern in patterns)
            if not found:
                missing_fields[field] = self._get_field_prompt(field, study_type)
        
        return {
            'critical_missing': bool(missing_fields),
            'critical_fields': missing_fields,
            'study_type_specific': True if study_type else False
        }

    def _get_study_type_requirements(self, study_type: str) -> Dict:
        '''Get required fields based on study type'''
        base_fields = {
            'study_population': [
                'inclusion criteria', 'patient population', 'subjects',
                'eligible patients', 'study population'
            ],
            'primary_objective': [
                'primary objective', 'primary endpoint',
                'primary goal', 'main objective'
            ]
        }
        
        # Add study-type specific fields
        if study_type == 'systematic_review':
            base_fields.update({
                'search_strategy': [
                    'search strategy', 'database search',
                    'literature search', 'systematic search'
                ],
                'eligibility_criteria': [
                    'inclusion criteria', 'exclusion criteria',
                    'study selection', 'eligibility'
                ]
            })
        elif study_type == 'secondary_rwe':
            base_fields.update({
                'data_source': [
                    'database', 'data source', 'real world data',
                    'electronic health records', 'claims data'
                ],
                'time_period': [
                    'study period', 'time frame', 'data period',
                    'observation period'
                ]
            })
        elif study_type == 'patient_survey':
            base_fields.update({
                'survey_instrument': [
                    'questionnaire', 'survey tool', 'assessment tool',
                    'patient reported outcome'
                ],
                'administration': [
                    'survey administration', 'data collection',
                    'survey method', 'questionnaire delivery'
                ]
            })
        
        return base_fields

    def _get_field_prompt(self, field: str, study_type: str) -> str:
        '''Get context-aware prompt for missing field'''
        base_prompts = {
            'study_population': 'Please specify the target study population',
            'primary_objective': 'What is the primary objective of the study?'
        }
        
        study_specific_prompts = {
            'systematic_review': {
                'search_strategy': 'What databases will be searched? Include search strategy details',
                'eligibility_criteria': 'Define inclusion/exclusion criteria for study selection'
            },
            'secondary_rwe': {
                'data_source': 'Which database(s) or data source(s) will be used?',
                'time_period': 'What is the study time period for data collection?'
            },
            'patient_survey': {
                'survey_instrument': 'What survey instrument or questionnaire will be used?',
                'administration': 'How will the survey be administered to participants?'
            }
        }
        
        if study_type and study_type in study_specific_prompts:
            base_prompts.update(study_specific_prompts[study_type])
        
        return base_prompts.get(field, f'Please provide information about {field.replace("_", " ")}')

    def analyze_protocol_sections(self, sections: Dict[str, str]) -> Dict:
        """Analyze all protocol sections for missing information"""
        analysis_results = {}
        overall_completeness = 0.0
        total_sections = len(sections)
        
        for section_name, content in sections.items():
            section_analysis = self.missing_info_handler.analyze_section_completeness(
                section_name, content
            )
            analysis_results[section_name] = section_analysis
            overall_completeness += section_analysis['completeness_score']
            
        if total_sections > 0:
            overall_completeness /= total_sections
            
        return {
            'section_analyses': analysis_results,
            'overall_completeness': overall_completeness,
            'overall_quality_score': self._calculate_quality_score(analysis_results)
        }

    def validate_section(self, section_name: str, content: str, study_type: str) -> Dict:
        """Validate individual protocol section"""
        section_results = {
            "issues": [],
            "warnings": [],
            "suggestions": [],
            "score": 0
        }
        
        # Add section-specific validation
        self._validate_section_requirements(section_name, content, study_type, section_results)
        
        # Check completeness
        self._validate_section_completeness(section_name, content, study_type, section_results)
        
        # Check placeholders
        self._check_placeholders(content, section_results)
        
        # Check timeline if relevant
        if section_name in ['study_design', 'procedures']:
            timeline_issues = self._validate_timeline(content)
            section_results["issues"].extend(timeline_issues)
        
        # Calculate score
        section_results["score"] = self._calculate_section_score(section_results)
        
        return section_results

    def _validate_section_requirements(self, section_name: str, content: str, study_type: str, results: Dict):
        """Check section-specific requirements"""
        section_requirements = {
            "objectives": {
                "required_elements": ["primary_objective", "secondary_objectives"],
                "forbidden_terms": ["tbd", "to be determined", "placeholder"],
                "min_length": 200
            },
            "study_design": {
                "required_elements": ["design_type", "duration", "population"],
                "study_type_specific": {
                    "phase1": ["dose_escalation", "safety_monitoring"],
                    "phase2": ["endpoints", "sample_size"],
                    "phase3": ["randomization", "blinding", "interim_analysis"],
                    "phase4": ["real_world_setting", "comparator"]
                }
            },
            "safety": {
                "required_elements": ["safety_parameters", "monitoring", "reporting"],
                "study_type_specific": {
                    "phase1": ["dose_limiting_toxicity", "safety_review"],
                    "phase2": ["adverse_events", "safety_endpoints"],
                    "phase3": ["data_monitoring_committee", "stopping_rules"]
                }
            }
        }
        
        if section_name in section_requirements:
            reqs = section_requirements[section_name]
            
            # Check required elements
            for element in reqs.get("required_elements", []):
                if element.lower() not in content.lower():
                    results["issues"].append({
                        "type": "missing_element",
                        "severity": "major",
                        "message": f"Missing required element '{element}' in {section_name}",
                        "suggestion": f"Add {element} to section"
                    })
            
            # Check study type specific requirements
            if study_type and "study_type_specific" in reqs and study_type in reqs["study_type_specific"]:
                for element in reqs["study_type_specific"][study_type]:
                    if element.lower() not in content.lower():
                        results["issues"].append({
                            "type": "missing_element",
                            "severity": "major",
                            "message": f"Missing {study_type}-specific element '{element}' in {section_name}",
                            "suggestion": f"Add {element} as required for {study_type} studies"
                        })

    def _check_duplications(self, sections: Dict[str, str]) -> List[Dict]:
        """Check for excessive duplication between sections"""
        SYNOPSIS_THRESHOLD = 0.8  # Higher threshold for Synopsis
        GENERAL_THRESHOLD = 0.6   # Stricter for other sections
        
        duplication_issues = []
        
        for section1, content1 in sections.items():
            for section2, content2 in sections.items():
                if section1 >= section2:
                    continue
                    
                similarity = self._calculate_similarity(content1, content2)
                threshold = SYNOPSIS_THRESHOLD if "synopsis" in (section1.lower(), section2.lower()) else GENERAL_THRESHOLD
                
                if similarity > threshold:
                    severity = "minor" if "synopsis" in (section1.lower(), section2.lower()) else "major"
                    duplication_issues.append({
                        "type": "duplication",
                        "severity": severity,
                        "message": f"Content similarity {similarity:.1%} between {section1} and {section2}",
                        "suggestion": "Review if duplication is justified" if severity == "minor" else "Consider consolidating information"
                    })
        
        return duplication_issues

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        shorter_len = min(len(words1), len(words2))
        return len(intersection) / shorter_len if shorter_len > 0 else 0

    def _validate_timeline(self, content: str) -> List[Dict]:
        """Validate timeline consistency"""
        timeline_issues = []
        timeline_pattern = r'(\d+)\s*(day|week|month|year)s?\s*(prior to|after|from|to)\s*(\w+)'
        
        def convert_to_days(value: int, unit: str) -> int:
            conversions = {'day': 1, 'week': 7, 'month': 30, 'year': 365}
            return value * conversions[unit.lower()]
        
        # Extract and validate timeline entries
        timeline_items = re.findall(timeline_pattern, content, re.IGNORECASE)
        
        for i in range(len(timeline_items)-1):
            current = convert_to_days(int(timeline_items[i][0]), timeline_items[i][1])
            next_item = convert_to_days(int(timeline_items[i+1][0]), timeline_items[i+1][1])
            
            if current >= next_item:
                timeline_issues.append({
                    "type": "timeline",
                    "severity": "major",
                    "message": f"Timeline inconsistency between {timeline_items[i]} and {timeline_items[i+1]}",
                    "suggestion": "Review timeline sequence and adjust durations"
                })
        
        return timeline_issues

    def _calculate_section_score(self, results: Dict) -> float:
        """Calculate section quality score"""
        base_score = 100
        deductions = {
            "critical": 20,
            "major": 10,
            "minor": 5
        }
        
        # Apply deductions for issues
        for issue in results["issues"]:
            base_score -= deductions[issue["severity"]]
        
        # Add bonuses for good practices
        if not any(i["severity"] == "critical" for i in results["issues"]):
            base_score += 5
        
        if len(results["issues"]) == 0:
            base_score += 10
        
        return max(0, min(100, base_score))

    def _check_placeholders(self, content: str, results: Dict):
        """Check for remaining placeholders in content"""
        placeholder_pattern = r'\[PLACEHOLDER:\s*\*(.*?)\*\]'
        placeholders = re.findall(placeholder_pattern, content)
        
        if placeholders:
            for placeholder in placeholders:
                results["issues"].append({
                    "type": "placeholder",
                    "severity": "major",
                    "message": f"Unresolved placeholder: {placeholder}",
                    "suggestion": f"Replace placeholder with actual content for {placeholder}"
                })

    def _validate_section_completeness(self, section_name: str, content: str, study_type: str, results: Dict):
        """Check section completeness"""
        analysis = self.missing_info_handler.analyze_section_completeness(section_name, content)
        
        if analysis['missing_fields']:
            for field in analysis['missing_fields']:
                results["issues"].append({
                    "type": "missing_field",
                    "severity": "major",
                    "message": f"Missing required field: {field}",
                    "suggestion": self._get_field_prompt(field, study_type)
                })
        
        if analysis['recommendations']:
            for rec in analysis['recommendations']:
                results["suggestions"].append({
                    "type": "improvement",
                    "message": rec,
                    "severity": "minor"
                })

    def _calculate_quality_score(self, analyses: Dict) -> float:
        """Calculate overall quality score based on completeness and recommendations"""
        total_score = 0.0
        total_weight = 0
        
        weights = {
            'background': 1.0,
            'objectives': 1.2,
            'study_design': 1.5,
            'population': 1.2,
            'procedures': 1.0,
            'statistical_analysis': 1.3,
            'safety': 1.4,
            'endpoints': 1.3
        }
        
        for section_name, analysis in analyses.items():
            weight = weights.get(section_name, 1.0)
            score = analysis['completeness_score']
            
            # Reduce score for sections with many missing fields
            if len(analysis['missing_fields']) > 3:
                score *= 0.8
                
            # Adjust score based on recommendations
            if analysis['recommendations']:
                score *= 0.9
                
            total_score += score * weight
            total_weight += weight
            
        if total_weight == 0:
            return 0.0
            
        return round((total_score / total_weight) * 10, 1)  # Score out of 10

    def get_improvement_suggestions(self, section_name: str, analysis: Dict) -> str:
        """Generate improvement suggestions with enhanced formatting"""
        if not analysis['missing_fields'] and not analysis['recommendations']:
            return "✅ Section is complete and well-structured."
        
        suggestions = []
        
        if analysis['missing_fields']:
            suggestions.append("🔍 Required information missing:")
            for field in analysis['missing_fields']:
                suggestions.append(f"• {field.replace('_', ' ').title()}")
                
        if analysis['improvement_suggestions']:
            suggestions.append("\n📝 Specific improvements needed:")
            for suggestion in analysis['improvement_suggestions']:
                suggestions.append(f"• {suggestion}")
                
        if analysis['recommendations']:
            suggestions.append("\n💡 Recommendations for enhancement:")
            for rec in analysis['recommendations']:
                suggestions.append(f"• {rec}")
                
        completeness = analysis['completeness_score'] * 100
        suggestions.append(f"\n📊 Section Completeness: {completeness:.1f}%")
        
        return "\n".join(suggestions)

    def generate_field_prompt(self, field_name: str, section_name: str) -> str:
        """Generate a user-friendly prompt for missing field input"""
        field_prompts = {
            'sample_size': "What is the target sample size for this study?",
            'primary_objective': "What is the primary objective of this study?",
            'duration': "What is the planned duration of the study?",
            'inclusion_criteria': "Please specify the key inclusion criteria:",
            'exclusion_criteria': "Please specify the key exclusion criteria:",
            'primary_endpoints': "What are the primary endpoints of the study?",
            'safety_parameters': "What safety parameters will be monitored?"
        }
        
        return field_prompts.get(
            field_name,
            f"Please provide information about {field_name.replace('_', ' ')}:"
        )