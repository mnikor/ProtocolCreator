SECTION_PROMPTS = {
    'background': """
Generate the Background and Rationale section based on the following synopsis information:
{synopsis_content}

Include:
1. Disease/Condition background
2. Current therapeutic landscape
3. Study drug/intervention background
4. Study rationale
    """,
    
    'objectives': """
Generate the Objectives and Endpoints section based on the following synopsis information:
{synopsis_content}

Include:
1. Primary objective and endpoint
2. Secondary objectives and endpoints
3. Exploratory objectives (if applicable)
    """,
    
    'study_design': """
Generate the Study Design section based on the following synopsis information:
{synopsis_content}

Previous sections for context:
{previous_sections}

Include:
1. Overall design description
2. Study population
3. Treatment groups
4. Study procedures overview
    """
}
