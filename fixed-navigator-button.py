def render_navigator():
    """Render the section navigator sidebar"""
    # Debug information at the top
    with st.sidebar.expander("🔍 Debug Info", expanded=True):
        st.write({
            "Synopsis Present": st.session_state.get('synopsis_content') is not None,
            "Synopsis Length": len(st.session_state.get('synopsis_content', '')) if st.session_state.get('synopsis_content') else 0,
            "Study Type": st.session_state.get('study_type'),
            "Sections Status": st.session_state.get('sections_status', {}),
            "Current Section": st.session_state.get('current_section')
        })

    # Protocol Generation Section
    st.sidebar.markdown("## 🚀 Protocol Generation")
    
    # Update the condition check
    if st.session_state.get('synopsis_content') is not None and st.session_state.get('study_type'):
        st.sidebar.markdown("Generate a complete protocol from your synopsis")
        
        # Add some spacing and styling
        st.sidebar.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 0.5rem;
                border-radius: 5px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Primary generation button
        if st.sidebar.button(
            "🚀 Generate Complete Protocol",
            help="Generate all protocol sections at once",
            use_container_width=True
        ):
            try:
                with st.spinner("Generating complete protocol..."):
                    generate_all_sections()
            except Exception as e:
                st.error(f"Error generating protocol: {str(e)}")
    else:
        if st.session_state.get('synopsis_content') is None:
            st.sidebar.warning("⚠️ Please upload synopsis first")
        if not st.session_state.get('study_type'):
            st.sidebar.warning("⚠️ Please select study type")

    st.sidebar.markdown("---")
    
    # Rest of your navigator code...