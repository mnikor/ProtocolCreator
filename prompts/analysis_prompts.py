SYNOPSIS_ANALYSIS_PROMPT = '''
Analyze the following synopsis thoroughly and provide a complete structured output. For any missing or unclear information, explicitly state 'Not specified' or 'None' - do not leave any fields empty. If information is missing, provide a detailed explanation in the Missing Information section.

=== STUDY TYPE AND DESIGN ===
Primary Classification: [classification or 'Not specified']
Design Type: [type or 'Not specified']
Phase: [phase or 'Not specified']
Key Features:
- [feature 1 or 'None if no features identified']

=== CRITICAL PARAMETERS ===
Population: [description or 'Not specified']
Intervention: [description or 'Not specified']
Control/Comparator: [description or 'Not specified']
Primary Endpoint: [description or 'Not specified']
Secondary Endpoints:
- [endpoint or 'None if no secondary endpoints']

=== REQUIRED SECTIONS ===
- [List ALL required protocol sections based on study type]
- [Must include standard ICH/GCP required sections]
- [Include any additional sections based on study design]

=== MISSING INFORMATION ===
- [List each missing element with explanation]
- [Identify critical gaps that need addressing]
- [Suggest additional information needed]

Synopsis to analyze:
{synopsis_text}
'''
