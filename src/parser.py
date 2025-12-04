import spacy
import pdfplumber
import docx2txt
import re
from typing import Dict, List, Any

"""
Resume Parser Module

This module handles the core logic of extracting structured information from
unstructured resume documents (PDF, DOCX). It uses a hybrid approach combining:
1.  spaCy NER: For extracting entities like Names and Organizations.
2.  Regular Expressions: For pattern-based extraction (Email, Phone).
3.  Keyword Matching: For identifying skills and job titles.

Dependencies:
- spaCy (en_core_web_sm model)
- pdfplumber (PDF extraction)
- docx2txt (DOCX extraction)
"""

# Load spaCy model
# We use the small English model for efficiency. It's sufficient for basic NER tasks.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Model not found. Please install en_core_web_sm.")
    nlp = spacy.blank("en")

class ResumeParser:
    """
    Parses resume files to extract candidate information.
    
    Attributes:
        nlp: The loaded spaCy language model.
        skill_list: A predefined list of technical skills to search for.
    """
    def __init__(self):
        self.nlp = nlp
        # Common technical skills to look for.
        # In a production system, this should likely be loaded from a database or config file.
        self.skill_list = [
            "Python", "Java", "C++", "JavaScript", "React", "Node.js", "SQL", "NoSQL",
            "MongoDB", "AWS", "Azure", "Docker", "Kubernetes", "Machine Learning",
            "Deep Learning", "Data Science", "Pandas", "NumPy", "Scikit-learn",
            "TensorFlow", "PyTorch", "Git", "CI/CD", "Agile", "Scrum", "Communication",
            "Leadership", "Problem Solving"
        ]

    def extract_text_from_pdf(self, file_path_or_buffer) -> str:
        text = ""
        with pdfplumber.open(file_path_or_buffer) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    def extract_text_from_docx(self, file_path_or_buffer) -> str:
        return docx2txt.process(file_path_or_buffer)

    def extract_email(self, text: str) -> str:
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""

    def extract_phone(self, text: str) -> str:
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else ""

    def extract_skills(self, text: str) -> List[str]:
        """
        Extracts skills using a hybrid approach:
        1. Direct keyword matching against self.skill_list.
        2. NER extraction for ORG, PRODUCT, and LANGUAGE entities that match known skills.
        """
        doc = self.nlp(text)
        found_skills = set()
        text_lower = text.lower()
        
        # 1. Keyword Matching (Case-insensitive)
        for skill in self.skill_list:
            if skill.lower() in text_lower:
                found_skills.add(skill)
        
        # 2. NER-based extraction (Context-aware)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "LANGUAGE"]:
                if ent.text in self.skill_list:
                    found_skills.add(ent.text)
        return list(found_skills)

    def extract_name(self, text: str) -> str:
        """
        Extracts the candidate's name using heuristics and NER.
        
        Strategy:
        1. Focus on the first few lines (header area).
        2. Filter out lines containing forbidden words (titles, skills, generic headers).
        3. Identify potential candidates based on word count (names are usually 2-3 words).
        4. Use spaCy NER to confirm if a candidate is a PERSON entity.
        5. Fallback to the first plausible line if NER fails.
        """
        # 1. Get first few non-empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return ""
            
        # 2. Define forbidden words (skills, titles, keywords)
        # These words indicate the line is likely NOT a name (e.g., "Senior Developer", "Resume of...")
        forbidden_words = set(s.lower() for s in self.skill_list)
        forbidden_words.update([
            "resume", "cv", "curriculum", "vitae", "profile", "summary", 
            "experience", "education", "contact", "email", "phone", "address",
            "skills", "projects", "references", "languages", "certifications",
            "senior", "junior", "associate", "lead", "manager", "director", "vp",
            "engineer", "developer", "architect", "consultant", "analyst", "intern"
        ])
        
        # 3. Identify potential name candidates from the first 3 lines
        candidates = []
        for i, line in enumerate(lines[:3]):
            # Clean line
            line_clean = re.sub(r'[^\w\s]', '', line)
            words = line_clean.split()
            
            # Basic filters
            if not words:
                continue
            if any(char.isdigit() for char in line):
                continue
            if any(w.lower() in forbidden_words for w in words):
                continue
            
            # Length check: Names are usually 1-4 words
            if 1 <= len(words) <= 4:
                candidates.append(line)

        # 4. Use NER to find the best candidate
        header_text = "\n".join(lines[:10])
        doc = self.nlp(header_text)
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip()
                # Clean and validate
                if '\n' in name:
                    name = name.split('\n')[0]
                name_clean = re.sub(r'[^\w\s]', '', name)
                
                if not name_clean:
                    continue
                if any(char.isdigit() for char in name):
                    continue
                if name_clean.lower() in forbidden_words:
                    continue
                if any(w.lower() in forbidden_words for w in name.split()):
                    continue
                
                # If this name is one of our top-line candidates, it's a very strong match
                if name in candidates:
                    return name
                
                # Otherwise, it's still a good match if it looks like a name
                if len(name.split()) >= 2:
                    return name

        # 5. Fallback: Return the first valid candidate from the top lines
        if candidates:
            return candidates[0].title()
                 
        return ""

    def extract_job_title(self, text: str) -> str:
        """
        Attempts to identify the candidate's current or most recent job title.
        Scans the first 10 lines for known job titles.
        """
        job_titles = [
            "Software Engineer", "Data Scientist", "Product Manager", "Project Manager",
            "Business Analyst", "DevOps Engineer", "Full Stack Developer", "Frontend Developer",
            "Backend Developer", "Machine Learning Engineer", "Data Engineer", "System Administrator",
            "Network Engineer", "QA Engineer", "UI/UX Designer", "Graphic Designer",
            "Marketing Manager", "Sales Manager", "Accountant", "HR Manager", "Consultant",
            "Director", "VP", "Chief", "Lead", "Senior", "Junior", "Associate", "Intern"
        ]
        
        # Search in the first 10 lines for a job title
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:10]:
            for title in job_titles:
                if title.lower() in line.lower():
                    # Return the matched title, or the whole line if it's short enough
                    if len(line.split()) <= 5:
                        return line.title()
                    return title
        return ""

    def parse(self, file_buffer, file_type: str) -> Dict[str, Any]:
        if file_type == "pdf":
            text = self.extract_text_from_pdf(file_buffer)
        elif file_type == "docx":
            text = self.extract_text_from_docx(file_buffer)
        else:
            raise ValueError("Unsupported file type")

        return {
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "job_title": self.extract_job_title(text),
            "raw_text": text
        }
