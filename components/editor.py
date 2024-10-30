import streamlit as st
from utils.template_section_generator import TemplateSectionGenerator
from utils.protocol_formatter import ProtocolFormatter

def render_editor():
    """Render the protocol editor interface"""
    st.header('Protocol Editor')
    
    # Make the generate button more prominent with custom styling
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #4CAF50;
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 1rem;
            border-radius: 10px;
            margin: 20px 0;
            width: 100%;
        }
        div.stButton > button:hover {
            background-color: #45a049;
            border-color: #45a049;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Add clear instructions above the button
    st.markdown("""
        ### Generate Complete Protocol
        Click the button below to automatically generate all protocol sections based on your synopsis.
        Progress will be shown in real-time.
    """)
    
    # Make the button more prominent and accessible
    if st.button('🔄 Generate Complete Protocol', 
                 key='generate_protocol_btn',
                 help='Click to generate all protocol sections automatically',
                 use_container_width=True):
        generate_complete_protocol()
        
    st.markdown('---')  # Add separator line
    
    if st.session_state.current_section:
        edit_section(st.session_state.current_section)
    else:
        # Add a more informative message with visual cue
        st.info("👈 Select a section from the navigator to begin editing")

def generate_complete_protocol():
    """Generate all protocol sections in sequence"""
    generator = TemplateSectionGenerator()
    
    # Create a more visible progress indicator
    st.markdown("### Generation Progress")
    progress_bar = st.progress(0)
    status_container = st.empty()
    
    # Add a spinning indicator during generation
    with st.spinner('Generating protocol sections...'):
        total_sections = len(st.session_state.sections_status)
        completed = 0
        
        try:
            for section_name in st.session_state.sections_status.keys():
                # Update progress with more detailed status
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
            
            # Final status update with clear success/failure indication
            if completed == total_sections:
                status_container.success("✅ Protocol generation completed successfully!")
                st.balloons()  # Add visual celebration
            else:
                status_container.warning(
                    f"⚠️ Protocol generation completed with {total_sections - completed} failed sections. "
                    "You can regenerate failed sections individually."
                )
                
        except Exception as e:
            status_container.error(f"❌ Error during protocol generation: {str(e)}")

def edit_section(section_name):
    """Edit individual protocol section"""
    st.subheader(section_name.replace('_', ' ').title())
    
    # Generate button if section not yet generated
    if section_name not in st.session_state.generated_sections:
        st.button(
            "📝 Generate Section",
            key=f"generate_{section_name}",
            help=f"Click to generate the {section_name} section",
            on_click=lambda: generate_section(section_name)
        )
            
    # Edit interface
    if section_name in st.session_state.generated_sections:
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
                help="Save your edits to this section"
            ):
                st.session_state.generated_sections[section_name] = content
                st.success("✅ Changes saved successfully!")
                
        with col2:
            if st.button(
                "🔄 Regenerate",
                key=f"regenerate_{section_name}",
                help="Regenerate this section from scratch"
            ):
                generate_section(section_name)
                
    # Export options
    if st.session_state.generated_sections:
        st.markdown("---")
        st.subheader("Export Options")
        if st.button(
            "📥 Export Protocol",
            key="export_protocol",
            help="Export the complete protocol as a Word document"
        ):
            export_protocol()

def generate_section(section_name):
    """Generate individual protocol section using templates"""
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

def export_protocol():
    """Export complete protocol document"""
    try:
        with st.spinner("Preparing protocol document for export..."):
            formatter = ProtocolFormatter()
            doc = formatter.format_protocol(st.session_state.generated_sections)
            
            # Save temporarily and provide download link
            doc.save("protocol.docx")
            
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
