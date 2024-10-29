SYNOPSIS_ANALYSIS_PROMPT = """
You are an expert medical writer analyzing a clinical study synopsis. Your task is to:
1. Identify study type and key design elements
2. Extract critical parameters
3. Determine required protocol sections
4. Identify missing essential information

Review the provided synopsis and output a structured analysis:
{synopsis_text}

Required Output Format:
1. Study Type & Design:
   - Primary classification
   - Design type
   - Phase (if applicable)
   - Key features

2. Critical Parameters:
   - Population
   - Intervention
   - Control/Comparator
   - Primary endpoint
   - Key secondary endpoints

3. Required Protocol Sections:
   [List specific sections needed based on study type]

4. Missing Information:
   [List any essential elements not found in synopsis]
"""
