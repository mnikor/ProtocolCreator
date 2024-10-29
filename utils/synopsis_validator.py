import re
from utils.gpt_handler import GPTHandler

def validate_synopsis(content):
    """Validate synopsis structure and content"""
    required_sections = [
        'background',
        'objectives',
        'study design',
        'population',
        'endpoints',
        'statistical considerations'
    ]
    
    missing_sections = []
    warnings = []
    
    # Basic structure validation
    for section in required_sections:
        if not re.search(rf'\b{section}\b', content.lower()):
            missing_sections.append(section)
    
    # Use GPT for detailed analysis
    try:
        gpt_handler = GPTHandler()
        detailed_analysis = gpt_handler.analyze_synopsis(content)
        
        return {
            'is_valid': len(missing_sections) == 0,
            'missing_sections': missing_sections,
            'warnings': warnings,
            'detailed_analysis': detailed_analysis
        }
    except Exception as e:
        raise Exception(f"Error validating synopsis: {str(e)}")
