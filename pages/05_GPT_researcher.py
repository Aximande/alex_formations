import streamlit as st
from gpt_researcher import GPTResearcher
import asyncio
import streamlit.components.v1 as components

async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query=query, report_type=report_type)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def run_async_report(query, report_type):
    if 'report_future' not in st.session_state or st.session_state.report_future.done():
        st.session_state.report_future = asyncio.ensure_future(get_report(query, report_type))

def check_report():
    if 'report_future' in st.session_state:
        if st.session_state.report_future.done():
            # If the report is done, display it
            report = st.session_state.report_future.result()
            components.html(report, height=500, scrolling=True)
        else:
            # If the report is not done, show a spinner and re-run the script
            with st.spinner("Generating report..."):
                st.experimental_rerun()

def main():
    st.title("GPT Researcher Integration")

    # User input for research query
    query = st.text_input("Enter your research query:", key="query")

    # User input for report type
    report_type = st.selectbox("Select the report type:", ["research_report", "outline", "resources", "lessons"], key="report_type")

    # Button to trigger report generation
    if st.button("Generate Report"):
        if query:
            run_async_report(query, report_type)
            check_report()
        else:
            st.warning("Please enter a research query.")

if __name__ == "__main__":
    main()
