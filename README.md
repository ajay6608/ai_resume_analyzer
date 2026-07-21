# AI Resume Analyzer

Upload a PDF resume, get an instant AI-powered analysis: overall score, ATS score,
strengths, weaknesses, missing skills, and grammar suggestions — in a clean web UI.

## Tech Stack
- **Streamlit** — web UI (Python only, no separate frontend needed)
- **pdfplumber** — PDF text extraction
- **Google Gemini API (free tier)** — resume analysis via a structured-JSON prompt

## Project Structure
```
resume_analyzer/
├── app.py                  # Streamlit UI + main flow
├── utils/
│   ├── pdf_extractor.py    # PDF -> text
│   └── ai_analyzer.py      # text -> AI analysis (calls Claude, parses JSON)
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a free API key**: go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey),
   sign in with a Google account, and click "Create API key." No credit card needed
   for the free tier.

4. **Set up your environment file**:
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and paste your key:
   ```
   GEMINI_API_KEY=AIza...
   ```

5. **Run the app**:
   ```bash
   streamlit run app.py
   ```
   It will open in your browser at `http://localhost:8501`.

## How It Works (for your resume/interview talking points)

1. **PDF → text**: `pdfplumber` extracts raw text page by page.
2. **Prompt engineering**: instead of asking the model to "review this resume" in
   free text, `ai_analyzer.py` gives it a strict JSON schema (scores, lists, etc.)
   to fill in. This turns an LLM into a *structured data* source your app can
   render reliably — a core pattern in real AI products.
3. **Defensive parsing**: the code strips markdown code fences and handles
   JSON parse errors gracefully, since LLM output isn't always perfectly clean.
4. **UI**: Streamlit renders the parsed JSON as metrics, lists, and tags.

## Ideas for Version 2 (nice additions once V1 works)
- Support DOCX uploads too (using `python-docx`).
- Compare resume against a pasted job description for role-specific fit scoring.
- Highlight suggested edits directly on the extracted text.
- Add a "before/after" score history if the user re-uploads after editing.
- Move from Streamlit to Flask/FastAPI + React for a more "full-stack" portfolio piece.
- Deploy it (Streamlit Community Cloud is free and easy) so you can link a live demo
  on your resume/LinkedIn — recruiters love a clickable demo link.

## Notes
- Works best on **text-based PDFs**. Scanned/image resumes won't extract text
  (would need OCR — a good V2 addition if you want to explore that).
- Keep your `.env` file out of version control (already covered if you add a
  `.gitignore` with `.env` in it before pushing to GitHub).
