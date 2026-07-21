"""
app.py
------
AI Resume Analyzer — main Streamlit app.

Flow:
1. User uploads a PDF resume (and optionally types a target role).
2. We extract text from the PDF (utils/pdf_extractor.py).
3. We send that text to Claude for structured analysis (utils/ai_analyzer.py).
4. We render the results as scores, lists, and suggestions.
"""

import streamlit as st
from utils.pdf_extractor import extract_text_from_pdf, basic_clean
from utils.ai_analyzer import analyze_resume

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="centered")

st.title("📄 AI Resume Analyzer")
st.write(
    "Upload your resume as a PDF and get an instant AI-powered review: "
    "an overall score, an ATS-friendliness score, strengths, weaknesses, "
    "missing skills, and grammar suggestions."
)

with st.sidebar:
    st.header("Settings")
    target_role = st.text_input(
        "Target role (optional)",
        placeholder="e.g. Machine Learning Engineer",
        help="If you tell us the role you're applying for, the analysis (especially "
        "missing skills) will be tailored to it.",
    )
    st.caption(
        "Tip: Leave this blank and the AI will infer your field from the resume itself."
    )

uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

analyze_clicked = st.button("Analyze Resume", type="primary", disabled=uploaded_file is None)

if analyze_clicked and uploaded_file is not None:
    try:
        with st.spinner("Extracting text from your PDF..."):
            raw_text = extract_text_from_pdf(uploaded_file)
            resume_text = basic_clean(raw_text)

        with st.spinner("Analyzing your resume with AI... (this can take 10-20s)"):
            result = analyze_resume(resume_text, target_role or None)

        st.success("Analysis complete!")

        # ---- Scores ----
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall Score", f"{result['overall_score']}/100")
        with col2:
            st.metric("ATS Score", f"{result['ats_score']}/100")

        st.info(result.get("summary", ""))

        # ---- Strengths ----
        st.subheader("✅ Strengths")
        for item in result.get("strengths", []):
            st.markdown(f"- {item}")

        # ---- Weaknesses ----
        st.subheader("⚠️ Weaknesses")
        for item in result.get("weaknesses", []):
            st.markdown(f"- {item}")

        # ---- Missing Skills ----
        st.subheader("🧩 Missing Skills")
        missing_skills = result.get("missing_skills", [])
        if missing_skills:
            st.markdown(" ".join(f"`{skill}`" for skill in missing_skills))
        else:
            st.markdown("None identified — good keyword coverage!")

        # ---- Grammar Suggestions ----
        st.subheader("✍️ Grammar Suggestions")
        grammar = result.get("grammar_suggestions", [])
        if grammar:
            for g in grammar:
                st.markdown(f"- {g}")
        else:
            st.markdown("No grammar issues found.")

        # ---- Raw extracted text (collapsible, useful for debugging) ----
        with st.expander("View extracted resume text"):
            st.text(resume_text)

    except ValueError as e:
        st.error(str(e))
    except RuntimeError as e:
        st.error(f"Something went wrong during analysis: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

elif uploaded_file is None:
    st.caption("Upload a PDF to get started.")
