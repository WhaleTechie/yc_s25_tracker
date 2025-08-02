## How to Use

1. **Activate your Python environment and install dependencies:**

   ```bash
   source ./env/Scripts/activate   # Windows PowerShell: .\env\Scripts\Activate.ps1
   pip install -r requirements.txt

2. **Run the Streamlit app:**
   
   ```bash
    streamlit run app.py

3. **Use the UI buttons to:**

Run the YC parser to extract companies.

Run LinkedIn enrichment to gather additional company info.

Run LinkedIn-only search to find companies mentioning YC S25 on LinkedIn but missing from YC's directory.

4. **View the results displayed as cards**

## CHALLENGES

- LinkedIn often blocks automated scraping if you are not logged in, making direct parsing difficult.
- Google searches for LinkedIn pages also tend to get blocked or rate-limited.
- To work around this, the project uses Bing for searching LinkedIn pages, combined with delays (`sleep`) between requests to avoid getting blocked.
- Despite these efforts, some data may be missing due to these restrictions.
- SerpAPI Integration for Search
This project uses SerpAPI to perform Bing searches for YC S25 startups and extract LinkedIn company profiles efficiently, replacing slower and more fragile Selenium scraping. But its limited with 500 requests per month

**Live Demo**
Check out the live version of the YC S25 Startups Tracker app here:

🔗 https://ycs25lidia.streamlit.app/