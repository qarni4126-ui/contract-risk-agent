import streamlit as st
import os
import traceback
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

from langchain_groq import ChatGroq

from loader.loader import load_document
from processor.chunker import split_contract
from extractor.extractor import extract_all_clauses
from risk.scorer import score_contract, calculate_contract_risk_score
from embedder.embedder import ContractRAG
from rag.qa import ContractQA
from utils.prompts import SUMMARY_PROMPT
from pdf_generator import generate_risk_report_pdf

# =====================================================
# CONFIGURATION
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Load exact .env beside app.py for local development
load_dotenv(dotenv_path=ENV_PATH, override=True)

st.set_page_config(
    page_title="Contract Risk Agent",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =====================================================
# CACHED FUNCTIONS
# =====================================================

@st.cache_data(show_spinner=False)
def load_and_process_document(_file_bytes, file_name: str):
    temp_path = BASE_DIR / f"temp_{file_name}"
    
    with open(temp_path, "wb") as f:
        f.write(_file_bytes)

    try:
        raw_text = load_document(str(temp_path))
        chunks = split_contract(raw_text)
        chunks = extract_all_clauses(chunks)
        chunks = score_contract(chunks)
        risk_summary = calculate_contract_risk_score(chunks)
        return raw_text, chunks, risk_summary
    finally:
        if temp_path.exists():
            temp_path.unlink()

@st.cache_resource(show_spinner=False)
def get_llm(api_key: str):
    return ChatGroq(
        model_name="llama-3.1-8b-instant",
        groq_api_key=api_key
    )

@st.cache_resource(show_spinner=False)
def init_rag(chunks):
    rag = ContractRAG()
    rag.add_chunks(chunks)
    return rag

# =====================================================
# HEADER
# =====================================================
st.title("📋 Contract Risk Agent")
st.caption("Simple contract analysis in seconds")

# =====================================================
# API KEY HANDLING
# =====================================================
# Priority: Streamlit Secrets (Cloud) -> Environment Variable -> Manual Input
if "GROQ_API_KEY" in st.secrets:
    groq_key = st.secrets["GROQ_API_KEY"]
else:
    groq_key = os.getenv("GROQ_API_KEY", "").strip()

with st.sidebar:
    st.header("🔑 Settings")
    if not groq_key:
        manual_key = st.text_input("Enter Groq API Key", type="password")
        if manual_key:
            groq_key = manual_key.strip()
            os.environ["GROQ_API_KEY"] = groq_key

if not groq_key:
    st.error("❌ GROQ_API_KEY not found. Please add it to Streamlit Secrets or enter it in the sidebar.")
    st.stop()

# =====================================================
# FILE UPLOAD
# =====================================================
uploaded_file = st.file_uploader(
    "📤 Upload Contract",
    type=["pdf", "docx", "png", "jpg", "jpeg", "bmp", "txt", "eml"]
)

# =====================================================
# MAIN EXECUTION (WITH ERROR HANDLING)
# =====================================================
if uploaded_file:
    try:
        with st.spinner("⏳ Analyzing contract..."):
            raw_text, chunks, risk_summary = load_and_process_document(
                uploaded_file.getbuffer(),
                uploaded_file.name
            )

        st.success("✅ Analysis Complete")
        st.markdown("---")

        # Risk Dashboard
        col1, col2 = st.columns(2)
        with col1:
            score = risk_summary["overall_score"]
            level = risk_summary["overall_level"]
            if level == "HIGH": st.error(f"### ⚠️ HIGH RISK\n**{score}/100**")
            elif level == "MEDIUM": st.warning(f"### ⚠️ MEDIUM RISK\n**{score}/100**")
            else: st.success(f"### ✅ LOW RISK\n**{score}/100**")
        
        with col2:
            st.metric("High Risk Issues", risk_summary["high_risk_count"])
            st.metric("Medium Risk Issues", risk_summary["medium_risk_count"])
            st.metric("Total Issues", risk_summary["total_risks"])

        st.markdown("---")

        # Top Risks
        if risk_summary["top_risks"]:
            st.subheader("🔴 Top Risk Issues")
            for i, risk in enumerate(risk_summary["top_risks"], start=1):
                with st.expander(f"{i}. {risk['risk_text'][:80]}"):
                    st.write(f"**Risk Score:** {risk['score']}/100")
                    st.write(f"**Category:** {risk['category']}")
                    if risk.get("reasons"):
                        for reason in risk["reasons"][:3]:
                            st.write(f"- {reason}")

        st.markdown("---")

        # Summary
        st.subheader("📝 AI Summary")
        with st.spinner("Generating summary..."):
            llm = get_llm(groq_key)
            summary = llm.invoke(SUMMARY_PROMPT.format(contract_text=raw_text[:4000])).content
        st.info(summary)

        st.markdown("---")

        # PDF
        st.subheader("📥 Download Report")
        pdf_bytes = generate_risk_report_pdf(
            filename=uploaded_file.name,
            risk_summary=risk_summary,
            summary=summary
        )
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"risk_report_{uploaded_file.name.split('.')[0]}.pdf",
            mime="application/pdf"
        )

        st.markdown("---")

        # Q&A
        st.subheader("💬 Ask Questions About This Contract")
        rag = init_rag(chunks)
        qa = ContractQA(rag)
        question = st.text_input("Type your question:", placeholder="Example: What are payment terms?")

        if question.strip():
            with st.spinner("Searching contract..."):
                answer = qa.answer_question(question)
            st.markdown("### Answer")
            st.write(answer["answer"])
            if answer.get("sources"):
                with st.expander("📌 Source Sections"):
                    for i, source in enumerate(answer["sources"], start=1):
                        st.caption(f"{i}. {source['header']} (Relevance: {source['similarity']:.0%})")
                        st.caption(source["preview"])
            st.success("✅ Question answered!")

    except Exception as e:
        # THIS IS THE CRITICAL CHANGE: It will now show the actual error
        st.error("🚨 An error occurred during analysis!")
        st.exception(e)
        st.stop()
else:
    st.info("👆 Upload a contract file to begin.")
