import streamlit as st
import anthropic
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from the .env file

st.image(
    Image.open("static/brutAI_logo_noir_background.png"),
    width=300,
)

st.title("SEO Article Generator from Transcripts")

transcript = st.text_area("Enter your video transcript:", height=200)
target_languages = st.multiselect("Select target languages for translation (optional):", ["French", "Spanish", "German"])
feedback = st.text_input("Provide feedback on the generated article (optional):")

button = st.button("Generate SEO Article")

if button:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        client = anthropic.Anthropic(api_key=api_key)
        # Rest of your code
    else:
        st.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0,
        system="""You are an AI assistant skilled at converting video transcripts into SEO-optimized articles.
        you follow carefully those instructions step by step - and provide the direct results, don't explain your logic or reasoning, eliminate adjectives or adverbsunecessary
        here are the step:

Preprocess the transcript:

Extract the transcript text from the <transcript> tags
Remove speaker names/labels (e.g. Valentin:, BRUT:)
Remove non-verbal cues in parentheses (e.g. (rires))
Fix any obvious typos or transcription errors
Split the text into individual sentences/utterances
Output: cleaned_transcript (a list of strings, each representing a sentence/utterance)


Analyze the preprocessed transcript:

Input: cleaned_transcript
Identify the main topic based on tf-idf scores of n-grams
Extract named entities (people, places, organizations) to identify subtopics
Identify question-answer pairs based on typical question words/phrases
Extract key phrases using an unsupervised keyphrase extraction model
Output: main_topic (string), subtopics (list of strings), qa_pairs (list of tuples), key_phrases (list of strings)


Generate the article content:

Inputs: cleaned_transcript, main_topic, subtopics, qa_pairs, key_phrases, examples
Determine article structure based on the examples (e.g. lead paragraph, key points, interview quotes)
Generate a lead paragraph introducing the main topic
Generate body paragraphs for each subtopic, using relevant sentences from the transcript
Convert question-answer pairs into interview quote paragraphs
Ensure coherence and fluency using a large language model
Output: article_content (string)


Optimize for SEO:

Input: article_content, main_topic, subtopics, key_phrases
Generate an engaging, keyword-rich title under 60 characters
Generate a meta description under 156 characters summarizing the article
Identify 5-10 target keywords/keyphrases based on the key_phrases
Suggest relevant meta tags (e.g. article:author, article:published_time, og:image)
Ensure keywords are used in the title, meta description, article headers and body text
Output: seo_title (string), meta_description (string), keywords (list), meta_tags (list)


Generate H1 and Chapô:

Input: article_content, main_topic, seo_title
Generate an H1 tag that is slightly different from the SEO title and under 60 characters
Generate a chapô (introductory paragraph) under 300 characters
Output: h1 (string), chapo (string)


Output the final article:

Generate the complete article in HTML format
Include the SEO-optimized title, meta description, keywords and other meta tags in the HTML <head>
Include the H1 tag in the <body> section, right before the article content
Add the chapô paragraph after the H1 tag
Structure the body content with relevant header tags (H1, H2, etc), ensuring H2 subheadings are within 80 characters
Use schema markup where relevant (e.g. InterviewObject for interview quotes)
Output: seo_optimized_article (HTML string)


        """,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Here is the transcript:\n\n<transcript>\n{transcript}\n</transcript>\n\nTarget languages: {', '.join(target_languages) if target_languages else 'None'}\n\nFeedback: {feedback}"
                    }
                ]
            }
        ]
    )

    st.header("Generated SEO Article")
    st.write(message.content)
