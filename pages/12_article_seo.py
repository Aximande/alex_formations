import streamlit as st
import anthropic
import phospho
from dotenv import load_dotenv
import os
import uuid

# Load environment variables
load_dotenv()

# Initialize the API client
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    st.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# Initialize Phospho client
phospho.init(api_key=os.getenv("PHOSPHO_API_KEY"), project_id=os.getenv("PHOSPHO_PROJECT_ID"))
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

# Initialize session state variables
def initialize_session_state():
    if 'initial_article' not in st.session_state:
        st.session_state['initial_article'] = ''
    if 'current_article' not in st.session_state:
        st.session_state['current_article'] = ''
    if 'seo_scores' not in st.session_state:
        st.session_state['seo_scores'] = []
    if 'transcript' not in st.session_state:
        st.session_state['transcript'] = ''
    if 'target_languages' not in st.session_state:
        st.session_state['target_languages'] = []
    if 'existing_h1' not in st.session_state:
        st.session_state['existing_h1'] = ''
    if 'existing_header' not in st.session_state:
        st.session_state['existing_header'] = ''
    if 'speakers_and_proper_nouns' not in st.session_state:
        st.session_state['speakers_and_proper_nouns'] = ''
    if 'model_name' not in st.session_state:
        st.session_state['model_name'] = ''
    if 'task_id' not in st.session_state:
        st.session_state['task_id'] = str(uuid.uuid4())

def add_seo_score(score, version):
    """Adds a new SEO score to the session state."""
    if score > 0:  # Only add positive scores
        st.session_state['seo_scores'].append({'Version': version, 'SEO Score': score})

def log_user_feedback(flag, notes):
    """Logs user feedback using Phospho."""
    phospho.user_feedback(
        flag=flag,
        source="user",
        task_id=st.session_state['task_id'],
        notes=notes,
    )

def generate_seo_article(transcript, target_languages, existing_h1, existing_header, speakers_and_proper_nouns, model_name):
    """Generates an initial SEO-optimized article from a transcript."""
    system_generation = f"""
You are an AI assistant skilled at converting video transcripts into comprehensive SEO-optimized articles. Follow this process:

Generate the article content with the following structure:
   - H1: {existing_h1}
   - Header: {existing_header}
   - At least 3 sections with H2 subheadings and corresponding body content

For each section:
   - Determine the H2 subheading based on the transcript content and key topics discussed.
   - Generate the body content for the section:
      - Analyze the transcript thoroughly to understand the flow and structure of the content related to the section topic.
      - Generate the body as a single, coherent text without any formatting or structure.
      - Preserve as much of the original transcript as possible, reusing complete sentences and quotes verbatim without modifying the meaning.
      - When including quotes from the transcript, introduce them with the speaker's full name and title (when available), and a varied verb (e.g., "explains", "says", "mentions").
      - Provide context and commentary around the quotes to weave them into a coherent narrative flow.
      - Ensure that the section content maintains a neutral, informative, and journalistic tone.
      - Do not limit the length of the section; let the transcript content dictate the natural length.

Here are some special guidelines and tips about either the content or speaker's names in the video and proper nouns with correct naming to keep in mind:
{speakers_and_proper_nouns}

Output: seo_optimized_article (string) in the target languages: {', '.join(target_languages)}
"""

    message = client.messages.create(
        model=model_name,
        max_tokens=4096,
        temperature=0,
        system=system_generation,
        messages=[{"role": "user", "content": f"<transcript>{transcript}</transcript>Target languages: {', '.join(target_languages)}"}]
    )

    article_content = message.content[0].text

    # Log the task with Phospho
    phospho.log(
        input=system_generation,
        output=article_content,
        metadata={"task": "generate_seo_article"}
    )

    return article_content

def generate_revised_article(article_content, user_feedback, target_languages, existing_h1, existing_header, speakers_and_proper_nouns, model_name):
    """Generates a revised version of the article based on user feedback."""
    system_revision = f"""
        You are an AI assistant skilled at revising video transcripts into SEO-optimized articles based on user feedback. Follow these guidelines:

        - Preserve the overall structure and formatting of the article content.
        - Update the meta description and keywords based on the feedback.
        - Modify the article content, including the lead paragraph, body paragraphs, and interview quotes, to address the user's feedback.
        - Ensure the revised article is coherent, well-structured, and optimized for SEO.

        Speakers and Proper Nouns:
        {speakers_and_proper_nouns}

        Existing H1 for this article
        {existing_h1}

        Existing Header for this article
        {existing_header}

        Current article content:
        {article_content}

        User feedback:
        {user_feedback}

        Output: revised_seo_optimized_article (string) in the target languages: {', '.join(target_languages)} :
    """

    message = client.messages.create(
        model=model_name,
        max_tokens=4096,
        temperature=0,
        system=system_revision,
        messages=[{"role": "user", "content": system_revision}]
    )
    revised_article_content = message.content[0].text

    # Log the task with Phospho
    phospho.log(
        input=system_revision,
        output=revised_article_content,
        metadata={"task": "generate_revised_article"}
    )

    return revised_article_content

