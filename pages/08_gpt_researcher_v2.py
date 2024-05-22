import streamlit as st
from gpt_researcher import GPTResearcher
import asyncio
from dotenv import load_dotenv
import os
import validators

# Load environment variables for Langchain and OpenAI
load_dotenv()
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

async def generate_report(query, report_type, sources=None):
    if sources:
        researcher = GPTResearcher(query=query, report_type=report_type, source_urls=sources)
    else:
        researcher = GPTResearcher(query=query, report_type=report_type)

    progress_bar = st.progress(0)
    progress_text = st.empty()

    await researcher.conduct_research()
    progress_bar.progress(50)
    progress_text.text("Research completed. Generating report...")

    report = await researcher.write_report()
    progress_bar.progress(100)
    progress_text.text("Report generated successfully!")

    return report

def validate_urls(urls):
    valid_urls = []
    for url in urls:
        if validators.url(url):
            valid_urls.append(url)
    return valid_urls

def main():
    st.set_page_config(page_title="GPTResearcher Report Generator", page_icon=":memo:", layout="wide")
    st.markdown('<div class="header">GPTResearcher Report Generator</div>', unsafe_allow_html=True)

    query = st.text_input("Enter your query:")
    report_type = st.selectbox("Select the type of report:", ["research_report", "resource_report", "outline_report", "custom_report"])

    research_option = st.radio("Select research option:", ("Web Search", "Specific URLs"))
    sources = None
    if research_option == "Specific URLs":
        urls = st.text_area("Enter URLs (one per line):")
        sources = validate_urls([url.strip() for url in urls.split("\n") if url.strip()])
        if not sources:
            st.error("Please enter at least one valid URL.")

    if st.button("Generate Report"):
        if not query:
            st.error("Please enter a query.")
        else:
            try:
                with st.spinner("Generating report..."):
                    report = asyncio.run(generate_report(query, report_type, sources))
                st.markdown('<div class="subheader">Generated Report</div>', unsafe_allow_html=True)
                st.write(report)
                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name=f"{report_type}.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
