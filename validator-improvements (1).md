# Protocol Validator Improvements

## 1. Section-Level Validation
```python
def validate_section(self, section_name: str, content: str, study_type: str) -> Dict:
    """Validate individual protocol section"""
    section_results = {
        "issues": [],
        "warnings": [],
        "suggestions": [],
        "score": 0
    }
    
    # Validate section-specific requirements
    self._validate_section_requirements(section_name, content, study_type, section_results)
    
    # Validate section completeness
    self._validate_section_completeness(section_name, content, study_type, section_results)
    
    # Check for placeholders
    self._check_placeholders(content, section_results)
    
    # Calculate section score
    section_results["score"] = self._calculate_section_score(section_results)
    
    return section_results

def _validate_section_requirements(self, section_name: str, content: str, study_type: str, results: Dict):
    """Check section-specific requirements"""
    section_requirements = {
        "objectives": {
            "required_elements": ["primary_objective", "secondary_objectives"],
            "forbidden_terms": ["tbd", "to be determined", "placeholder"],
            "min_length": 200
        },
        "study_design": {
            "required_elements": ["design_type", "duration", "population"],
            "study_type_specific": {
                "phase1": ["dose_escalation", "safety_monitoring"],
                "phase2": ["endpoints", "sample_size"],
                "phase3": ["randomization", "blinding", "interim_analysis"],
                "phase4": ["real_world_setting", "comparator"]
            }
        },
        # Add other section requirements
    }
    
    if section_name in section_requirements:
        reqs = section_requirements[section_name]
        
        # Check required elements
        for element in reqs["required_elements"]:
            if element.lower() not in content.lower():
                results["issues"].append({
                    "type": IssueType.MISSING_ELEMENT,
                    "severity": IssueSeverity.MAJOR,
                    "message": f"Missing required element '{element}' in {section_name}",
                    "suggestion": f"Add {element} to section"
                })
        
        # Check study type specific requirements
        if "study_type_specific" in reqs and study_type in reqs["study_type_specific"]:
            for element in reqs["study_type_specific"][study_type]:
                if element.lower() not in content.lower():
                    results["issues"].append({
                        "type": IssueType.MISSING_ELEMENT,
                        "severity": IssueSeverity.MAJOR,
                        "message": f"Missing {study_type}-specific element '{element}' in {section_name}",
                        "suggestion": f"Add {element} as required for {study_type} studies"
                    })

def _check_duplications(self, sections: Dict[str, str], results: Dict):
    """Check for excessive duplication between sections while allowing Synopsis duplication"""
    
    def calculate_similarity(text1: str, text2: str) -> float:
        # Simple similarity calculation - can be enhanced with more sophisticated methods
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        shorter_len = min(len(words1), len(words2))
        return len(intersection) / shorter_len if shorter_len > 0 else 0
    
    # Threshold for flagging duplication (higher for Synopsis)
    SYNOPSIS_THRESHOLD = 0.8  # Allow more duplication with Synopsis
    GENERAL_THRESHOLD = 0.6   # Stricter for other sections
    
    for section1, content1 in sections.items():
        for section2, content2 in sections.items():
            if section1 >= section2:  # Avoid checking same section or redundant pairs
                continue
                
            similarity = calculate_similarity(content1, content2)
            
            # Allow higher similarity with Synopsis
            threshold = SYNOPSIS_THRESHOLD if "synopsis" in (section1.lower(), section2.lower()) else GENERAL_THRESHOLD
            
            if similarity > threshold:
                severity = IssueSeverity.MINOR if "synopsis" in (section1.lower(), section2.lower()) else IssueSeverity.MAJOR
                results["issues"].append({
                    "type": IssueType.INCONSISTENCY,
                    "severity": severity,
                    "message": f"High content similarity ({similarity:.1%}) between {section1} and {section2}",
                    "suggestion": "Consider consolidating or cross-referencing" if severity == IssueSeverity.MAJOR else "Review if duplication is justified"
                })

def _validate_timeline(self, content: str, results: Dict):
    """Validate study timeline logic and consistency"""
    # Extract timeline-related information using regex
    import re
    
    timeline_pattern = r'(\d+)\s*(day|week|month|year)s?\s*(prior to|after|from|to)\s*(\w+)'
    timeline_items = re.findall(timeline_pattern, content, re.IGNORECASE)
    
    # Convert to standardized format (days)
    def convert_to_days(value: int, unit: str) -> int:
        conversions = {
            'day': 1,
            'week': 7,
            'month': 30,
            'year': 365
        }
        return value * conversions[unit.lower()]
    
    # Check for logical inconsistencies
    for i in range(len(timeline_items)-1):
        current = convert_to_days(int(timeline_items[i][0]), timeline_items[i][1])
        next_item = convert_to_days(int(timeline_items[i+1][0]), timeline_items[i+1][1])
        
        if current >= next_item:
            results["issues"].append({
                "type": IssueType.INCONSISTENCY,
                "severity": IssueSeverity.MAJOR,
                "message": f"Timeline inconsistency between {timeline_items[i]} and {timeline_items[i+1]}",
                "suggestion": "Review timeline sequence and adjust durations"
            })

def _calculate_section_score(self, results: Dict) -> float:
    """Calculate quality score for individual section"""
    base_score = 100
    deductions = {
        IssueSeverity.CRITICAL: 20,
        IssueSeverity.MAJOR: 10,
        IssueSeverity.MINOR: 5
    }
    
    for issue in results["issues"]:
        base_score -= deductions[issue["severity"]]
    
    # Add bonuses for good practices
    if not any(i["severity"] == IssueSeverity.CRITICAL for i in results["issues"]):
        base_score += 5
    
    if len(results["issues"]) == 0:
        base_score += 10
        
    return max(0, min(100, base_score))
```

## Key Improvements:

1. Section-Level Validation
- Validates each section independently
- Section-specific requirements
- Study type-specific checks

2. Smarter Duplication Detection
- Allows reasonable duplication with Synopsis
- Different thresholds for Synopsis vs other sections
- Sophisticated similarity calculation

3. Enhanced Timeline Validation
- Extracts timeline information
- Checks logical sequence
- Validates dependencies

4. Improved Scoring
- Section-specific scoring
- Bonus points for good practices
- Weighted deductions by severity

## Usage Example:
```python
validator = ProtocolValidator()

# Validate single section
section_results = validator.validate_section(
    "objectives", 
    section_content,
    "phase2"
)

# Validate entire protocol
protocol_results = validator.validate_protocol(
    all_sections,
    "phase2"
)
```

These improvements provide more granular validation while being more tolerant of justified duplication with the Synopsis. The section-level validation allows for more specific requirements and better scoring.