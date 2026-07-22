# AI_cover_letter_customizer-v2

## What It Does
A web app that uses AI to generate tailored cover letters. Paste a job description and your background, click a button, and get a professional draft. Download it as a .txt file.

## Why I Built It
Applying to jobs is time-consuming. Tailoring each cover letter manually takes 30-45 minutes. I wanted to build a tool that does the heavy lifting while keeping the human in control.

## How to Run It
1. Clone this repo
2. Install dependencies: `pip install -r requirements.txt`
3. Get a free API key from console.groq.com
4. Run: `python -m streamlit run cover_letter_app.py`
5. Paste your API key, job description, and background. Generate.

## Tech Used
- Python 3
- Streamlit (web interface)
- Groq API (AI model access)
- llama-3.1-8b-instant (the model)

## What I Learned
- **API integration:** Calling a cloud AI model from Python code.
- **Prompt engineering in code:** Building structured, repeatable prompts with f-strings.
- **Response handling:** Extracting AI-generated text from a JSON response object.
- **Error handling for APIs:** Using try/except to handle failed calls gracefully.
- **Streamlit sidebar:** Organizing settings separately from main content.

## What's New in v2
- **Two-step AI pipeline:** First AI drafts the cover letter. Second AI reviews and improves it.
- **Structured output parsing:** Reviewer provides feedback and a rewritten version.
- **Better UX:** Spinners show progress, first draft is in an expander, final version highlighted in green.