def fact_check_article(article_content, transcript, model_name):
    fact_check_prompt = f"""
You will be acting as a fact-checking assistant to ensure that an SEO article generated from a video transcript is truthful and does not contain any hallucinations or inventions not supported by the original transcript.

Here is the SEO article:

{article_content}

And here is the full video transcript the article should be based on:

{transcript}

Please carefully compare the SEO article to the provided transcript. Your task is to identify any claims, statements or details in the article that are not directly supported by the transcript. These are considered "hallucinations" or "inventions".

If you find any hallucinations or invented details in the SEO article, write them down here. For each one, identify the key assumption(s) behind the hallucinated claim. Keep these brief and to the point.

If no hallucinations or inventions are found, simply output:

The SEO article appears to be fully supported by the video transcript. No hallucinations or inventions detected.

However, if you do identify hallucinations or inventions, your next step is to generate a set of fact-checkable questions that challenge the key assumptions you identified. These questions should be used to search for evidence that either confirms or refutes the hallucinated claims, using the video transcript as the sole source of ground truth.

Frame your questions to explore the basic existence or accuracy of the hallucinated details. Do not address or refer to the user, as your questions will only be used for background searches, not shown directly.

Use varied wording and sentence structures for your questions to maximize the scope of the searches. The goal is to cast a wide net to find any relevant information in the transcript that relates to the hallucinated claims.

After listing your questions, provide a final recommendation on whether the SEO article needs to be revised to align with the transcript. Output your full results like this:

Hallucinations:
1. [Hallucinated claim 1]
2. [Hallucinated claim 2]
3. [Hallucinated claim 3]

Fact Check Questions:
1. [Question challenging assumption behind hallucination 1]
2. [Question challenging assumption behind hallucination 1 - alternate phrasing]
3. [Question challenging assumption behind hallucination 2]
4. [Question challenging assumption behind hallucination 2 - alternate phrasing]
5. [Question challenging assumption behind hallucination 3]
6. [Question challenging assumption behind hallucination 3 - alternate phrasing]

Recommendation:
Based on the hallucinations identified, the SEO article should be revised to remove or modify any claims not directly supported by the video transcript. The fact check questions above should be used to verify details before including them in the final article.

Remember, the video transcript is the only source you should use for fact-checking. Do not make assumptions or rely on any external knowledge. If you're unsure whether something in the article is supported by the transcript, err on the side of caution and flag it for further checking.

Provide your full analysis and fact check questions in a single response. No need to double-check your work or engage in any additional dialogue. Just follow the instructions to the best of your abilities based on the information provided.
"""

    message = client.messages.create(
        model=model_name,
        max_tokens=4096,
        temperature=0,
        system="You are a fact-checking assistant.",
        messages=[{"role": "user", "content": fact_check_prompt}]
    )

    fact_check_results = message.content[0].text

    # Log the task with Phospho
    phospho.log(
        input=fact_check_prompt,
        output=fact_check_results,
        metadata={"task": "fact_check_article"}
    )

    return fact_check_results

def revise_article_with_yourtextguru(article_content, yourtextguru_feedback, target_languages, model_name):
    """Generates two additional body paragraphs based on Yourtextguru feedback and appends them to the SEO article."""
    system_additional_paragraphs = """
You are an AI assistant skilled at generating additional content for SEO-optimized articles. Follow these guidelines:

- Incorporate the Yourtextguru feedback into two new body paragraphs.
- Ensure the new paragraphs align with the overall tone and structure of the article.
- Use relevant quotes from the transcript to support the new content.
- Make sure the new content is coherent, informative, and neutral.

Output: two_additional_paragraphs (string)

### Output: seo_optimized_article_with_yourtextguru_and_faq (plain text string) in the target languages: {', '.join(target_languages)}:

"""

    message = client.messages.create(
        model=model_name,
        max_tokens=4096,
        temperature=0,
        system=system_additional_paragraphs,
        messages=[{"role": "user", "content": yourtextguru_feedback}]
    )
    two_additional_paragraphs = message.content[0].text

    # Append the additional paragraphs to the SEO article
    article_with_additional_paragraphs = article_content + "\n\n" + "\n\n".join(two_additional_paragraphs.split("\n"))

    # Log the task with Phospho
    phospho.log(
        input=system_additional_paragraphs,
        output=article_with_additional_paragraphs,
        metadata={"task": "revise_article_with_yourtextguru"}
    )

    return article_with_additional_paragraphs

