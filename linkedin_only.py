import os
import json
import re
import streamlit as st
from serpapi import GoogleSearch

def has_s25_postfix(text):
    return bool(re.search(r"\(?\s*(yc\s*)?s25\s*\)?", text, re.IGNORECASE))

def serpapi_bing_search_s25_companies(query, api_key):
    if not api_key:
        raise ValueError("SERPAPI_API_KEY environment variable not set")

    params = {
        "engine": "bing",
        "q": query,
        "api_key": api_key,
        "count": 20
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    found_companies = []

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
    api_key = st.secrets.get("SERPAPI_API_KEY")
    if not api_key:
        st.error("SERPAPI_API_KEY is not set in secrets.")
        return

    queries = [
        'site:linkedin.com/company "YC S25"',
        'site:linkedin.com/company "S25"'
    ]

    all_new_companies = []
    for query in queries:
        found_companies = serpapi_bing_search_s25_companies(query, api_key)
        all_new_companies.extend(found_companies)

    st.write("Found companies:")
    st.json(all_new_companies)

if __name__ == "__main__":
    main()