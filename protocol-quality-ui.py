# protocol_quality_ui.py

import streamlit as st
import plotly.graph_objects as go
from typing import Dict

def display_quality_metrics(validation_results: Dict):
    """Display protocol quality metrics in the UI"""
    
    # Create radar chart of dimension scores
    scores = {dim: results['score'] for dim, results in validation_results.items()}
    
    fig = go.Figure(data=go.Scatterpolar(
        r=[scores[dim] for dim in scores],
        theta=list(scores.keys()),
        fill='toself'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False,
        title="Protocol Quality Dimensions"
    )

    st.plotly_chart(fig)

def display_validation_details(validation_results: Dict):
    """Display detailed validation results"""
    
    # Add expandable sections for each dimension
    for dimension, results in validation_results.items():
        with st.expander(f"{dimension.replace('_', ' ').title()} (Score: {results['score']:.2%})"):
            # Show missing items
            if results['missing_items']:
                st.markdown("#### Missing Elements:")
                for item in results['missing_items']:
                    st.error(f"• {item}")
            else:
                st.success("✓ All required elements present")

            # Show recommendations
            if results['recommendations']:
                st.markdown("#### Recommendations:")
                for rec in results['recommendations']:
                    st.info(f"• {rec}")

def display_improvement_options(validation_results: Dict, on_improve_callback):
    """Display options to improve protocol sections"""
    
    st.markdown("### 🔄 Protocol Improvement Options")
    
    # Show improvement buttons for sections with issues
    for dimension, results in validation_results.items():
        if results['missing_items']:
            if st.button(f"Improve {dimension.replace('_', ' ').title()} Section"):
                on_improve_callback(dimension)

def render_protocol_quality_ui(sections: Dict, validation_results: Dict):
    """Main UI component for protocol quality"""
    
    st.markdown("## Protocol Quality Assessment")
    
    # Overall score
    overall_score = sum(r['score'] for r in validation_results.values()) / len(validation_results)
    st.metric(
        label="Overall Protocol Quality", 
        value=f"{overall_score:.2%}",
        delta=f"{(overall_score-0.8)*100:.1f}% from target" if overall_score < 0.8 else "Meets target"
    )
    
    # Quality visualization
    col1, col2 = st.columns([2, 1])
    with col1:
        display_quality_metrics(validation_results)
    with col2:
        st.markdown("### Quality Summary")
        total_issues = sum(len(r['missing_items']) for r in validation_results.values())
        if total_issues > 0:
            st.warning(f"Found {total_issues} items needing attention")
        else:
            st.success("Protocol meets all quality criteria")
    
    # Detailed results
    st.markdown("### Detailed Assessment")
    display_validation_details(validation_results)
    
    # Improvement options
    if any(len(r['missing_items']) > 0 for r in validation_results.values()):
        st.markdown("---")
        display_improvement_options(validation_results, on_improve_callback=improve_section)

def improve_section(section_name: str):
    """Callback for section improvement"""
    with st.spinner(f"Improving {section_name} section..."):
        # Add your improvement logic here
        st.session_state.needs_update = True