import streamlit as st
import plotly.graph_objects as go
from typing import Dict

def display_quality_metrics(validation_results: Dict):
    """Display protocol quality metrics visualization"""
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
    # Show dimension-specific results
    for dimension, results in validation_results.items():
        with st.expander(f"{dimension.replace('_', ' ').title()} (Score: {results['score']:.2%})"):
            if results.get('missing_items'):
                st.markdown("#### Missing Elements:")
                for item in results['missing_items']:
                    st.error(f"• {item}")
            else:
                st.success("✓ All required elements present")

            if results.get('recommendations'):
                st.markdown("#### Recommendations:")
                for rec in results['recommendations']:
                    st.info(f"• {rec}")

def render_quality_assessment(validation_results: Dict):
    """Render the quality assessment UI"""
    st.markdown("## Protocol Quality Assessment")

    # Overall quality score
    overall_score = sum(r['score'] for r in validation_results.values()) / len(validation_results)
    st.metric(
        "Overall Protocol Quality",
        f"{overall_score:.2%}",
        f"{(overall_score-0.8)*100:.1f}% from target" if overall_score < 0.8 else "Meets target"
    )

    # Quality visualization
    col1, col2 = st.columns([2, 1])
    with col1:
        display_quality_metrics(validation_results)
    with col2:
        st.markdown("### Quality Summary")
        total_issues = sum(len(r.get('missing_items', [])) for r in validation_results.values())
        if total_issues > 0:
            st.warning(f"Found {total_issues} items needing attention")
        else:
            st.success("Protocol meets all quality criteria")

    # Detailed assessment
    st.markdown("### Detailed Assessment")
    display_validation_details(validation_results)
