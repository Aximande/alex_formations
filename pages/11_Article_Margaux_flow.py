import streamlit as st
import anthropic
from dotenv import load_dotenv
import os
import base64
import streamlit.components.v1 as components

#########################################

# Load environment variables
load_dotenv()

# Initialize the API client
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    st.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

#########################################

def download_html(html_content, file_name):
    """Convert HTML content to a base64-encoded data URI and generate a download link."""
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{file_name}">Download {file_name}</a>'
    return href

def generate_article_v1(transcript, existing_h1, existing_header):
    system_prompt = "You are an AI assistant that generates SEO articles based on video transcripts."
    user_prompt = f"Please generate an SEO article based on the following transcript:\n\n{transcript}\n\nUse the existing H1 and header:\nH1: {existing_h1}\nHeader: {existing_header}"

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    article_v1 = message.content[0].text

    return article_v1

def fact_check_article(article_v1, transcript):
    system_prompt = "You are an AI assistant that fact-checks articles against video transcripts."
    user_prompt = f"Please fact-check the following article against the provided transcript:\n\nArticle:\n{article_v1}\n\nTranscript:\n{transcript}\n\nAre there any crucial missing elements or discrepancies?"

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    fact_check_result = message.content[0].text

    return fact_check_result

def generate_article_v2(article_v1, fact_check_result):
    system_prompt = "You are an AI assistant that generates updated articles based on fact-check results."
    user_prompt = f"Please generate an updated article based on the following:\n\nOriginal Article:\n{article_v1}\n\nFact-Check Results:\n{fact_check_result}"

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    article_v2 = message.content[0].text

    return article_v2

def generate_faq_answers(questions, transcript, article):
    faq_answers = []
    for question in questions:
        system_prompt = "You are an AI assistant that provides answers to questions based on a transcript and an article."
        user_prompt = f"Please provide an answer to the following question based on the transcript and article:\n\nQuestion: {question}\n\nTranscript:\n{transcript}\n\nArticle:\n{article}"

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        answer = message.content[0].text

        faq_answers.append(answer)

    return faq_answers

def generate_yourtextguru_paragraphs(article, yourtextguru_keywords):
    system_prompt = "You are an AI assistant that generates additional paragraphs based on Yourtextguru keywords."
    user_prompt = f"Please generate 2 additional paragraphs at the end of the following article, incorporating the provided Yourtextguru keywords:\n\nArticle:\n{article}\n\nKeywords: {', '.join(yourtextguru_keywords)}"

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    additional_paragraphs = message.content[0].text

    return additional_paragraphs

def main():
    st.set_page_config(page_title="SEO Article Generator", page_icon=":memo:", layout="wide")

    st.title("SEO Article Generator")

    transcript = st.text_area("Enter the video transcript:")
    existing_h1 = st.text_input("Enter the existing H1:")
    existing_header = st.text_input("Enter the existing header:")

    if st.button("Generate Article V1"):
        article_v1 = generate_article_v1(transcript, existing_h1, existing_header)
        st.session_state['article_v1'] = article_v1
        st.session_state['transcript'] = transcript

        st.subheader("Article V1")
        st.write(article_v1)

    if 'article_v1' in st.session_state:
        if st.button("Fact-Check Article"):
            fact_check_result = fact_check_article(st.session_state['article_v1'], st.session_state['transcript'])
            st.session_state['fact_check_result'] = fact_check_result

            st.subheader("Fact-Check Results")
            st.write(fact_check_result)

    if 'fact_check_result' in st.session_state:
        if st.button("Generate Article V2"):
            article_v2 = generate_article_v2(st.session_state['article_v1'], st.session_state['fact_check_result'])
            st.session_state['article_v2'] = article_v2

            st.subheader("Article V2")
            st.write(article_v2)

    if 'article_v2' in st.session_state:
        questions = []
        for i in range(3):
            question = st.text_input(f"Enter question {i+1} for the FAQ:")
            if question:
                questions.append(question)

        if questions:
            if st.button("Generate FAQ Answers"):
                faq_answers = generate_faq_answers(questions, st.session_state['transcript'], st.session_state['article_v2'])
                st.session_state['faq_answers'] = faq_answers

                st.subheader("FAQ Answers")
                for i, answer in enumerate(faq_answers):
                    st.write(f"Question {i+1}: {questions[i]}")
                    st.write(f"Answer: {answer}")

    if 'article_v2' in st.session_state:
        yourtextguru_keywords = st.text_input("Enter Yourtextguru keywords (comma-separated):")

        if yourtextguru_keywords:
            if st.button("Generate Yourtextguru Paragraphs"):
                yourtextguru_keywords = [kw.strip() for kw in yourtextguru_keywords.split(",")]
                additional_paragraphs = generate_yourtextguru_paragraphs(st.session_state['article_v2'], yourtextguru_keywords)
                st.session_state['additional_paragraphs'] = additional_paragraphs

                st.subheader("Updated Article with Yourtextguru Paragraphs")
                st.write(st.session_state['article_v2'] + "\n\n" + additional_paragraphs)

if __name__ == "__main__":
    main()
