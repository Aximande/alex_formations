import streamlit as st
from gpt_researcher import GPTResearcher
import asyncio

async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query, report_type)
    report = await researcher.run()
    return report

def app():
    st.title("NBA Finals Prediction")
    query = st.text_input("Enter your query", "what team may win the NBA finals?")
    report_type = "research_report"

    if st.button("Get Report"):
        with st.spinner("Generating report..."):
            report = asyncio.run(get_report(query, report_type))
            st.write(report)

if __name__ == "__main__":
    app()

