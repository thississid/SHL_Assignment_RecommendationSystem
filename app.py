import re
import streamlit as st
import pandas as pd
import requests

# Load the catalog from your CSV file.
# The CSV file is expected to have columns like:
# name, url, remote_testing, adaptive, duration, test_type, keywords
# where the 'keywords' column is a comma-separated string.
@st.cache_data
def load_catalog():
    df = pd.read_csv("asdasd.csv")
    # Convert the 'keywords' column into a list of keywords (lowercase) if it exists.
    if 'keywords' in df.columns:
        df['keywords'] = df['keywords'].apply(lambda x: [k.strip().lower() for k in str(x).split(',')])
    return df

catalog_df = load_catalog()

def call_gemini_api(query):
    """
    Call the Gemini API to parse the query.
    Replace the below stub with an actual API call.
    
    For example, if Gemini provides an endpoint for parsing queries:
      url = "https://api.gemini.ai/v1/parse"
      headers = {"Authorization": "Bearer YOUR_API_KEY", "Content-Type": "application/json"}
      data = {"query": query}
      response = requests.post(url, json=data, headers=headers)
      response_json = response.json()
      return response_json
    
    In this stub, we simulate the response by extracting duration and keywords.
    """
    # Simulate duration extraction (e.g., "40 minutes")
    criteria = {}
    duration_match = re.search(r'(\d+)\s*minutes?', query, re.IGNORECASE)
    if duration_match:
        criteria["duration"] = int(duration_match.group(1))
    
    # Simulate keyword extraction.
    # Adjust the list below to include any keywords relevant for your assessments.
    search_keywords = ["java", "python", "sql", "javascript", "analyst", "cognitive", "personality", "technical", "aptitude"]
    found_keywords = []
    for kw in search_keywords:
        if re.search(r'\b' + kw + r'\b', query, re.IGNORECASE):
            found_keywords.append(kw)
    criteria["keywords"] = found_keywords
    
    return criteria

def search_catalog(criteria, catalog_df):
    """
    Searches the catalog DataFrame for assessments that meet the criteria.
    Returns a DataFrame with at most 10 matching items.
    """
    results = []
    for index, row in catalog_df.iterrows():
        # Check duration: extract a number from the duration field.
        item_duration_match = re.search(r'(\d+)', str(row["duration"]))
        item_duration = int(item_duration_match.group(1)) if item_duration_match else None
        duration_ok = True
        if "duration" in criteria and item_duration is not None:
            if item_duration > criteria["duration"]:
                duration_ok = False
        
        # Check for keyword matches.
        keywords_ok = True
        if "keywords" in criteria and criteria["keywords"]:
            # Ensure we compare in lowercase.
            item_keywords = row["keywords"] if pd.notnull(row["keywords"]) else []
            if not any(kw in item_keywords for kw in criteria["keywords"]):
                keywords_ok = False
        
        if duration_ok and keywords_ok:
            results.append(row)
    
    if results:
        result_df = pd.DataFrame(results)
    else:
        result_df = pd.DataFrame(columns=catalog_df.columns)
    return result_df.head(10)

def main():
    st.title("SHL Assessment Recommendation System")
    st.write("Enter a natural language query or job description:")

    query = st.text_area("Query", height=150, placeholder="e.g. I am hiring for Java developers who can complete a test in 40 minutes")
    
    if st.button("Search"):
        if not query.strip():
            st.warning("Please enter a query.")
        else:
            # Use the Gemini API to parse the query.
            criteria = call_gemini_api(query)
            st.write("**Extracted Criteria:**", criteria)
            # Search for matching assessments in the catalog.
            result_df = search_catalog(criteria, catalog_df)
            
            if not result_df.empty:
                st.write("### Results")
                # Display the results in a table.
                st.dataframe(result_df[["name", "url", "remote_testing", "adaptive", "duration", "test_type"]])
            else:
                st.info("No assessments found for the given query.")

if __name__ == "__main__":
    main()
