import streamlit as st
import anthropic
from dotenv import load_dotenv
import os
import base64
import asyncio
import streamlit.components.v1 as components
from gpt_researcher import GPTResearcher

# Load environment variables
load_dotenv()

# Initialize the API client
api_key = os.getenv("ANTHROPIC_API_KEY")

tavily_api_key = os.getenv("TAVILY_API_KEY")

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
    system_processing = f"""
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

        3. Generate alternative H1 and header suggestions:
           - Based on the main topic, subtopics, and key phrases, generate 2-3 alternative H1 suggestions.
           - Ensure the suggested H1s are engaging, concise, and capture the main theme of the transcript.
           - Based on the main topic and the existing header, generate 2-3 alternative header suggestions.
           - Ensure the suggested headers provide a compelling introduction to the article and align with the H1.
           - Output: alt_h1_suggestions (list of strings), alt_header_suggestions (list of strings).

        Existing H1: {existing_h1}
        Existing Header: {existing_header}
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
   - Determine the article structure based on the pre-processed transcript content
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

Existing H1 for this article =
"
{existing_h1}
"

Existing H1 for this article =
"
{existing_header}
"

Initial pre-processed transcript =
"
{raw_output}
"


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

def generate_revised_article(html_content, user_feedback, initial_request, target_languages, existing_h1, existing_header):
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

        Existing H1 for this article
        {existing_h1}

        Existing Header for this article
        {existing_header}

        Current article HTML:
        {html_content}

        User feedback:
        {user_feedback}

        Output: revised_seo_optimized_article (HTML string) in the target languages: {', '.join(target_languages)} :
    """

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        temperature=0,
        system=system_revision,
        messages=[{"role": "user", "content": system_revision}]
    )
    revised_html_content = message.content[0].text
    return revised_html_content

def fact_check_article(article_content, transcript):
    fact_check_prompt = f"""
You will be acting as a fact-checking assistant to ensure that an SEO article generated from a video transcript is truthful and does not contain any hallucinations or inventions not supported by the original transcript.

Here is the SEO article:

<seo_article>
{article_content}
</seo_article>

And here is the full video transcript the article should be based on:

<transcript>
{transcript}
</transcript>

Please carefully compare the SEO article to the provided transcript. Your task is to identify any claims, statements or details in the article that are not directly supported by the transcript. These are considered "hallucinations" or "inventions".

<scratchpad>
If you find any hallucinations or invented details in the SEO article, write them down here. For each one, identify the key assumption(s) behind the hallucinated claim. Keep these brief and to the point.
</scratchpad>

If no hallucinations or inventions are found, simply output:

<result>
The SEO article appears to be fully supported by the video transcript. No hallucinations or inventions detected.
</result>

However, if you do identify hallucinations or inventions, your next step is to generate a set of fact-checkable questions that challenge the key assumptions you identified. These questions should be used to search for evidence that either confirms or refutes the hallucinated claims, using the video transcript as the sole source of ground truth.

Frame your questions to explore the basic existence or accuracy of the hallucinated details. Do not address or refer to the user, as your questions will only be used for background searches, not shown directly.

Use varied wording and sentence structures for your questions to maximize the scope of the searches. The goal is to cast a wide net to find any relevant information in the transcript that relates to the hallucinated claims.

After listing your questions, provide a final recommendation on whether the SEO article needs to be revised to align with the transcript. Output your full results like this:

<result>
<hallucinations>
1. [Hallucinated claim 1]
2. [Hallucinated claim 2]
3. [Hallucinated claim 3]
</hallucinations>

<fact_check_questions>
1. [Question challenging assumption behind hallucination 1]
2. [Question challenging assumption behind hallucination 1 - alternate phrasing]
3. [Question challenging assumption behind hallucination 2]
4. [Question challenging assumption behind hallucination 2 - alternate phrasing]
5. [Question challenging assumption behind hallucination 3]
6. [Question challenging assumption behind hallucination 3 - alternate phrasing]
</fact_check_questions>

<recommendation>
Based on the hallucinations identified, the SEO article should be revised to remove or modify any claims not directly supported by the video transcript. The fact check questions above should be used to verify details before including them in the final article.
</recommendation>
</result>

Remember, the video transcript is the only source you should use for fact-checking. Do not make assumptions or rely on any external knowledge. If you're unsure whether something in the article is supported by the transcript, err on the side of caution and flag it for further checking.

Provide your full analysis and fact check questions in a single response. No need to double-check your work or engage in any additional dialogue. Just follow the instructions to the best of your abilities based on the information provided.
"""

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        temperature=0,
        system="You are a fact-checking assistant.",
        messages=[{"role": "user", "content": fact_check_prompt}]
    )

    fact_check_results = message.content[0].text
    return fact_check_results

