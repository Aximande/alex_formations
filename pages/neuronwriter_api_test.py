import streamlit as st
import requests
import json
import time

def get_neuronwriter_keywords(article_content, existing_h1):
    API_ENDPOINT = 'https://app.neuronwriter.com/neuron-api/0.5/writer'
    API_KEY = st.secrets["NEURONWRITER_API_KEY"]  # Store your API key in Streamlit secrets

    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Create a new query
    new_query_payload = json.dumps({
        "project": st.secrets["NEURONWRITER_PROJECT_ID"],  # Store your project ID in Streamlit secrets
        "keyword": existing_h1,
        "engine": "google.fr",
        "language": "French",
    })

    with st.spinner("Creating new query..."):
        response = requests.post(f"{API_ENDPOINT}/new-query", headers=headers, data=new_query_payload)
        query_id = response.json().get("query")

    if not query_id:
        st.error("Failed to create a new query.")
        return None

    # Import the full article content
    import_content_payload = json.dumps({
        "query": query_id,
        "html": article_content,
        "title": existing_h1
    })

    with st.spinner("Importing article content..."):
        response = requests.post(f"{API_ENDPOINT}/import-content", headers=headers, data=import_content_payload)
        if response.status_code != 200:
            st.error("Failed to import article content.")
            return None

    # Check query status and get recommendations
    get_query_payload = json.dumps({"query": query_id})

    with st.spinner("Waiting for recommendations..."):
        for _ in range(12):  # Try for 2 minutes (12 * 10 seconds)
            response = requests.post(f"{API_ENDPOINT}/get-query", headers=headers, data=get_query_payload)
            data = response.json()

            if data.get('status') == 'ready':
                return {
                    'basic_terms': data['terms_txt']['content_basic'],
                    'terms_with_ranges': data['terms_txt']['content_basic_w_ranges'],
                    'entities': data['terms_txt']['entities'],
                    'word_count': data['metrics']['word_count']['target']
                }

            time.sleep(10)  # Wait 10 seconds before checking again

    st.error("Recommendations not ready after 2 minutes.")
    return None

# Streamlit UI
st.title("NeuronWriter Keyword Recommendation Tester")

existing_h1 = st.text_input("Enter your H1 title:", "Best Trail Running Shoes in 2024")
article_content = st.text_area("Enter your article content:", height=300)

if st.button("Get NeuronWriter Recommendations"):
    if article_content and existing_h1:
        results = get_neuronwriter_keywords(article_content, existing_h1)
        if results:
            st.success("Successfully retrieved NeuronWriter recommendations!")
            st.subheader("Basic Terms")
            st.write(results['basic_terms'])
            st.subheader("Terms with Usage Ranges")
            st.write(results['terms_with_ranges'])
            st.subheader("Entities")
            st.write(results['entities'])
            st.subheader("Recommended Word Count")
            st.write(results['word_count'])
        else:
            st.error("Failed to retrieve recommendations. Please try again.")
    else:
        st.warning("Please enter both the H1 title and article content.")
