from src.external_search import ExternalJobSearch

def test_enhanced_search():
    print("Testing enhanced job search...")
    search = ExternalJobSearch()
    
    # Test 1: Basic search with job title
    print("\n--- Test 1: Basic search ---")
    results = search.recommend_jobs(
        skills=["Python", "Machine Learning"],
        job_title="Data Scientist",
        limit=5
    )
    print(f"Results: {len(results)}")
    for r in results:
        print(f"  - {r['title']}")
        print(f"    URL: {r['link']}")
        print(f"    Location: {r.get('location', 'N/A')}")
        print(f"    Remote: {r.get('is_remote', False)}")
    
    # Test 2: Remote only
    print("\n--- Test 2: Remote only ---")
    results = search.recommend_jobs(
        skills=["Python"],
        job_title="Software Engineer",
        remote_only=True,
        limit=5
    )
    print(f"Results: {len(results)}")
    for r in results:
        print(f"  - {r['title']} | Remote: {r.get('is_remote')}")
    
    # Test 3: With location
    print("\n--- Test 3: With location (New York) ---")
    results = search.recommend_jobs(
        skills=["Python"],
        job_title="Software Engineer",
        location="New York",
        limit=5
    )
    print(f"Results: {len(results)}")

if __name__ == "__main__":
    test_enhanced_search()
