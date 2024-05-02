import streamlit as st
import anthropic
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
from PIL import Image

load_dotenv()  # Load environment variables from the .env file

#with open("style.css") as f:
#    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#st.image(
#    Image.open("static/brutAI_logo_noir_background.png"),
#    width=300,
#)

st.title("SEO Article Generator from Transcripts")

transcript = st.text_area("Enter your video transcript:", height=200)
target_languages = st.multiselect("Select target languages for translation (optional):", ["French", "Spanish", "German"])


button = st.button("Generate SEO Article")

if button:
    if not transcript:
        st.error("Please enter a video transcript.")
    elif len(transcript) < 100:
        st.error("The transcript is too short. Please provide a longer transcript.")
    else:
        progress_text = "Generating SEO Article..."
        progress_bar = st.progress(0, text=progress_text)

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            client = anthropic.Anthropic(api_key=api_key)
        else:
            st.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")

        progress_bar.progress(0.2, text="Preprocessing the transcript...")
        progress_bar.progress(0.4, text="Analyzing the preprocessed transcript...")
        progress_bar.progress(0.6, text="Generating the article content...")
        progress_bar.progress(0.8, text="Optimizing for SEO...")
        progress_bar.progress(1.0, text="Generating the final SEO-optimized article...")

        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            temperature=0,
            system=f"""
            You are an AI assistant skilled at converting video transcripts into SEO-optimized articles. Follow this process:

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

        # Extract the HTML content from the API response
        html_content = message.content[0].text

        # Display the raw generated content
        st.subheader("Raw Generated Content")
        st.write(html_content)

        # Display the HTML content if it's not empty
        if html_content.strip():
            st.header("Generated SEO Article")
            components.html(html_content, height=600, scrolling=True)
        else:
            st.warning("No HTML content was generated.")
