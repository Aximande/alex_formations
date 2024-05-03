import streamlit as st
from gpt_researcher import GPTResearcher
import asyncio
import streamlit.components.v1 as components
import pdfkit
import base64

async def generate_report(query, report_type):
    researcher = GPTResearcher(query=query, report_type=report_type, config_path=None)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def download_pdf(pdf_data):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="report.pdf">Download PDF</a>'
    return href

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
                report = asyncio.run(generate_report(query, report_type))
            components.html(report, height=500, scrolling=True)

            # Generate PDF and provide download link
            pdf_data = pdfkit.from_string(report, False)
            st.markdown(download_pdf(pdf_data), unsafe_allow_html=True)
        else:
            st.warning("Please enter a research query.")

if __name__ == "__main__":
    main()
