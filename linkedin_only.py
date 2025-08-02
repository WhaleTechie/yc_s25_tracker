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
import os

from selected_updated import setup_driver, random_delay, check_for_block

def has_s25_postfix(text):
    return bool(re.search(r"\(?\s*(yc\s*)?s25\s*\)?", text, re.IGNORECASE))

def bing_search_s25_companies(driver, query, max_wait=10):
    driver.delete_all_cookies()
    driver.get("https://www.bing.com")
    random_delay(2, 4)

    if check_for_block(driver):
        return []

    try:
        search_box = WebDriverWait(driver, max_wait).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
    except TimeoutException:
        return []

    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    try:
        WebDriverWait(driver, max_wait).until(
            EC.presence_of_element_located((By.ID, "b_content"))
        )
    except TimeoutException:
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    results = soup.find_all("li", class_="b_algo")

    found_companies = []

    for result in results:
        a_tag = result.find("a", href=True)
        if not a_tag:
            continue
        href = a_tag["href"]
        if "linkedin.com/company" not in href:
            continue

        title_tag = result.find("h2")
        title_text = title_tag.get_text(strip=True) if title_tag else ""

        if has_s25_postfix(title_text):
            clean_name = re.sub(r"\(?\s*(yc\s*)?s25\s*\)?", "", title_text, flags=re.IGNORECASE).strip()
            found_companies.append({
                "name": clean_name,
                "linkedin_url": href,
                "S25": True
            })

    return found_companies

def normalize_name(name):
    return re.sub(r"\(?\s*(yc\s*)?s25\s*\)?", "", name, flags=re.IGNORECASE).strip().lower()

def merge_company_lists(existing_path, new_path, merged_path):
    if os.path.exists(existing_path):
        with open(existing_path, "r", encoding="utf-8") as f:
            merged_companies = json.load(f)
    else:
        merged_companies = []

    if os.path.exists(new_path):
        with open(new_path, "r", encoding="utf-8") as f:
            new_companies = json.load(f)
    else:
        new_companies = []

    existing_urls = {comp.get("linkedin_url").lower() for comp in merged_companies if comp.get("linkedin_url")}
    existing_names = {normalize_name(comp.get("name", "")) for comp in merged_companies if comp.get("name")}

    for comp in new_companies:
        url = comp.get("linkedin_url")
        if not url:
            continue
        url_lower = url.lower()
        norm_name = normalize_name(comp.get("name", ""))
        if url_lower not in existing_urls and norm_name not in existing_names:
            merged_companies.append(comp)
            existing_urls.add(url_lower)
            existing_names.add(norm_name)

    with open(merged_path, "w", encoding="utf-8") as f:
        json.dump(merged_companies, f, ensure_ascii=False, indent=2)

def main():
    existing_path = "data/yc_selected_companies_with_linkedin.json"
    output_path = "data/s25_found.json"
    merged_path = "data/merged_s25_companies.json"

    if not os.path.exists(existing_path):
        return

    with open(existing_path, "r", encoding="utf-8") as f:
        existing_companies = json.load(f)

    existing_links = {c.get("linkedin_url", "").lower() for c in existing_companies if c.get("linkedin_url")}

    driver = setup_driver()
    all_new_companies = []

    queries = [
        'site:linkedin.com/company "YC S25"',
        'site:linkedin.com/company "S25"'
    ]

    try:
        for query in queries:
            found_companies = bing_search_s25_companies(driver, query)
            for comp in found_companies:
                link_lower = comp["linkedin_url"].lower()
                if link_lower not in existing_links:
                    all_new_companies.append(comp)
                    existing_links.add(link_lower)
            random_delay(5, 10)

        if all_new_companies:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(all_new_companies, f, ensure_ascii=False, indent=2)

            merge_company_lists(existing_path, output_path, merged_path)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
