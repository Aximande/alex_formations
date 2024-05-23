import streamlit as st
import anthropic
from dotenv import load_dotenv
import os
import asyncio
import base64
import streamlit.components.v1 as components
from gpt_researcher import GPTResearcher


# Load environment variables
load_dotenv()

# Initialize the API client
api_key = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

def download_html(html_content, file_name):
    """Convert HTML content to a base64-encoded data URI and generate a download link."""
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{file_name}">Download {file_name}</a>'
    return href

def generate_seo_article(transcript, target_languages, existing_h1, existing_header, tone):
    """Generates an initial SEO-optimized article from a transcript."""
    system_processing = f"""
Preprocess the transcript:

Extract the transcript text from the <transcript> tags.
identify speaker name or labels when possible to understand who is talking
Fix any obvious typos or transcription errors.
Split the text into individual sentences/utterances.
Output: cleaned_transcript with diarization (a list of strings, each representing a sentence/utterance).

Analyze the preprocessed transcript:

Identify the main topic based on tf-idf scores of n-grams.
Extract named entities (people, places, organizations) to identify subtopics.
Identify question-answer pairs based on typical question words/phrases.
Extract key phrases using an unsupervised keyphrase extraction model.
Output: main_topic (string), subtopics (list of strings), qa_pairs (list of tuples), key_phrases (list of strings).

Generate alternative suggestions for meta title, meta description, H1, and header:

Based on the main topic, subtopics, and key phrases, generate 2-3 alternative suggestions for each element:

Meta title (max 60 characters)
Meta description (max 156 characters)
H1 (max 60 characters)
Header (max 300 characters)

Ensure the suggested elements are engaging, concise, and capture the main theme of the transcript.
Include the main keywords of the article in each element.
Output: alt_meta_title_suggestions (list of strings), alt_meta_description_suggestions (list of strings), alt_h1_suggestions (list of strings), alt_header_suggestions (list of strings).

Existing H1: {existing_h1}
Existing Header: {existing_header}
Tone: {tone}
"""

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0,
        system=system_processing,
        messages=[{"role": "user", "content": f"<transcript>{transcript}</transcript>Target languages: {', '.join(target_languages)}"}]
    )

    raw_output = message.content[0].text
    st.subheader("Preliminary analysis of your current transcript")
    st.write(raw_output)

    system_generation = f"""
You are an AI assistant skilled at converting video transcripts into SEO-optimized articles. It is absolutely essential that you create an article that is based on the transcript provided and preserve quotes from the transcript without modification. This is the most important aspect of the task.
Follow this process:

Generate the article content:

Use the provided H1 and header as context:
<h1>{existing_h1}</h1>
<header>{existing_header}</header>

Determine the article structure based on the pre-processed transcript content.
Generate H2 subheadings:

For each key quote or key phrase in the transcript, create an H2 subheading.
If a quote, use the quote text between quotation marks as the H2.
If not a quote, use a phrase with essential keywords related to the H1.

Generate body paragraphs for each H2 subheading:

Create two paragraphs, each consisting of 7-8 sentences.
Preserve as much of the original transcript as possible without modifying the meaning.
When quotes are present in the transcript, use them as direct quotes in the body text, enclosed in quotation marks.
Introduce each quote with the speaker's full name and title (when available) and a varied verb (e.g., "explains", "says", "mentions", "indique", "ajoute", "précise", "affirme", "déclare").
Provide context or commentary around the quotes to create a coherent narrative.

Maintain a neutral, journalistic, and informative tone throughout the article.
Preserve quotes from the transcript without modification, and include as many relevant quotes as possible to capture the nuances and complexity of the topic.
Use a {tone} tone throughout the article.

Generate FAQ section:

Based on the article content, generate 1-2 relevant FAQ questions and answers.
Format each FAQ as a subheading (e.g., <h3>Question?</h3>) followed by the answer paragraph.

Output the final article:

Generate the complete article in HTML format.
Include the generated meta title and meta description in the HTML <head> section.
Include the provided H1 in the <body> section, right before the article content.
Add the provided header paragraph after the H1 tag.
Structure the body content with the generated H2 subheadings.
Include the meta description, keywords, and other meta tags in the HTML <head>.
Append the generated FAQ section at the end of the article content.
Use schema markup where relevant (e.g., InterviewObject for interview quotes, FAQPage for FAQ section).
Output: seo_optimized_article_with_faq (HTML string).

Remember, preserving quotes from the transcript and creating an article based on the given transcript is of utmost importance. Success in following these instructions will result in a golden VIP ticket for Taylor Swift's concert!
Existing H1 for this article = "{existing_h1}"
Existing Header for this article = "{existing_header}"
Initial pre-processed transcript = "{raw_output}"
Output: seo_optimized_article_with_faq (HTML string) in the target languages: {', '.join(target_languages)}:
"""
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0,
        system=system_generation,
        messages=[{"role": "user", "content": system_generation}]
    )
    html_content_with_faq = message.content[0].text
    return html_content_with_faq, raw_output

