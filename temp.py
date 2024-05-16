import sqlite_override
import streamlit as st
import anthropic
from dotenv import load_dotenv
import os
import base64
import streamlit.components.v1 as components
#from data_common.connectors.sm_connector import SecretManager


# Load environment variables
load_dotenv()

# Initialize the API client
api_key = os.getenv("ANTHROPIC_API_KEY")
######################################################

if not api_key:
    st.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

def download_html(html_content, file_name):
    """Convert HTML content to a base64-encoded data URI and generate a download link."""
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{file_name}">Download {file_name}</a>'
    return href

def generate_seo_article(transcript, target_languages, existing_h1, existing_header):
    """Generates an initial SEO-optimized article from a transcript."""
    system_processing = """
        1. Preprocess the transcript:
           - Extract the transcript text from the <transcript> tags.
           - Remove speaker names/labels (e.g., Valentin:, BRUT:).
           - Remove non-verbal cues in parentheses (e.g., (laughs), (applause)).
           - Fix any obvious typos or transcription errors.
           - Split the text into individual sentences/utterances.
           - Output: cleaned_transcript (a list of strings, each representing a sentence/utterance).

        2. Analyze the preprocessed transcript:
           - Identify the main topic based on tf-idf scores of n-grams.
           - Extract named entities (people, places, organizations) to identify subtopics.
           - Identify question-answer pairs based on typical question words/phrases.
           - Extract key phrases using an unsupervised keyphrase extraction model.
           - Output: main_topic (string), subtopics (list of strings), qa_pairs (list of tuples), key_phrases (list of strings).
    """

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        temperature=0,
        system=system_processing,
        messages=[{"role": "user", "content": f"<transcript>{transcript}</transcript>Target languages: {', '.join(target_languages)}"}]
    )

    raw_output = message.content[0].text
    st.subheader("Preliminary analysis of your current transcript")
    st.write(raw_output)

    system_generation = f"""
You are an AI assistant skilled at converting video transcripts into SEO-optimized articles. Follow this process:

3. Generate the article content:
   - Use the provided H1 and header as context:
     <h1>{existing_h1}</h1>
     <header>{existing_header}</header>
   - Determine the article structure based on the transcript content:
     <transcript>{transcript}</transcript>
   - Generate H2 subheadings:
     - For each key quote or key phrase in the transcript, create an H2 subheading.
     - If a quote, use the quote text between quotation marks as the H2.
     - If not a quote, use a phrase with essential keywords related to the H1.
   - Generate body paragraphs for each H2 subheading:
     - Create two paragraphs, each consisting of 5-6 sentences.
     - Preserve as much of the original transcript as possible without modifying the meaning.
     - When quotes are present in the transcript, use them as direct quotes in the body text, enclosed in quotation marks.
     - Introduce each quote with the speaker's name and a verb (e.g., "explains", "says", "mentions").
     - Provide context or commentary around the quotes to create a coherent narrative.
   - Ensure the article maintains a neutral, informative, and journalistic tone.
   - Do not limit the length of the article.
   - Output: article_content (string).

4. Optimize for SEO:
   - Generate a meta description under 156 characters summarizing the article.
   - Identify 5-10 target keywords/keyphrases based on the key phrases.
   - Suggest relevant meta tags (e.g., article:author, article:published_time, og:image).
   - Ensure keywords are used in the meta description, article headers, and body text.
   - Output: meta_description (string), keywords (list), meta_tags (list).

5. Output the final article:
   - Generate the complete article in HTML format.
   - Include the provided H1 in the <body> section, right before the article content.
   - Add the provided header paragraph after the H1 tag.
   - Structure the body content with the generated H2 subheadings.
   - Include the meta description, keywords, and other meta tags in the HTML <head>.
   - Use schema markup where relevant (e.g., InterviewObject for interview quotes).
   - Output: seo_optimized_article (HTML string).

Existing H1 for this article
{existing_h1}

Existing H1 for this article
{existing_header}

Initial request:
<transcript>{raw_output}</transcript>

Output: seo_optimized_article (HTML string) in the target languages: {', '.join(target_languages)} :
"""
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        temperature=0,
        system=system_generation,
        messages=[{"role": "user", "content": system_generation}]
    )
    html_content = message.content[0].text
    return html_content, raw_output

