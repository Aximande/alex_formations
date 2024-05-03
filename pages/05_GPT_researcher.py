import streamlit as st
from gpt_researcher import GPTResearcher
import asyncio
import streamlit.components.v1 as components

# Define the asynchronous function as before
async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query=query, report_type=report_type)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def load_report():
    # Run the asyncio task in the existing event loop
    loop = asyncio.get_event_loop()
    if not loop.is_running():
        # This should not happen in a normal Streamlit environment
        # but added here for robustness in different setups
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_report(st.session_state.query, st.session_state.report_type))
    report = loop.run_until_complete(future)
    st.session_state.report = report

def main():
    st.title("GPT Researcher Integration")

    # User input for research query
    query = st.text_input("Enter your research query:", key="query")

    # User input for report type
    report_type = st.selectbox("Select the report type:", ["research_report", "outline", "resources", "lessons"], key="report_type")

    # Button to trigger report generation
    if st.button("Generate Report"):
        if query:
            # Store query and report type in session state
            st.session_state.query = query
            st.session_state.report_type = report_type

            # Use spinner to indicate loading and call load report function
            with st.spinner("Generating report..."):
                load_report()

            # Display the report
            if "report" in st.session_state:
                components.html(st.session_state.report, height=500, scrolling=True)
        else:
            st.warning("Please enter a research query.")

if __name__ == "__main__":
    main()
