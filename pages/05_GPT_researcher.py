import streamlit as st
from gpt_researcher import GPTResearcher
import asyncio
import streamlit.components.v1 as components
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

async def get_report(query: str, report_type: str) -> str:
    try:
        researcher = GPTResearcher(query=query, report_type=report_type)
        await researcher.conduct_research()
        report = await researcher.write_report()
        return report
    except Exception as e:
        logger.exception("Error generating report")
        raise e

def run_async_report(query, report_type):
    if 'report_future' not in st.session_state or st.session_state.report_future.done():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        st.session_state.report_future = asyncio.ensure_future(asyncio.shield(get_report(query, report_type)))  # Use asyncio.shield

def check_report():
    if 'report_future' in st.session_state:
        if st.session_state.report_future.done():
            try:
                report = st.session_state.report_future.result()
                components.html(report, height=500, scrolling=True)
            except Exception as e:
                logger.exception("Error displaying report")
                st.error("An error occurred while displaying the report.")
        else:
            with st.spinner("Generating report..."):
                st.rerun()

def main():
    st.title("GPT Researcher Integration")

    query = st.text_input("Enter your research query:", key="query")
    report_type = st.selectbox("Select the report type:", ["research_report", "outline", "resources", "lessons"], key="report_type")

    if st.button("Generate Report"):
        if query:
            run_async_report(query, report_type)
            check_report()
        else:
            st.warning("Please enter a research query.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Unhandled exception")
        st.error("An unexpected error occurred. Please check the logs for more details.")
