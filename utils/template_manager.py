from typing import Dict, List
import json

class TemplateManager:
    def __init__(self):
        self.templates = {
            'phase1': {
                'name': 'Phase 1 Study',
                'sections': {
                    'background': 'templates/phase1/background.json',
                    'objectives': 'templates/phase1/objectives.json',
                    'study_design': 'templates/phase1/study_design.json',
                    'population': 'templates/phase1/population.json',
                    'procedures': 'templates/phase1/procedures.json',
                    'statistical': 'templates/phase1/statistical.json',
                    'safety': 'templates/phase1/safety.json'
                }
            },
            'phase2': {
                'name': 'Phase 2 Study',
                'sections': {
                    'background': 'templates/phase2/background.json',
                    'objectives': 'templates/phase2/objectives.json',
                    'study_design': 'templates/phase2/study_design.json',
                    'population': 'templates/phase2/population.json',
                    'procedures': 'templates/phase2/procedures.json',
                    'statistical': 'templates/phase2/statistical.json',
                    'safety': 'templates/phase2/safety.json'
                }
            },
            'phase3': {
                'name': 'Phase 3 Study',
                'sections': {
                    'background': 'templates/phase3/background.json',
                    'objectives': 'templates/phase3/objectives.json',
                    'study_design': 'templates/phase3/study_design.json',
                    'population': 'templates/phase3/population.json',
                    'procedures': 'templates/phase3/procedures.json',
                    'statistical': 'templates/phase3/statistical.json',
                    'safety': 'templates/phase3/safety.json'
                }
            }
        }

    def get_template_types(self) -> List[str]:
        """Get list of available template types"""
        return list(self.templates.keys())

    def get_template(self, template_type: str) -> Dict:
        """Get specific template configuration"""
        if template_type not in self.templates:
            raise ValueError(f"Template type {template_type} not found")
        return self.templates[template_type]

    def get_section_template(self, template_type: str, section: str) -> Dict:
        """Get template for specific section"""
        template = self.get_template(template_type)
        section_path = template['sections'].get(section)
        if not section_path:
            raise ValueError(f"Section {section} not found in template {template_type}")
            
        try:
            with open(section_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {section_path}")
