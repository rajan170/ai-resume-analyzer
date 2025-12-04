# AI-Driven Resume Analyser

A local, AI-powered recruitment tool built with Streamlit, spaCy, and MongoDB. This application automates the process of parsing resumes, storing candidate profiles, and matching them with open job opportunities based on skill relevance.

## Features

- **Resume Parsing**: Automatically extracts Name, Email, Phone, Skills, and **Job Title** from PDF and DOCX resumes.
- **AI-Powered Analysis**: Uses local LLMs (via Ollama) to provide detailed qualitative feedback and career advice.
- **Smart Candidate Database**: 
    - Stores profiles with "Name - Job Title" convention.
    - Full management capabilities: Edit names, delete profiles, and view detailed info.
- **Job Management**: Post job openings and manage requirements.
- **Intelligent Matching**: 
    - **Semantic Search**: Uses `sentence-transformers` to match candidates based on meaning, not just keywords.
    - **Keyword Scoring**: Boosts scores for exact skill matches.
- **External Job Search**: Integrated search for LinkedIn, Indeed, and other job boards.
- **Professional UI**: Polished, emoji-free interface with dark/light mode support.

## Prerequisites

- **Python 3.12+**
- **MongoDB**: Must be installed and running locally on port `27017`.
- **Ollama**: Required for local AI analysis. [Download Ollama](https://ollama.ai).
- **uv**: An extremely fast Python package installer and resolver.

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd resume-analyser
   ```

2. **Initialize Environment & Install Dependencies**
   ```bash
   uv sync
   ```

3. **Setup AI Models**
   - **spaCy**: Download the English model for parsing.
     ```bash
     uv run python -m spacy download en_core_web_sm
     ```
   - **Ollama**: Pull the Llama 3.2 model for AI critique.
     ```bash
     ollama pull llama3.2
     ```

4. **Start MongoDB**
   Ensure your local MongoDB instance is running.
   ```bash
   # On macOS with Homebrew
   brew services start mongodb-community
   ```

## Running the Application

To start the Streamlit app, run:

```bash
uv run streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

## Usage Guide

1. **Upload Resume**: Drag & drop a PDF/DOCX file. The system will auto-detect the candidate's name and job title.
2. **AI Critique**: Click "Generate AI Feedback" to get a detailed review from the local AI model.
3. **Manage Candidates**: 
    - Go to "Candidate Dashboard".
    - Click a name to view full details.
    - Use "Edit" to rename or "Delete" to remove a profile.
4. **Match Jobs**: Select a candidate and click "Find Matching Jobs" to see semantically ranked opportunities.

## Project Structure

- `app.py`: Main Streamlit application with professional UI.
- `src/parser.py`: Resume parsing logic (spaCy + regex) with job title extraction.
- `src/matcher.py`: Semantic matching using `sentence-transformers`.
- `src/llm_analyser.py`: Interface for local LLM analysis via Ollama.
- `src/db.py`: MongoDB operations including update/delete support.
- `src/external_search.py`: Integration with external job search engines.
- `src/scorer.py`: Rule-based ATS scoring logic.
