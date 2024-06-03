import streamlit as st
from gpt_researcher import GPTResearcher
import asyncio
from dotenv import load_dotenv
import os

# Set and load environment variables for Langchain and OpenAI
load_dotenv()

OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query, report_type)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

async def main():
    st.title("NBA Finals Prediction")
    query = st.text_input("Enter your query", "what team may win the NBA finals?")
    report_type = "resource_report"

    if st.button("Get Report"):
        with st.spinner("Generating report..."):
            report = await get_report(query, report_type)
            st.write(report)

if __name__ == "__main__":
    asyncio.run(main())
