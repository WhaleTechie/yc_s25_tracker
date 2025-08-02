import os
import json
import re
from serpapi import GoogleSearch  # SerpAPI Python client

API_KEY = os.getenv("SERPAPI_API_KEY")  # Set your SerpAPI API key as env var

def has_s25_postfix(text):
    return bool(re.search(r"\(?\s*(yc\s*)?s25\s*\)?", text, re.IGNORECASE))

def serpapi_bing_search_s25_companies(query):
    if not API_KEY:
        raise ValueError("SERPAPI_API_KEY environment variable not set")

    params = {
        "engine": "bing",
        "q": query,
        "api_key": API_KEY,
        "count": 20
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    found_companies = []

    # Parse organic results
    organic_results = results.get("organic_results", [])
    for result in organic_results:
        link = result.get("link", "")
        title = result.get("title", "")

        if "linkedin.com/company" not in link:
            continue

        if has_s25_postfix(title):
            clean_name = re.sub(r"\(?\s*(yc\s*)?s25\s*\)?", "", title, flags=re.IGNORECASE).strip()
            found_companies.append({
                "name": clean_name,
                "linkedin_url": link,
                "S25": True
            })

    return found_companies

def main():
    queries = [
        'site:linkedin.com/company "YC S25"',
        'site:linkedin.com/company "S25"'
    ]

    all_new_companies = []
    for query in queries:
        found_companies = serpapi_bing_search_s25_companies(query)
        all_new_companies.extend(found_companies)

    # Save or process all_new_companies as needed
    print(json.dumps(all_new_companies, indent=2))

if __name__ == "__main__":
    main()
