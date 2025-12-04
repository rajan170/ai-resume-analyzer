import re
from typing import Dict, List, Any

"""
ATS Scorer Module

This module implements a rule-based Applicant Tracking System (ATS) scorer.
It evaluates resumes based on common ATS criteria:
- Contact Information Completeness
- Skills Presence
- Essential Sections (Experience, Education)
- Quantifiable Metrics
- Length/Formatting

Note: This is a simplified heuristic. Real ATS systems are more complex and vary by vendor.
"""

class ATSScorer:
    """
    Rule-based scorer for resumes, mimicking basic ATS evaluation criteria.
    """
    def __init__(self):
        # Sections we expect to find in a well-structured resume
        self.essential_sections = ["experience", "education", "skills", "projects", "summary", "objective"]
        # Action verbs that indicate impact (not currently used but available for future enhancements)
        self.action_verbs = [
            "developed", "managed", "created", "led", "designed", "implemented", "optimized",
            "increased", "decreased", "saved", "achieved", "launched", "mentored"
        ]

    def check_sections(self, text: str) -> List[str]:
        """Checks which essential sections are present in the resume text."""
        text_lower = text.lower()
        found_sections = []
        for section in self.essential_sections:
            if section in text_lower:
                found_sections.append(section)
        return found_sections

    def check_metrics(self, text: str) -> bool:
        """
        Heuristic to detect quantifiable impact statements.
        Looks for percentages, dollar signs, or numbers tied to business metrics.
        """
        # Patterns: %, $, or numbers with keywords like 'users', 'revenue', etc.
        return bool(re.search(r'\d+%|\$\d+|\d+\s?(?:users|clients|customers|revenue|sales)', text))

    def score_resume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates an ATS score (0-100) for a resume based on multiple criteria.
        
        Scoring Breakdown:
        - Contact Info (20 points): Name, Email, Phone
        - Skills (25 points): Presence and quantity of skills
        - Sections (30 points): Experience and Education sections
        - Metrics (15 points): Quantifiable achievements
        - Format/Length (10 points): Appropriate word count
        
        Returns:
            Dictionary with 'ats_score', 'feedback' (list of suggestions), and 'found_sections'.
        """
        score = 0
        feedback = []
        
        # 1. Contact Info (20 points)
        contact_score = 0
        if data.get("name"):
            contact_score += 5
        else:
            feedback.append("Name not detected. Ensure it's prominent.")
        
        if data.get("email"):
            contact_score += 10
        else:
            feedback.append("Email not detected.")
        
        if data.get("phone"):
            contact_score += 5
        else:
            feedback.append("Phone number not detected.")
        
        score += contact_score

        # 2. Skills (25 points)
        skills = data.get("skills", [])
        if len(skills) >= 5:
            score += 25
        elif len(skills) > 0:
            score += 15
            feedback.append(f"Only found {len(skills)} skills. Try to include at least 5 relevant technical skills.")
        else:
            feedback.append("No skills detected. Use standard keywords for your industry.")

        # 3. Sections & Content (30 points)
        raw_text = data.get("raw_text", "")
        found_sections = self.check_sections(raw_text)
        
        if "experience" in found_sections or "work history" in raw_text.lower():
            score += 15
        else:
            feedback.append("Missing 'Experience' or 'Work History' section.")
            
        if "education" in found_sections:
            score += 15
        else:
            feedback.append("Missing 'Education' section.")

        # 4. Impact & Metrics (15 points)
        # Quantifiable achievements are highly valued by recruiters and ATS.
        if self.check_metrics(raw_text):
            score += 15
        else:
            feedback.append("No quantifiable metrics found (e.g., 'increased revenue by 20%'). Quantify your impact.")

        # 5. Formatting/Length (10 points)
        word_count = len(raw_text.split())
        if 200 <= word_count <= 1000:  # Rough estimate for 1-2 pages
            score += 10
        elif word_count < 200:
            feedback.append("Resume seems too short. Elaborate on your experience.")
        else:
            feedback.append("Resume might be too long. Aim for 1-2 pages.")

        return {
            "ats_score": score,
            "feedback": feedback,
            "found_sections": found_sections
        }
