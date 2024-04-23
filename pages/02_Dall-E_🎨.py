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

# Predefined cool prompts
cool_prompts = [
    "An ultra-hyperrealistic photo of a thrilling car chase in a cinematic setting. The scene captures a silver 1967 Ford Mustang Shelby GT500 and a deep green 1969 Pontiac Firebird racing side by side on a misty mountain road. The dense fog adds a mysterious, almost surreal quality, while the wet road reflects the cars' sleek designs and the surrounding dense, dark green pine trees. The intensity and determination on the drivers' faces are visible through their windshields, adding to the drama and realism of the scene.",
    "Cinematic Crane Shot, The sun setting over the scenic coastline of Malibu, a luxury convertible cruising along the Pacific Coast Highway, capturing the carefree and glamourous LA lifestyle, as if through the lens of a vintage Panavision camera",
    "A ransom drop-off in dirty LA backstreets, gritty surroundings, neon lights clash with the stark, moonless night, mimicking the suspense of Tarantino's plots. Captured on lustrous Kodak Vision3 Color Negative Film 500T 5219",
    # Add more cool prompts here
]

# Streamlit UI layout setup
st.set_page_config(page_title="DALL-E Image Generator", page_icon=":art:", layout='wide')
st.title("DALL-E Image Generator 🎨")
st.image(Image.open("static/brutAI_logo_noir_background.png"), width=200)

with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Create Your Own Image")
        user_prompt = st.text_area("Describe the image you want to generate", height=150, placeholder="Enter a detailed image description here...")
        size_options = ['1024x1024', '1024x1792', '1792x1024']
        selected_size = st.radio("Select image size", size_options)
        submit_button = st.button("Generate Image")

        if submit_button and user_prompt:
            with st.spinner("Generating image..."):
                generated_image = generate_dalle_image(user_prompt, selected_size)
                st.image(generated_image, caption="Generated Image", use_column_width=True)

                # Feedback section
                st.subheader("Request Feedback or Modifications")
                feedback = st.text_area("Enter your feedback or additional instructions", height=100, placeholder="Enter your feedback here...")
                feedback_button = st.button("Generate with Feedback")

                if feedback_button and feedback:
                    with st.spinner("Generating new image..."):
                        new_prompt = f"{user_prompt}. {feedback}"
                        feedback_image = generate_dalle_image(new_prompt, selected_size)
                        st.image(feedback_image, caption="New Image", use_column_width=True)

                # Request feedback on generated image
                request_feedback_button = st.button("Request Feedback on Generated Image")
                if request_feedback_button:
                    st.write("Please provide your feedback or desired modifications for the generated image.")
                    image_feedback = st.text_area("Enter your feedback or modifications", height=150)
                    feedback_submit_button = st.button("Submit Feedback")

                    if feedback_submit_button and image_feedback:
                        with st.spinner("Generating new image..."):
                            new_image_prompt = f"Based on the provided image: {image_feedback}"
                            new_image = generate_dalle_image(new_image_prompt, selected_size)
                            st.image(new_image, caption="New Image Based on Feedback", use_column_width=True)

        st.markdown("---")
        st.subheader("Or Try These Cool Prompts")
        st.write("Need some inspiration? Check out these cool prompts and try generating images from them.")
        for prompt in cool_prompts:
            with st.expander(prompt[:50] + "..."):
                st.write(prompt)
                try_prompt_button = st.button(f"Try Prompt", key=f"try_prompt_{prompt}")
                if try_prompt_button:
                    with st.spinner("Generating image..."):
                        prompt_image = generate_dalle_image(prompt, selected_size)
                        st.image(prompt_image, caption="Generated Image", use_column_width=True)
