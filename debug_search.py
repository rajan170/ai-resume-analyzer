from src.external_search import ExternalJobSearch

def test_search():
    print("Initializing search...")
    search = ExternalJobSearch()
    
    skills = ["Python", "Machine Learning"]
    job_title = "Data Scientist"
    
    print(f"Searching for: Title='{job_title}', Skills={skills}")
    results = search.recommend_jobs(skills, job_title)
    
    print(f"Found {len(results)} results:")
    for res in results:
        print(f"- {res['title']}: {res['link']}")

if __name__ == "__main__":
    test_search()
