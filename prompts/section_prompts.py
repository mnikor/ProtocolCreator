SECTION_PROMPTS = {
    'background': """
Generate a comprehensive Background and Rationale section based on the following synopsis information:
{synopsis_content}

Required Structure:
1. Disease/Condition Overview (2-3 paragraphs)
   - Current understanding and pathophysiology
   - Epidemiology and disease burden
   - Current treatment landscape
   - Unmet medical needs

2. Product Background (2-3 paragraphs)
   - Mechanism of action
   - Preclinical evidence
   - Clinical experience to date
   - Therapeutic rationale

3. Study Rationale (1-2 paragraphs)
   - Justification for current study
   - Expected benefits
   - Risk-benefit assessment
   - Development program context

Format Requirements:
- Use clear scientific language
- Include relevant references
- Follow ICH guidelines
- Maintain logical flow
""",
    
    'objectives': """
Generate clear Objectives and Endpoints section based on the following synopsis information:
{synopsis_content}

Required Structure:
1. Primary Objective
   - Single, clear statement
   - Specific and measurable
   - Aligned with study phase
   - Clear timeframe

2. Primary Endpoint(s)
   - Direct measure of objective
   - Clear definition
   - Measurement timing
   - Assessment method

3. Secondary Objectives
   - Clear hierarchy
   - Supportive measurements
   - Additional benefits
   - Safety considerations

4. Secondary Endpoints
   - Specific measures
   - Assessment timing
   - Analysis methods
   - Clinical relevance

Format Requirements:
- Numbered format
- Clear and concise statements
- Consistent structure
- Aligned with ICH guidelines
""",
    
    'study_design': """
Generate detailed Study Design section based on the following synopsis information:
{synopsis_content}

Previous sections for context:
{previous_sections}

Required Structure:
1. Overall Design
   - Study type and phase
   - Design characteristics
   - Control type
   - Blinding/masking
   - Randomization
   - Duration

2. Study Schema
   - Study periods
   - Visit schedule
   - Key assessments
   - Decision points

3. Study Population
   - Key eligibility criteria
   - Sample size
   - Recruitment approach
   - Stratification

4. Treatment Groups
   - Intervention details
   - Dosing regimen
   - Treatment duration
   - Comparative groups

Format Requirements:
- Include study schema
- Clear timelines
- Logical organization
- ICH compliance
""",

    'statistical_considerations': """
Generate comprehensive Statistical Considerations section based on the following synopsis information:
{synopsis_content}

Required Structure:
1. Sample Size Determination
   - Primary endpoint basis
   - Effect size assumptions
   - Power calculations
   - Adjustment factors

2. Analysis Populations
   - Definition of analysis sets
   - Handling missing data
   - Protocol deviations
   - Subgroup analyses

3. Statistical Methods
   - Primary analysis
   - Secondary analyses
   - Interim analyses
   - Multiple testing
   - Safety analyses

4. Study Success Criteria
   - Primary endpoint
   - Key secondary endpoints
   - Interim analyses
   - Stopping rules

Format Requirements:
- Clear statistical methods
- Justified assumptions
- ICH alignment
- Detailed procedures
"""
}
