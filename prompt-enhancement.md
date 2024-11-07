# Protocol Generation Prompt Analysis & Improvements

## Current Strengths
1. Good basic structure for all study types
2. Clear section organization
3. Basic study type considerations

## Areas Needing Enhancement

### 1. Study Type-Specific Thinking Process
```markdown
Add to General Instructions:

Think through study type requirements:

1. For Clinical Trials:
   Consider:
   - Phase-specific requirements
   - Regulatory guidance
   - Quality standards
   - Safety monitoring needs

2. For RWE Studies:
   Consider:
   - Data source quality
   - Variable definitions
   - Bias control
   - Generalizability

3. For Systematic Reviews:
   Consider:
   - Search methodology
   - Quality assessment
   - Evidence synthesis
   - Bias evaluation

4. For Patient Registries:
   Consider:
   - Data collection standards
   - Quality control measures
   - Long-term follow-up
   - Real-world evidence generation
```

### 2. Enhanced Statistical Section
```markdown
Add study-specific statistical considerations:

1. Clinical Trials
   Think through:
   - Power calculations
   - Sample size justification
   - Interim analyses
   - Missing data handling

2. RWE Studies
   Think through:
   - Confounding control
   - Propensity scoring
   - Sensitivity analyses
   - Time-varying effects

3. Systematic Reviews
   Think through:
   - Meta-analysis methods
   - Heterogeneity assessment
   - Publication bias
   - Subgroup analyses

4. Patient Registries
   Think through:
   - Descriptive statistics
   - Time-to-event analyses
   - Quality indicators
   - Missing data patterns
```

### 3. Enhanced Quality Control Framework
```markdown
Add study-specific quality measures:

1. Clinical Trials
   Quality Focus:
   - GCP compliance
   - Data validation
   - Site monitoring
   - Training requirements

2. RWE Studies
   Quality Focus:
   - Data source validation
   - Code list validation
   - Variable definitions
   - Database quality

3. Systematic Reviews
   Quality Focus:
   - Search documentation
   - Selection process
   - Data extraction
   - Quality assessment

4. Patient Registries
   Quality Focus:
   - Data completeness
   - Consistency checks
   - Follow-up rates
   - Data validation
```

### 4. Validity Considerations
```markdown
Add study-specific validity requirements:

1. Internal Validity
   For Clinical Trials:
   - Randomization
   - Blinding
   - Protocol compliance
   - Standardization

   For RWE:
   - Confounding control
   - Selection bias
   - Information bias
   - Missing data

   For Systematic Reviews:
   - Search completeness
   - Selection criteria
   - Quality assessment
   - Data extraction

2. External Validity
   For Clinical Trials:
   - Population representation
   - Setting applicability
   - Clinical relevance
   - Implementation

   For RWE:
   - Database coverage
   - Population characteristics
   - Practice patterns
   - Coding accuracy

   For Systematic Reviews:
   - Question relevance
   - Evidence applicability
   - Setting variation
   - Population coverage
```

### 5. Chain of Thought Elements
```markdown
Add to each section:

1. Think Through Process
   - What are key considerations for this study type?
   - What are potential validity threats?
   - What quality measures are needed?
   - What documentation is required?

2. Design Decisions
   - What design elements are critical?
   - How to ensure quality?
   - What standardization is needed?
   - What monitoring is required?

3. Implementation Planning
   - What resources are needed?
   - What training is required?
   - What documentation is necessary?
   - How to ensure compliance?
```

## Implementation Strategy

1. **Update Base Prompts**
```markdown
Modify each section prompt to:
- Include study type-specific considerations
- Add chain of thought elements
- Include validity checks
- Specify quality requirements
```

2. **Add Cross-References**
```markdown
Include references to:
- Related sections
- Quality requirements
- Validation needs
- Documentation standards
```

3. **Quality Framework**
```markdown
Add quality considerations for:
- Study design elements
- Data collection
- Analysis methods
- Documentation
```

## Recommendations

1. **Immediate Updates**
- Add study type-specific thinking process
- Include validity considerations
- Enhance quality requirements
- Add chain of thought elements

2. **Secondary Improvements**
- Expand cross-references
- Add implementation guidance
- Enhance documentation requirements
- Include validation checks

The goal is to make prompts that guide thorough, well-reasoned protocol development across all study types while maintaining flexibility and ensuring appropriate rigor for each type.