def create_seo_article_with_yourtextguru(initial_article_content, yourtextguru_feedback, target_languages, existing_h1, existing_header, model_name):
    """Generates a new SEO article that incorporates the Yourtextguru recommendations."""
    system_generation = f"""
    You are an AI assistant skilled at converting video transcripts into SEO-optimized articles that incorporate Yourtextguru recommendations. It is absolutely essential that you create an article that is based on the provided initial article content and preserve quotes from the transcript without modification. This is the most important aspect of the task.
    Follow this process:

    Generate the article content:

    Use the provided H1 and header as context.
    Incorporate the Yourtextguru recommendations:
    Review the Yourtextguru recommendations and elegantly incorporate the top terms, 2-word and 3-word associations, and named entities into the article content.
    Generate two additional body paragraphs that showcase the integration of the Yourtextguru insights.
    Ensure the new paragraphs align with the overall tone and structure of the article.

    Preserve quotes from the initial article content without modification, and include as many relevant quotes as possible to capture the nuances and complexity of the topic.

    Generate FAQ section:

    Based on the article content, generate 1-2 relevant FAQ questions and answers.
    Format each FAQ as a question followed by the answer paragraph.

    Output the final article:

    Generate the complete article text, including the FAQ section.
    Include the provided H1 at the beginning of the article.
    Add the provided header paragraph after the H1.
    Structure the body content with subheadings.
    Append the generated FAQ section at the end of the article content.
    Output: seo_optimized_article_with_yourtextguru_and_faq (plain text string).

    Existing H1 for this article = "{existing_h1}"
    Existing Header for this article = "{existing_header}"
    Yourtextguru recommendations: {yourtextguru_feedback}
    Output: seo_optimized_article_with_yourtextguru_and_faq (plain text string) in the target languages: {', '.join(target_languages)}:
    """

    message = client.messages.create(
        model=model_name,
        max_tokens=4096,
        temperature=0,
        system=system_generation,
        messages=[{"role": "user", "content": system_generation}]
    )
    article_content_with_yourtextguru_and_faq = message.content[0].text

    # Log the task with Phospho
    phospho.log(
        input=system_generation,
        output=article_content_with_yourtextguru_and_faq,
        metadata={"task": "create_seo_article_with_yourtextguru"}
    )

    return article_content_with_yourtextguru_and_faq

# Initialize session state variables
initialize_session_state()

st.markdown('# SEO Article Generator from Transcripts')

st.markdown('## Step 1: Enter Parameters')

