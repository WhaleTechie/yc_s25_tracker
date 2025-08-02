import json
import pandas as pd
import streamlit as st
import os
import subprocess
import sys

st.set_page_config(page_title="YC S25 Tracker", layout="wide")

# Define paths to each stage's output
DATA_FILES = {
    "parser": "data/yc_selected_companies.json",
    "enriched": "data/yc_selected_companies_with_linkedin.json",
    "linkedin_only": "data/merged_s25_companies.json"
}

def run_script(script_name):
    """Run a Python script using the current interpreter and capture output."""
    try:
        result = subprocess.run(
            [sys.executable, script_name], 
            check=True, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"❌ Error: {e.stderr}"

def load_data(path):
    """Load JSON file into a pandas DataFrame."""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

def create_link(url):
    """Return an HTML link if URL is provided."""
    if url:
        return f'<a href="{url}" target="_blank">[Link]</a>'
    return ""

if "data_stage" not in st.session_state:
    st.session_state.data_stage = None

st.title("🚀 YC S25 Startups Tracker")

# Layout buttons side by side
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Run YC Parser"):
        with st.spinner("Running yc_parser.py..."):
            output = run_script("yc_parser.py")
        st.success("✅ YC Parser completed.")
        st.session_state.data_stage = "parser"
        st.code(output)

with col2:
    if st.button("🧠 Run LinkedIn Enrichment"):
        with st.spinner("Running selected_updated.py..."):
            output = run_script("selected_updated.py")
        st.success("✅ LinkedIn enrichment completed.")
        st.session_state.data_stage = "enriched"
        st.code(output)

with col3:
    if st.button("🔍 Run LinkedIn-Only Search"):
        with st.spinner("Running linkedin_only.py..."):
            output = run_script("linkedin_only.py")
        st.success("✅ LinkedIn-only merge completed.")
        st.session_state.data_stage = "linkedin_only"
        st.code(output)

data_stage = st.session_state.data_stage

# Display data table based on latest stage selected
if data_stage:
    df = load_data(DATA_FILES[data_stage])
    if df is None or df.empty:
        st.warning("No data available after update.")
    else:
        # Add visual links if columns exist
        if "yc_url" in df.columns:
            df["YC Page"] = df["yc_url"].apply(create_link)
        if "linkedin_url" in df.columns:
            df["LinkedIn"] = df["linkedin_url"].apply(create_link)

        if "name" in df.columns:
            df_display = df.copy()
            df_display = df_display.rename(columns={
                "name": "Company Name",
                "website": "Website",
                "description": "Description",
                "S25": "LinkedIn mentions YC S25"
            })

            # Show one-by-one cards
            for idx, row in df_display.iterrows():
                st.markdown(f"### {row.get('Company Name', 'Unnamed')}")
                st.markdown(f"- 🌐 Website: {row.get('Website', '')}")
                st.markdown(f"- 📝 Description: {row.get('Description', '')}")
                st.markdown(f"- 📄 YC Page: {row.get('YC Page', '')}", unsafe_allow_html=True)
                st.markdown(f"- 🔗 LinkedIn: {row.get('LinkedIn', '')}", unsafe_allow_html=True)
                s25_flag = row.get("LinkedIn mentions YC S25", False)
                st.markdown(f"- 🧾 YC S25 Mention on LinkedIn: {'✅' if s25_flag else '❌'}")
                st.markdown("---")
        else:
            st.dataframe(df)
else:
    st.info("👆 Select a script to run and display the data.")
