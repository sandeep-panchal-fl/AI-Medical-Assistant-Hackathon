import streamlit as st
import uuid
from conversation_agent import ConversationAgent
from chat_summary_agent import ChatSummaryAgent
from retrieval_agent import MedicalDataRetrieval
from report_generator_agent import ReportGeneratorAgent
from doctor_validation import SummarizeValidatedReport

# Page configuration
st.set_page_config(
    page_title="AI Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'conversation_agent' not in st.session_state:
    st.session_state.conversation_agent = ConversationAgent()
if 'summary_agent' not in st.session_state:
    st.session_state.summary_agent = ChatSummaryAgent()
if 'retrieval_agent' not in st.session_state:
    st.session_state.retrieval_agent = MedicalDataRetrieval()
if 'report_generator' not in st.session_state:
    st.session_state.report_generator = ReportGeneratorAgent()
if 'summarize_validated_report' not in st.session_state:
    st.session_state.summarize_validated_report = SummarizeValidatedReport()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_ended' not in st.session_state:
    st.session_state.conversation_ended = False
if 'chat_summary' not in st.session_state:
    st.session_state.chat_summary = None
if 'full_chat' not in st.session_state:
    st.session_state.full_chat = None
if 'medical_report' not in st.session_state:
    st.session_state.medical_report = None
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False
if 'retrieved_data' not in st.session_state:
    st.session_state.retrieved_data = None
if 'processing_stage' not in st.session_state:  # NEW: Track current processing stage
    st.session_state.processing_stage = None  # 'summary', 'retrieval', 'report'
if 'doctor_validated' not in st.session_state:
    st.session_state.doctor_validated = False
if 'doctor_action_taken' not in st.session_state:
    st.session_state.doctor_action_taken = False
if 'validated_text_ses' not in st.session_state:
    st.session_state.validated_text_ses = False
if 'edited_report' not in st.session_state:
    st.session_state.edited_report = None

# Header
st.title("🏥 AI Medical Assistant")
st.markdown("Describe your symptoms and I'll help gather information for medical assessment.")

# Sidebar - STATIC PROGRESS TRACKING
with st.sidebar:
    st.header("🩺 Assistant Controls")
    st.markdown("""
    This AI medical assistant helps you by:
    - Asking about your symptoms  
    - Understanding their severity and duration  
    - Summarizing key clinical details  
    - Retrieving relevant medical insights  
    - Generating a concise medical summary report  

    **User Guidance:**
    - This tool is for informational purposes only and **not a substitute for professional medical advice**.  
    """)
    
    if st.button("🔄 Start New Conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.conversation_agent = ConversationAgent()
        st.session_state.summary_agent = ChatSummaryAgent()
        st.session_state.retrieval_agent = MedicalDataRetrieval()
        st.session_state.report_generator = ReportGeneratorAgent()
        st.session_state.summarize_validated_report = SummarizeValidatedReport()
        st.session_state.messages = []
        st.session_state.conversation_ended = False
        st.session_state.chat_summary = None
        st.session_state.full_chat = None
        st.session_state.medical_report = None
        st.session_state.report_generated = False
        st.session_state.retrieved_data = None
        st.session_state.processing_stage = None
        st.session_state.doctor_validated = False
        st.session_state.doctor_action_taken = False
        st.session_state.validated_text_ses = False
        st.session_state.edited_report = None
        st.rerun()

    st.info("💡Send **‘stop’** in the chat to end the conversation!")

    st.markdown("---")
    st.subheader("📊 Progress")
    
    # Conversation status
    if st.session_state.conversation_ended:
        st.success("✅ Conversation Completed")
    elif st.session_state.messages:
        st.info("🔄 Conversation In-Progress")
    else:
        st.info("⏳ Conversation Not Started")
    
    # Clinical summary status
    if st.session_state.processing_stage == 'summary':
        st.warning("🔄 Generating Chat Summary...")
    elif st.session_state.chat_summary:
        st.success("✅ Chat Summary Generated")
    else:
        st.info("⏳ Chat Summary Pending")
    
    # Data retrieval status
    if st.session_state.processing_stage == 'retrieval':
        st.warning("🔍 Retrieving Medical Data...")
    elif st.session_state.retrieved_data:
        st.success("✅ Medical Data Retrieved")
    else:
        st.info("⏳ Medical Data Retrieval Pending")
    
    # Report status
    if st.session_state.processing_stage == 'report':
        st.warning("🏥 Generating Medical Report...")
    elif st.session_state.report_generated:
        st.success("✅ Medical Report Generated")
    else:
        st.info("⏳ Medical Report Pending")

    # Doctor validation
    if st.session_state.processing_stage == 'doctor_validation_stage':
        st.warning("🏥 Doctor Validation In-Progress ...")
    elif st.session_state.doctor_validated:
        st.success("✅ Medical Validation Completed")
    else:
        st.info("⏳ Doctor Validation Pending")

    # Session info
    st.markdown("---")
    st.write(f"**Session ID:** `{st.session_state.session_id}`")
    st.write(f"**Messages:** {len(st.session_state.messages)}")
    if st.session_state.processing_stage:
        st.write(f"**Current Stage:** {st.session_state.processing_stage.title()}")

# Main content area - ONLY CONVERSATION AND RESULTS
st.subheader("💬 Conversation")

# Display conversation
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                # st.markdown(message["content"])
                st.markdown(f"**You:** {message['content']}")
        else:
            with st.chat_message("assistant"):
                # st.markdown(message["content"])
                st.markdown(f"**Assistant:** {message['content']}")
    
    if st.session_state.conversation_ended:
        with st.chat_message("assistant"):
            st.info("Conversation Ended!")

# Chat input (only show if conversation is active)
if not st.session_state.conversation_ended:
    if prompt := st.chat_input("👤 Describe your symptoms...    OR   Send ‘stop’ to end the conversation!"):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(f"**You:** {prompt}")
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 **Thinking...**"):
                response, conversation_ended, full_chat = st.session_state.conversation_agent.chat(
                    st.session_state.session_id, prompt
                )
                
                # Display AI response
                st.markdown(f"**Assistant:** {response}")
                
                # Add AI response to messages
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Handle conversation end
                if conversation_ended :
                    st.session_state.conversation_ended = True
                    st.session_state.full_chat = full_chat
                    st.session_state.processing_stage = 'summary'
                    print("st.session_state.full_chat", st.session_state.full_chat)
                    st.rerun()

# Step 1: Set chat summary and show processing
if st.session_state.processing_stage == 'summary':
    with st.spinner("🔍 **Generating Chat Summary...**", show_time=True):
        chat_summary = st.session_state.summary_agent.generate_chat_summary(st.session_state.full_chat)
        st.session_state.chat_summary = chat_summary
        st.session_state.processing_stage = 'retrieval'
        print("st.session_state.full_chat", st.session_state.chat_summary)
        st.rerun()

# Clinical Summary Section
if st.session_state.chat_summary:
    st.markdown("---")
    st.subheader("📋 Chat Summary")
    with st.expander("View Chat Summary"):
        st.text_area(
            "Chat Summary", 
            st.session_state.chat_summary, 
            height=150, 
            key="chat_summary_display", 
            label_visibility="collapsed"
        )

# Step 2: Retrieve medical data
if st.session_state.processing_stage == 'retrieval':
    with st.spinner("🔍 **Retrieving Medical Information...**", show_time=True):
        retrieved_data = st.session_state.retrieval_agent.retrieve_data(st.session_state.chat_summary)
        st.session_state.retrieved_data = retrieved_data
        st.session_state.processing_stage = 'report'
        print("st.session_state.retrieved_data", st.session_state.retrieved_data)
        st.rerun()

# Step 3: Generate medical report with retrieved data
if st.session_state.processing_stage == 'report':
    with st.spinner("🏥 **Generating Medical Report...**", show_time=True):
        medical_report = st.session_state.report_generator.generate_final_medical_report(
            full_chat=st.session_state.full_chat,
            chat_summary=st.session_state.chat_summary,
            retrieved_knowledge=st.session_state.retrieved_data
        )

        st.session_state.medical_report = medical_report
        st.session_state.report_generated = True

        st.session_state.processing_stage = 'doctor_validation_stage'
        print("st.session_state.medical_report", st.session_state.medical_report)

        # Final rerun to show everything
        st.rerun()

# Medical Report Section
if st.session_state.medical_report:
    st.markdown("---")
    st.subheader("🏥 Medical Assessment Report")
    
    # Enhanced report display
    with st.expander("View Medical Report", expanded=True):
        # Add styling to the report
        st.markdown("""
        <style>
        .medical-report {
            background-color: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="medical-report">{st.session_state.medical_report}</div>', unsafe_allow_html=True)
    
    # Download button
    st.download_button(
        label="📥 Download Medical Report",
        data=st.session_state.medical_report,
        file_name=f"medical_report_{st.session_state.session_id}.txt",
        mime="text/plain",
        use_container_width=True
    )

# Show conversation analytics
with st.expander("📊 Conversation Details"):
    st.write(f"Session ID: {st.session_state.session_id}")
    st.write(f"Total Messages: {len(st.session_state.messages)}")
    st.write(f"Conversation Ended: {st.session_state.conversation_ended}")
    st.write(f"Full Chat Available: {st.session_state.full_chat is not None}")
    st.write(f"Chat Summary Available: {st.session_state.chat_summary is not None}")
    st.write(f"Retrieved Data Available: {st.session_state.retrieved_data is not None}")
    st.write(f"Medical Report Generated: {st.session_state.report_generated}")
    st.write(f"Current Processing Stage: {st.session_state.processing_stage}")
    
    if st.session_state.retrieved_data:
        st.write(f"Number of Retrieved Results: {len(st.session_state.retrieved_data)}")

# Full Chat Data
if st.session_state.medical_report:
    with st.expander("📜 View Full Chat"):
        st.json(st.session_state.full_chat)

# After report generation
if st.session_state.medical_report:
    st.markdown("---")
    st.subheader("🩺 Doctor Validation")

    st.markdown("""
    Review the generated report below.  
    You can make changes to the diagnosis, medicines, or treatment if necessary.
    """)

    # Disable once validated
    text_area_disabled = st.session_state.doctor_action_taken
    button_disabled = st.session_state.doctor_action_taken
    
    if not text_area_disabled:
        display_report = st.session_state.medical_report
    else:
        display_report = st.session_state.edited_report

    validated_text = st.text_area(
        "Edit or Validate Report",
        display_report,
        height=300,
        key="doctor_validation_area",
        disabled=text_area_disabled
    )

    st.session_state.edited_report = validated_text.strip()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Validate & Save", use_container_width=True, disabled=button_disabled):
            with st.spinner("Checking doctor modifications...", show_time=True):

                if st.session_state.edited_report != st.session_state.medical_report.strip():
                    st.session_state.summarize_validated_report.summarize_doctor_validated_report(st.session_state.edited_report)
                    st.success("✅ Doctor-modified report saved")
                else:
                    st.info("🟡 No modifications detected — skipping storage.")

                st.session_state.processing_stage = None
                st.session_state.doctor_validated = True
                st.session_state.doctor_action_taken = True
                st.rerun()

    with col2:
        if st.button("🚫 No Modification", use_container_width=True, disabled=button_disabled):
            st.info("🟡 No modifications done by doctor — skipping storage.")
            st.session_state.processing_stage = None
            st.session_state.doctor_validated = True
            st.session_state.doctor_action_taken = True
            st.rerun()

    # 🔒 After doctor action, show message and keep section visible but locked
    if st.session_state.doctor_action_taken:
        st.markdown("### 🔒 Report locked after doctor validation.")
        st.markdown("You can view but not modify the report now.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 14px;'>
    <div>💡 Send <strong>‘stop’</strong> in the chat to end conversation and generate report</div>
    <div>⚠️ For emergencies, contact emergency services immediately</div>
    </div>
    """, 
    unsafe_allow_html=True
)