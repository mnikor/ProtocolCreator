
SECTION_PROMPTS = {
    # Background
    """
    Generate a comprehensive background section detailing the clinical context, significance of the disease, and rationale for the study. Use formal, precise language without any marketing or promotional tone. Avoid terms like "groundbreaking" or "revolutionary"; instead, use objective terms such as "effective" or "widely studied." Maintain consistency in terminology and vary sentence structure to avoid repetitive phrasing typical of LLMs. If any key details (e.g., disease prevalence, prior studies) are missing, insert placeholders in *italic font* and suggest user validation where applicable.
    """

    # Example Output:
    """
    [PLACEHOLDER: *Insert specific prevalence or incidence statistics for the disease*].
    [SUGGESTED CONTENT: *Background on the disease impact in specific populations or prior treatment outcomes; validate with current literature or study data*].
    """

    # Objectives
    """
    Generate primary and secondary objectives based strictly on the provided synopsis. Clearly align each objective with respective study endpoints, using standards aligned with the study’s phase (e.g., Phase I focuses on safety, Phase III on efficacy). Avoid assumptions about outcomes not specified in the synopsis. Use placeholders for any missing objectives or endpoints and provide a recommendation for user validation, in *italic font*. Language should remain professional and avoid promotional phrases.
    """

    # Example Output:
    """
    [PLACEHOLDER: *Primary objective needs further specification*].
    [SUGGESTED CONTENT: *Objective could include efficacy metrics or patient-reported outcomes; confirm specific objectives with study goals*].
    """

    # Study Design
    """
    Describe the study design according to the synopsis, including design type (e.g., randomized, double-blind), phases, control arms, and follow industry standards like CONSORT for interventional studies or STROBE for observational studies. If the design lacks specific details (e.g., blinding method), use placeholders. Avoid terms like "experiment" and use "study" or "trial" instead. Ensure varied sentence structure and adhere to formal clinical writing standards. *If necessary, add placeholders and suggest validation in italic font*.
    """

    # Example Output:
    """
    [PLACEHOLDER: *Specify whether study design is blinded or open-label*].
    [SUGGESTED CONTENT: *If randomized, provide description of randomization process; validate with protocol specifics*].
    """

    # Population and Sampling
    """
    Define the study population and sampling criteria based on inclusion and exclusion guidelines in the synopsis. Clearly state the criteria, using only information given. If details are missing (e.g., age range or specific diagnostic criteria), use placeholders. Ensure that language is neutral, formal, and avoids promotional tone. Recommend validation in *italic font* for any placeholder text.
    """

    # Example Output:
    """
    [PLACEHOLDER: *Additional inclusion criteria needed, such as age range or specific diagnostic factors*].
    [SUGGESTED CONTENT: *Typical criteria may include demographic factors; validate for alignment with protocol*].
    """

    # Endpoints and Outcomes
    """
    Generate a list of primary and secondary endpoints directly aligned with the objectives. Specify measurable and precise endpoints using available information. Avoid extrapolating additional outcomes beyond the synopsis. If certain endpoints are missing, provide placeholders and suggest likely measures while recommending validation in *italic font*. Avoid promotional language, focusing on objective phrasing.
    """

    # Example Output:
    """
    [PLACEHOLDER: *Clarify specific primary endpoint, e.g., progression-free survival or overall survival*].
    [SUGGESTED CONTENT: *Secondary endpoints may include quality-of-life measures; confirm with study objectives*].
    """

    # Data Sources and Collection Methods
    """
    Outline the data sources (e.g., electronic health records, claims databases) and collection methods based on available information. Avoid assumptions if specific data sources are not mentioned. For missing elements, use placeholders and add a validation recommendation. Ensure varied sentence structure and avoid repetitive phrasing. Avoid casual language, keeping the tone formal and clinical.
    """

    # Example Output:
    """
    [PLACEHOLDER: *Confirm specific data sources to be used, such as Flatiron Health or SEER-Medicare*].
    [SUGGESTED CONTENT: *Data sources could include EHRs and registries; validate with research team*].
    """

    # Statistical Analysis Plan
    """
    Provide a detailed statistical analysis plan based on the study’s objectives and endpoints. Include specific tests (e.g., Cox proportional hazards for survival analysis) where indicated. Avoid proposing statistical tests not mentioned in the synopsis. If information is missing, use placeholders, recommending validation by a biostatistician in *italic font*. Follow GCP guidelines for statistical methods.
    """

    # Example Output:
    """
    [PLACEHOLDER: *Confirm primary statistical tests, such as Cox proportional hazards for survival analysis*].
    [SUGGESTED CONTENT: *Consider Kaplan-Meier analysis for survival endpoints; validate with study objectives*].
    """

    # Safety and Risk Management
    """
    Develop the safety and risk management section, emphasizing adherence to ICH E6 guidelines for adverse event monitoring. Use formal language and avoid implying unverified safety concerns. If certain protocols are unspecified, insert placeholders and suggest validation. Avoid repetitive sentence structures and include placeholders for user verification in *italic font*.
    """

    # Example Output:
    """
    [PLACEHOLDER: *Specify detailed adverse event monitoring protocols*].
    [SUGGESTED CONTENT: *Safety protocols might include periodic safety reviews; confirm with clinical safety standards*].
    """

    # Ethical and Regulatory Compliance
    """
    Describe ethical and regulatory compliance requirements, including IRB/EC approval, informed consent, and data privacy (HIPAA/GDPR). Avoid ambiguous or assumptive language, using only information provided in the synopsis. Insert placeholders for unspecified regulations and recommend validation. Use varied sentence structures to maintain a professional tone. Insert placeholders and recommendations in *italic font*.
    """

    # Example Output:
    """
    [PLACEHOLDER: *Confirm IRB or EC requirements and informed consent details*].
    [SUGGESTED CONTENT: *Ensure alignment with GDPR or HIPAA regulations for data privacy; confirm with compliance officers*].
    """

    # Documentation and Record Keeping
    """
    Detail documentation and record-keeping practices, including data storage, archival, and audit trails. Avoid casual language and ensure content is suitable for a regulatory audience. Follow data standards relevant to the study type. Use table format for detailed schedules or procedures where applicable. If specifics are missing, use placeholders and suggest validation in *italic font*.
    """

    # Example Output:
    """
    [PLACEHOLDER: *Specify data storage location and security measures*].
    [SUGGESTED CONTENT: *Consider long-term storage of de-identified data; validate based on institutional requirements*].
    """

    # Study Procedures and Assessment
    """
    Present the study procedures and assessment schedule in a clear table format. For each procedure, include the timing (e.g., baseline, follow-up visits), type of assessment, and rationale. Use precise, concise language without marketing terms. If any information is missing, add placeholders and recommend validation in *italic font*.
    """

    # Example Output in Table Format:
    | Visit Timing | Procedure            | Assessment Type         | Rationale                                 |
    |--------------|----------------------|-------------------------|-------------------------------------------|
    | Baseline     | Physical Examination | Safety and Tolerability | To assess baseline health status          |
    | Follow-up    | Blood Sample         | Biomarker Analysis      | To monitor treatment response             |
    | End of Study | Imaging              | Disease Progression     | To evaluate final disease status          |


}
