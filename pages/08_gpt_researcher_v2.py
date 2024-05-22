import streamlit as st
from gpt_researcher import GPTResearcher
import asyncio
from dotenv import load_dotenv
import os

# Charger les variables d'environnement pour Langchain et OpenAI
load_dotenv()
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

async def generate_report(query, report_type):
    researcher = GPTResearcher(query=query, report_type=report_type)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def main():
    st.set_page_config(page_title="GPTResearcher Report Generator", page_icon=":memo:", layout="wide")

    st.markdown('<div class="header">GPTResearcher Report Generator</div>', unsafe_allow_html=True)

    query = st.text_input("Enter your query:")
    report_type = st.selectbox("Select the type of report:", ["research_report", "resource_report", "custom_report"])

    if st.button("Generate Report"):
        if not query:
            st.error("Please enter a query.")
        else:
            with st.spinner("Generating report..."):
                report = asyncio.run(generate_report(query, report_type))

            st.markdown('<div class="subheader">Generated Report</div>', unsafe_allow_html=True)
            st.write(report)

            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"{report_type}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
