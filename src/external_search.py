from ddgs import DDGS
from typing import List, Dict
import re

class ExternalJobSearch:
    def __init__(self):
        self.ddgs = DDGS()

    def search_jobs(self, query: str, limit: int = 5, timelimit: str = None) -> List[Dict]:
        """
        Searches for jobs using DuckDuckGo.
        Args:
            timelimit: 'd' (day), 'w' (week), 'm' (month)
        """
        results = []
        try:
            ddg_results = self.ddgs.text(query, max_results=limit * 2, timelimit=timelimit)  # Get more to filter
            
            if ddg_results:
                for res in ddg_results:
                    # Extract metadata from snippet
                    snippet = res.get("body", res.get("description", ""))
                    
                    results.append({
                        "title": res.get("title", "No Title"),
                        "link": res.get("href", res.get("link", "#")),
                        "snippet": snippet,
                        "location": self._extract_location(snippet),
                        "is_remote": self._is_remote(snippet),
                    })
        except Exception as e:
            print(f"Error searching external jobs: {e}")
            
        return results

    def _extract_location(self, text: str) -> str:
        """Extract location from job snippet."""
        # Try to extract from title first (e.g., "Job Title - City, State")
        title_location = re.search(r'-\s*([A-Z][a-z]+(?:,\s*[A-Z]{2})?)\s*-', text)
        if title_location:
            return title_location.group(1).strip()
        
        # Common patterns for locations in snippets
        location_patterns = [
            r'(?:Location|Based in|Office in):\s*([^•\n]+)',
            r'(?:Remote|Hybrid)\s*-\s*([^•\n,]+)',
            r'\b([A-Z][a-z]+,\s*[A-Z]{2})\b',  # City, State
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+,\s*[A-Z]{2})\b',  # Multi-word city
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return "Not specified"

    def _is_remote(self, text: str) -> bool:
        """Check if job is remote."""
        remote_keywords = ['remote', 'work from home', 'wfh', 'anywhere', 'telecommute']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in remote_keywords)

    def _is_specific_job_posting(self, url: str) -> bool:
        """Check if URL is likely a specific job posting vs category page."""
        # Patterns that indicate specific job postings
        specific_patterns = [
            '/jobs/view/',
            '/job/',
            '/viewjob',
            '/posting/',
            r'/\d{6,}',  # Job ID numbers
        ]
        
        # Patterns to avoid (category/listing pages)
        avoid_patterns = [
            '/jobs/search',
            '-jobs$',
            '/jobs/?$',
            '/careers/?$',
        ]
        
        url_lower = url.lower()
        
        # Skip category pages
        for pattern in avoid_patterns:
            if re.search(pattern, url_lower):
                return False
        
        # Prefer specific postings
        for pattern in specific_patterns:
            if re.search(pattern, url_lower):
                return True
        
        return False


    def recommend_jobs(
        self,
        skills: List[str],
        job_title: str = None,
        location: str = None,
        remote_only: bool = False,
        limit: int = 5,
        posted_last_24h: bool = False
    ) -> List[Dict]:
        """
        Recommends specific job postings with enhanced filtering.
        
        Args:
            skills: List of candidate skills
            job_title: Target job title
            location: Desired location (e.g., "New York", "United States", "Remote")
            remote_only: Filter for remote jobs only
            limit: Number of results to return
            posted_last_24h: If True, only return jobs posted in last 24 hours
        """
        if not skills and not job_title:
            return []
        
        # Set time limit for DDG
        timelimit = "d" if posted_last_24h else None
        
        all_results = []
        
        # If no job title, create one from skills
        search_title = job_title
        if not search_title and skills:
            # Use primary skill + "Engineer" as fallback
            search_title = f"{skills[0]} Engineer"
            print(f"No job title provided, using: {search_title}")
        
        # Strategy 1: LinkedIn specific postings
        if search_title:
            linkedin_query = self._build_query(
                search_title, skills, location, remote_only, source="linkedin"
            )
            print(f"LinkedIn search: {linkedin_query}")
            all_results.extend(self.search_jobs(linkedin_query, limit=limit, timelimit=timelimit))
        
        # Strategy 2: Indeed postings
        if search_title:
            indeed_query = self._build_query(
                search_title, skills, location, remote_only, source="indeed"
            )
            print(f"Indeed search: {indeed_query}")
            all_results.extend(self.search_jobs(indeed_query, limit=limit, timelimit=timelimit))
        
        # Filter for quality
        quality_results = self._filter_results(
            all_results, remote_only=remote_only, location=location
        )
        
        # If filtering results in 0 jobs and we had some results, return unfiltered
        if len(quality_results) == 0 and len(all_results) > 0:
            print(f"Filtering removed all results, returning unfiltered ({len(all_results)} jobs)")
            quality_results = all_results
        
        # Deduplicate by URL
        seen_links = set()
        unique_results = []
        for result in quality_results:
            if result['link'] not in seen_links:
                seen_links.add(result['link'])
                unique_results.append(result)
        
        print(f"Found {len(unique_results)} unique job postings")
        return unique_results[:limit]

    def _build_query(
        self, 
        job_title: str, 
        skills: List[str], 
        location: str, 
        remote_only: bool,
        source: str = "linkedin"
    ) -> str:
        """Build optimized search query."""
        parts = []
        
        # Add job title
        if job_title:
            parts.append(f'"{job_title}"')
        
        # Add primary skill for context
        if skills and len(skills) > 0:
            parts.append(skills[0])
        
        # Add location or remote
        if remote_only:
            parts.append("remote")
        elif location:
            parts.append(location)
        
        # Add source site
        if source == "linkedin":
            parts.append("site:linkedin.com/jobs")
        elif source == "indeed":
            parts.append("site:indeed.com/viewjob")
        
        return " ".join(parts)

    def _filter_results(
        self, 
        results: List[Dict], 
        remote_only: bool = False,
        location: str = None
    ) -> List[Dict]:
        """Filter results for quality and criteria."""
        filtered = []
        
        for result in results:
            # Skip non-specific URLs
            if not self._is_specific_job_posting(result['link']):
                continue
            
            # Filter by remote if needed (strict)
            if remote_only and not result['is_remote']:
                continue
            
            # Location filtering (lenient - only filter if we can extract location)
            if location and not remote_only:
                # If we couldn't extract location, include the job anyway
                extracted_loc = result.get('location', '')
                if extracted_loc != "Not specified":
                    # Only filter if location was extracted and doesn't match
                    if location.lower() not in extracted_loc.lower():
                        if not result['is_remote']:  # Remote jobs always OK
                            continue
            
            filtered.append(result)
        
        return filtered
