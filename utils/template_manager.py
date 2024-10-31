import os
import json
import logging

logger = logging.getLogger(__name__)

class TemplateManager:
    def __init__(self):
        self.templates = {}
        self.template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self._load_templates()
    
    def _load_templates(self):
        '''Load all templates from template directory'''
        try:
            for phase_dir in os.listdir(self.template_dir):
                phase_path = os.path.join(self.template_dir, phase_dir)
                if os.path.isdir(phase_path):
                    self.templates[phase_dir] = {}
                    for template_file in os.listdir(phase_path):
                        if template_file.endswith('.json'):
                            section_name = template_file[:-5]
                            with open(os.path.join(phase_path, template_file)) as f:
                                self.templates[phase_dir][section_name] = json.load(f)
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            raise

    def get_template(self, study_type):
        '''Get template for specific study type'''
        return self.templates.get(study_type, {})
    
    def get_section_template(self, study_type, section_name):
        '''Get template for specific section'''
        return self.templates.get(study_type, {}).get(section_name, {})
    
    def get_template_types(self):
        '''Get list of available template types'''
        return list(self.templates.keys())
