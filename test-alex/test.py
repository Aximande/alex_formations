#api_key = "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"

import streamlit as st
import anthropic
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
from PIL import Image
import base64  # Required for file download functionality

def generate_seo_article(transcript, target_languages):
    progress_text = "Generating SEO Article..."
    progress_bar = st.progress(0, text=progress_text)

    api_key = "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"
    if api_key:
        client = anthropic.Anthropic(api_key=api_key)
    else:
        st.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")

    progress_bar.progress(0.2, text="Preprocessing the transcript...")
    progress_bar.progress(0.4, text="Analyzing the preprocessed transcript...")

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2000,
        temperature=0,
        system="""
        1. Preprocess the transcript:
           - Extract the transcript text from the <transcript> tags
           - Remove speaker names/labels (e.g., Valentin:, BRUT:)
           - Remove non-verbal cues in parentheses (e.g., (rires))
           - Fix any obvious typos or transcription errors
           - Split the text into individual sentences/utterances
           - Output: cleaned_transcript (a list of strings, each representing a sentence/utterance)

        2. Analyze the preprocessed transcript:
           - Identify the main topic based on tf-idf scores of n-grams
           - Extract named entities (people, places, organizations) to identify subtopics
           - Identify question-answer pairs based on typical question words/phrases
           - Extract key phrases using an unsupervised keyphrase extraction model
           - Output: main_topic (string), subtopics (list of strings), qa_pairs (list of tuples), key_phrases (list of strings)
        """,
        messages=[
            {
                "role": "user",
                "content": f"""
                <transcript>
                {transcript}
                </transcript>

                Target languages: {', '.join(target_languages) if target_languages else 'None'}
                """
            }
        ]
    )

    # Extract the raw text output from the API response
    raw_output = message.content[0].text

    progress_bar.progress(0.6, text="Generating the article content...")
    progress_bar.progress(0.8, text="Optimizing for SEO...")
    progress_bar.progress(1.0, text="Generating the final SEO-optimized article...")

    initial_request = f"""
    Raw output from preprocessing and analysis:
    {raw_output}

    Target languages: {', '.join(target_languages) if target_languages else 'None'}
    """

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4000,
        temperature=0,
        system=f"""
        You are an AI assistant skilled at converting video transcripts into SEO-optimized articles. Follow this process:

        3. Generate the article content:
           - Determine article structure based on the examples (e.g., lead paragraph, key points, interview quotes)
           - Generate a lead paragraph introducing the main topic
           - Generate body paragraphs for each subtopic, using relevant sentences from the transcript
           - Convert question-answer pairs into interview quote paragraphs
           - Ensure coherence and fluency using a large language model
           - Output: article_content (string)

        4. Optimize for SEO:
           - Generate an engaging, keyword-rich title under 60 characters
           - Generate a meta description under 156 characters summarizing the article
           - Identify 5-10 target keywords/keyphrases based on the key_phrases
           - Suggest relevant meta tags (e.g., article:author, article:published_time, og:image)
           - Ensure keywords are used in the title, meta description, article headers, and body text
           - Output: seo_title (string), meta_description (string), keywords (list), meta_tags (list)

        5. Generate H1 and Chapô:
           - Generate an H1 tag that is slightly different from the SEO title and under 60 characters
           - Generate a chapô (introductory paragraph) under 300 characters
           - Output: h1 (string), chapo (string)

        6. Output the final article:
           - Generate the complete article in HTML format
           - Include the SEO-optimized title, meta description, keywords, and other meta tags in the HTML <head>
           - Include the H1 tag in the <body> section, right before the article content
           - Add the chapô paragraph after the H1 tag
           - Structure the body content with relevant header tags (H1, H2, etc.), ensuring H2 subheadings are within 80 characters
           - Use schema markup where relevant (e.g., InterviewObject for interview quotes)
           - Output: seo_optimized_article (HTML string)

        Initial request:
        {initial_request}
        """,
        messages=[
            {
                "role": "user",
                "content": initial_request
            }
        ]
    )

    # Extract the HTML content from the API response
    html_content = message.content[0].text
    return html_content

