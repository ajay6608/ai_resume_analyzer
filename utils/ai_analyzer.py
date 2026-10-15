"""
ai_analyzer.py
--------------
Sends resume text to Google Gemini (free tier) and gets back a structured analysis.

Key idea (worth understanding for interviews): we don't just ask the model
"analyze this resume" and hope for readable prose. We give it a strict
JSON schema to fill in, so the output is *structured data* our app can
render as cards/scores/lists reliably, not just a block of text.
"""

import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.5-flash-lite"  # alias that always points to Google's current stable Flash model

SYSTEM_PROMPT = """You are an expert technical recruiter and resume/ATS (Applicant \
Tracking System) reviewer. You review resumes for tech/CS roles and give honest, \
specific, actionable feedback.

You must respond with ONLY valid JSON matching this exact schema, and nothing else \
(no markdown code fences, no preamble, no explanation outside the JSON):

{
  "overall_score": <integer 0-100>,
  "ats_score": <integer 0-100>,
  "strengths": [<3-5 short strings>],
  "weaknesses": [<3-5 short strings>],
  "missing_skills": [<list of relevant skills/keywords missing for the target role, \
based on what's implied by the resume's field. If a target role is given, tailor to it>],
  "grammar_suggestions": [<specific grammar/phrasing fixes, quote the problematic \
phrase and suggest a fix. Empty list if none found>],
  "summary": "<2-3 sentence overall verdict>"
}

Scoring guidance:
- overall_score: holistic quality (impact of bullet points, clarity, relevance, structure).
- ats_score: how well this would parse/rank in an automated ATS keyword scan \
(standard section headers, no images/tables-in-text, keyword coverage for the field).
Be honest and specific. Do not inflate scores. Avoid generic feedback like \
"add more skills" without naming which skills.
"""


def _build_user_prompt(resume_text: str, target_role) -> str:
    role_line = (
        f"The candidate is targeting this specific role/field: {target_role}\n\n"
        if target_role
        else "No specific target role was given — infer the likely field from the resume itself.\n\n"
    )
    return (
        f"{role_line}"
        f"Here is the resume text (extracted from PDF, formatting may be imperfect):\n\n"
        f"---\n{resume_text}\n---\n\n"
        f"Analyze this resume and respond with the JSON object as specified."
    )


def _extract_json(raw_text: str) -> dict:
    """
    Defensive parsing: even with a strict system prompt, models occasionally
    wrap output in ```json fences. Strip those before parsing.
    """
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def analyze_resume(resume_text: str, target_role=None) -> dict:
    """
    Send resume text to Gemini and return a parsed analysis dict.

    Args:
        resume_text: cleaned plain text extracted from the resume PDF.
        target_role: optional role the user is applying for (e.g. "ML Engineer").

    Returns:
        dict matching the schema described in SYSTEM_PROMPT.

    Raises:
        RuntimeError: if the API call fails or the response can't be parsed.
    """
    raw_text = ""
    try:
        model = genai.GenerativeModel(
            model_name=MODEL,
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(
            _build_user_prompt(resume_text, target_role),
            generation_config={"response_mime_type": "application/json"},
        )
        raw_text = response.text
        return _extract_json(raw_text)

    except json.JSONDecodeError as e:
        raise RuntimeError(f"Model returned invalid JSON: {e}\nRaw output: {raw_text}")
    except Exception as e:
        raise RuntimeError(f"AI analysis failed: {e}")
