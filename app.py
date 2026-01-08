import streamlit as st
import pandas as pd
import os
import sys

# Ensure src can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- CRITICAL FIX: Use Lite Pipeline to prevent memory crash ---
# We switched to rag_pipeline_lite because the full model (flan-t5) 
# requires more RAM than is available on this environment.
from src.rag_pipeline_lite import RAGService

# Page Configuration
st.set_page_config(
    page_title="CrediTrust Complaint Analyst", 
    page_icon="🏦",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .stChatInput {border-color: #4CAF50;}
    .main-header {font-size: 2.5rem; color: #1E3A8A;}
    </style>
""", unsafe_allow_html=True)

# Initialize RAG Service
# We use the lite service which initializes instantly and safely
@st.cache_resource
def get_rag_service():
    return RAGService()

rag = get_rag_service()

# Header
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("# 🏦")
with col2:
    st.title("CrediTrust Complaint Insights")
    st.caption("AI-Powered Analysis of Consumer Financial Protection Bureau Data")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This tool uses **RAG (Retrieval-Augmented Generation)** logic to answer questions based on customer complaints.
    
    **Scope:**
    - Credit Cards
    - Personal Loans
    - Savings Accounts
    - Money Transfers
    
    *Note: Running in Memory-Safe Mode.*
    """)
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add an initial greeting
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I analyze customer complaints. Ask me about trends, specific product issues, or payment problems."
    })

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If message has sources, show them in an expander
        if "sources" in message:
            with st.expander("🔍 View Source Complaints (Evidence)"):
                st.dataframe(message["sources"], hide_index=True)

# User Input
if prompt := st.chat_input("Ex: What are the main complaints about Credit Card late fees?"):
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing complaints database..."):
            try:
                answer, docs = rag.answer_question(prompt)
                
                st.markdown(answer)
                
                # Format sources for display
                source_data = []
                for doc in docs:
                    # Handle both dictionary (from lite mode) and object (from full mode)
                    if isinstance(doc, dict):
                        meta = doc.get('metadata', {})
                        content = doc.get('page_content', '')
                    else:
                        meta = doc.metadata
                        content = doc.page_content

                    source_data.append({
                        "Product": meta.get("product", "Unknown"),
                        "Issue": meta.get("issue", "Unknown"),
                        "Complaint ID": meta.get("complaint_id", "N/A"),
                        "Narrative Excerpt": content[:300] + "..."
                    })
                
                df_sources = pd.DataFrame(source_data)
                
                # Display sources
                if not df_sources.empty:
                    with st.expander("🔍 View Source Complaints (Evidence)"):
                        st.dataframe(df_sources, hide_index=True)
                
                # Add to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": df_sources
                })
                
            except Exception as e:
                st.error(f"An error occurred: {e}")