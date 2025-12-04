import os
from pymongo import MongoClient
from dotenv import load_dotenv

"""
Database Module

This module handles all interactions with MongoDB, our choice for persistence.
We use MongoDB because:
1. Resume data is semi-structured (not every resume has the same fields).
2. Schema flexibility allows us to evolve the data model as we add features.
3. JSON-like documents map naturally to Python dictionaries.

Dependencies:
- pymongo (MongoDB driver for Python)
"""

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "resume_analyser"

class Database:
    """
    MongoDB client wrapper for the Resume Analyser application.
    
    Manages two collections:
    - candidates: Stores parsed resume data, scores, and feedback.
    - jobs: Stores job postings with required skills.
    """
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.candidates = self.db.candidates
        self.jobs = self.db.jobs

    def insert_candidate(self, candidate_data):
        """Inserts a new candidate profile and returns the MongoDB ObjectId."""
        return self.candidates.insert_one(candidate_data).inserted_id

    def get_all_candidates(self):
        """
        Retrieves all candidate profiles.
        Converts ObjectId to string for JSON serialization.
        """
        candidates = list(self.candidates.find({}))
        for candidate in candidates:
            # Convert ObjectId to string so it can be serialized by Streamlit/JSON
            candidate['_id'] = str(candidate['_id'])
        return candidates

    def update_candidate_name(self, candidate_id, new_name):
        """
        Updates the name field for a candidate.
        Useful for correcting parsing errors or implementing the Edit feature.
        """
        from bson.objectid import ObjectId
        return self.candidates.update_one(
            {"_id": ObjectId(candidate_id)},
            {"$set": {"name": new_name}}
        )

    def delete_candidate(self, candidate_id):
        """
        Deletes a candidate profile from the database.
        This is a destructive operation with no undo.
        """
        from bson.objectid import ObjectId
        return self.candidates.delete_one({"_id": ObjectId(candidate_id)})

    def insert_job(self, job_data):
        """Inserts a new job posting."""
        return self.jobs.insert_one(job_data).inserted_id

    def get_all_jobs(self):
        """
        Retrieves all job postings.
        Note: We exclude _id from the results as it's not needed for matching.
        """
        return list(self.jobs.find({}, {"_id": 0}))

# Global database instance
# This follows the Singleton pattern for simplicity in a local app.
db = Database()
