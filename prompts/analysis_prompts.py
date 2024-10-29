SYNOPSIS_ANALYSIS_PROMPT = '''
You are a protocol analysis assistant. Analyze the synopsis thoroughly and provide a complete structured output. For any missing or unclear information, explicitly state 'Not specified' or 'None' - do not leave any fields empty. If information is missing, provide a detailed explanation in the Missing Information section.

=== STUDY TYPE AND DESIGN ===
Primary Classification: [classification or 'Not specified']
Design Type: [type or 'Not specified']
Phase: [phase or 'Not specified']
Key Features:
- [List specific design features. If none, state 'None specified']
- [Examples: randomization, blinding, control type, etc.]

=== CRITICAL PARAMETERS ===
Population: [Clear description of study population or 'Not specified']
Intervention: [Details of study intervention or 'Not specified']
Control/Comparator: [REQUIRED - Details of control/comparator or 'Not specified']
Primary Endpoint: [REQUIRED - Clear description of primary endpoint or 'Not specified']
Secondary Endpoints:
- [List each endpoint. If none, state 'None specified']
- [Must explain if no secondary endpoints are provided]

=== REQUIRED SECTIONS ===
The following sections are mandatory and must be present:
- Background and Rationale [REQUIRED]
- Objectives and Endpoints [REQUIRED]
- Study Design [REQUIRED]
- Statistical Considerations [REQUIRED]
- Study Population [REQUIRED]
[List additional required sections based on study type]

=== MISSING INFORMATION ===
Provide detailed feedback for:
- Missing mandatory sections with explanations
- Incomplete critical parameters
- Required content not found in synopsis
- Suggested additions for completeness

For each missing item, explain:
1. Why it is required
2. Impact on protocol development
3. Suggested information to request

Synopsis to analyze:
{synopsis_text}

Note: Your analysis must explicitly identify all missing or unclear information. Do not assume missing information can be filled in later without noting it as missing.
'''
