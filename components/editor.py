import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter

def render_editor():
    """Render the protocol editor interface"""
    st.header("Protocol Editor")
    
    # Debug information
    st.write("Debug Info:")
    st.write(f"Synopsis Content: {'Available' if st.session_state.get('synopsis_content') else 'Not Available'}")
    st.write(f"Study Type: {st.session_state.get('study_type') if st.session_state.get('study_type') else 'Not Selected'}")
    
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
            generate_complete_protocol()
    else:
        st.warning("⚠️ Please upload a synopsis and select a study type to generate the protocol.")
    
    st.markdown("---")  # Separator
    
    # Section editing interface
    if st.session_state.get('current_section'):
        edit_section(st.session_state.current_section)
    else:
        st.info("👈 Select a section from the navigator to begin editing")

def generate_complete_protocol():
    """Generate all protocol sections in sequence"""
    generator = TemplateSectionGenerator()
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_container = st.empty()
    
    try:
        # Show spinner during generation
        with st.spinner('Generating protocol sections...'):
            total_sections = len(st.session_state.sections_status)
            completed = 0
            
            for section_name in st.session_state.sections_status.keys():
                # Update status
                status_text = f"📝 Generating {section_name.replace('_', ' ').title()} section..."
                status_container.info(status_text)
                st.session_state.sections_status[section_name] = 'In Progress'
                
                try:
                    # Generate section content
                    content = generator.generate_section(
                        section_name,
                        st.session_state.study_type,
                        st.session_state.synopsis_content,
                        st.session_state.generated_sections
                    )
                    
                    # Update session state
                    st.session_state.generated_sections[section_name] = content
                    st.session_state.sections_status[section_name] = 'Generated'
                    
                    # Update progress
                    completed += 1
                    progress_bar.progress(completed / total_sections)
                    
                except Exception as e:
                    st.error(f"❌ Error generating {section_name} section: {str(e)}")
                    st.session_state.sections_status[section_name] = 'Not Started'
                    continue
            
            # Final status update
            if completed == total_sections:
                status_container.success("✅ Protocol generation completed successfully!")
                st.balloons()
            else:
                status_container.warning(
                    f"⚠️ Protocol generation completed with {total_sections - completed} failed sections. "
                    "You can regenerate failed sections individually."
                )
                
    except Exception as e:
        st.error(f"❌ Error during protocol generation: {str(e)}")
        return False
        
    return True

def edit_section(section_name):
    """Edit individual protocol section"""
    st.subheader(section_name.replace('_', ' ').title())
    
    # Section generation button
    if section_name not in st.session_state.get('generated_sections', {}):
        if st.button(
            "📝 Generate Section",
            key=f"generate_{section_name}",
            help=f"Click to generate the {section_name} section",
            use_container_width=True
        ):
            generate_section(section_name)
            
    # Edit interface
    if section_name in st.session_state.get('generated_sections', {}):
        content = st.text_area(
            "Edit Content",
            value=st.session_state.generated_sections[section_name],
            height=400,
            key=f"edit_{section_name}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                "💾 Save Changes",
                key=f"save_{section_name}",
                help="Save your edits to this section",
                use_container_width=True
            ):
                st.session_state.generated_sections[section_name] = content
                st.success("✅ Changes saved successfully!")
                
        with col2:
            if st.button(
                "🔄 Regenerate",
                key=f"regenerate_{section_name}",
                help="Regenerate this section from scratch",
                use_container_width=True
            ):
                generate_section(section_name)
                
    # Export options
    if st.session_state.get('generated_sections'):
        st.markdown("---")
        st.subheader("Export Options")
        
        if st.button(
            "📥 Export Protocol",
            key="export_protocol",
            help="Export the complete protocol as a Word document",
            use_container_width=True
        ):
            export_protocol()

def generate_section(section_name):
    """Generate individual protocol section"""
    with st.spinner(f"Generating {section_name.replace('_', ' ').title()} section..."):
        try:
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
            
        except Exception as e:
            st.error(f"❌ Error generating section: {str(e)}")
            return False
            
    return True

def export_protocol():
    """Export complete protocol document"""
    try:
        with st.spinner("Preparing protocol document for export..."):
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
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    help="Download the complete protocol as a Word document"
                )
                
    except Exception as e:
        st.error(f"❌ Error exporting protocol: {str(e)}")
        return False
        
    return True
