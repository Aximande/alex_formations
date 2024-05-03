import streamlit as st
from gpt_researcher import GPTResearcher

st.title('GPT Researcher')

query = st.text_input("Enter your query:")
if st.button("Conduct Research"):
    researcher = GPTResearcher(query=query, report_type="research_report")
    report = await researcher.conduct_research()
    await researcher.write_report()
    st.write(report)