def generate_revised_article(html_content, user_feedback, initial_request, target_languages, existing_h1, existing_header):
    """Generates a revised version of the article based on user feedback."""
    system_revision = f"""
You are an AI assistant skilled at revising video transcripts into SEO-optimized articles based on user feedback. It is crucial that you preserve the original transcript content and quotes as much as possible, as these SEO articles are generated from real video transcripts.
Follow these guidelines:

Preserve the overall structure and formatting of the HTML content.
Update the meta title, meta description, keywords, and other metadata based on the feedback.
Modify the article content, including the lead paragraph, body paragraphs, and interview quotes, to address the user's feedback while maintaining the integrity of the original transcript.
Ensure that quotes from the original transcript are preserved without modification and used appropriately in the revised article.
Ensure the revised article is coherent, well-structured, and optimized for SEO.
Use schema markup where relevant (e.g., InterviewObject for interview quotes, FAQPage for FAQ section).

Remember, preserving the original transcript content and quotes is of utmost importance when revising the SEO article. Your success in following these instructions will be greatly appreciated and rewarded!
Initial request: {initial_request}
Existing H1 for this article: {existing_h1}
Existing Header for this article: {existing_header}
Current article HTML: {html_content}
User feedback: {user_feedback}
Output: revised_seo_optimized_article_with_faq (HTML string) in the target languages: {', '.join(target_languages)}:
"""

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0,
        system=system_revision,
        messages=[{"role": "user", "content": system_revision}]
    )
    revised_html_content_with_faq = message.content[0].text
    return revised_html_content_with_faq

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
        </hallucinations>

        <fact_check_questions>
        1. [Question challenging assumption behind hallucination 1]
        2. [Question challenging assumption behind hallucination 1 - alternate phrasing]
        3. [Question challenging assumption behind hallucination 2]
        4. [Question challenging assumption behind hallucination 2 - alternate phrasing]
        </fact_check_questions>

        <recommendation>
        Based on the hallucinations identified, the SEO article should be revised to remove or modify any claims not directly supported by the video transcript. The fact check questions above should be used to verify details before including them in the final article.
        </recommendation>
        </result>

        Remember, the video transcript is the only source you should use for fact-checking. Do not make assumptions or rely on any external knowledge. If you're unsure whether something in the article is supported by the transcript, err on the side of caution and flag it for further checking.

        Provide your full analysis and fact check questions in a single response. No need to double-check your work or engage in any additional dialogue. Just follow the instructions to the best of your abilities based on the information provided.
        """

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0,
        system="You are a fact-checking assistant.",
        messages=[{"role": "user", "content": fact_check_prompt}]
    )

    fact_check_results = message.content[0].text
    return fact_check_results

def generate_faq_from_article(article_content, target_languages):
    """Generates 2-3 FAQ questions and answers based on the article content in the target languages."""
    system_faq_generation = f"""
You are an AI assistant skilled at generating 2-3 concise FAQ questions and answers based on an article in the following target languages: {', '.join(target_languages)}. [...]

Article content:
{article_content}

Output the generated FAQ questions and answers in the following format:

Q: Question 1
A: Answer 1

Q: Question 2
A: Answer 2

