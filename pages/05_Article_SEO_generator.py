import streamlit as st
import anthropic
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
from PIL import Image

load_dotenv()  # Load environment variables from the .env file

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
            max_tokens=2500,
            temperature=0,
            system=f"""
            ... (system prompt omitted for brevity) ...
            """,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    <transcript>
                    {transcript}
                    </transcript>

                    Target languages: {', '.join(target_languages) if target_languages else 'None'}

                    Feedback: {feedback}
                    """
                }
            ]
        )

        # Extract the HTML content from the API response
        html_content = message.content[0].text

        # Display the HTML content in an iframe using st.components.v1.iframe
        st.header("Generated SEO Article")
        components.iframe(html_content, height=600, scrolling=True)
