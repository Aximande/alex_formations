import sqlite_override
import os
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
from uuid import uuid4
import requests
from io import BytesIO
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper

# Set and load environment variables for Langchain and OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Setup for Langchain observability
unique_id = uuid4().hex[0:8]  # Generating a unique ID for this session
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Project - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__5d5b2266e1ac446a85974cd1db8349c5"  # Replace with your actual API key - to change for more security

# Function to generate an image using Dall-E based on a given description and size
def generate_dalle_image(description, size):
    llm = ChatOpenAI(temperature=0.9)
    prompt = PromptTemplate(
        input_variables=["image_desc"],
        template="Generate a detailed prompt to generate an image based on the following description: {image_desc}",
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    image_url = DallEAPIWrapper(model='dall-e-3', size=size).run(chain.run(description))
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img

# Streamlit UI layout setup
st.set_page_config(page_title="DALL-E Image Generator", page_icon=":art:", layout='wide')
st.title("DALL-E Image Generator 🎨")

# Display the logo at the top of the page
st.image(Image.open("static/brutAI_logo_noir_background.png"), width=200)

with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        input_text = st.text_area("Describe the image you want to generate", height=150, placeholder="Enter a detailed image description here...")
        size_options = ['1024x1024', '1024x1792', '1792x1024']
        selected_size = st.radio("Select image size", size_options)
        submit_button = st.button("Generate Image")

        if submit_button and input_text:
            with st.spinner("Generating image..."):
                generated_image = generate_dalle_image(input_text, selected_size)
                st.image(generated_image, caption="Generated Image", use_column_width=True)

                # Feedback and modification section
                st.subheader("Feedback and Modification")
                feedback = st.text_area("Provide feedback or modifications for the image", height=100, placeholder="Enter your feedback or desired modifications here...")
                modify_button = st.button("Modify Image")

                if modify_button and feedback:
                    with st.spinner("Modifying image..."):
                        modified_description = f"{input_text}. {feedback}"
                        modified_image = generate_dalle_image(modified_description, selected_size)
                        st.image(modified_image, caption="Modified Image", use_column_width=True)
