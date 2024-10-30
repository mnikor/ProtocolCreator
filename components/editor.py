import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter

def render_editor():
    """Render the protocol editor interface"""
    st.header("Protocol Editor")
    
    # Debug information
    st.write("Session State Debug Info:")
    st.write({
        "Synopsis Content": "Available" if st.session_state.get('synopsis_content') else "Not Available",
        "Study Type": st.session_state.get('study_type', "Not Selected"),
        "Generated Sections": len(st.session_state.get('generated_sections', {})),
        "Current Section": st.session_state.get('current_section', "None")
    })
    
    # Generate Complete Protocol button section
    st.markdown("### 🚀 Protocol Generation")
    
    # Check conditions for generation
    can_generate = st.session_state.get('synopsis_content') and st.session_state.get('study_type')
    
    if can_generate:
        st.markdown('''
            <style>
            div.stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 20px 0;
                width: 100%;
                border: none;
                text-transform: uppercase;
                letter-spacing: 1px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            div.stButton > button:first-child:hover {
                background-color: #45a049;
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
                transform: translateY(-2px);
                transition: all 0.3s ease;
            }
            </style>''', unsafe_allow_html=True)
        
        st.markdown("Click below to generate all protocol sections based on your synopsis:")
        
        if st.button('🔄 GENERATE COMPLETE PROTOCOL', use_container_width=True):
            generate_all_sections()
    else:
        missing_items = []
        if not st.session_state.get('synopsis_content'):
            missing_items.append("- Upload a synopsis")
        if not st.session_state.get('study_type'):
            missing_items.append("- Select a study type")
            
        st.warning("⚠️ Please complete the following before generating the protocol:\n" + "\n".join(missing_items))
    
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
                status.success("✅ Protocol generation completed successfully!")
                st.balloons()
            else:
                status.warning(f"⚠️ Generated {completed}/{total_sections} sections")
                
    except Exception as e:
        st.error(f"❌ Error during generation: {str(e)}")

def edit_section(section_name):
    """Edit individual protocol section"""
    st.subheader(section_name.replace('_', ' ').title())
    
    # Section status indicator
    status = st.session_state.sections_status.get(section_name, 'Not Started')
    st.info(f"Current Status: {status}")
    
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
            if st.button("🔄 Regenerate Section", use_container_width=True):
                generate_section(section_name)
    else:
        st.warning("Section not yet generated. Use the generate button above to create content.")

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
