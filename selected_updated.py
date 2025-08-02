import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import sys
import subprocess
from webdriver_setup import create_driver

# --- Driver Setup ---
def setup_driver():
    return create_driver()

# --- Helpers ---
def random_delay(min_seconds=3, max_seconds=7):
    delay = random.uniform(min_seconds, max_seconds)
    #print(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)

def check_for_block(driver):
    page_text = driver.page_source.lower()
    if "captcha" in page_text or "verify" in page_text or "unusual traffic" in page_text:
        print("⚠️ Detected CAPTCHA or bot verification. Stopping script.")
        return True
    return False

import re

def has_yc_s25_postfix(text, company_name):
    # This pattern matches:
    # company_name optionally followed by whitespace
    # optionally '(' or '['
    # optional 'yc' followed by whitespace (optional)
    # s25
    # optionally ')' or ']'
    pattern = re.compile(
        re.escape(company_name) + r"\s*(\(|\[)?\s*(yc\s*)?s25(\)|\])?",
        re.IGNORECASE
    )
    return bool(pattern.search(text))

def bing_search_linkedin(driver, query, company_name, max_wait=10):
    driver.delete_all_cookies()
    driver.get("https://www.bing.com")
    random_delay(2, 4)

    if check_for_block(driver):
        return None, False

    try:
        search_box = WebDriverWait(driver, max_wait).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
    except TimeoutException:
        print("Search box not found.")
        return None, False

    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    try:
        WebDriverWait(driver, max_wait).until(
            EC.presence_of_element_located((By.ID, "b_content"))
        )
    except TimeoutException:
        print("Search results did not load.")
        return None, False

    soup = BeautifulSoup(driver.page_source, "html.parser")
    results = soup.find_all("li", class_="b_algo")

    fallback_url = None
    found_any = False
    company_name_lower = company_name.lower()

    for result in results:
        a_tag = result.find("a", href=True)
        if not a_tag:
            continue

        href = a_tag["href"]
        if "linkedin.com/company" not in href:
            continue

        found_any = True

        # Extract the title text (usually in <h2> or <a>)
        title_tag = result.find("h2")
        title_text = title_tag.get_text(strip=True).lower() if title_tag else ""

        # Extract snippet/description text
        snippet_tag = result.find("p")
        snippet_text = snippet_tag.get_text(strip=True).lower() if snippet_tag else ""

        # Check if YC S25 or S25 postfix appears in title or snippet related to company
        combined_text = f"{title_text} {snippet_text}"

        if has_yc_s25_postfix(combined_text, company_name_lower):
            print(f"  Found YC S25 LinkedIn URL: {href}")
            return href, True  # Found URL with S25 mention

        if not fallback_url:
            fallback_url = href

    # If no YC S25 mention found, return first LinkedIn URL found with False
    if found_any:
        return fallback_url, False
    else:
        print("  ⚠️ No LinkedIn company links found in search results.")
        return None, False

# --- Main Runner ---
def main():
    input_path = "data/yc_selected_companies.json"
    output_path = "data/yc_selected_companies_with_linkedin.json"

    with open(input_path, "r", encoding="utf-8") as f:
        companies = json.load(f)

    driver = setup_driver()

    try:
        for i, company in enumerate(companies):
            name = company.get("name", "")
            print(f"🔍 Searching LinkedIn for: {name}")
            query = f'linkedin.com/company "{name}"'

            url, s25_found = bing_search_linkedin(driver, query, name)
            company["linkedin_url"] = url
            company["S25"] = s25_found

            if url and "linkedin.com/company" in url:
                print(f"  ✅ LinkedIn URL: {url}")
                print(f"  🏷️ YC S25 Mentioned: {s25_found}")
            else:
                company["linkedin_url"] = None
                company["S25"] = False
                print("  ⚠️ No LinkedIn URL found.")

            # Save progress after each company
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(companies, f, ensure_ascii=False, indent=2)

            random_delay(5, 10)

        print(f"\n✅ Done! Results saved to: {output_path}")

    finally:
        driver.quit()

def run_selected_updated():
    python_executable = sys.executable
    subprocess.run([python_executable, "selected_updated.py"], check=True)
