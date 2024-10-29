SYNOPSIS_ANALYSIS_PROMPT = '''
Analyze the following synopsis and provide structured output following this exact format:

=== STUDY TYPE AND DESIGN ===
Primary Classification: [classification]
Design Type: [type]
Phase: [phase]
Key Features:
- [feature 1]
- [feature 2]

=== CRITICAL PARAMETERS ===
Population: [description]
Intervention: [description]
Control/Comparator: [description]
Primary Endpoint: [description]
Secondary Endpoints:
- [endpoint 1]
- [endpoint 2]

=== REQUIRED SECTIONS ===
- [section 1]
- [section 2]

=== MISSING INFORMATION ===
- [missing item 1]
- [missing item 2]

Synopsis to analyze:
{synopsis_text}
'''
