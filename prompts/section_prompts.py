"""
Improved prompts for protocol sections with better formatting guidelines
"""

SECTION_PROMPTS = {
    'background': """
You are a medical writer generating the Background section of a clinical protocol. Based on this synopsis:

{synopsis_content}

Generate a Background section following these strict rules:
1. Use one single # for the main heading (no repeating headers)
2. Use ## for subsections only
3. Format each subsection in clear paragraphs
4. Required subsections:
   - Disease Background
   - Current Treatment Landscape
   - Product Background
   - Study Rationale
5. No markdown formatting or special characters
6. No bullet points - use proper paragraphs
7. No numbered lists in this section

Format example:
# Background

## Disease Background
[Clear paragraph about disease]

## Current Treatment Landscape
[Clear paragraph about treatments]

[etc.]

Previously generated sections if available:
{previous_sections}
""",

    'objectives': """
You are a medical writer generating the Objectives section of a clinical protocol. Based on this synopsis:

{synopsis_content}

Generate an Objectives section following these strict rules:
1. Use single # for main heading
2. Use ## for subsections
3. Format objectives and endpoints as follows:
   - Primary Objective(s)
   - Primary Endpoint(s)
   - Secondary Objectives
   - Secondary Endpoints
4. Number each objective and endpoint clearly (1., 2., etc.)
5. No bullet points - use numbered lists
6. No markdown formatting
7. Ensure clear alignment between objectives and endpoints

Format example:
# Objectives

## Primary Objective(s)
1. [First objective]
2. [Second objective]

[etc.]

Previously generated sections if available:
{previous_sections}
""",

    'study_design': """
You are a medical writer generating the Study Design section of a clinical protocol. Based on this synopsis:

{synopsis_content}

Generate a Study Design section following these strict rules:
1. Use single # for main heading
2. Use ## for subsections
3. Include these subsections:
   - Overall Design
   - Study Schema
   - Study Duration
   - Treatment Groups
4. For tables, use this exact format:
   | Header 1 | Header 2 | Header 3 |
   |----------|----------|----------|
   | Cell 1   | Cell 2   | Cell 3   |
5. No markdown formatting
6. Use clear paragraphs for text
7. Number items only when specifically listing steps or procedures

Format example:
# Study Design

## Overall Design
[Clear paragraph describing design]

[etc.]

Previously generated sections if available:
{previous_sections}
""",

    'population': """
You are a medical writer generating the Study Population section of a clinical protocol. Based on this synopsis:
{synopsis_content}
Generate a Population section following these rules:
1. Use clear heading structure
2. Include these components:
   - Overview of Study Population
   - Inclusion Criteria (numbered list)
   - Exclusion Criteria (numbered list)
   - Withdrawal Criteria
   - Replacement Policy
3. Format consistently with no markdown or escape characters
4. Use clear numbering for criteria
5. Group related criteria logically
6. Include specific measurements and timeframes
7. Define all medical terms used
Previously generated sections if available:
{previous_sections}
""",

    'procedures': """
You are a medical writer generating the Study Procedures section of a clinical protocol. Based on this synopsis:
{synopsis_content}
Generate a Study Procedures section following these rules:
1. Use clear heading structure (## for sections)
2. Include these components:
   - Study Procedures Overview
   - Screening/Baseline Procedures
   - Treatment Phase Procedures
   - Follow-up Procedures
   - Safety Assessments
   - Efficacy Assessments
   - Laboratory Assessments
   - Other Assessments
3. Each procedure should include:
   - Clear timing
   - Specific requirements
   - Responsible personnel
4. Format all lists consistently
5. No markdown or escape characters
6. Use consistent terminology
7. Include any special handling instructions
Previously generated sections if available:
{previous_sections}
""",

    'statistical': """
You are a medical writer generating the Statistical Analysis section of a clinical protocol. Based on this synopsis:
{synopsis_content}
Generate a Statistical Analysis section following these rules:
1. Use clear heading structure
2. Include these components:
   - Statistical Hypotheses
   - Sample Size Determination
   - Analysis Populations
   - Statistical Methods
   - Interim Analyses
   - Missing Data Handling
3. Format consistently without markdown
4. Include specific statistical tests
5. Define significance levels
6. Describe analysis sets clearly
7. Include multiplicity adjustments
Previously generated sections if available:
{previous_sections}
""",

    'safety': """
You are a medical writer generating the Safety section of a clinical protocol. Based on this synopsis:
{synopsis_content}
Generate a Safety section following these rules:
1. Use clear heading structure
2. Include these components:
   - Safety Parameters
   - Adverse Event Definitions
   - Adverse Event Reporting
   - Safety Monitoring
   - Risk Management
   - Data Monitoring Committee
   - Stopping Rules
3. Format consistently
4. Include reporting timeframes
5. Define severity grades
6. Specify reporting requirements
7. Include safety oversight procedures
Previously generated sections if available:
{previous_sections}
"""
}