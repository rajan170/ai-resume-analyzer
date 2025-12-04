from duckduckgo_search import DDGS
from typing import List, Dict

class ExternalJobSearch:
    def __init__(self):
        self.ddgs = DDGS()

    def search_jobs(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Searches for jobs using DuckDuckGo.
        """
        results = []
        try:
            # Construct a job-specific query
            search_query = f"{query} jobs"
            
            # Use DDGS to search
            ddg_results = self.ddgs.text(search_query, max_results=limit, backend="html")
            
            if ddg_results:
                for res in ddg_results:
                    results.append({
                        "title": res.get("title"),
                        "link": res.get("href"),
                        "snippet": res.get("body")
                    })
        except Exception as e:
            print(f"Error searching external jobs: {e}")
            
        return results

    def recommend_jobs(self, skills: List[str], limit: int = 5) -> List[Dict]:
        # Create a query from the primary skill to ensure results
        if not skills:
            return []
        
        primary_skill = skills[0]
        query = f"{primary_skill} Developer"
        return self.search_jobs(query, limit)
