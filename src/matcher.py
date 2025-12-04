from typing import Dict, List
from sentence_transformers import SentenceTransformer, util
import numpy as np

"""
Job Matcher Module

This module implements the core recommendation logic using Semantic Search.
It uses a pre-trained Transformer model to generate vector embeddings for 
resumes and job descriptions, allowing for matching based on *meaning* 
rather than just keyword overlap.

Dependencies:
- sentence_transformers (Hugging Face)
- numpy
"""

class JobMatcher:
    """
    Matches candidates to jobs using semantic similarity and keyword boosting.
    """
    def __init__(self):
        try:
            # Load a lightweight, efficient model optimized for semantic search.
            # 'all-MiniLM-L6-v2' is a great balance between speed and accuracy.
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Computes the cosine similarity between two text strings.
        Returns a score between 0 and 100.
        """
        if not self.model or not text1 or not text2:
            return 0.0
        
        # Encode texts into high-dimensional vectors (embeddings)
        embeddings1 = self.model.encode(text1, convert_to_tensor=True)
        embeddings2 = self.model.encode(text2, convert_to_tensor=True)
        
        # Compute cosine similarity (dot product of normalized vectors)
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        return round(float(cosine_scores[0][0]) * 100, 2)

    def match_jobs(self, candidate: Dict, jobs: List[Dict]) -> List[Dict]:
        """
        Ranks a list of jobs for a given candidate using a Hybrid Search approach.
        
        Algorithm:
        1. Semantic Score: Cosine similarity between candidate profile and job description.
        2. Keyword Boost: Bonus points for exact skill matches (up to 20%).
        3. Final Score: Semantic Score + Keyword Boost (capped at 100).
        """
        ranked_jobs = []
        candidate_skills = " ".join(candidate.get("skills", []))
        # Combine text for richer context (Resume Text + Explicit Skills)
        candidate_text = f"{candidate.get('raw_text', '')} {candidate_skills}"

        for job in jobs:
            job_skills = " ".join(job.get("required_skills", []))
            job_text = f"{job.get('description', '')} {job_skills} {job.get('title', '')}"
            
            # 1. Semantic Similarity
            semantic_score = self.calculate_similarity(candidate_text, job_text)
            
            # 2. Keyword Boost (Hybrid Search)
            # We explicitly check for required skills to ensure candidates with 
            # specific technical requirements get a boost even if the semantic context varies.
            skill_match_count = 0
            required_skills = job.get("required_skills", [])
            if required_skills:
                candidate_skill_set = set([s.lower() for s in candidate.get("skills", [])])
                for skill in required_skills:
                    if skill.lower() in candidate_skill_set:
                        skill_match_count += 1
                
                # Add bonus for exact skill matches (up to 20 points)
                semantic_score += (skill_match_count / len(required_skills)) * 20 
            
            ranked_jobs.append({
                **job,
                "match_score": min(semantic_score, 100)
            })
        
        # Sort by highest match score
        ranked_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        return ranked_jobs
