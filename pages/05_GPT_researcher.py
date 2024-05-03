import streamlit as st
from gpt_researcher import GPTResearcher
import asyncio
import streamlit.components.v1 as components

async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query=query, report_type=report_type)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def main():
    st.title("GPT Researcher Integration")

    # User input for research query
    query = st.text_input("Enter your research query:")

    # User input for report type
    report_type = st.selectbox("Select the report type:", ["research_report", "outline", "resources", "lessons"])

    # Button to trigger report generation
    if st.button("Generate Report"):
        if query:
            with st.spinner("Generating report..."):
                report = asyncio.run(get_report(query, report_type))
            components.html(report, height=500, scrolling=True)
        else:
            st.warning("Please enter a research query.")

if __name__ == "__main__":
    main()
