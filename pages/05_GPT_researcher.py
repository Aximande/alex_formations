import streamlit as st
from gpt_researcher import GPTResearcher
import asyncio

# Define a function to run asyncio tasks
def run_asyncio_task(query, report_type):
    async def fetch_report():
        researcher = GPTResearcher(query=query, report_type=report_type, config_path=None)
        await researcher.conduct_research()
        return await researcher.write_report()

    return asyncio.run(fetch_report())

# Streamlit interface
def main():
    st.title("Research Report Generator")
    query = st.text_input("Enter your query", "What happened in the latest burning man floods?")
    report_type = st.selectbox("Select Report Type", options=["research_report", "summary", "analysis"], index=0)

    if st.button("Generate Report"):
        with st.spinner('Generating Report...'):
            report = run_asyncio_task(query, report_type)
            st.write(report)

if __name__ == "__main__":
    main()