def generate_revised_article(transcript, target_languages, user_feedback):
    progress_text = "Generating Revised SEO Article..."
    progress_bar = st.progress(0, text=progress_text)

    api_key = "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"
    if api_key:
        client = anthropic.Anthropic(api_key=api_key)
    else:
        st.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")

    progress_bar.progress(0.2, text="Incorporating user feedback...")
    progress_bar.progress(0.4, text="Analyzing the preprocessed transcript...")
    progress_bar.progress(0.6, text="Generating the revised article content...")
    progress_bar.progress(0.8, text="Optimizing for SEO...")
    progress_bar.progress(1.0, text="Generating the final revised SEO-optimized article...")

    initial_request = generate_seo_article(transcript, target_languages)

    current_article_html = initial_request

    system_prompt = f"""
    You are an AI assistant skilled at converting video transcripts into SEO-optimized articles and revising them based on user feedback.

    Here was the initial request:
    {initial_request}

    Here is the current article in HTML format:
    {current_article_html}

    Here is the desired feedback from the user about this current article:
    {user_feedback}

    Based on this feedback, generate a revised version of the article in HTML format, incorporating the user's suggestions while maintaining SEO optimization. Follow these guidelines:

    1. Preserve the overall structure and formatting of the HTML content.
    2. Update the title, meta description, keywords, and other metadata based on the feedback.
    3. Modify the article content, including the lead paragraph, body paragraphs, and interview quotes, to address the user's feedback.
    4. Ensure the revised article is coherent, well-structured, and optimized for SEO.
    5. Use schema markup where relevant (e.g., InterviewObject for interview quotes).

    Output: revised_seo_optimized_article (HTML string)
    """

    # Print the final system prompt
    st.write("Final System Prompt:")
    st.code(system_prompt, language="text")

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4000,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": system_prompt
            }
        ]
    )

    # Extract the HTML content from the API response
    revised_html_content = message.content[0].text
    return revised_html_content

load_dotenv()  # Load environment variables from the .env file

st.title("SEO Article Generator from Transcripts")

transcript = st.text_area("Enter your video transcript:", height=200)
target_languages = st.multiselect("Select target languages for translation (optional):", ["French", "Spanish", "German"])

button_generate = st.button("Generate SEO Article")

if button_generate:
    if not transcript:
        st.error("Please enter a video transcript.")
    elif len(transcript) < 100:
        st.error("The transcript is too short. Please provide a longer transcript.")
    else:
        html_content = generate_seo_article(transcript, target_languages)

        # Display the raw generated content
        st.subheader("Raw Generated Content")
        st.write(html_content)

        # Display the HTML content if it's not empty
        if html_content.strip():
            # Split the screen into two columns
            col1, col2 = st.columns(2)

            with col1:
                st.header("Initial SEO Article")
                components.html(html_content, height=600, scrolling=True)

                # Add a button to download the HTML content
                output_file_name = "generated_article.html"
                data = html_content.encode()
                b64 = base64.b64encode(data).decode()
                href = f'<a href="data:file/html;base64,{b64}" download="{output_file_name}">Download HTML File</a>'
                st.markdown(href, unsafe_allow_html=True)

            with col2:
                st.header("Revised SEO Article")
                revised_html_content = ""  # Initialize with an empty string

                # Ask for user feedback
                st.subheader("Provide Feedback")
                user_feedback = st.text_area("Enter your feedback (optional):", height=200)

                # Create a button to submit feedback
                button_submit_feedback = st.button("Submit Feedback")

                # Generate revised article if user feedback is provided and the "Submit Feedback" button is clicked
                if button_submit_feedback and user_feedback:
                    revised_html_content = generate_revised_article(transcript, target_languages, user_feedback)

                if revised_html_content:
                    components.html(revised_html_content, height=600, scrolling=True)
                else:
                    st.info("No revised article generated yet.")

        else:
            st.warning("No HTML content was generated.")
