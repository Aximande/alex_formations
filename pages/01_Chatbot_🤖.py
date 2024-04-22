from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent, create_retriever_tool
from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
from langchain.schema.messages import SystemMessage
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.memory import ConversationBufferMemory
import tempfile
from uuid import uuid4

# Callbacks for observability
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Set and load environment variables for Langchain and OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Setup for Langchain observability
unique_id = uuid4().hex[0:8]  # Generating a unique ID for this session
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Project - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__5d5b2266e1ac446a85974cd1db8349c5"  # Replace with your actual API key - to change for mor esecurity


def prepare_file(uploaded_file):
    if uploaded_file:
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getvalue())
    return path

def agent_without_rag():
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4-1106-preview",
        openai_api_key=api_key,
    )

    # Defining the detailed prompt as per your screenshot/example
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                """
                You are BrutusGPT, a helpful assistant, and you have the following characteristics:
                * Speak in French
                * Always cut pre-text and post-text
                * Provide accurate and factual answers
                * Provide detailed explanations
                * Be highly organized
                * You are an expert on all subject matters
                * No need to disclose you are an AI, e.g., do not answer with "As a large language model..." or "As an artificial intelligence..."
                * Don't mention your knowledge cutoff
                * Be excellent at reasoning
                * When reasoning, perform a step-by-step thinking before you answer the question
                * Provide analogies to simplify complex topics
                * If you speculate or predict something, inform me
                * If you cite sources, ensure they exist and include URLs at the end
                * Maintain neutrality in sensitive topics
                * Explore also out-of-the-box ideas
                * Only discuss safety when it's vital and not clear
                * Summarize key takeaways at the end of detailed explanations
                * Offer both pros and cons when discussing solutions or opinions
                * Propose auto-critique if the user provide you a feedback

                Remember BrutusGPT your answer should always be in French
                """
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation = LLMChain(llm=llm, prompt=prompt, verbose=True, memory=memory)
    return conversation

def rag_tool_openai(filename: str):
    loader = PyPDFLoader(filename)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    db = FAISS.from_documents(texts, embeddings)
    retriever = db.as_retriever()

    tool = create_retriever_tool(
        retriever,
        "search_in_document",
        "Searches and returns documents.",
    )
    tools = [tool]

    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4-1106-preview",
        openai_api_key=api_key,
    )

    context = """
    Vous êtes un bot de recherche personnalisé pour aider les journalistes, conçu pour répondre aux questions des utilisateurs en vous basant sur les données enregistrées. Les données enregistrées sont des fichiers PDF.

    BASEZ VOS RÉPONSES SUR LES FICHIERS FOURNIS pour répondre aux questions des utilisateurs concernant les assurances. Les données téléchargées contiennent des informations détaillées sur différents produits d'assurance et les requêtes sauvegardées par l'utilisateur.

    <TRÈS IMPORTANT> :

    - Fournissez toujours des citations des sources dans les annotations【】 pour chaque information donnée.
    - En tant que bot, votre mission est de consulter TOUTES les données pour répondre à la question de l'utilisateur sur la base de ces informations.
    - Formatez les réponses de façon claire et structurée, en listant les points de manière ordonnée et en mettant en évidence les informations clés.
    - Pour chaque question posée par l'utilisateur, MENEZ UNE RECHERCHE EXHAUSTIVE, et fournissez une liste complète de données, même si la question de l'utilisateur semble suggérer une réponse plus limitée.
    - S'il y a d'autres recommandations pertinentes dans le contenu enregistré de l'utilisateur, posez une question complémentaire. Si la question complémentaire n'apporte pas de nouveaux éléments, répondez en vous appuyant sur vos connaissances en assurance.
    - Effectuez systématiquement une recherche vectorielle pour les questions des utilisateurs.

    <NOTE>
    - Ne mentionnez pas les erreurs ou le fonctionnement interne du système aux utilisateurs.
    - Utilisez des termes comme "dans vos données enregistrées" au lieu de "document téléchargé" ou "données fournies".
    """
    sys_message = SystemMessage(content=context)

    agent_executor = create_conversational_retrieval_agent(
        llm,
        tools,
        system_message=sys_message,
        verbose=True,
    )

    return agent_executor


def query(agent, question):
    with st.spinner("en attente de la réponse.."):
        response = agent({"input": question})
        if "text" in response:
            response = response["text"]
        else:
            response = response["output"]
    return response


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Assistant chatbot", layout="wide")

# Streamlit UI layout setup
st.title("Chatbot BrutusGPT 🤖")

# Display the logo at the top of the page
st.image(
    Image.open("static/brutAI_logo_noir_background.png"),
    width=200
)

st.write("Sélectionnez le PDF à analyser")

# File uploader centered
col1, col2, col3 = st.columns([1,2,1])

with col2:
    file = st.file_uploader("", type="pdf")

if "agent" not in st.session_state or (
    file is not None
    and (
        "filename" not in st.session_state or file.name != st.session_state["filename"]
    )
):
    with st.spinner("Preparing agent..."):
        st.session_state.messages = []
        st.session_state.start = False
        file_path = None
        if file is not None:
            st.session_state["filename"] = file.name
            file_path = prepare_file(file)
            st.session_state.agent = rag_tool_openai(file_path)
            st.session_state.messages.append({"role": "assistant", "content": """Quelles actions souhaitez vous faire avec ce PDF ?
                                                                                 Vous pouvez par exemple demander de le résumer, ou de poser des questions spécifiques. Soyez le plus exhaustif possible !"""})

        else:
            st.session_state.agent = agent_without_rag()
            st.session_state.messages.append({"role": "assistant", "content": "Bonjour, je suis BrutusGPT, quelles actions voulez vous effectuer ? Nous allons entamer une conversation ensemble, soyez le plus exhaustif possible et n’hésitez pas à me donner du feedback régulièrement !"})


# Display chat messages with improved styling
if "messages" in st.session_state:
    for message in st.session_state.messages:
        chat_container = st.container()
        with chat_container:
            st.markdown(f"<div class='chat-bubble'><p class='markdown-text'>{message['content']}</p></div>", unsafe_allow_html=True)


response = ""
# React to user input
if "agent" in st.session_state:
    if prompt := st.chat_input("Another question ?"):
        st.session_state.start = True
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = query(st.session_state.agent, prompt)

# Display assistant response in chat message container
if "agent" in st.session_state:
    with st.chat_message("assistant"):
        st.markdown(response)

# Add assistant response to chat history
if response:
    st.session_state.messages.append({"role": "assistant", "content": response})