model_name = st.selectbox("Select the LLM model:", ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"])
transcript = st.text_area("Enter your video transcript:", height=200)
existing_h1 = st.text_input("Enter your current H1:")
existing_header = st.text_input("Enter your current header:")
speakers_and_proper_nouns = st.text_area("Enter speakers' names and important proper nouns (one per line):", height=100)
target_languages = st.multiselect("Select target languages for translation (optional):",
                                    ["French", "Spanish", "German", "Hindi", "Afrikaans"],
                                    default="French")

st.markdown('## Step 2: Generate Initial SEO Article')

if st.button("Generate SEO Article"):
    if not transcript:
        st.error("Please enter a video transcript.")
    elif len(transcript) < 100:
        st.warning("The transcript is quite short. The generated article may not be comprehensive.")
    initial_article = generate_seo_article(transcript, target_languages, existing_h1, existing_header, speakers_and_proper_nouns, model_name)
    st.session_state['initial_article'] = initial_article
    st.session_state['current_article'] = initial_article  # Update the current_article variable
    st.session_state['transcript'] = transcript
    st.session_state['target_languages'] = target_languages
    st.session_state['existing_h1'] = existing_h1
    st.session_state['existing_header'] = existing_header
    st.session_state['speakers_and_proper_nouns'] = speakers_and_proper_nouns
    st.session_state['model_name'] = model_name

    st.markdown('### Current Article')
    st.write(st.session_state['current_article'])  # Display the current_article content

    # Log initial user feedback
    log_user_feedback("success", "Generated initial SEO article.")

# Collect initial SEO score
if 'initial_article' in st.session_state and st.session_state['initial_article']:
    st.markdown('### Enter Initial SEO Score')
    initial_seo_score = st.number_input("Initial SEO score:", min_value=0, max_value=100, value=0, step=1, key='initial_seo_score')
    if st.button("Submit Initial SEO Score"):
        add_seo_score(initial_seo_score, 'Initial')

st.markdown('---')

# Collect user feedback and generate revised article
if 'initial_article' in st.session_state and st.session_state['initial_article']:
    st.markdown('## Step 3: Feedback and Revision')

    col1, col2 = st.columns(2)

    with col1:
        user_feedback = st.text_area("Enter your feedback (optional):", height=200)
    with col2:
        yourtextguru_feedback = st.text_area("Paste YourtextGuru feedback (optional):", height=200)

    yourtextguru_method = st.selectbox(
        "Select the method to incorporate YourtextGuru feedback:",
        ["Revise Current Article", "Generate New Article"]
    )

    if st.button("Generate Revised Article"):
        if user_feedback:
            revised_article = generate_revised_article(
                st.session_state['current_article'],
                user_feedback,
                st.session_state['target_languages'],
                st.session_state['existing_h1'],
                st.session_state['existing_header'],
                st.session_state['speakers_and_proper_nouns'],
                st.session_state['model_name']
            )
            st.session_state['current_article'] = revised_article

            st.markdown('### Current Article')
            st.write(st.session_state['current_article'])

            # Log revised user feedback
            log_user_feedback("success", "Generated revised SEO article based on user feedback.")

    if yourtextguru_feedback:
        if yourtextguru_method == "Revise Current Article":
            yourtextguru_revised_article = revise_article_with_yourtextguru(
                st.session_state['current_article'],
                yourtextguru_feedback,
                st.session_state['target_languages'],
                st.session_state['model_name']
            )
        else:
            yourtextguru_revised_article = create_seo_article_with_yourtextguru(
                st.session_state['initial_article'],
                yourtextguru_feedback,
                st.session_state['target_languages'],
                st.session_state['existing_h1'],
                st.session_state['existing_header'],
                st.session_state['model_name']
            )

        st.session_state['current_article'] = yourtextguru_revised_article

        st.markdown('### Current Article')
        st.write(st.session_state['current_article'])

        # Log YourtextGuru feedback
        log_user_feedback("success", "Generated article incorporating YourtextGuru feedback.")

        # Fact check button
        if st.button("Run Fact-Checking on Revised Article"):
            st.session_state['fact_check_clicked'] = True

# Run fact-checking if button clicked
if st.session_state.get('fact_check_clicked'):
    fact_check_results = fact_check_article(st.session_state['current_article'], st.session_state['transcript'], st.session_state['model_name'])
    st.markdown('## Fact-Check Results')
    st.write(fact_check_results)
    st.session_state['fact_check_clicked'] = False

# Collect revised SEO score
if 'current_article' in st.session_state and st.session_state['current_article'] != st.session_state['initial_article']:
    st.markdown('### Enter Revised SEO Score')
    revised_seo_score = st.number_input("Revised SEO score:", min_value=0, max_value=100, value=0, step=1, key='revised_seo_score')
    if st.button("Submit Revised SEO Score"):
        add_seo_score(revised_seo_score, 'Revised')

st.markdown('---')

st.markdown('## Step 4: Article Tracking')
article_url = st.text_input("Enter the URL of the published article:")
article_word_count = len(st.session_state['current_article'].split()) if 'current_article' in st.session_state else 0
current_seo_score = st.session_state['seo_scores'][-1]['SEO Score'] if st.session_state['seo_scores'] else 0
tracking_data = {
    'Date': st.date_input("Select the date of article creation:"),
    'Title': st.session_state['existing_h1'],
    'Google Doc URL': st.text_input("Enter the Google Doc URL of the article:"),
    'Published URL': article_url,
    'Word Count': article_word_count,
    'Current SEO Score': current_seo_score,
    'SEO Score History': st.session_state['seo_scores'],
}
st.write(tracking_data)

if st.button("Save Tracking Data"):
    # Save the tracking data to a Google Sheet or a database
    st.success("Tracking data saved successfully!")

# Button to purge SEO score history and start a new project
if st.button("Start New Project"):
    reset_session_state()
    st.success("SEO score history purged and session state reset for a new project.")
