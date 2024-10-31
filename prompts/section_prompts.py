"""
Protocol section prompts with improved formatting guidelines
"""

SECTION_PROMPTS = {
    'background': """
You are writing the Background section of a clinical protocol. Start directly with a clear heading structure:

# Background

## Disease Background
[Write disease background without introductory phrases]

## Current Treatment Landscape
[Write treatment landscape without meta-commentary]

## Product Background
[Write product background directly]

## Study Rationale
[Write study rationale directly]

Rules:
1. No introductory phrases or meta-commentary
2. No markdown formatting or special characters
3. Use clear paragraphs
4. Start each subsection directly with content

Context:
{synopsis_content}

Previously generated sections:
{previous_sections}
""",

    'objectives': """
You are writing the Objectives section of a clinical protocol. Use this structure:

# Objectives

## Primary Objective(s)
1. [First objective]
2. [Second objective]

## Primary Endpoint(s)
1. [First endpoint]
2. [Second endpoint]

## Secondary Objectives
1. [First objective]
2. [Second objective]

## Secondary Endpoints
1. [First endpoint]
2. [Second endpoint]

Rules:
1. Start each objective/endpoint directly
2. Use clear numbering
3. No introductory text
4. Align endpoints with objectives

Context:
{synopsis_content}

Previously generated sections:
{previous_sections}
""",

    'study_design': """
You are writing the Study Design section of a clinical protocol. Use this structure:

# Study Design

## Overall Design
[Write design overview directly]

## Study Schema
[Include clear study diagram]

## Study Duration
[Specify duration details]

## Treatment Groups
[List treatment groups]

Rules:
1. No introductory phrases
2. Use clear headings
3. Include specific details
4. No meta-commentary

Context:
{synopsis_content}

Previously generated sections:
{previous_sections}
""",

    'population': """
You are writing the Study Population section. Use this structure:

# Study Population

## Overview
[Population description]

## Inclusion Criteria
1. [First criterion]
2. [Second criterion]

## Exclusion Criteria
1. [First criterion]
2. [Second criterion]

## Withdrawal Criteria
[Withdrawal conditions]

Rules:
1. Start each section directly with content
2. Use clear numbering for criteria
3. No introductory phrases
4. Include specific measurements

Context:
{synopsis_content}

Previously generated sections:
{previous_sections}
""",

    'statistical': """
You are writing the Statistical Analysis section. Use this structure:

# Statistical Analysis

## Statistical Hypotheses
[State hypotheses directly]

## Sample Size
[Sample size calculation]

## Analysis Populations
[Define populations]

## Statistical Methods
[Detail methods]

Rules:
1. Start each section directly
2. Include specific tests
3. No meta-commentary
4. Use clear paragraphs

Context:
{synopsis_content}

Previously generated sections:
{previous_sections}
""",

    'safety': """
You are writing the Safety section. Use this structure:

# Safety

## Safety Parameters
[List parameters]

## Adverse Events
[Define and classify]

## Safety Monitoring
[Describe procedures]

## Risk Management
[Detail strategies]

Rules:
1. Start directly with content
2. Include specific details
3. No introductory phrases
4. Use clear paragraphs

Context:
{synopsis_content}

Previously generated sections:
{previous_sections}
"""
}
