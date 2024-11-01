"""Protocol section prompts configuration"""

SECTION_PROMPTS = {
    'background': """
Generate the Background section following this structure:

## Disease Background
[Disease overview and epidemiology]

## Current Treatment Landscape
[Available treatments and unmet needs]

## Product Background
[Investigational product details]

## Study Rationale
[Justification for the study]

Context:
{synopsis_content}

Previously generated sections:
{previous_sections}
""",

    'objectives': """
Generate the Objectives section following this structure:

## Primary Objective(s)
1. [First objective]
2. [Second objective if applicable]

## Primary Endpoint(s)
1. [First endpoint]
2. [Second endpoint if applicable]

## Secondary Objectives
1. [First objective]
2. [Second objective]

## Secondary Endpoints
1. [First endpoint]
2. [Second endpoint]

Context:
{synopsis_content}

Previously generated sections:
{previous_sections}
""",

    'study_design': """
Generate the Study Design section following this structure:

## Overall Design
[Study design overview]

## Study Schema
[Visual representation of study flow]

## Treatment Groups
[Description of treatment arms]

## Study Duration
[Timeline and key periods]

Context:
{synopsis_content}

Previously generated sections:
{previous_sections}
"""
}

def get_section_prompt(section_name: str, study_type: str) -> str:
    """Get appropriate prompt for section and study type"""
    base_prompt = SECTION_PROMPTS.get(section_name, "")
    return base_prompt