async def generate_faq(query: str, report_type: str) -> str:
    query = f"Generate a short FAQs related to the topic: {article_content}"
    researcher = GPTResearcher(query=query, report_type="research_report")
    # Conduct research on the given query
    faq_content = await researcher.run()
    return faq_content

st.set_page_config(page_title="SEO Article Generator", page_icon=":memo:", layout="wide")

st.image("brutAI_logo_noir_background.png", width=300)

st.markdown('<div class="header">SEO Article Generator from Transcripts</div>', unsafe_allow_html=True)
transcript = st.text_area("Enter your video transcript:", height=200)
existing_h1 = st.text_input("Enter your current H1:")
existing_header = st.text_input("Enter your current header:")
target_languages = st.multiselect("Select target languages for translation (optional):",
                                    ["French", "Spanish", "German", "Hindi", "Afrikaans"],
                                    default="French")

if st.button("Generate SEO Article"):
    if not transcript:
        st.error("Please enter a video transcript.")
    elif len(transcript) < 100:
        st.warning("The transcript is quite short. The generated article may not be comprehensive.")
    initial_article, raw_output = generate_seo_article(transcript, target_languages, existing_h1, existing_header)
    st.session_state['initial_article'] = initial_article
    st.session_state['raw_output'] = raw_output
    st.session_state['transcript'] = transcript
    st.session_state['target_languages'] = target_languages
    st.session_state['existing_h1'] = existing_h1
    st.session_state['existing_header'] = existing_header

    st.markdown('<div class="subheader">Initial SEO Article</div>', unsafe_allow_html=True)
    st.expander("View Raw HTML").code(initial_article)
    components.html(f'<div class="html-content" style="background-color: #FFFFFF;>{initial_article}</div>', height=500, scrolling=True)
    st.markdown(download_html(initial_article, "initial_article.html"), unsafe_allow_html=True)

    fact_check_results = fact_check_article(initial_article, transcript)
    st.markdown('<div class="subheader">Fact-Check Results</div>', unsafe_allow_html=True)
    st.write(fact_check_results)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

if 'initial_article' in st.session_state:
    st.markdown('<div class="subheader">Feedback and Revision</div>', unsafe_allow_html=True)
    user_feedback = st.text_area("Enter your feedback (optional):", height=200)

    if st.button("Submit Feedback"):
        if user_feedback:
            revised_article = generate_revised_article(
                st.session_state['initial_article'],
                user_feedback,
                st.session_state['raw_output'],
                st.session_state['target_languages'],
                st.session_state['existing_h1'],
                st.session_state['existing_header']
            )
            st.session_state['revised_article'] = revised_article

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="subheader">Initial SEO Article</div>', unsafe_allow_html=True)
                components.html(f'<div class="html-content" style="background-color: #FFFFFF;>{st.session_state["initial_article"]}</div>', height=500, scrolling=True)
            with col2:
                st.markdown('<div class="subheader">Revised SEO Article</div>', unsafe_allow_html=True)
                st.expander("View Raw HTML").code(revised_article)
                components.html(f'<div class="html-content" style="background-color: #FFFFFF;>{revised_article}</div>', height=500, scrolling=True)
                st.markdown(download_html(revised_article, "revised_article.html"), unsafe_allow_html=True)

                fact_check_results = fact_check_article(revised_article, st.session_state['transcript'])
                st.markdown('<div class="subheader">Fact-Check Results</div>', unsafe_allow_html=True)
                st.write(fact_check_results)
        else:
            st.warning("Please provide feedback to generate a revised article.")

    generate_faq_checkbox = st.checkbox("Generate FAQ Section")
    if generate_faq_checkbox:
        with st.spinner("Generating FAQ section..."):
            if 'revised_article' in st.session_state:
                faq_content = asyncio.run(generate_faq(st.session_state['revised_article']))
            else:
                faq_content = asyncio.run(generate_faq(st.session_state['initial_article']))
        st.markdown('<div class="subheader">FAQ Section</div>', unsafe_allow_html=True)
        st.write(faq_content)
