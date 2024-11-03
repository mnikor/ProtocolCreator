
SECTION_PROMPTS = {
    # Title
    "title": """
    Generate a descriptive Title for the study. This should clearly indicate:
    - Study focus (e.g., intervention, condition)
    - Phase of the study (if applicable)
    - Population or key demographics
    - If title specifics are missing, use *[PLACEHOLDER: Confirm study title]*.

    # Example Output:
    """
    [PLACEHOLDER: *Confirm study title and include intervention and target population*].
    """

    *Validate the title for clarity and alignment with the study objectives.*
    """,

    # Background
    "background": """
    Generate a comprehensive Background section with clinical context, treatment landscape, and study rationale based on the provided synopsis. Follow document guidelines for clarity and conciseness.

    1. **Disease Background**:
       - Describe disease prevalence, impact, and unmet needs. If prevalence data or historical treatment details are missing, insert *[PLACEHOLDER: Insert disease-specific statistics]*.
       - Avoid marketing language; use "commonly used treatments" rather than "groundbreaking treatments."

    2. **Current Treatment Landscape**:
       - Outline current treatment options, limitations, and how this study addresses unmet needs. If details on treatment limitations are missing, add *[PLACEHOLDER: Confirm treatment landscape details]*.

    3. **Study Rationale**:
       - Explain why the chosen population, study design, and interventions are appropriate. Include justification for any specific patient demographics or exclusion criteria if relevant.
       - If rationale details are absent, add *[PLACEHOLDER: Provide rationale for study population selection and study design]*.

    4. **Formatting and Presentation**:
       - Use headers for subtopics and avoid introductory language. Aim for varied sentence structure to prevent repetitive phrasing.

    # Example Output:
    """
    [PLACEHOLDER: *Insert disease-specific statistics for incidence and prevalence*].
    [SUGGESTED CONTENT: *Describe the limitations of current treatment approaches and validate with recent studies*].
    """

    *Validate any placeholders with relevant literature or study-specific data.*
    """,

    # Objectives
    "objectives": """
    Generate the Objectives section, ensuring primary and secondary objectives are clearly aligned with endpoints. If objectives are missing, include placeholders with validation recommendations.

    1. **Primary Objective(s)**:
       - Define the primary focus, e.g., "Evaluate safety of [study intervention] in [population]." Use *[PLACEHOLDER: Define primary objective(s)]* if specific objectives are not provided.

    2. **Secondary Objective(s)**:
       - Add secondary outcomes of interest (e.g., biomarker responses, QoL measures). If absent, include *[PLACEHOLDER: Confirm secondary objectives]*.

    3. **Endpoints and Hypothesis**:
       - List endpoints in a table format for clarity, including the objectives and the measurement methods.

    # Example Output:
    """
    [PLACEHOLDER: *Confirm primary objective, such as overall survival or progression-free survival*].
    [SUGGESTED CONTENT: *Secondary objectives might include quality of life or biomarker measures; validate with study scope*].
    """

    *Validate placeholders to ensure objectives are specific and align with study scope.*
    """,

    # Study Design
    "study_design": """
    Describe the Study Design based on the provided synopsis and document standards. Include rationale for design elements and follow specific formatting instructions.

    1. **Overall Design**:
       - Provide a high-level overview (e.g., double-blind, randomized) and include details like intervention assignment methods and blinding. If not specified, use *[PLACEHOLDER: Confirm overall study design details]*.

    2. **Intervention Groups**:
       - Define each intervention arm, dose, and administration details. Insert *[PLACEHOLDER: Describe intervention groups and dose details]* if missing.

    3. **Study Duration**:
       - Specify the length of each study phase. If unclear, use *[PLACEHOLDER: Specify study duration for each phase]*.

    4. **Study Schema**:
       - Include a schematic diagram showing study phases if feasible.

    # Example Output:
    """
    [PLACEHOLDER: *Define study blinding method (e.g., single-blind, double-blind)*].
    [SUGGESTED CONTENT: *Summarize intervention groups and validate duration with study timeline*].
    """

    *Validate placeholders with study coordinators for comprehensive detail.*
    """,

    # Population
    "population": """
    Generate the Population section including key demographic details, eligibility, and sample size. If specifics are missing, use placeholders.

    1. **Inclusion Criteria**:
       - Detail the requirements for participant eligibility (e.g., age, disease status). Use *[PLACEHOLDER: Confirm inclusion criteria]* if incomplete.

    2. **Exclusion Criteria**:
       - Define exclusion factors to avoid potential confounders. Insert *[PLACEHOLDER: Confirm exclusion criteria]* if needed.

    3. **Sample Size Justification**:
       - Explain the sample size calculation or rationale, using *[PLACEHOLDER: Provide sample size details]* if information is missing.

    # Example Output:
    """
    [PLACEHOLDER: *List inclusion/exclusion criteria relevant to the study population*].
    [SUGGESTED CONTENT: *Provide a justification for sample size based on study endpoints*].
    """

    *Review placeholders for accuracy and alignment with study scope.*
    """,

    # Procedures
    "procedures": """
    Detail study procedures including assessments, treatment administration, and follow-up based on protocol requirements.

    1. **Screening Procedures**:
       - Outline screening assessments and initial evaluations. Use *[PLACEHOLDER: Specify screening procedures]* if missing.

    2. **Treatment Administration**:
       - Describe how the intervention will be administered, including frequency and dosage. Insert *[PLACEHOLDER: Describe treatment procedures]* if not provided.

    3. **Follow-up Procedures**:
       - Specify follow-up schedule and assessments. If unclear, add *[PLACEHOLDER: Confirm follow-up procedures]*.

    # Example Output:
    """
    [PLACEHOLDER: *List screening procedures and follow-up intervals*].
    [SUGGESTED CONTENT: *Provide specifics on treatment administration and follow-up assessments*].
    """

    *Validate each placeholder with study design requirements for accuracy.*
    """,

    # Statistical Analysis Plan
    "statistical_analysis": """
    Generate a detailed Statistical Analysis Plan in line with study objectives. Use placeholders for missing methods or sample size calculations and provide recommendations for validation.

    1. **Primary Analysis**:
       - Specify primary statistical methods (e.g., Cox regression for survival analysis). If these are missing, add *[PLACEHOLDER: Confirm primary analysis method]*.

    2. **Sample Size Calculation**:
       - Specify sample size and power calculations. If not provided, add *[PLACEHOLDER: Insert sample size details]*.

    # Example Output:
    """
    [PLACEHOLDER: *Specify statistical methods like Cox regression or Kaplan-Meier analysis*].
    [SUGGESTED CONTENT: *Include sample size and power calculation details; validate with a statistician*].
    """

    *Validate placeholders with a biostatistician to ensure methodological rigor.*
    """,

    # Safety and Risk Management
    "safety": """
    Generate a detailed Safety and Risk Management section for the protocol, focusing on regular monitoring, adverse event reporting, and adherence to ICH E6 guidelines.

    1. **Vital Signs and Clinical Assessments**:
       - Specify measurements (e.g., heart rate, blood pressure) and assessment schedules based on the synopsis. If any timing or frequency details are missing, insert *[PLACEHOLDER: Define schedule for specific vital sign assessments]*.

    2. **Adverse Events and Serious Adverse Events (SAEs)**:
       - Describe the AE and SAE capture process, including specific reporting timelines and follow-up procedures. If these details are missing, add *[PLACEHOLDER: Confirm AE and SAE reporting protocols]*.

    # Example Output:
    """
    [PLACEHOLDER: *Specify timelines for SAE reporting and monitoring*].
    [SUGGESTED CONTENT: *Detail adverse event monitoring according to ICH guidelines*].
    """

    *Please validate any placeholders to ensure that this Safety section meets study-specific and regulatory requirements.*
    """,

    # Ethical Considerations
    "ethical_considerations": """
    Create an Ethical Considerations section covering:

    1. **Regulatory Compliance**:
       - Outline adherence to Good Clinical Practice (GCP) and applicable regulations.

    2. **Informed Consent**:
       - Describe the informed consent process, including information shared with participants.

    3. **Data Privacy**:
       - Mention measures for data confidentiality and participant privacy.

    If any details are not specified, add *[PLACEHOLDER: Confirm ethical considerations]*.

    # Example Output:
    """
    [PLACEHOLDER: *Confirm GCP and informed consent requirements*].
    [SUGGESTED CONTENT: *Detail participant rights and data protection measures*].
    """

    *Validate placeholders with ethics and regulatory teams.*
    """,

    # Data Monitoring and Quality Control
    "data_monitoring": """
    Generate a Data Monitoring and Quality Control section detailing:

    1. **Data Validation**:
       - Describe measures for data consistency and accuracy (e.g., validation checks).

    2. **Monitoring Visits**:
       - Mention frequency and scope of monitoring visits to sites.

    3. **Audit Procedures**:
       - Outline audit processes for data integrity.

    If any information is missing, insert *[PLACEHOLDER: Confirm quality control and monitoring details]*.

    # Example Output:
    """
    [PLACEHOLDER: *Define monitoring intervals and data validation requirements*].
    [SUGGESTED CONTENT: *Detail frequency of monitoring visits and audit standards*].
    """

    *Confirm placeholders with data management to ensure protocol compliance.*
    """,

    # Completion and Discontinuation Criteria
    "completion_criteria": """
    Define the Completion and Discontinuation Criteria for the study, including:

    1. **Participant Withdrawal**:
       - Detail the conditions under which a participant might withdraw.

    2. **Study Termination**:
       - Specify criteria that would trigger early termination of the study.

    Use *[PLACEHOLDER: Confirm discontinuation criteria]* for any missing details.

    # Example Output:
    """
    [PLACEHOLDER: *Specify withdrawal and study termination conditions*].
    [SUGGESTED CONTENT: *Outline criteria for early study termination if applicable*].
    """

    *Validate placeholders for consistency with study requirements.*
    """,

    # Informed Consent Process
    "informed_consent": """
    Detail the Informed Consent Process, focusing on procedural aspects:

    1. **Consent Documentation**:
       - Describe how consent will be documented.

    2. **Information Disclosure**:
       - Outline how key information (risks, benefits) is conveyed to participants.

    Use *[PLACEHOLDER: Confirm consent process and documentation]* if specifics are absent.

    # Example Output:
    """
    [PLACEHOLDER: *Describe who will obtain consent and where it will be documented*].
    [SUGGESTED CONTENT: *Ensure consent form covers risks, benefits, and study procedures*].
    """

    *Validate any placeholders to align with IRB and regulatory requirements.*
    """,

    # Randomization and Blinding
    "randomization_and_blinding": """
    Generate a Randomization and Blinding section based on study design requirements. Detail the process for randomization, any blinding procedures, and use placeholders for missing details.

    1. **Randomization Process**:
       - Explain the method used for randomization (e.g., stratified, simple randomization). If the method is not specified, add *[PLACEHOLDER: Confirm randomization method]*.

    2. **Blinding Procedures**:
       - Describe whether the study is single-blind, double-blind, or open-label, and explain how blinding will be maintained. If unclear, add *[PLACEHOLDER: Specify blinding approach]*.

    # Example Output:
    """
    [PLACEHOLDER: *Specify whether study is blinded and method used to conceal allocation*].
    [SUGGESTED CONTENT: *Consider central randomization for unbiased assignment*].
    """

    *Validate any placeholders with the clinical team for study integrity.*
    """
}

