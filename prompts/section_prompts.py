
SECTION_PROMPTS = {
   # Full Clinical Protocol Generation Prompt with Example Outputs

   # Background
   """
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
   """

   # Objectives
   """
   Generate the Objectives section, ensuring primary and secondary objectives are clearly aligned with endpoints. If objectives are missing, include placeholders with validation recommendations.

   1. **Primary Objective(s)**:
      - Define the primary focus, e.g., "Evaluate safety of [study intervention] in [population]." Use *[PLACEHOLDER: Define primary objective(s)]* if specific objectives are not provided.

   2. **Secondary Objective(s)**:
      - Add secondary outcomes of interest (e.g., biomarker responses, QoL measures). If absent, include *[PLACEHOLDER: Confirm secondary objectives]*.

   3. **Endpoints and Hypothesis**:
      - List endpoints in a table format and clarify any linked hypotheses.

   # Example Output:
   """
   [PLACEHOLDER: *Confirm primary objective, such as overall survival or progression-free survival*].
   [SUGGESTED CONTENT: *Secondary objectives might include quality of life or biomarker measures; validate with study scope*].
   """

   *Validate placeholders to ensure objectives are specific and align with study scope.*
   """

   # Study Design
   """
   Describe the Study Design based on the provided synopsis and document standards. Include rationale for design elements and follow specific formatting instructions.

   1. **Overall Design**:
      - Provide a high-level overview (e.g., double-blind, randomized) and include details like intervention assignment methods and blinding. If not specified, use *[PLACEHOLDER: Confirm overall study design details]*.

   2. **Intervention Groups**:
      - Define each intervention arm, dose, and administration details. Insert *[PLACEHOLDER: Describe intervention groups and dose details]* if missing.

   3. **Study Duration**:
      - Specify the length of each study phase. If unclear, use *[PLACEHOLDER: Specify study duration for each phase]*.

   4. **Study Schema**:
      - Include a schematic diagram showing study phases, if feasible. Reference any sub-studies planned as per the document.

   5. **Formatting and Presentation**:
      - Use bullet points or a table format to outline key components like treatment groups and duration.

   # Example Output:
   """
   [PLACEHOLDER: *Define study blinding method (e.g., single-blind, double-blind)*].
   [SUGGESTED CONTENT: *Summarize intervention groups and validate duration with study timeline*].
   """

   *Validate placeholders with study coordinators for comprehensive detail.*
   """

   # Endpoints and Outcomes
   """
   Generate the Endpoints and Outcomes section, aligned with primary and secondary objectives. If any endpoints are missing, use placeholders.

   1. **Primary Endpoint**:
      - Define the main outcome, e.g., “Overall survival.” If absent, add *[PLACEHOLDER: Define primary endpoint]*.

   2. **Secondary Endpoints**:
      - List secondary outcomes, including any specific biomarkers or QoL measures. Use *[PLACEHOLDER: Specify secondary endpoints]* if missing.

   3. **Formatting Guidance**:
      - Present primary and secondary endpoints in a table format.

   # Example Output:
   """
   [PLACEHOLDER: *Define primary endpoint, such as progression-free survival*].
   [SUGGESTED CONTENT: *Include relevant secondary outcomes, like QoL or symptom reduction; confirm with objectives*].
   """

   *Review placeholders for alignment with study goals.*
   """

   # Data Sources and Collection Methods
   """
   Detail the data sources and collection methods according to document requirements. Use placeholders for any missing information.

   1. **Data Sources**:
      - List all sources (e.g., EHR, claims data). If data sources are not fully specified, add *[PLACEHOLDER: Confirm data sources]*.

   2. **Data Collection Procedures**:
      - Describe procedures, such as electronic data capture or paper CRFs, and timing. If specific methods are missing, insert *[PLACEHOLDER: Define data collection method]*.

   3. **Formatting and Presentation**:
      - Present data sources in a list format, using tables for schedules if necessary.

   # Example Output:
   """
   [PLACEHOLDER: *Specify primary data sources like Flatiron or SEER-Medicare*].
   [SUGGESTED CONTENT: *Consider other secondary data sources; validate with data management*].
   """

   *Confirm placeholders with the data management team.*
   """

   # Statistical Analysis Plan
   """
   Generate a detailed Statistical Analysis Plan in line with study objectives. Use placeholders for missing methods or sample size calculations and provide recommendations for validation.

   1. **Primary Analysis**:
      - Specify primary statistical methods (e.g., Cox regression for survival analysis). If these are missing, add *[PLACEHOLDER: Confirm primary analysis method]*.

   2. **Sample Size Calculation**:
      - Specify sample size and power calculations. If not provided, add *[PLACEHOLDER: Insert sample size details]*.

   3. **Formatting Guidance**:
      - Use structured paragraphs or bullet points, and avoid overly technical terms where possible.

   # Example Output:
   """
   [PLACEHOLDER: *Specify statistical methods like Cox regression or Kaplan-Meier analysis*].
   [SUGGESTED CONTENT: *Include sample size and power calculation details; validate with a statistician*].
   """

   *Validate placeholders with a biostatistician to ensure methodological rigor.*
   """

   # Safety and Risk Management
   """
   Generate a detailed Safety and Risk Management section for the protocol, focusing on regular monitoring, adverse event reporting, and adherence to ICH E6 guidelines. Structure content based on available information from the synopsis. If key safety details are missing, provide clear placeholders in *italic font* with validation recommendations.

   1. **Vital Signs and Clinical Assessments**:
      - Specify measurements (e.g., heart rate, blood pressure) and assessment schedules based on the synopsis. If any timing or frequency details are missing, insert *[PLACEHOLDER: Define schedule for specific vital sign assessments]* and recommend validation with clinical study coordinators.

   2. **Adverse Events and Serious Adverse Events (SAEs)**:
      - Describe the AE and SAE capture process, including specific reporting timelines and follow-up procedures. If these details are missing, add *[PLACEHOLDER: Confirm AE and SAE reporting protocols]*.

   3. **Severity and Causality Assessment**:
      - Indicate any standard criteria (e.g., MedDRA for coding AEs and WHO causality categories). If not provided, add *[PLACEHOLDER: Confirm criteria for severity and causality]*.

   # Example Output:
   """
   [PLACEHOLDER: *Specify timelines for SAE reporting and monitoring*].
   [SUGGESTED CONTENT: *Detail adverse event monitoring according to ICH guidelines; validate with regulatory team*].
   """

   *Please validate any placeholders to ensure that this Safety section meets study-specific and regulatory requirements.*
   """

   # Informed Consent Process
   """
   Generate an Informed Consent Process section, describing how participants will be informed about the study and how consent will be documented. Follow ethical and regulatory standards, and include placeholders for any missing details.

   1. **Consent Procedures**:
      - Describe the process for obtaining informed consent, including who will obtain it and when. If specifics are missing, insert *[PLACEHOLDER: Specify consent process details]*.

   2. **Participant Information**:
      - Outline the key information that will be provided to participants, including study purpose, procedures, risks, and benefits. If certain details are not available, add *[PLACEHOLDER: Confirm participant information content]*.

   # Example Output:
   """
   [PLACEHOLDER: *Describe who will obtain consent and where it will be documented*].
   [SUGGESTED CONTENT: *Ensure consent form covers risks, benefits, and study procedures; confirm with IRB*].
   """

   *Validate any placeholders to align with IRB and regulatory requirements.*
   """

   # Randomization and Blinding
   """
   Generate a Randomization and Blinding section based on study design requirements. Detail the process for randomization, any blinding procedures, and use placeholders for missing details.

   1. **Randomization Process**:
      - Explain the method used for randomization (e.g., stratified, simple randomization). If the method is not specified, add *[PLACEHOLDER: Confirm randomization method]*.

   2. **Blinding Procedures**:
      - Describe whether the study is single-blind, double-blind, or open-label, and explain how blinding will be maintained. If unclear, add *[PLACEHOLDER: Specify blinding approach]*.

   # Example Output:
   """
   [PLACEHOLDER: *Specify whether study is blinded and method used to conceal allocation*].
   [SUGGESTED CONTENT: *Consider central randomization for unbiased assignment; confirm with study design requirements*].
   """

   *Validate any placeholders with the clinical team for study integrity.*
   """

   # Quality Control and Data Management
   """
   Generate a Quality Control and Data Management section, detailing processes for ensuring data quality and handling. Include placeholders for any missing details.

   1. **Quality Control Measures**:
      - Describe quality control practices (e.g., monitoring visits, data validation checks). If not specified, add *[PLACEHOLDER: Confirm quality control procedures]*.

   2. **Data Collection and Entry**:
      - Explain data collection and entry methods, specifying electronic or paper-based systems. If missing, use *[PLACEHOLDER: Define data entry method]*.

   3. **Data Security and Confidentiality**:
      - Outline how data will be securely stored and accessed. If security protocols are not detailed, add *[PLACEHOLDER: Confirm data security and confidentiality measures]*.

   # Example Output:
   """
   [PLACEHOLDER: *Specify data validation checks and monitoring schedule*].
   [SUGGESTED CONTENT: *Consider regular data audits to ensure accuracy; validate with data management team*].
   """

   *Confirm placeholders with data management to ensure protocol compliance.*
   """



}