def generate_revised_article(html_content, user_feedback, initial_request, target_languages):
    """Generates a revised version of the article based on user feedback."""
    system_revision = f"""
        You are an AI assistant skilled at revising video transcripts into SEO-optimized articles based on user feedback. Follow these guidelines:

        - Preserve the overall structure and formatting of the HTML content.
        - Update the title, meta description, keywords, and other metadata based on the feedback.
        - Modify the article content, including the lead paragraph, body paragraphs, and interview quotes, to address the user's feedback.
        - Ensure the revised article is coherent, well-structured, and optimized for SEO.
        - Use schema markup where relevant (e.g., InterviewObject for interview quotes).

        Initial request:
        {initial_request}

        Current article HTML:
        {initial_request}  # Assuming the initial_request contains the current HTML content

        User feedback:
        {user_feedback}

        Output: revised_seo_optimized_article (HTML string) in the target languages: {', '.join(target_languages)} :
    """

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        temperature=0,
        system=system_revision,
        messages=[{"role": "user", "content": user_feedback}]
    )
    revised_html_content = message.content[0].text
    return revised_html_content

def main():
    st.set_page_config(page_title="SEO Article Generator", page_icon=":memo:", layout="wide")

    # Load CSS file
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.image("static/brutAI_logo_noir_background.png", width=300)

    st.markdown('<div class="header">SEO Article Generator from Transcripts</div>', unsafe_allow_html=True)
    transcript = st.text_area("Enter your video transcript:", height=200)
    target_languages = st.multiselect("Select target languages for translation (optional):", ["French", "Spanish", "German", "Hindi", "Afrikaans"])

    if st.button("Generate SEO Article"):
        if not transcript:
            st.error("Please enter a video transcript.")
        elif len(transcript) < 100:
            st.warning("The transcript is quite short. The generated article may not be comprehensive.")
            initial_article, initial_request = generate_seo_article(transcript, target_languages)
            st.session_state['initial_article'] = initial_article
            st.session_state['initial_request'] = initial_request
            st.session_state['target_languages'] = target_languages
            st.markdown('<div class="subheader">Initial SEO Article</div>', unsafe_allow_html=True)
            components.html(f'<div class="html-content">{initial_article}</div>', height=500, scrolling=True)
            st.markdown(download_html(initial_article, "initial_article.html"), unsafe_allow_html=True)
        else:
            initial_article, initial_request = generate_seo_article(transcript, target_languages)
            st.session_state['initial_article'] = initial_article
            st.session_state['initial_request'] = initial_request
            st.session_state['target_languages'] = target_languages
            st.markdown('<div class="subheader">Initial SEO Article</div>', unsafe_allow_html=True)
            components.html(f'<div class="html-content">{initial_article}</div>', height=500, scrolling=True)
            st.markdown(download_html(initial_article, "initial_article.html"), unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if 'initial_article' in st.session_state:
        st.markdown('<div class="subheader">Feedback and Revision</div>', unsafe_allow_html=True)
        user_feedback = st.text_area("Enter your feedback (optional):", height=200)

        if st.button("Submit Feedback"):
            if 'initial_request' in st.session_state and user_feedback:
                revised_article = generate_revised_article(
                    st.session_state['initial_article'], user_feedback, st.session_state['initial_request'], st.session_state['target_languages']
                )
                st.session_state['revised_article'] = revised_article
                st.markdown('<div class="subheader">Revised SEO Article</div>', unsafe_allow_html=True)
                components.html(f'<div class="html-content">{revised_article}</div>', height=500, scrolling=True)
                st.markdown(download_html(revised_article, "revised_article.html"), unsafe_allow_html=True)
            else:
                st.warning("Please provide feedback to generate a revised article.")

if __name__ == "__main__":
    main()


-------



div.row-widget.stRadio>div {
  flex-direction: row;
  align-items: stretch;
}

div.row-widget.stRadio>div[role="radiogroup"]>label[data-baseweb="radio"] {
  background-color: #323439;
  padding-right: 30px;
  padding-left: 20px;
  padding-top: 15px;
  padding-bottom: 15px;
  margin: 4px;
}


.html-content {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 5px;
  color: #333333;
}

.html-content h1,
.html-content h2,
.html-content h3,
.html-content h4,
.html-content h5,
.html-content h6 {
  color: #2E86C1;
}

.html-content a {
  color: #2E86C1;
}