Q: Question 3 (optional)
A: Answer 3 (optional)
"""

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0,
        system=system_faq_generation,
        messages=[{"role": "user", "content": system_faq_generation}]
    )
    generated_faq = message.content[0].text.strip().split("\n\n")
    faq_pairs = [faq.split("\n") for faq in generated_faq]
    return faq_pairs

def incorporate_faq(article_html, faq_pairs):
    """Incorporates the FAQ section with questions and answers into the SEO article HTML."""
    faq_section = "<h2>Frequently Asked Questions</h2>\n"
    for pair in faq_pairs:
        question = pair[0].replace("Q: ", "").strip()
        answer = pair[1].replace("A: ", "").strip()
        faq_section += f"<h3>{question}</h3>\n<p>{answer}</p>\n"

    # Find the closing </body> tag
    closing_body_tag = article_html.find("</body>")

    # Insert the FAQ section before the closing </body> tag
    revised_html = article_html[:closing_body_tag] + faq_section + article_html[closing_body_tag:]

    return revised_html

def revise_article_with_yourtextguru(article_content, yourtextguru_feedback, target_languages):
    """Generates two additional body paragraphs based on Yourtextguru feedback and appends them to the SEO article."""
    system_additional_paragraphs = f"""
        You are an AI assistant skilled at generating two additional body paragraphs for an SEO article based on Yourtextguru recommendations.
        Follow these guidelines:

        - Carefully review the Yourtextguru recommendations provided.
        - The recommendations include top terms (1 word, 2 words, and 3 words) and named entities.
        - The top terms are ranked by importance, with larger and higher-placed words being more important.
        - The 2 and 3-word associations indicate which words go well together.
        - Named entities are proper nouns detected in web content, such as people, services, organizations, or locations.
        - Generate two new body paragraphs that elegantly incorporate the top terms and named entities.
        - Use the 2 and 3-word associations to create relevant and coherent phrases.
        - Ensure the generated paragraphs are coherent, informative, and align with the overall theme of the article.
        - Maintain a natural flow and style consistent with the existing article content.

        Current SEO article:
        {article_content}

        Yourtextguru recommendations:
        {yourtextguru_feedback}

        Output: two_additional_paragraphs (string with the two paragraphs separated by a newline character):
