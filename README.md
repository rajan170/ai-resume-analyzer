# AI-Driven Resume Analyser

A local, AI-powered recruitment platform built with Streamlit, spaCy, and MongoDB. This application automates resume parsing, candidate management, and intelligent job matching using semantic search and local LLMs.

## Features

### Resume Analysis
- **Intelligent Parsing**: Automatically extracts Name, Email, Phone, Skills, and Job Title from PDF and DOCX resumes using spaCy NLP
- **ATS Scoring**: Rule-based scoring system (0-100) that evaluates resumes on contact info, skills, sections, metrics, and formatting
- **AI-Powered Critique**: Local LLM analysis via Ollama (Llama 3.2) provides detailed qualitative feedback, career advice, and actionable improvement suggestions

### Candidate Management
- **Smart Database**: MongoDB-based storage with "Name - Job Title" convention for easy identification
- **Full CRUD Operations**: View detailed profiles, delete candidates, and manage your talent pipeline
- **Dashboard Analytics**: Real-time metrics showing total candidates, average ATS scores, and top performers (80+)
- **Profile Viewer**: Detailed view of each candidate with all extracted data and analysis

### Job Management
- **Job Posting**: Create and manage job openings with title, department, description, and required skills
- **Active Listings**: View all current job postings with full details
- **Flexible Schema**: MongoDB allows easy evolution of job requirements

### Intelligent Matching
- **Semantic Search**: Uses `sentence-transformers` (all-MiniLM-L6-v2) to match candidates based on contextual meaning, not just keywords
- **Hybrid Scoring**: Combines semantic similarity (cosine similarity) with keyword matching for skill-specific boosts (up to 20%)
- **Internal Job Matching**: Automatically ranks candidates against your posted jobs with match percentage scores
- **Smart Match Page**: Compare any resume (upload or paste) against any job description (existing or paste) with AI-powered fit analysis

### External Job Search
- **Multi-Platform Search**: Integrated search for LinkedIn, Indeed, Glassdoor, and Google Jobs
- **Smart Filters**: Location, remote-only, posting date (last 24h), and result limits
- **Auto-Query Generation**: Automatically builds search queries from candidate profiles or job requirements
- **Clean Results Display**: HTML-cleaned job listings with direct links to applications

## Architecture

The application follows a clean, layered architecture:

- **Presentation Layer**: Streamlit with professional custom CSS, dark/light mode support, and responsive design
- **Application Layer**: 
  - **Parser** (`src/parser.py`): spaCy + Regex for entity extraction and job title detection
  - **Scorer** (`src/scorer.py`): Rule-based ATS scoring system
  - **Matcher** (`src/matcher.py`): Semantic matching using sentence transformers
  - **LLM Analyser** (`src/llm_analyser.py`): Local LLM interface via Ollama for qualitative analysis and fit assessment
  - **External Search** (`src/external_search.py`): Multi-platform job board search integration
- **Data Layer**: MongoDB for flexible, schema-free storage of candidates and jobs

## Prerequisites

