import streamlit as st
from PIL import Image
from utils.images_generator import generate_image_openai

# Configurer le style de la page avec les paramètres du thème si ce n'est pas déjà fait
st.set_page_config(
    page_title="Créateur d'Images DALL-E",
    page_icon=":art:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.pathedalle.com/help',
        'About': "# C'est une application pour générer des images avec DALL-E!"
    }
)

# Utilisation des colonnes pour un meilleur layout
left_col, center_col, right_col = st.columns([1, 2, 1])
with center_col:
    st.image(Image.open("static/bpilogo1.png"), width=200)
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
