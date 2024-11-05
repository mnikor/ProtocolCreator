SECTION_PROMPTS = {
 

   # General Instructions
    "general_instructions": """
When generating each section, consider the specific type of study provided in the synopsis (e.g., Phase 1-3 clinical trials, Phase 2b, secondary Real World Evidence (RWE) studies, prospective cohorts, patient surveys, disease registries, etc.).

Ensure that the content is tailored to the objectives, design, methodologies, and regulatory requirements appropriate for that specific study type.

Include sections only when relevant based on the provided information and the study type. Do not create sections or subsections solely to state that they are not applicable.

Avoid including any disallowed content, and ensure all information is based solely on the provided synopsis without making unsupported assumptions.

Use formal, objective language appropriate for a scientific document, and ensure compliance with ethical and regulatory standards throughout.
""",

       # Title
       "title": """
   Generate a descriptive and concise Title for the study that clearly indicates:

   - The study focus (e.g., intervention, condition, exposure)
   - The type of study (e.g., Phase 2b clinical trial, prospective cohort study, patient survey, disease registry)
   - The target population or key demographics

   Ensure the title adheres to regulatory guidelines and maintains confidentiality by avoiding the inclusion of any proprietary or sensitive information.

   If sufficient details are not provided in the synopsis to generate a meaningful title, omit this section.

   *Ensure the title is clear, aligns with the study objectives, and is free of confidential information.*
   """,
   
    # Synopsis
    "synopsis": """
Generate a concise and comprehensive Synopsis for the study, summarizing the key elements based on the provided information.

The Synopsis should include:

1. **Study Title**:
   - Provide the full title of the study as generated or provided.

2. **Study Type and Phase**:
   - Indicate the type of study (e.g., Phase 2b clinical trial, prospective cohort study, patient survey, disease registry).

3. **Background and Rationale**:
   - Briefly describe the background and the rationale for the study, focusing on the unmet needs or gaps the study intends to address.

4. **Objectives**:
   - Summarize the primary and secondary objectives of the study.

5. **Study Design**:
   - Outline the overall study design, including key features such as randomization, blinding (if applicable), and study duration.
   - For observational studies, describe the design (e.g., cohort, case-control, cross-sectional).

6. **Population**:
   - Describe the target population, including key inclusion and exclusion criteria.

7. **Interventions or Exposures**:
   - For interventional studies, summarize the interventions.
   - For observational studies, describe the exposures or variables of interest.

8. **Endpoints/Outcome Measures**:
   - List the primary and secondary endpoints or outcome measures.

9. **Statistical Methods**:
   - Briefly mention the primary statistical methods to be used for data analysis.

10. **Ethical Considerations**:
    - Note any key ethical considerations, such as informed consent procedures and data confidentiality measures.

**Instructions**:

- **Conciseness**: Keep the Synopsis concise, ideally within 1-2 pages.
- **Clarity**: Use clear and precise language to ensure that the summary is easily understood.
- **Consistency**: Ensure that the information in the Synopsis aligns with the detailed sections of the protocol.
- **Relevance**: Include only the elements relevant to the study type and based on the information provided.
- **Compliance**: Avoid including any disallowed content or confidential information.
- **Accuracy**: Base the Synopsis solely on the information provided in the study synopsis without making unsupported assumptions.

*Ensure that the Synopsis provides a clear and comprehensive overview of the study, facilitating understanding for readers.*
""",


    # Background
    "background": """
Generate a comprehensive Background section that provides clinical context, the current knowledge landscape, and the study rationale based on the provided synopsis and the study type.

1. **Background Context**:
   - Describe the condition, exposure, or issue being studied, including prevalence and impact.
   - Use only the information provided; do not fabricate statistics or data.
   - For RWE or observational studies, discuss the gap in knowledge or unmet needs.

2. **Current Knowledge or Treatment Landscape**:
   - Outline current understanding, treatments, or interventions relevant to the study.
   - For registries or surveys, discuss the importance of data collection on the subject.

3. **Study Rationale**:
   - Explain the rationale for the chosen study design and objectives in the context of the study type.
   - Include justification for any specific populations or methodologies.
   - Focus on summarizing the available rationale without making unsupported assumptions.

4. **Formatting and Presentation**:
   - Use clear headings for subtopics.
   - Ensure varied sentence structures to enhance readability.
   - Do not include placeholders; if information is missing, omit that content.

*Ensure the background is informative, based solely on the provided information, and adheres to ethical and regulatory standards. Do not include fabricated data or references.*
""",

    # Objectives
    "objectives": """
Generate the Objectives section, ensuring that the primary and secondary objectives are clearly stated and align with the study endpoints, based on the information provided in the synopsis and the study type.

1. **Primary Objective(s)**:
   - Clearly define the primary objective(s) of the study, ensuring they are specific, measurable, and appropriate for the study type.
   - For clinical trials, focus on efficacy and safety endpoints.
   - For observational studies (e.g., RWE, cohorts), focus on associations, incidence, or prevalence.
   - For patient surveys, focus on patient-reported outcomes or satisfaction measures.

2. **Secondary Objective(s)**:
   - Include any secondary objectives relevant to the study type.
   - For registries, may include long-term outcomes or natural history data.

3. **Endpoints and Hypotheses**:
   - Specify endpoints that align with the objectives and are appropriate for the study type.
   - For observational studies, endpoints may include risk factors, health outcomes, or resource utilization metrics.

*Ensure that all objectives and endpoints are based solely on the provided information and are appropriate for the study type. Do not include assumptions or unsupported content.*
""",

    # Study Design
    "study_design": """
Describe the Study Design based on the provided synopsis and the study type, ensuring clarity and adherence to standard guidelines.

1. **Overall Design**:
   - Provide a concise overview of the study design appropriate for the type (e.g., randomized controlled trial, prospective cohort, cross-sectional survey, disease registry).
   - Include details relevant to the study type:
     - For interventional studies, describe intervention assignment methods.
     - For observational studies, describe data sources, timeframes, and participant selection methods.

2. **Population and Setting**:
   - Define the study population and setting.
   - For registries, describe the data collection methods and inclusion criteria.

3. **Data Collection Methods**:
   - Describe how data will be collected (e.g., electronic health records for RWE, questionnaires for surveys).
   - Include any relevant instruments or tools.

4. **Study Duration**:
   - Specify the study period, including any follow-up times appropriate for the study type.

5. **Study Schema**:
   - Provide a detailed textual description of the study flow suitable for generating a diagram using the Mermaid library, if applicable.

*Ensure the study design is appropriate for the study type and described accurately based on the provided information.*
""",

    # Population
    "population": """
Generate the Population section, including key demographic details, eligibility criteria, and sample size justification, based on the information provided.

1. **Inclusion Criteria**:
   - Detail the requirements for participant eligibility (e.g., age range, disease status, exposure history).
   - Ensure criteria are ethically appropriate and relevant to the study objectives and type.
   - For surveys or registries, describe the sampling strategy.

2. **Exclusion Criteria**:
   - Define factors that would exclude potential participants to avoid confounding variables and ensure safety.
   - If exclusion criteria are not provided, omit this subsection.

3. **Sample Size Justification**:
   - Provide a rationale for the sample size, referencing study endpoints or statistical considerations if available.
   - For observational studies, discuss considerations for statistical power or representativeness.
   - Do not fabricate calculations; use only the information given.

*Ensure all content is based solely on the provided synopsis, without adding unsupported details or assumptions.*
""",

    # Procedures
    "procedures": """
Detail the study procedures, including assessments, data collection methods, and follow-up, based on the information provided in the synopsis and appropriate for the study type.

1. **Data Collection Procedures**:
   - Describe how data will be collected, including tools and instruments used.
   - For surveys, detail the administration method (e.g., online, telephone).
   - For registries, explain the data entry process.

2. **Intervention Procedures** (if applicable):
   - For interventional studies, describe how the intervention(s) will be administered, including dosage, frequency, and mode of administration.
   - Use only the provided details; do not make assumptions.

3. **Follow-up Procedures**:
   - Specify the follow-up schedule and any assessments or evaluations during the follow-up period.
   - For cohort studies, include information on tracking participants over time.

*Ensure all procedures are described in alignment with current guidelines and standards, and based solely on the provided information.*
""",

    # Statistical Analysis Plan
    "statistical_analysis": """
Generate a Statistical Analysis Plan based on the study objectives, design, and type provided in the synopsis.

1. **Primary Analysis**:
   - Specify the statistical methods appropriate for analyzing the primary endpoints.
   - For clinical trials, include methods for efficacy and safety analyses.
   - For observational studies, include methods for association analyses (e.g., regression models, survival analysis).
   - For surveys, include descriptive statistics and analyses of survey responses.

2. **Handling of Confounding and Bias**:
   - For observational studies, describe strategies to address confounding factors and potential biases (e.g., multivariable adjustments, propensity score matching).

3. **Sample Size Calculation**:
   - If applicable, provide a rationale for the sample size.
   - For surveys and registries, discuss the expected number of participants and any considerations for representativeness.
   - Do not fabricate calculations; use only the information provided.

*Ensure that the statistical methods are appropriate for the study type and based on the provided information.*
""",

    # Safety and Risk Management
    "safety": """
Generate a Safety and Risk Management section based on the information provided and appropriate for the study type.

1. **Risk Assessment**:
   - Describe any potential risks to participants associated with the study.
   - For interventional studies, include risks related to the intervention.
   - For observational studies or surveys, risks may be minimal but consider data privacy and confidentiality.

2. **Safety Monitoring**:
   - For clinical trials, describe safety assessments and monitoring procedures.
   - For other study types, if applicable, mention any monitoring for adverse events.

3. **Risk Mitigation Strategies**:
   - Outline measures taken to minimize risks to participants.
   - Include data security measures for protecting sensitive information.

*Ensure that all safety procedures and risk management strategies are described accurately and comply with relevant ethical and regulatory standards.*
""",

    # Ethical Considerations
    "ethical_considerations": """
Create an Ethical Considerations section based on the information provided and appropriate for the study type.

1. **Regulatory Compliance**:
   - Describe adherence to relevant guidelines (e.g., GCP for clinical trials, STROBE for observational studies).
   - Mention compliance with local and international regulations.

2. **Informed Consent**:
   - Outline the informed consent process, tailored to the study type.
   - For secondary data analyses or registries, discuss consent waivers or de-identification methods.

3. **Data Privacy and Confidentiality**:
   - Describe measures to protect participant data.
   - Reference compliance with data protection laws (e.g., GDPR, HIPAA).

4. **Risk-Benefit Analysis**:
   - Discuss the risk-benefit profile appropriate for the study type.

*Ensure all ethical considerations prioritize participant welfare and adhere to all relevant ethical and regulatory standards.*
""",

    # Data Monitoring and Quality Control
    "data_monitoring": """
Generate a Data Monitoring and Quality Control section based on the information provided.

1. **Data Management and Validation**:
   - Describe procedures for ensuring data consistency, accuracy, and completeness.
   - Include any data validation processes specified.
   - Mention compliance with data protection regulations (e.g., GDPR, HIPAA).

2. **Monitoring Procedures**:
   - For clinical trials, outline the frequency and scope of monitoring activities.
   - For observational studies, describe any data quality checks or audits.

3. **Quality Assurance and Audits**:
   - Describe any quality assurance measures or audit procedures that will be implemented to maintain data integrity.
   - Ensure compliance with relevant regulatory requirements.

*Ensure all data monitoring and quality control processes are described accurately and comply with regulatory requirements.*
""",

    # Completion and Discontinuation Criteria
    "completion_criteria": """
Define the Completion and Discontinuation Criteria based on the information provided.

1. **Participant Withdrawal**:
   - Detail the conditions under which a participant may voluntarily withdraw from the study.
   - Include any criteria for mandatory withdrawal (e.g., non-compliance), if specified.

2. **Study Termination**:
   - Specify any criteria that could lead to early termination of the study (e.g., safety concerns, insufficient enrollment).
   - Ensure that participant safety and data integrity are primary considerations.

*Ensure all criteria are described clearly, ethically, and based on the provided information, prioritizing participant safety and well-being.*
""",

    # Informed Consent Process
    "informed_consent": """
Detail the Informed Consent Process based on the information provided.

1. **Consent Process**:
   - Describe how informed consent will be obtained from participants.
   - Include who will obtain consent and the setting in which it will occur.
   - For surveys or minimal risk studies, discuss any consent waivers if applicable.

2. **Consent Documentation**:
   - Explain how consent will be documented and stored securely.
   - Mention that consent forms will include comprehensive information on the study, including risks, benefits, and procedures.

3. **Participant Understanding**:
   - Outline steps taken to ensure participants fully understand the information provided.
   - Consider cultural and language needs to facilitate understanding.

*Ensure that the informed consent process is thorough, respects participant autonomy, and complies with ethical and regulatory standards.*
""",

    # Randomization and Blinding
    "randomization_and_blinding": """
Include a "Randomization and Blinding" section **only if** these elements are part of the study, such as in randomized controlled trials.

**Instructions**:

- **If Randomization and Blinding Are Applicable**:
  - **Randomization Process**:
    - Describe the randomization method used.
    - Include allocation concealment strategies.
  - **Blinding Procedures**:
    - Explain the blinding method.
    - Detail who is blinded and how blinding is maintained.

- **If Randomization and Blinding Are Not Applicable**:
  - **Do Not Include** this section.
  - **Do Not Mention** randomization or blinding anywhere in the protocol.

*Ensure that only relevant sections are included based on the study type. Avoid adding sections or statements about non-applicability.*
""",

    # Data Sources (for RWE and Secondary Data Analyses)
    "data_sources": """
Include a Data Sources section if applicable to the study type, such as in RWE studies, registries, or secondary data analyses.

1. **Data Source Description**:
   - Describe the databases, registries, or datasets that will be used.
   - Include information on data provenance, quality, and completeness.

2. **Data Extraction and Management**:
   - Outline the processes for data extraction, cleaning, and management.
   - Mention any software or tools that will be used.

3. **Data Linkage**:
   - If data from multiple sources will be linked, describe the methods and any privacy considerations.

*Ensure that the description is based solely on the provided information and is appropriate for the study type.*
""",

    # Pharmacokinetics and Pharmacodynamics (if applicable)
    "pk_pd": """
If applicable based on the study type and provided information, generate a section on Pharmacokinetics and Pharmacodynamics.

1. **Pharmacokinetic Assessments**:
   - Describe any pharmacokinetic (PK) evaluations planned.
   - Include details on sampling schedules, analytes measured, and bioanalytical methods.

2. **Pharmacodynamic Assessments**:
   - Outline any pharmacodynamic (PD) assessments.
   - Include biomarkers or clinical endpoints relevant to the study's focus.

*Include this section only if PK/PD assessments are relevant to the study type and provided information.*
""",
}



