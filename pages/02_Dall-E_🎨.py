import sqlite_override
import os
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
from uuid import uuid4
import requests
from io import BytesIO
from langchain.chat_models import ChatOpenAI

# Callbacks for observability
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper

# Assuming the utility functions are in a module named `utils` in the same directory or in your PYTHONPATH
from utils.image_generator import generate_image_openai, save_img

# Set and load environment variables for Langchain and OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Setup for Langchain observability
unique_id = uuid4().hex[0:8]  # Generating a unique ID for this session
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Project - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__5d5b2266e1ac446a85974cd1db8349c5"  # Replace with your actual API key - to change for mor esecurity

# Setup Streamlit UI
st.set_page_config(page_title="DALL-E 3 Image Generator", page_icon=":art:", layout='wide')
st.title("DALL-E 3 Image Generator 🎨")

with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        input_text = st.text_area("Describe the image you want to generate", height=150, placeholder="Enter a detailed image description here...")
        submit_button = st.button("Generate Image")

        if submit_button and input_text:
            with st.spinner("Generating image..."):
                image_url = generate_image_openai(input_text)
                response = requests.get(image_url)  # Fetch the image from the URL
                image = Image.open(BytesIO(response.content))
                st.image(image, caption="Generated Image", use_column_width=True)

                # Optional: Save the image locally
                save_path = f"generated_images/image_{uuid4()}.png"
                save_img(image_url, save_path)
                st.success(f"Image saved to {save_path}")
