# Interview Coach AI

A Python + Streamlit app for interview practice. Choose a job role, get practice questions, submit answers, and review constructive coaching feedback.

## Features
- Role, experience level, interview type, difficulty, and question-count settings
- AI-generated questions and answer feedback when an OpenAI API key is configured
- Demo mode without an API key
- Per-answer coaching score, strengths, improvement suggestions, sample answer, and follow-up
- Session summary and optional local session history
- Simple interface designed for local use

## Requirements
- Python 3.11 or newer recommended
- Internet access for OpenAI API mode
- An OpenAI API key for AI features (API usage may incur charges)

## Windows PowerShell setup
```powershell
cd path\to\ai-interview-practice
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
streamlit run app.py
```
Put your API key after `OPENAI_API_KEY=` in `.env`. Save the file and restart the app. If PowerShell blocks activation, you can run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py` without activating the environment.

## macOS / Linux setup
```bash
cd ai-interview-practice
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```
Edit `.env`, add your API key, then run:
```bash
streamlit run app.py
```

## Demo mode
If `OPENAI_API_KEY` is blank, the app uses sample questions and clearly basic, simulated coaching feedback. This allows the UI to be explored without an API key. In AI mode, the app sends the question and answer to the configured OpenAI API. Do not submit sensitive personal information.

## Voice answers
Typed answers work by default. This initial version does not bundle a browser microphone recorder or speech-to-text engine because availability varies by browser and deployment. You can paste a transcript into the answer field. Voice support can be added later using a compatible Streamlit audio-recording component and a transcription API.

## Tests
```bash
pytest
```

## Troubleshooting
- **`streamlit` not found:** activate `.venv`, then run `python -m pip install -r requirements.txt`.
- **Missing API key:** use demo mode or add a valid key to `.env`.
- **API errors:** check network access, key validity, account billing, and model availability.
- **Port is busy:** run `streamlit run app.py --server.port 8502`.

## Privacy and costs
Answers may be sent to the AI provider when AI mode is enabled. Session history is stored locally in `interview_history.json`; it can contain personal information. Delete that file to remove saved sessions. API calls may cost money. AI scores are approximate coaching guidance, not a hiring prediction.

## GitHub
The `.gitignore` file excludes `.env`, virtual environments, Python caches, and local history. Before pushing, run `git status` and confirm `.env` is not staged.
