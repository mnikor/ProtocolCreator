# Protocol Generation Prompt System

## Initial Synopsis Analysis Prompt
```plaintext
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
```

## Section Generation Master Prompt
```plaintext
You are an expert medical writer developing a protocol section based on synopsis information. Follow these principles:
- Maintain scientific accuracy and regulatory compliance
- Use clear, precise language
- Follow ICH/GCP guidelines
- Ensure internal consistency
- Support operational implementation

Synopsis Information:
{synopsis_content}

Previous Sections Generated:
{previous_sections}

Generate the {section_name} section following:
1. Required content elements for this section
2. Appropriate detail level for protocol
3. Cross-references to other sections
4. Proper formatting and structure
5. Standard protocol language
```

## Section-Specific Prompts

### 1. Background & Rationale
```plaintext
Using the synopsis background information, create a comprehensive protocol background section that:

Structure Requirements:
1. Disease/Condition (1-2 paragraphs)
   - Current understanding
   - Epidemiology
   - Burden of disease

2. Current Therapies (1-2 paragraphs)
   - Treatment landscape
   - Unmet needs
   - Treatment challenges

3. Product Background (1-2 paragraphs)
   - Mechanism of action
   - Current evidence
   - Development rationale

4. Benefit/Risk (1 paragraph)
   - Potential benefits
   - Known/potential risks
   - Benefit-risk assessment

Format Requirements:
- Use proper citation markers [X]
- Include relevant guidelines
- Reference key studies
- Maintain scientific tone

Synopsis Information:
{synopsis_background}
```

### 2. Objectives and Endpoints
```plaintext
Based on the synopsis objectives, create a structured protocol objectives section that:

Required Structure:
1. Primary Objective
   - Single clear statement
   - Linked to primary endpoint
   - Measurable outcome
   - Clear timepoint

2. Secondary Objectives
   - Clear hierarchy
   - Linked to endpoints
   - Measurable outcomes
   - Defined timepoints

3. Exploratory Objectives (if applicable)
   - Clear separation from key objectives
   - Appropriate scope
   - Future implications

Format Requirements:
- Use consistent verb forms
- Include clear measurements
- Specify timepoints
- Maintain parallel structure

Synopsis Information:
{synopsis_objectives}
```

### 3. Study Design
```plaintext
Transform the synopsis design information into a detailed protocol study design section:

Required Elements:
1. Overall Design
   - Study type/phase
   - Design characteristics
   - Duration/periods
   - Population size

2. Scientific Rationale
   - Design choice justification
   - Control selection
   - Duration justification
   - Endpoint timing

3. Design Diagram
   - Study periods
   - Treatment arms
   - Decision points
   - Assessment timing

Format Requirements:
- Include schematic diagram
- Use clear timepoints
- Detail study periods
- Specify visits/assessments

Synopsis Information:
{synopsis_design}
```

### 4. Statistical Considerations
```plaintext
Expand the synopsis statistical information into a comprehensive statistical section:

Required Elements:
1. Sample Size
   - Primary calculation
   - Assumptions
   - Power justification
   - Adjustments

2. Analysis Sets
   - Clear definitions
   - Population criteria
   - Handling rules

3. Analysis Methods
   - Primary analysis
   - Secondary analyses
   - Missing data
   - Interim analyses

Format Requirements:
- Include tables where appropriate
- Specify statistical tests
- Detail assumptions
- Define significance levels

Synopsis Information:
{synopsis_statistics}
```

## Quality Check Prompt
```plaintext
Review the generated protocol section for:

1. Content Completeness
   - Required elements
   - Appropriate detail
   - Scientific accuracy
   - Regulatory compliance

2. Format Compliance
   - Section structure
   - Numbering system
   - Table formatting
   - Cross-references

3. Consistency Check
   - Terminology
   - Cross-references
   - Scientific content
   - Methods description

4. Language Quality
   - Scientific tone
   - Clear expression
   - Grammar/spelling
   - Protocol conventions

Section for Review:
{generated_section}

Previous Sections:
{previous_sections}
```

Would you like me to:
1. Add more section-specific prompts?
2. Provide prompt variations for different study types?
3. Include format-specific prompts?
4. Add validation prompts?

These prompts ensure:
- Consistent content generation
- Appropriate detail level
- Regulatory compliance
- Internal consistency
- Professional quality