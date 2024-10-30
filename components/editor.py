import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter

def render_editor():
    """Render the protocol editor interface"""
    # Debug information at the top
    st.write("Debug Session State:", {
        "synopsis_content": st.session_state.get('synopsis_content', 'None'),
        "study_type": st.session_state.get('study_type', 'None'),
        "sections_status": st.session_state.get('sections_status', {}),
        "current_section": st.session_state.get('current_section', 'None')
    })

    st.header("Protocol Editor")

    # Generate Complete Protocol button
    if st.session_state.get('synopsis_content') and st.session_state.get('study_type'):
        st.markdown('''
            <style>
            div.stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 1rem;
                border-radius: 10px;
                margin: 20px 0;
                width: 100%;
            }
            div.stButton > button:first-child:hover {
                background-color: #45a049;
                border-color: #45a049;
            }
            </style>''', unsafe_allow_html=True)
        
        st.markdown("### 🚀 Generate Protocol")
        st.markdown("Click the button below to generate all protocol sections based on your synopsis.")
        
        if st.button('🔄 Generate Complete Protocol', use_container_width=True):
            generate_all_sections()
    else:
        st.warning("⚠️ Please upload a synopsis and select a study type to generate the protocol.")
    
    st.markdown("---")  # Separator

    # Section editing interface
    if st.session_state.get('current_section'):
        edit_section(st.session_state.current_section)
    else:
        st.info("👈 Select a section from the navigator to begin editing")

def generate_all_sections():
    """Generate all protocol sections"""
    generator = TemplateSectionGenerator()
    
    progress = st.progress(0)
    status = st.empty()
    
    try:
        with st.spinner('Generating protocol sections...'):
            total_sections = len(st.session_state.sections_status)
            completed = 0
            
            for section_name in st.session_state.sections_status.keys():
                status.info(f"📝 Generating {section_name.replace('_', ' ').title()}...")
                st.session_state.sections_status[section_name] = 'In Progress'
                
                try:
                    content = generator.generate_section(
                        section_name,
                        st.session_state.study_type,
                        st.session_state.synopsis_content,
                        st.session_state.generated_sections
                    )
                    
                    st.session_state.generated_sections[section_name] = content
                    st.session_state.sections_status[section_name] = 'Generated'
                    completed += 1
                    
                except Exception as e:
                    st.error(f"Error generating {section_name}: {str(e)}")
                    st.session_state.sections_status[section_name] = 'Error'
                    continue
                
                progress.progress(completed / total_sections)
            
            if completed == total_sections:
                status.success("✅ Protocol generation completed!")
                st.balloons()
            else:
                status.warning(f"⚠️ Generated {completed}/{total_sections} sections")
                
    except Exception as e:
        st.error(f"❌ Error during generation: {str(e)}")

def edit_section(section_name):
    """Edit individual protocol section"""
    st.subheader(section_name.replace('_', ' ').title())
    
    if section_name in st.session_state.generated_sections:
        content = st.text_area(
            "Edit Content",
            value=st.session_state.generated_sections[section_name],
            height=400,
            key=f"edit_{section_name}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Changes", use_container_width=True):
                st.session_state.generated_sections[section_name] = content
                st.success("✅ Changes saved!")
                
        with col2:
            if st.button("🔄 Regenerate", use_container_width=True):
                generate_section(section_name)
    else:
        st.warning("Section not yet generated")

def generate_section(section_name):
    """Generate individual protocol section"""
    try:
        with st.spinner(f"Generating {section_name.replace('_', ' ').title()} section..."):
            generator = TemplateSectionGenerator()
            content = generator.generate_section(
                section_name,
                st.session_state.study_type,
                st.session_state.synopsis_content,
                st.session_state.generated_sections
            )
            
            st.session_state.generated_sections[section_name] = content
            st.session_state.sections_status[section_name] = 'Generated'
            st.success("✅ Section generated successfully!")
            st.experimental_rerun()
            
    except Exception as e:
        st.error(f"❌ Error generating section: {str(e)}")

def export_protocol():
    """Export complete protocol document"""
    try:
        with st.spinner("Creating protocol document..."):
            formatter = ProtocolFormatter()
            doc = formatter.format_protocol(st.session_state.generated_sections)
            
            # Save temporarily
            doc.save("protocol.docx")
            
            # Provide download
            with open("protocol.docx", "rb") as file:
                st.download_button(
                    label="📥 Download Protocol",
                    data=file,
                    file_name="protocol.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            st.success("✅ Protocol exported successfully!")
            
    except Exception as e:
        st.error(f"❌ Error exporting protocol: {str(e)}")
