# AI-Driven Resume Analyser: Final Presentation

## Slide 1: Title Slide
- **Project Name**: AI-Driven Resume Analyser
- **Team Members**: [Your Names]
- **Tagline**: "Modernizing Recruitment with Intelligent Automation"

## Slide 2: Problem Statement
- **Challenge**: Recruiters are overwhelmed by thousands of unstructured resumes.
- **Pain Points**:
    - Manual screening is slow and biased.
    - High operational costs.
    - Missed top talent due to fatigue.
- **Goal**: Build a real-time system to parse, score, and match candidates automatically.

## Slide 3: Solution Overview
- **Core Features**:
    1. **Resume Parsing**: Extracts key data (Name, Skills, Contact) using NLP (spaCy).
    2. **ATS Scoring**: Evaluates resume quality and provides actionable feedback.
    3. **Intelligent Matching**: Ranks candidates against internal job openings.
    4. **External Search**: Finds relevant jobs on LinkedIn/Indeed/Glassdoor.

## Slide 4: System Architecture
- **Tech Stack**:
    - **Frontend**: Streamlit (Python)
    - **Backend Logic**: Python (spaCy, scikit-learn)
    - **Database**: MongoDB (NoSQL for flexible schema)
- **Flow**: Upload -> Parse -> Store -> Score -> Match -> Recommend

## Slide 5: Key Technical Challenges & Solutions
- **Name Extraction**:
    - *Challenge*: Distinguishing names from titles or skills (e.g., "Azure Cloud").
    - *Solution*: Implemented strict filtering, position-based heuristics, and NER refinement.
- **External Search**:
    - *Challenge*: Getting reliable results without official APIs.
    - *Solution*: Used `duckduckgo-search` with optimized query construction ("Skill + Developer").

## Slide 6: Live Demo
- **Walkthrough**:
    1. Upload a resume.
    2. Show extracted data and ATS score.
    3. Demonstrate internal job matching.
    4. Click "Search Online Jobs" for external results.

## Slide 7: Future Improvements
- **Advanced NLP**: Use Transformer models (BERT) for deeper semantic understanding.
- **Cloud Deployment**: Host on AWS/Azure for accessibility.
- **User Accounts**: Separate logins for Recruiters and Candidates.

## Slide 8: Q&A
- Thank you!
