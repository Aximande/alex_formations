import os
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
from io import BytesIO
import requests
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper

# Set and load environment variables for Langchain and OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

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

# Initial prompt
initial_prompt = "An ultra-hyperrealistic photo of a thrilling car chase in a cinematic setting. The scene captures a silver 1967 Ford Mustang Shelby GT500 and a deep green 1969 Pontiac Firebird racing side by side on a misty mountain road. The dense fog adds a mysterious, almost surreal quality, while the wet road reflects the cars' sleek designs and the surrounding dense, dark green pine trees. The intensity and determination on the drivers' faces are visible through their windshields, adding to the drama and realism of the scene."

with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("Initial Prompt:")
        st.write(initial_prompt)
        size_options = ['1024x1024', '1024x1792', '1792x1024']
        selected_size = st.radio("Select image size", size_options)
        submit_button = st.button("Generate Image")

        if submit_button:
            with st.spinner("Generating image..."):
                generated_image = generate_dalle_image(initial_prompt, selected_size)
                st.image(generated_image, caption="Generated Image", use_column_width=True)

                # Feedback and modification section
                st.subheader("Provide a New Prompt")
                new_prompt = st.text_area("Enter a new prompt with your desired modifications:", height=150, placeholder="Enter your modified prompt here...")
                new_submit_button = st.button("Generate New Image")

                if new_submit_button and new_prompt:
                    with st.spinner("Generating new image..."):
                        new_image = generate_dalle_image(new_prompt, selected_size)
                        st.image(new_image, caption="New Image", use_column_width=True)
