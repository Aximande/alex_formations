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


# Set and load environment variables for Langchain and OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Setup for Langchain observability
unique_id = uuid4().hex[0:8]  # Generating a unique ID for this session
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Project - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__5d5b2266e1ac446a85974cd1db8349c5"  # Replace with your actual API key - to change for mor esecurity


# Function to generate an image using Dall-E based on a given description
def generate_dalle_image(description):
    llm = ChatOpenAI(temperature=0.9)
    prompt = PromptTemplate(
        input_variables=["image_desc"],
        template="Generate a detailed prompt to generate an image based on the following description: {image_desc}",
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Use 'invoke' if that's the updated method according to deprecation warnings
    image_url = DallEAPIWrapper().run(chain.run(description))

    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img


# Streamlit UI for input and image display
st.set_page_config(page_title="DALL-E Image Generator", page_icon=":art:")
st.title("DALL-E Image Generator 🎨")

input_text = st.text_area("Describe the image you want to generate", height=150, placeholder="Enter a detailed image description here...")
submit_button = st.button("Generate")

if submit_button and input_text:
    with st.spinner("Generating image..."):
        generated_image = generate_dalle_image(input_text)
        st.image(generated_image, caption="Generated Image", use_column_width=True)
