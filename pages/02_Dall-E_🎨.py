import streamlit as st
import os 
from PIL import Image
from utils.images_generator import generate_image_openai

from uuid import uuid4

# Callbacks for observability
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


# Setup for Langchain observability
unique_id = uuid4().hex[0:8]  # Generating a unique ID for this session
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Project - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__5d5b2266e1ac446a85974cd1db8349c5"  # Replace with your actual API key - to change for mor esecurity


# Configurer le style de la page avec les paramètres du thème si ce n'est pas déjà fait
st.set_page_config(
    page_title="Créateur d'Images DALL-E",
    page_icon=":art:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://media.beehiiv.com/cdn-cgi/image/fit=scale-down,format=auto,onerror=redirect,quality=80/uploads/asset/file/63e21bf5-75c0-4444-83b0-66e0d98b47d0/628B5B43-B2F2-4948-B419-49B3813B6528.png',
        'About': "# C'est une application pour générer des images avec DALL-E!"
    }
)

# Utilisation des colonnes pour un meilleur layout
left_col, center_col, right_col = st.columns([1, 2, 1])
with center_col:
    st.image(Image.open("static/campus-logo-white.png"), width=200)
    st.markdown("# Dall-e 🎨")

# Zone de texte plus grande pour la description de l'image
input_text = st.text_area("Décrivez l'image que vous souhaitez générer", height=150, placeholder="Entrez une description détaillée de l'image ici...")
submit_button = st.button("Générer")

# Validation de l'entrée utilisateur
if submit_button:
    if input_text:
        with st.spinner("Création de l'image..."):
            generated_image = generate_image_openai(input_text)
            st.image(generated_image, width=703)
    else:
        st.error("Veuillez entrer une description pour générer l'image.")
