import ollama
from typing import Dict, Any

"""
LLM Analyser Module

This module interfaces with local Large Language Models (LLMs) via Ollama to 
provide qualitative analysis of resumes.

It uses the 'llama3.2' model to generate:
- Executive Summaries
- Strengths & Weaknesses
- Career Path Recommendations
- Actionable Improvement Tips

Dependencies:
- ollama (Python client for Ollama)
"""

class LLMAnalyser:
    """
    Wrapper for the Ollama API to perform resume analysis.
    """
    def __init__(self, api_key: str = None):
        # We use Ollama for local, privacy-preserving, and free inference.
        # The 'api_key' parameter is kept for backward compatibility or future
        # cloud API integration but is not used for Ollama.
        print("Initializing AI model...")
        self.model = "llama3.2"  # Llama 3.2 is efficient and capable for this task 
        
    def analyze_resume(self, resume_text: str) -> str:
        """
        Generates a detailed critique of the resume using Llama 3.2.
        
        The prompt is engineered to:
        1. Adopt a persona (Expert Career Coach).
        2. Request specific sections (Summary, Pros, Cons, Career Paths).
        3. Enforce a structured output format for easy reading.
        """
        # Truncate text to avoid context window limits, though Llama 3.2 has a decent window.
        # 3000 chars is usually enough to capture the essence of a resume.
        prompt = f"""You are an expert Resume Reviewer and Career Coach with 15+ years of experience in recruitment and career development.

Analyze the following resume in detail and provide a comprehensive, personalized critique.

RESUME TEXT:
{resume_text[:3000]}

Please provide a detailed analysis in the following format:

### Executive Summary
Write a 3-4 sentence professional summary of this candidate's profile, highlighting their career level, primary expertise, and overall market positioning.

### Pros (Key Strengths)
List 4-5 specific strengths with detailed explanations:
- [Strength]: [Why this is valuable and how it positions the candidate]
- [Strength]: [Specific evidence from the resume]
- Continue with specific, actionable observations

### Cons (Areas for Improvement)
List 4-5 specific, actionable improvements with reasoning:
- [Issue]: [Why this matters and how to fix it]
- [Issue]: [Specific recommendation with examples]
- Continue with constructive, detailed feedback

### Recommended Career Paths
Based on the skills, experience, and background, suggest 3-4 specific job titles or career directions with brief justification for each.

### Action Items
Provide 3-5 immediate, specific actions the candidate should take to improve their resume.

Be specific, professional, and constructive. Reference actual content from the resume in your analysis.
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            return response['message']['content']
        except Exception as e:
            # Handle connection errors gracefully.
            # This is common if the user hasn't started the Ollama service.
            error_msg = str(e)
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                return """### Ollama Not Running

**Error**: Could not connect to Ollama.

**To use AI Resume Critique:**
1. Install Ollama from https://ollama.ai
2. Run: `ollama pull llama3.2`
3. Start Ollama (it runs in the background)
4. Try "Generate AI Feedback" again

**Alternative**: The ATS Score and other features still work without AI critique!
"""
            return f"Error generating analysis: {e}"

    def analyze_fit(self, resume_text: str, job_description: str) -> str:
        """
        Analyzes the fit between a resume and a job description.
        """
        prompt = f"""You are an expert Talent Acquisition Specialist. 
        Compare the following Resume with the Job Description to determine the candidate's fit.

        RESUME:
        {resume_text[:3000]}

        JOB DESCRIPTION:
        {job_description[:3000]}

        Provide a structured analysis:

        ### Match Score
        Estimate a match percentage (0-100%) based on skills and experience alignment.

        ### Key Matching Skills
        List the top skills from the resume that directly match the JD.

        ### Missing Critical Skills
        List important skills or requirements from the JD that are missing or weak in the resume.

        ### Experience Alignment
        Briefly assess if the candidate's experience level (years, role type) fits the role.

        ### Final Recommendation
        One sentence: Strong Fit, Moderate Fit, or Weak Fit, and why.
        """

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                return "Error: Could not connect to Ollama. Please ensure it is running."
            return f"Error generating fit analysis: {e}"

    def extract_job_title(self, job_description: str) -> str:
        """
        Extracts the job title from a job description text using LLM.
        """
        prompt = f"""Extract the exact Job Title from the following Job Description.
        Return ONLY the job title, nothing else. Do not use "Job Title:" prefix.
        
        JOB DESCRIPTION:
        {job_description[:2000]}
        """
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content'].strip()
        except Exception:
            return ""



