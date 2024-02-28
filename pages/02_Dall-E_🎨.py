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

# Style personnalisé pour la zone de texte
st.markdown(
    """
    <style>
    .stTextArea>div>div>textarea {
        background-color: #fff3cd;  /* Couleur de fond jaune pâle */
        color: #212529;             /* Couleur de texte presque noire pour un bon contraste */
        border-radius: 10px;        /* Bords arrondis pour la zone de texte */
        padding: 10px;              /* Espacement intérieur pour le texte */
        font-size: 16px;            /* Taille de police pour une lecture facile */
        border: 1px solid #ced4da;  /* Bordure subtile pour la zone de texte */
    }
    .stButton>button {
        color: #ffffff;
        background-color: #f4bc47;  /* Couleur de fond du bouton pour correspondre à votre branding */
        border-radius: 5px;         /* Bords arrondis pour le bouton */
        border: none;
        padding: 10px 24px;         /* Espacement intérieur pour le bouton */
        font-size: 18px;            /* Taille de police plus grande pour le bouton */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Utilisation des colonnes pour un meilleur layout
left_col, center_col, right_col = st.columns([1, 2, 1])
with center_col:
    st.image(Image.open("static/bpilogo1.png"), width=200)
    st.markdown("# Dall-e 🎨", unsafe_allow_html=True)

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
