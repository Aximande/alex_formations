import streamlit as st
from PIL import Image
from utils.images_generator import generate_image_openai


left_co, cent_co, last_co = st.columns(3)
with cent_co:
    st.image(
        Image.open("static/pathe-logo-clean-PhotoRoom.png"),
        width=200,
    )

st.markdown("# Dall-e 🎨")


# we create a conversation with the user to create images using function generate_image_openai
input_text = st.text_input("Decrivez l'image que vous souhaitez générer")
if input_text:
    with st.spinner("Creation de l'image..."):
        st.image(generate_image_openai(input_text), width=703)
