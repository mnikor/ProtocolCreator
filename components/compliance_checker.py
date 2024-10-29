import streamlit as st
from utils.regulatory_compliance import RegulatoryCompliance

def render_compliance_checker():
    """Render the regulatory compliance checker interface"""
    st.header("Regulatory Compliance Check")

    if not st.session_state.generated_sections:
        st.warning("Generate protocol sections first to check compliance")
        return

    compliance_checker = RegulatoryCompliance()
    
    # Get study phase from session state
    study_phase = st.session_state.study_type if hasattr(st.session_state, 'study_type') else 'phase1'
    
    # Run compliance check
    with st.spinner("Checking regulatory compliance..."):
        compliance_report = compliance_checker.check_compliance(
            st.session_state.generated_sections,
            study_phase
        )
    
    # Display overall compliance status
    if compliance_report['overall_compliance']:
        st.success("Protocol complies with regulatory requirements")
    else:
        st.error("Protocol has compliance issues that need attention")
    
    # Display section-specific compliance
    st.subheader("Section Compliance")
    for section, report in compliance_report['section_compliance'].items():
        with st.expander(f"{section.replace('_', ' ').title()} Section"):
            if report['compliant']:
                st.success("✓ Compliant with ICH guidelines")
            else:
                st.error("× Non-compliant - missing required elements")
            
            # Show missing elements
            if report['missing_elements']:
                st.write("Missing Elements:")
                for element in report['missing_elements']:
                    st.write(f"• {element['element'].replace('_', ' ').title()}")
            
            # Show keyword coverage
            coverage = report['keyword_coverage'] * 100
            st.progress(report['keyword_coverage'])
            st.write(f"Guideline Keyword Coverage: {coverage:.1f}%")
    
    # Display phase-specific compliance
    st.subheader("Phase-Specific Requirements")
    phase_compliance = compliance_report['phase_compliance']
    if phase_compliance['compliant']:
        st.success(f"✓ Compliant with {study_phase.upper()} requirements")
    else:
        st.error(f"× Non-compliant with {study_phase.upper()} requirements")
        
    if phase_compliance['missing_elements']:
        st.write("Missing Phase-Specific Elements:")
        for element in phase_compliance['missing_elements']:
            st.write(f"• {element['element'].replace('_', ' ').title()}")
    
    # Display suggestions
    if compliance_report['suggestions']:
        st.subheader("Improvement Suggestions")
        for suggestion in compliance_report['suggestions']:
            st.info(f"💡 {suggestion}")

    # Export compliance report button
    if st.button("Export Compliance Report"):
        _export_compliance_report(compliance_report)

def _export_compliance_report(compliance_report):
    """Export compliance report as a text file"""
    try:
        report_content = ["PROTOCOL REGULATORY COMPLIANCE REPORT", "=" * 40, ""]
        
        # Overall status
        report_content.append("OVERALL COMPLIANCE STATUS:")
        report_content.append("✓ Compliant" if compliance_report['overall_compliance'] 
                            else "× Non-compliant")
        report_content.append("")
        
        # Section compliance
        report_content.append("SECTION-SPECIFIC COMPLIANCE:")
        report_content.append("-" * 30)
        for section, report in compliance_report['section_compliance'].items():
            report_content.append(f"\n{section.upper()}:")
            report_content.append(f"Status: {'✓ Compliant' if report['compliant'] else '× Non-compliant'}")
            if report['missing_elements']:
                report_content.append("Missing Elements:")
                for element in report['missing_elements']:
                    report_content.append(f"• {element['element'].replace('_', ' ')}")
            report_content.append(f"Keyword Coverage: {report['keyword_coverage']*100:.1f}%")
        
        # Phase-specific compliance
        report_content.extend([
            "",
            "PHASE-SPECIFIC COMPLIANCE:",
            "-" * 30
        ])
        phase_compliance = compliance_report['phase_compliance']
        report_content.append(f"Status: {'✓ Compliant' if phase_compliance['compliant'] else '× Non-compliant'}")
        if phase_compliance['missing_elements']:
            report_content.append("Missing Elements:")
            for element in phase_compliance['missing_elements']:
                report_content.append(f"• {element['element'].replace('_', ' ')}")
        
        # Suggestions
        if compliance_report['suggestions']:
            report_content.extend([
                "",
                "IMPROVEMENT SUGGESTIONS:",
                "-" * 30
            ])
            for suggestion in compliance_report['suggestions']:
                report_content.append(f"• {suggestion}")
        
        # Save report
        report_text = "\n".join(report_content)
        with open("compliance_report.txt", "w") as f:
            f.write(report_text)
        
        # Provide download link
        with open("compliance_report.txt", "rb") as f:
            st.download_button(
                "Download Compliance Report",
                f,
                "compliance_report.txt",
                "text/plain",
                key='download-compliance-report'
            )
            
    except Exception as e:
        st.error(f"Error exporting compliance report: {str(e)}")