"""

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        temperature=0,
        system=system_additional_paragraphs,
        messages=[{"role": "user", "content": system_additional_paragraphs}]
    )
    two_additional_paragraphs = message.content[0].text

    # Append the additional paragraphs to the SEO article
    article_with_additional_paragraphs = article_content + "\n".join([f"<p>{paragraph}</p>" for paragraph in two_additional_paragraphs.split("\n")])

    return article_with_additional_paragraphs

async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query, report_type)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def main():
    st.set_page_config(page_title="SEO Article Generator", page_icon=":memo:", layout="wide")

    # Add your logo at the top of the page
    st.image("static/brutAI_logo_noir_background.png", width=300)

    # Add CSS styling for larger section titles
    st.markdown("""
        <style>
        .header {
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .subheader {
            font-size: 24px;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="header">SEO Article Generator from Transcripts</div>', unsafe_allow_html=True)
    transcript = st.text_area("Enter your video transcript:", height=200)
    existing_h1 = st.text_input("Enter your current H1:")
    existing_header = st.text_input("Enter your current header:")
    target_languages = st.multiselect("Select target languages for translation (optional):",
                                      ["French", "Spanish", "German", "Hindi", "Afrikaans"],
                                      default="French")
    tone = st.selectbox("Select the tone of the article", ["Neutral", "Informative", "Persuasive"])

    if st.button("Generate SEO Article"):
        if not transcript:
            st.error("Please enter a video transcript.")
        elif len(transcript) < 100:
            st.warning("The transcript is quite short. The generated article may not be comprehensive.")
        with st.spinner("Generating SEO article..."):
            initial_article_with_faq, raw_output = generate_seo_article(transcript, target_languages, existing_h1, existing_header, tone)
            st.session_state['initial_article_with_faq'] = initial_article_with_faq
            st.session_state['raw_output'] = raw_output
            st.session_state['transcript'] = transcript
            st.session_state['target_languages'] = target_languages
            st.session_state['existing_h1'] = existing_h1
            st.session_state['existing_header'] = existing_header

            # Generate FAQ questions based on the initial article content
            faq_pairs = generate_faq_from_article(initial_article_with_faq, st.session_state['target_languages'])

            # Incorporate the FAQ section with questions and answers into the initial SEO article
            initial_article_with_faq = incorporate_faq(initial_article_with_faq, faq_pairs)

            st.markdown('<div class="subheader">Initial SEO Article with FAQ</div>', unsafe_allow_html=True)
            st.expander("View Raw HTML").code(initial_article_with_faq)
            components.html(f'<div class="html-content" style="background-color: #FFFFFF;>{initial_article_with_faq}</div>', height=800, scrolling=True)
            st.markdown(download_html(initial_article_with_faq, "initial_article_with_faq.html"), unsafe_allow_html=True)

            # Add a checkbox or button to allow the user to optionally trigger the fact_check_article function
            run_fact_check = st.checkbox("Run fact-checking on the initial SEO article")

            if run_fact_check:
                with st.spinner("Running fact-check..."):
                    fact_check_results = fact_check_article(initial_article_with_faq, transcript)
                    st.markdown('<div class="subheader">Fact-Check Results</div>', unsafe_allow_html=True)
                    st.write(fact_check_results)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Add a checkbox or button to allow the user to optionally run GPT-researcher
    run_gpt_researcher = st.checkbox("Run GPT-researcher")

    if run_gpt_researcher:
        faq_query = f"Generate a FAQ based on the following topic: {existing_h1}"
        research_query = st.text_input("Enter your research query:", value=faq_query)
        if st.button("Run GPT-researcher"):
            if not research_query:
                st.warning("Please enter a research query.")
            else:
                with st.spinner("Running GPT-researcher..."):
                    research_report = asyncio.run(get_report(research_query, "research_report"))
                    st.markdown('<div class="subheader">GPT-researcher Report</div>', unsafe_allow_html=True)
                    st.write(research_report)

    if 'initial_article_with_faq' in st.session_state:
        st.markdown('<div class="subheader">Feedback and Revision</div>', unsafe_allow_html=True)
        user_feedback = st.text_area("Enter your feedback (optional):", height=200)

        if st.button("Submit Feedback"):
            if user_feedback:
                with st.spinner("Generating revised article..."):
                    revised_article_with_faq = generate_revised_article(
                        st.session_state['initial_article_with_faq'],
                        user_feedback,
                        st.session_state['raw_output'],
                        st.session_state['target_languages'],
                        st.session_state['existing_h1'],
                        st.session_state['existing_header']
                    )
                    st.session_state['revised_article_with_faq'] = revised_article_with_faq

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="subheader">Initial SEO Article with FAQ</div>', unsafe_allow_html=True)
                        components.html(f'<div class="html-content" style="background-color: #FFFFFF;>{st.session_state["initial_article_with_faq"]}</div>', height=800, scrolling=True)
                    with col2:
                        st.markdown('<div class="subheader">Revised SEO Article with FAQ</div>', unsafe_allow_html=True)
                        st.expander("View Raw HTML").code(revised_article_with_faq)
                        components.html(f'<div class="html-content" style="background-color: #FFFFFF;>{revised_article_with_faq}</div>', height=800, scrolling=True)
                        st.markdown(download_html(revised_article_with_faq, "revised_article_with_faq.html"), unsafe_allow_html=True)
            else:
                st.warning("Please provide feedback to generate a revised article.")

    yourtextguru_feedback = st.text_area("Enter feedback from Yourtextguru:", height=200)
    if yourtextguru_feedback:
        if 'initial_article_with_faq' in st.session_state:
            article_content = st.session_state['initial_article_with_faq']
        elif 'revised_article_with_faq' in st.session_state:
            article_content = st.session_state['revised_article_with_faq']
        else:
            st.warning("Please generate an article first before providing Yourtextguru feedback.")
            article_content = None

        if article_content:
            with st.spinner("Generating additional paragraphs..."):
                article_with_additional_paragraphs = revise_article_with_yourtextguru(article_content, yourtextguru_feedback, st.session_state['target_languages'])
                st.session_state['article_with_additional_paragraphs'] = article_with_additional_paragraphs

                revised_article_with_yourtextguru_and_faq = incorporate_faq(article_with_additional_paragraphs, faq_questions)
                st.session_state['revised_article_with_yourtextguru_and_faq'] = revised_article_with_yourtextguru_and_faq

                st.markdown('<div class="subheader">Revised SEO Article with Additional Paragraphs and FAQ</div>', unsafe_allow_html=True)
                st.expander("View Raw HTML").code(revised_article_with_yourtextguru_and_faq)
                components.html(f'<div class="html-content" style="background-color: #FFFFFF;>{revised_article_with_yourtextguru_and_faq}</div>', height=800, scrolling=True)
                st.markdown(download_html(revised_article_with_yourtextguru_and_faq, "revised_article_with_yourtextguru_and_faq.html"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
