import streamlit as st
from PIL import Image

st.set_page_config(page_title="Accueil")

left_co, cent_co, last_co = st.columns(3)
with cent_co:
    st.image(
        Image.open("static/brutAI_logo_noir_background.png"),
        width=200,
    )

st.title("Welcome Lunch & Learn BrutAI 🤖")
st.write("Bienvenu(e)s sur notre application de démo pour ces lunch and learn dédiés à l'IA générative !")
st.write("Cette application est divisée en différentes pages, chacune illustrant un cas d'application particulier de l'IA générative grâce à des chatGPT (GPT-4) personnalisées pour les besoins de notre session :")
st.write("1. Accueil")
st.write("2. Chattez avec Brutus, l'assistant GPT-4 pouvant interagir avec un PDF 🤖")
st.write("3. Créez des images avec Dall-E 3 🎨")
st.write("4. Chattez acvec n'importe quel site web facilement ")
st.write("5. Découvrez des petits assistants, utiles pour certaines tâches très précises ")
st.write("Vous pouvez accéder à ces pages via le menu de gauche.")
st.write("Pour commencer, vous pouvez vous rendre sur la page 1. Chatbot avec Brutus.")

st.write("Ce site a pour vocation à s'enrichir et grandir avec le temps.")

st.write("A vos prompts ! !")
