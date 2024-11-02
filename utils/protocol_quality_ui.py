import streamlit as st
import plotly.graph_objects as go
from typing import Dict
import logging
import time

logger = logging.getLogger(__name__)

def display_quality_metrics(validation_results: Dict, key_suffix=''):
    # Create radar chart of dimension scores
    scores = {}
    for dim, results in validation_results.items():
        if dim == 'overall_score':
            continue
            
        if isinstance(results, dict) and 'score' in results:
            scores[dim] = results['score']
        elif isinstance(results, (int, float)):
            scores[dim] = float(results)
    
    if not scores:
        st.warning("No quality metrics available")
        return
        
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

    st.plotly_chart(fig, key=f"quality_metrics_{key_suffix}")

def display_validation_details(validation_results: Dict, key_suffix=''):
    for dimension, results in validation_results.items():
        if not isinstance(results, dict) or dimension == 'overall_score':
            continue
            
        with st.expander(
            f"{dimension.replace('_', ' ').title()} (Score: {results.get('score', 0):.2%})", 
            key=f"expander_{dimension}_{key_suffix}"
        ):
            if results.get('missing_items'):
                st.markdown("#### Missing Elements:")
                for idx, item in enumerate(results['missing_items']):
                    st.error(f"• {item}", key=f"error_{dimension}_{idx}_{key_suffix}")
            else:
                st.success("✓ All required elements present", key=f"success_{dimension}_{key_suffix}")

            if results.get('recommendations'):
                st.markdown("#### Recommendations:")
                for idx, rec in enumerate(results['recommendations']):
                    st.info(f"• {rec}", key=f"info_{dimension}_{idx}_{key_suffix}")

def render_quality_assessment(validation_results: Dict):
    current_time = int(time.time())
    key_suffix = f"{current_time}"
    
    try:
        # Calculate overall score safely
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
        
        # Calculate overall score
        overall_score = (total_score / valid_scores) if valid_scores > 0 else 0.0
        
        # Display overall score
        st.metric(
            "Overall Protocol Quality",
            f"{overall_score:.2%}",
            f"{(overall_score-0.8)*100:.1f}% from target" if overall_score < 0.8 else "Meets target",
            key=f"metric_overall_{key_suffix}"
        )
        
        # Quality visualization in main column
        display_quality_metrics(validation_results, key_suffix)
        
        # Quality summary
        st.markdown("### Quality Summary")
        total_issues = sum(
            len(r.get('missing_items', [])) 
            for r in validation_results.values() 
            if isinstance(r, dict) and 'missing_items' in r
        )
        if total_issues > 0:
            st.warning(f"Found {total_issues} items needing attention", key=f"warning_issues_{key_suffix}")
        else:
            st.success("Protocol meets all quality criteria", key=f"success_all_{key_suffix}")
        
        # Detailed assessment
        st.markdown("### Detailed Assessment")
        display_validation_details(validation_results, key_suffix)
        
    except Exception as e:
        logger.error(f"Error in quality assessment: {str(e)}")
        st.error("Error calculating quality metrics")
