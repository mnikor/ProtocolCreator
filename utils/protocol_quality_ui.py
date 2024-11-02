import streamlit as st
import plotly.graph_objects as go
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def display_quality_metrics(validation_results: Dict, key_suffix: str = ""):
    try:
        # Convert scores to 0-10 scale and create bar chart
        scores = {}
        for dim, results in validation_results.items():
            if dim == 'overall_score':
                continue
                
            if isinstance(results, dict) and 'score' in results:
                scores[dim.replace('_', ' ').title()] = round(results['score'] * 10, 1)
            elif isinstance(results, (int, float)):
                scores[dim.replace('_', ' ').title()] = round(float(results) * 10, 1)
        
        if not scores:
            st.warning("No quality metrics available")
            return
            
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=list(scores.values()),
                y=list(scores.keys()),
                orientation='h',
                marker_color='rgb(26, 118, 255)',
                text=[f"{score:.1f}/10" for score in scores.values()],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Protocol Quality Dimensions",
            xaxis_title="Score (0-10)",
            xaxis=dict(range=[0, 10]),
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        
        # Add unique key to plotly chart
        st.plotly_chart(fig, use_container_width=True, key=f"quality_chart_{key_suffix}")
        
    except Exception as e:
        logger.error(f"Error displaying quality metrics: {str(e)}")
        st.warning("Could not display quality metrics visualization")

def display_validation_details(validation_results: Dict, key_suffix: str = ""):
    for dimension, results in validation_results.items():
        if not isinstance(results, dict) or dimension == 'overall_score':
            continue
            
        # Remove key from expander
        with st.expander(
            f"{dimension.replace('_', ' ').title()} (Score: {results.get('score', 0)*10:.1f}/10)"
        ):
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

def render_quality_assessment(validation_results: Dict, key_suffix: str = ""):
    try:
        # Calculate overall score on 0-10 scale
        total_score = 0.0
        valid_scores = 0
        
        for dimension, results in validation_results.items():
            if dimension == 'overall_score':
                continue
                
            score = None
            if isinstance(results, dict) and 'score' in results:
                score = results['score']
            elif isinstance(results, (int, float)):
                score = float(results)
                
            if score is not None:
                total_score += score
                valid_scores += 1
        
        # Calculate overall score on 0-10 scale
        overall_score = (total_score / valid_scores * 10) if valid_scores > 0 else 0.0
        
        # Display overall score with unique key
        st.metric(
            label="Overall Protocol Quality",
            value=f"{overall_score:.1f}/10",
            delta=f"{(overall_score-8):.1f} points from target" if overall_score < 8 else "Meets target",
            delta_color="inverse",
            key=f"quality_metric_{key_suffix}"
        )
        
        # Quality visualization with unique key
        display_quality_metrics(validation_results, key_suffix)
        
        # Quality summary
        st.markdown("### Quality Summary")
        total_issues = sum(
            len(r.get('missing_items', [])) 
            for r in validation_results.values() 
            if isinstance(r, dict) and 'missing_items' in r
        )
        if total_issues > 0:
            st.warning(f"Found {total_issues} items needing attention")
        else:
            st.success("Protocol meets all quality criteria")
        
        # Detailed assessment
        st.markdown("### Detailed Assessment")
        display_validation_details(validation_results, key_suffix)
        
    except Exception as e:
        logger.error(f"Error in quality assessment: {str(e)}")
        st.error("Error calculating quality metrics")
