"""
Complete set of prompts for all protocol sections
"""

SECTION_PROMPTS = {
    'background': """
You are a medical writer generating the Background section of a clinical protocol. Based on this synopsis:
{synopsis_content}
Generate a Background section following these rules:
1. Use proper heading structure (single # for main heading, ## for subsections)
2. Do not include escape characters or markdown formatting
3. Format should be clean and consistent
4. Include these subsections:
   - Disease Background
   - Current Treatment Landscape
   - Product Background
   - Study Rationale
5. Keep references for a separate References section
6. Use clear paragraph breaks
7. Format numbers and statistics consistently
Previously generated sections if available:
{previous_sections}
""",

    'objectives': """
You are a medical writer generating the Objectives section of a clinical protocol. Based on this synopsis:
{synopsis_content}
Generate an Objectives section following these rules:
1. Use clear numbering for objectives and endpoints
2. Format consistently with:
   - Primary Objective(s)
   - Primary Endpoint(s)
   - Secondary Objectives
   - Secondary Endpoints
3. Each objective should align with specific endpoints
4. Use proper heading levels
5. Keep formatting clean without markdown or escape characters
6. Use consistent terminology
7. Include clear measurements and timeframes
Previously generated sections if available:
{previous_sections}
""",

    'study_design': """
You are a medical writer generating the Study Design section of a clinical protocol. Based on this synopsis:
{synopsis_content}
Generate a Study Design section following these rules:
1. Use clear heading structure
2. Include these components:
   - Overall Design
   - Study Schema
   - Study Duration
   - Treatment Groups
   - Study Procedures
3. Format all lists and tables consistently
4. No markdown formatting or escape characters
5. Include a clear Schedule of Assessments table
6. Use consistent terminology throughout
7. Detail timing of assessments and procedures clearly
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