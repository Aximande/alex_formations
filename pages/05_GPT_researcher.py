import streamlit as st
import gpt_researcher
import asyncio
import streamlit.components.v1 as components

async def generate_report(query):
    researcher = gpt_researcher.GPTResearcher(query=query, config_path=None)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def main():
    st.title("GPT Researcher Integration")

    # User input for research query
    query = st.text_input("Enter your research query:")

    # Button to trigger report generation
    if st.button("Generate Report"):
        if query:
            with st.spinner("Generating report..."):
                report = asyncio.run(generate_report(query))
            components.html(report, height=500, scrolling=True)
        else:
            st.warning("Please enter a research query.")

if __name__ == "__main__":
    main()
