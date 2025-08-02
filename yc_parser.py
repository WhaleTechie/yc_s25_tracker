import requests
import json
import re
from pathlib import Path
import sys
import subprocess

def run_yc_scraper():
    # Headers for Algolia request
    headers = {
        "x-algolia-agent": "Algolia for JavaScript (3.35.1); Browser; JS Helper (3.16.1)",
        "x-algolia-application-id": "45BWZJ1SGC",
        "x-algolia-api-key": "MjBjYjRiMzY0NzdhZWY0NjExY2NhZjYxMGIxYjc2MTAwNWFkNTkwNTc4NjgxYjU0YzFhYTY2ZGQ5OGY5NDMxZnJlc3RyaWN0SW5kaWNlcz0lNUIlMjJZQ0NvbXBhbnlfcHJvZHVjdGlvbiUyMiUyQyUyMllDQ29tcGFueV9CeV9MYXVuY2hfRGF0ZV9wcm9kdWN0aW9uJTIyJTVEJnRhZ0ZpbHRlcnM9JTVCJTIyeWNkY19wdWJsaWMlMjIlNUQmYW5hbHl0aWNzVGFncz0lNUIlMjJ5Y2RjJTIyJTVE"
    }

    batch_filters = '"batch": "Summer 2025"'

    payload = {
        "requests": [
            {
                "indexName": "YCCompany_production",
                "params": f'hitsPerPage=1000&filters={batch_filters}'
            }
        ]
    }

    response = requests.post(
        "https://45bwzj1sgc-dsn.algolia.net/1/indexes/*/queries",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    data = response.json()

    results = data['results'][0]['hits']
    extracted = []
    for item in results:
        name = item.get("name")

        # Build slug for YC URL (prefer slug if available)
        if item.get("slug"):
            slug = item.get("slug")
        else:
            slug = re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-')) if name else None

        yc_url = f"https://www.ycombinator.com/companies/{slug}" if slug else None

        extracted.append({
            "name": name,
            "website": item.get("website"),
            "batch": item.get("batch"),
            "description": item.get("long_description"),
            "location": item.get("all_locations"),
            "industry": item.get("industry"),
            "team_size": item.get("team_size"),
            "yc_url": yc_url
        })

    # Make sure data directory exists
    Path("data").mkdir(parents=True, exist_ok=True)

    with open("data/yc_selected_companies.json", "w", encoding="utf-8") as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(extracted)} companies to data/yc_selected_companies.json")

def run_yc_parser():
    python_executable = sys.executable  # This gets the Python interpreter used to run your Streamlit app (i.e., your .venv)
    subprocess.run([python_executable, "yc_parser.py"], check=True)
    