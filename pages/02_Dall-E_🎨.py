import streamlit as st
from PIL import Image
from utils.images_generator import generate_image_openai

# Custom CSS to inject into the webpage
st.markdown(
    """
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .image-gen-container {
        text-align: center;
        margin-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        padding: 10px;
        font-size: 16px;
        font-weight: bold;
        color: white;
        background-color: #f4bc47;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header image
st.image("static/pathe-logo-clean-PhotoRoom.png", width=200)

# Title and description
st.markdown("<div class='big-font'>Dall-e 🎨</div>", unsafe_allow_html=True)
st.write("Décrivez l'image que vous souhaitez générer dans la zone de saisie ci-dessous et appuyez sur Entrée.")

# User input with a bit more style
input_container = st.container()
col1, col2 = st.columns([0.8, 0.2])

with input_container:
    with col1:
        input_text = st.text_input("", "Description de l'image", key="input_text")
    with col2:
        # Button to generate image
        if st.button('Générer'):
            if input_text:
                with st.spinner("Création de l'image..."):
                    # Generate and display the image
                    st.markdown("<div class='image-gen-container'>", unsafe_allow_html=True)
                    st.image(generate_image_openai(input_text), width=703)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("Veuillez entrer une description.")
