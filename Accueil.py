import streamlit as st
from PIL import Image

st.set_page_config(page_title="Accueil")

left_co, cent_co, last_co = st.columns(3)
with cent_co:
    st.image(
        Image.open("static/pathe-logo-clean-PhotoRoom.png"),
        width=200,
    )

st.title("Accueil")
st.write("Ad's up campus: Bienvenue sur notre application de démonstration !")
st.write("Cette application est divisée en 3 pages :")
st.write("1. Accueil")
st.write("2. Chatbot 🤖")
st.write("3. Dall-E 🎨")
st.write("Vous pouvez accéder à ces pages via le menu de gauche.")
st.write("Pour commencer, vous pouvez vous rendre sur la page Chatbot.")
st.write("Bonne visite !")