- **Python 3.12+**
- **MongoDB**: Must be installed and running locally on port `27017`
- **Ollama**: Required for AI-powered features. [Download Ollama](https://ollama.ai)
- **uv**: Fast Python package manager (recommended) or pip

##  Installation & Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd resume-analyser
```

### 2. Create a `.env` file
```bash
# Optional: Set MongoDB URI if not using default
# MONGO_URI=mongodb://localhost:27017/
```

### 3. Install dependencies
**Using uv (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install -r requirements.txt
```

### 4. Download required models
```bash
# spaCy English NLP model
uv run python -m spacy download en_core_web_sm

# Ollama LLM (requires Ollama to be installed first)
ollama pull llama3.2
```

### 5. Start supporting services

**MongoDB** – Ensure it's running locally (default port 27017):
```bash
# macOS with Homebrew
brew services start mongodb-community

# Linux (systemd)
sudo systemctl start mongod

# Verify connection
mongosh
```

**Ollama** – Start the service (usually runs automatically after installation):
```bash
ollama serve   # or simply run `ollama` to keep the process alive
```

### 6. Run the application
```bash
uv run streamlit run app.py
```

The application will be available at `http://localhost:8501` in your browser.

## Usage Guide

### Analysis & Search Page
1. **Upload Resume**: Drag and drop a PDF/DOCX file (max 2MB)
2. **Process**: Click "Process Resume" to extract data and calculate ATS score
3. **Review**: View extracted information and ATS score summary
4. **Save**: Click "Save Profile to DB" to persist the candidate
5. **AI Critique**: Navigate to "AI Critique" tab and click "Generate Critique" for detailed LLM feedback
6. **Find Jobs**: 
   - View internal matches automatically ranked by semantic similarity
   - Use "Search Job Boards" to find external opportunities on LinkedIn, Indeed, etc.

### Candidate Dashboard
1. **View Metrics**: See total candidates, average scores, and top talent count
2. **Browse Profiles**: Scroll through all candidates with ATS scores
3. **View Details**: Click "View" to see full candidate profile
4. **Delete**: Remove candidates from the database
5. **Profile Detail**: Examine all extracted data in JSON format

### Job Management
1. **Create Jobs**: Fill out the form with title, department, skills, and description
2. **Publish**: Click "Publish Job" to add to the database
3. **View Listings**: All active jobs are displayed with full details

### Smart Match
1. **Choose Resume**: Upload a file or paste resume text
2. **Choose Job**: Select existing job or paste job description
3. **Analyze**: Click "Run Match Analysis" for AI-powered fit assessment
4. **Match Report**: Review detailed analysis including match score, matching skills, gaps, and recommendations
5. **External Search**: Automatically search LinkedIn and Indeed with extracted skills and job title

## Project Structure

```
resume-analyser/
├── app.py                      # Main Streamlit application (626 lines)
├── src/
│   ├── parser.py              # Resume parsing with spaCy and regex
│   ├── matcher.py             # Semantic job matching with sentence transformers
│   ├── llm_analyser.py        # AI analysis via Ollama (resume critique, fit analysis, title extraction)
│   ├── scorer.py              # Rule-based ATS scoring system
│   ├── db.py                  # MongoDB operations (CRUD for candidates and jobs)
│   ├── external_search.py     # Multi-platform job search integration
│   └── utils.py               # Helper utilities
├── tech_spec.md               # Technical specification and architecture
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── pyproject.toml             # UV project configuration
└── .env                       # Environment variables (not committed)
```

## Features in Detail

### ATS Scoring Algorithm
The scorer evaluates resumes on a 0-100 scale:
- **Contact Info (20 pts)**: Name (5), Email (10), Phone (5)
- **Skills (25 pts)**: Presence and quantity (need 5+ for full points)
- **Sections (30 pts)**: Experience section (15), Education section (15)
- **Impact Metrics (15 pts)**: Quantifiable achievements (%, $, numbers with business context)
- **Format/Length (10 pts)**: Appropriate word count (200-1000 words)

### Semantic Matching Algorithm
Hybrid approach combining AI and rules:
1. **Semantic Similarity**: Cosine similarity between candidate profile and job description using transformer embeddings
2. **Keyword Boost**: Exact skill match bonus (up to 20% boost)
3. **Final Score**: Semantic score + skill boost (capped at 100)

### AI Analysis Features
- **Resume Critique**: Executive summary, pros/cons, career paths, action items
- **Fit Analysis**: Match percentage, matching skills, gaps, experience alignment, recommendation
- **Job Title Extraction**: Intelligent extraction from unstructured job descriptions

### Database Schema

**Candidates Collection:**
```javascript
{
  "_id": ObjectId,
  "name": "John Doe - Software Engineer",  // Format: Name - Job Title
  "email": "john@example.com",
  "phone": "+1234567890",
  "skills": ["Python", "Machine Learning", "AWS"],
  "job_title": "Software Engineer",
  "raw_text": "Full resume text...",
  "ats_score": 85,
  "ats_feedback": ["Strong technical skills", "Add more metrics"],
  "created_at": DateTime
}
```

**Jobs Collection:**
```javascript
{
  "_id": ObjectId,
  "title": "Senior Python Developer",
  "department": "Engineering",
  "description": "We are looking for...",
  "required_skills": ["Python", "Django", "PostgreSQL"],
  "created_at": DateTime
}
```

## Privacy & Security

- **100% Local Processing**: All sensitive data processing happens on your machine
- **No Cloud Dependencies**: No external API calls for resume analysis (Ollama runs locally)
- **MongoDB Local**: Database runs on your infrastructure with optional authentication
- **GDPR-Ready**: Complete control over data retention and deletion

## Technology Stack

**Backend:**
- Python 3.12+
- spaCy (en_core_web_sm) - NLP and entity extraction
- sentence-transformers (all-MiniLM-L6-v2) - Semantic embeddings
- Ollama + Llama 3.2 - Local LLM for analysis
- pymongo - MongoDB driver

**Frontend:**
- Streamlit - Interactive web application
- Custom CSS - Professional UI with Inter font
- HTML/Markdown rendering for results

**Data:**
- MongoDB - NoSQL database for flexible schema
- pandas - Data manipulation and display

## Troubleshooting

**MongoDB Connection Error:**
```bash
# Check if MongoDB is running
brew services list   # macOS
sudo systemctl status mongod   # Linux

# Start MongoDB
brew services start mongodb-community   # macOS
sudo systemctl start mongod   # Linux
```

**Ollama Not Working:**
```bash
# Check if Ollama is installed
ollama --version

# Pull the model
ollama pull llama3.2

# Start Ollama service
ollama serve
```

**Model Download Issues:**
```bash
# Download spaCy model manually
python -m spacy download en_core_web_sm --no-cache-dir
```

## Contributing

This is a local recruitment tool designed for privacy and control. Feel free to fork and customize for your specific needs.

## License

MIT License - Feel free to use and modify for your recruitment needs.

## Future Enhancements

- Batch resume processing
- Email notifications for new matches
- Interview scheduling integration
- Advanced analytics and reporting
- Multi-language support
- Custom LLM fine-tuning for industry-specific analysis
- API endpoints for third-party integrations
