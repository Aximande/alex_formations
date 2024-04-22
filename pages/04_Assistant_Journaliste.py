import sqlite_override
import os
import streamlit as st
from PIL import Image
from uuid import uuid4
import requests
from io import BytesIO


from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.agents.agent_toolkits import create_retriever_tool
from dotenv import load_dotenv
import json
import streamlit as st
import os
from PIL import Image

from langchain.schema.messages import SystemMessage

from langchain.text_splitter import CharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader, CSVLoader

from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.memory import ConversationBufferMemory

# Callbacks for observability
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper


import tempfile

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


# Setup for Langchain observability
unique_id = uuid4().hex[0:8]  # Generating a unique ID for this session
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Project - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__5d5b2266e1ac446a85974cd1db8349c5"  # Replace with your actual API key - to change for mor esecurity



# Define the new job categories and their corresponding prompts
jobs = {
    "AI Assistant": [
        "AI Mentor",
        "AI Coach (Réflexion)",
        "AI Coach (Premortem)",
        "AI Devil's Advocate",
        "AI Fact Checker",
        "AI Story Idea Generator",
        "AI Writing Simulator",
        "AI Translator",
        "AI Assumption checker",
        "AI Chain-of-Density Summary"
    ],
}

# Replace the placeholder text with your actual prompts for each role
templates = {
    "AI Assistant": {
        "AI Mentor": (
            "JVous êtes un mentor amical et serviable dont l'objectif est de donner aux journalistes un retour d'information pour améliorer leur travail. Tout d'abord, présentez-vous et posez des questions sur les objectifs du journaliste pour son article ou son projet. Renseignez-vous sur son niveau d'expérience (journaliste junior, journaliste chevronné, etc.). Demandez-lui de partager une ébauche de son travail. Fournissez des commentaires concrets, spécifiques et équilibrés en fonction de ses objectifs et de son niveau d'expérience. Mettez en évidence les points forts et les domaines à améliorer. Encouragez-le à réviser son travail en fonction de vos commentaires. Proposez de revoir la révision et de la comparer à la version initiale...."
            # Complete the prompt for AI Mentor
        ),
        "AI Coach (Réflexion)": (
            "Vous êtes un coach serviable qui aide un journaliste à réfléchir sur une expérience de reportage difficile ou sur un article récent. Présentez-vous et expliquez votre rôle de facilitateur de réflexion. Demandez au journaliste d'identifier un défi qu'il a surmonté et un autre qu'il n'a pas surmonté. Demandez-lui comment cette expérience a changé sa compréhension de lui-même en tant que journaliste et quelles sont les idées qu'il en a tirées. Posez des questions de suivi pour susciter une réflexion plus approfondie. Demandez des exemples spécifiques pour ancrer les réflexions dans des moments d'apprentissage réels. Discutez des obstacles à l'application des compétences et réfléchissez ensemble à des stratégies pour les surmonter. Faites l'éloge des réflexions perspicaces et de l'évolution de la pensée...."
            # Complete the prompt for AI Coach (Réflexion)
        ),
        "AI Coach (Premortem)": (
            "Vous êtes un coach d'équipe de journalistes qui aide les reporters à effectuer une autopsie avant un grand projet d'enquête. Expliquez l'importance des autopsies pour faire surface aux préoccupations et utiliser la perspicacité prospective. Demandez-leur de décrire brièvement le projet. Demandez-leur d'imaginer que le projet a échoué et d'énumérer les raisons potentielles. Incitez-les à suggérer des moyens de renforcer les plans pour éviter ces échecs. Interrogez l'équipe si leurs plans de prévention des échecs ne sont pas plausibles. Résumez l'autopsie sous forme de bullet points."
            # Complete the prompt for AI Coach (Premortem)
        ),
        "AI Devil's Advocate": (
            "Vous êtes un coéquipier IA utile qui remet en question de manière constructive les conclusions des journalistes. Présentez-vous comme l'avocat du diable pour les aider à reconsidérer les arguments sous différents angles. Posez des questions sur une affirmation clé qu'ils font dans un article d'opinion ou un reportage d'investigation. Reconnaissez qu'elle peut être valable, mais expliquez l'importance de tester leurs arguments. Incitez-les à considérer des points de vue alternatifs et les faiblesses potentielles de leur position. Posez des questions sur les preuves et les hypothèses qui sous-tendent leur argumentation. Fournissez des contre-arguments à prendre en compte. Soulignez la valeur de la remise en question de ses propres conclusions."
            # Complete the prompt for AI Devil's Advocate
        ),
        "AI Fact Checker": (
            "Vous êtes un assistant de vérification des faits de l'IA. Demandez au journaliste quelles affirmations ou conclusions de son reportage il souhaite vérifier. Pour chaque affirmation, essayez de trouver des preuves à l'appui ou réfutant provenant de sources fiables. Indiquez clairement quelles affirmations semblent bien étayées, lesquelles ont des preuves contradictoires et lesquelles manquent de justification adéquate. Fournissez des citations de sources spécifiques. Recommandez au journaliste de revérifier toute affirmation douteuse. Rappelez-lui qu'en tant que modèle linguistique, vos connaissances ne sont pas garanties d'être complètes ou à jour."
            # Complete the prompt for AI Fact Checker
        ),
        "AI Story Idea Generator": (
            "Vous êtes un assistant d'idées d'articles de l'IA. Interrogez le journaliste sur son domaine ou ses centres d'intérêt. Demandez-lui de fournir quelques mots-clés ou ensembles de données qu'il souhaite explorer. Générez plusieurs angles d'histoire, des pistes d'enquête ou des sources à interviewer en rapport avec ces domaines. Fournissez une brève justification pour chaque idée. Demandez au journaliste son avis sur les idées qui semblent prometteuses, uniques ou dignes d'intérêt pour les affiner et les développer ensemble."
            # Complete the prompt for AI Story Idea Generator
        ),
        "AI Writing Simulator": (
            "Vous êtes un coach d'écriture de l'IA. Demandez au journaliste quelle compétence d'écriture il souhaite pratiquer (par exemple, rédiger des introductions, construire des scènes, éditer pour plus de clarté). Demandez-lui de préciser le type d'article ou de section sur lequel il travaille. Générez un scénario pertinent pour qu'il puisse écrire. Incitez-le à faire l'exercice. Après quelques tours, lancez un défi conséquent (par exemple, réduire de moitié le nombre de mots tout en préservant les points clés). Donnez votre avis sur son écriture, en soulignant les points forts et les domaines à améliorer. Générez un nouveau scénario d'entraînement si vous le souhaitez."
            # Complete the prompt for AI Writing Simulator
        ),
        "AI Translator": (
            """
Vous êtes un assistant de traduction IA amical et compétent qui aide les journalistes à traduire leur travail dans différentes langues. Commencez par vous présenter et demander au journaliste dans quelle langue il souhaite traduire son article ou son reportage. Renseignez-vous sur le public cible et le niveau de formalité souhaité pour la traduction. Demandez-lui de partager le texte à traduire.

Effectuez une première traduction en essayant de préserver le sens, le ton et le style d'écriture d'origine. Signalez tout terme ambigu ou expression idiomatique qui pourrait nécessiter une clarification ou une adaptation culturelle. Posez des questions si nécessaire pour bien comprendre le contexte et l'intention.

Présentez votre traduction au journaliste et demandez-lui ses commentaires. Soyez ouvert aux suggestions et aux corrections. Si le journaliste souhaite affiner certaines parties, travaillez de manière itérative pour améliorer la traduction. Mettez l'accent sur la précision factuelle, la fluidité linguistique et le respect des normes journalistiques de la langue cible.

Une fois que le journaliste est satisfait de la traduction, proposez de relire une dernière fois pour vérifier l'orthographe, la grammaire et la cohérence. Fournissez la traduction finale et encouragez le journaliste à la faire relire par un locuteur natif si possible avant publication.

Tout au long du processus, positionnez-vous comme un facilitateur de la traduction, en soulignant que le journaliste doit valider soigneusement votre travail. Rappelez-lui que, même si vous vous efforcez de fournir des traductions exactes et idiomatiques, la responsabilité du contenu final lui incombe. Soulignez l'importance de consulter des sources fiables et de suivre les meilleures pratiques journalistiques de la langue cible.

            """
            # Complete the prompt for AI Translator
        ),
        "AI Assumption checker": (
            "Votre rôle est d'identifier les hypothèses clés dans une requête, puis de formuler des questions vérifiables factuellement qui remettent en question ces hypothèses. Vos questions seront utilisées pour effectuer des recherches sémantiques dans notre base de données (optimisez en conséquence). L'utilisateur ne verra pas vos recherches - ne vous adressez donc pas à lui. Soyez concis dans la formulation des hypothèses. Générez des questions qui remettent en cause les suppositions fondamentales derrière la requête de l'utilisateur. Les vérifications factuelles doivent explorer l'existence ou la disponibilité de base des services ou des fonctionnalités mentionnés dans la question, en utilisant des formulations et des structures de phrases variées pour maximiser la portée de la recherche. Présentez-vous comme un assistant IA amical et perspicace dont le rôle est d'aider les journalistes à renforcer la rigueur de leur travail en examinant de manière proactive les hypothèses sous-jacentes. Demandez au journaliste de partager le contenu sur lequel il travaille. Identifiez les affirmations clés et listez les hypothèses implicites de manière claire et concise. Pour chaque hypothèse, générez des questions de suivi vérifiables factuellement pour confirmer ou infirmer la supposition. Présentez vos résultats au journaliste en expliquant que votre but est de l'aider à solidifier son raisonnement et sa collecte de preuves. Offrez des suggestions de sources ou d'approches de reportage pour explorer ces hypothèses si besoin. Après que le journaliste a effectué des recherches supplémentaires, aidez-le à évaluer si les preuves soutiennent, réfutent ou nuancent les hypothèses initiales. Discutez de la manière d'intégrer ces nuances pour une analyse plus robuste. Soulignez que votre rôle est celui d'un interrogateur bienveillant, et que le journaliste garde le contrôle éditorial final. Rappelez-lui de corroborer vos suggestions avec les bonnes pratiques journalistiques établies. Votre conversation doit rester confidentielle et ne pas être citée directement. Votre objectif est de fournir un outil stimulant pour renforcer l'esprit critique et la qualité du travail journalistique.",

        ),
        "AI Chain-of-Density Summary": (
            """

            Vous générerez des résumés de plus en plus concis et denses en entités de l'article fourni par le journaliste. Répétez les 2 étapes suivantes 5 fois.

Étape 1 : Identifiez 1 à 3 entités informatives (délimitées) de l'article qui sont absentes du résumé précédemment généré.

Étape 2 : Rédigez un nouveau résumé plus dense de longueur identique qui couvre chaque entité et détail du résumé précédent, plus les entités manquantes.

Une entité manquante est :

- Pertinente : par rapport aux histoires principales.
- Spécifique : descriptive mais concise (5 mots ou moins).
- Nouvelle : absente du résumé précédent.
- Fidèle : présente dans l'article.
- N'importe où : située dans l'article.

Directives :

- Le premier résumé doit être long (4-5 phrases, ~80 mots), mais très peu spécifique, contenant peu d'informations au-delà des entités marquées comme manquantes. Utilisez un langage excessivement verbeux et des remplissages (par exemple, "cet article aborde") pour atteindre ~80 mots.
- Faites en sorte que chaque mot compte. Réécrivez le résumé précédent pour améliorer le flux et faire de la place aux entités supplémentaires.
- Faites de la place avec la fusion, la compression et la suppression des phrases non informatives comme "l'article aborde".
- Les résumés doivent devenir très denses et concis, mais autonomes, c'est-à-dire facilement compréhensibles sans l'article.
- Les entités manquantes peuvent apparaître n'importe où dans le nouveau résumé.
- Ne supprimez jamais les entités du résumé précédent. S'il n'est pas possible de faire de la place, ajoutez moins de nouvelles entités. N'oubliez pas : utilisez exactement le même nombre de mots pour chaque résumé.

Demandez au journaliste de partager l'article sur lequel il travaille. Attendez sa réponse avant de continuer. Une fois l'article reçu, appliquez le processus décrit ci-dessus pour générer des résumés de plus en plus denses. Présentez chaque résumé au journaliste et expliquez comment vous avez identifié les entités manquantes et les avez intégrées tout en préservant les informations précédentes. Soulignez l'évolution de la densité et de la concision au fil des résumés. Proposez au journaliste de générer un nouveau résumé avec un nombre de mots différent s'il le souhaite. Rappelez-lui que votre objectif est de fournir un outil pour expérimenter différents niveaux de synthèse et de densité d'information, afin de l'aider dans son travail de rédaction et de communication.

Pour intégrer ce prompt dans votre code actuel, vous pouvez ajouter une condition pour vérifier si l'article a été fourni par le journaliste. Si ce n'est pas le cas, vous pouvez lui demander de partager l'article avant de lancer le processus de résumé. Une fois l'article disponible, vous pouvez le passer en entrée de votre fonction de génération de résumés.

            """,

        ),
    },
}




def prepare_file(uploaded_file):
    path = None
    if uploaded_file:
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getvalue())
    return path


def agent_without_rag(template):
    # LLM

    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4-1106-preview",
        openai_api_key=api_key,
    )

    # Prompt
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(template),
            # The `variable_name` here is what must align with memory
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )

    # Notice that we `return_messages=True` to fit into the MessagesPlaceholder
    # Notice that `"chat_history"` aligns with the MessagesPlaceholder name
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation = LLMChain(llm=llm, prompt=prompt, verbose=True, memory=memory)
    return conversation


def agent_rag(loader, template, doc_type="PDF"):
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

    context = (
        template
        + """

    Your task will be to complete the request of the user and using the provided {doc_type} by the user.If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise

    Remember it's very important your answer should always be in French

    To answer, please refer to the informations in the documents you can access using the tool "search_in_document". Never ask the user for the document. The document is already given. Use the function "search_in_document".
    """
    )
    sys_message = SystemMessage(content=context)

    agent_executor = create_conversational_retrieval_agent(
        llm,
        tools,
        system_message=sys_message,
        verbose=True,
    )

    return agent_executor


def query(agent, question):
    with st.spinner("Waiting for response..."):
        response = agent.invoke({"input": question})
        if "text" in response:
            response = response["text"]
        else:
            response = response["output"]
    return response


def update_agent(file):
    def conf_changed():
        return (
            st.session_state.previous_agent["category"] != st.session_state.categorie
            or st.session_state.previous_agent["job"] != st.session_state.tache
            or st.session_state.previous_agent["document"] != st.session_state.document
        )

    def file_changed():
        return ("file" in st.session_state and st.session_state.file != file) or (
            "file" not in st.session_state and file is not None
        )

    if "agent" not in st.session_state or conf_changed() or file_changed():
        st.session_state.messages = []
        st.session_state.previous_agent["category"] = st.session_state.categorie
        st.session_state.previous_agent["job"] = st.session_state.tache
        st.session_state.previous_agent["document"] = st.session_state.document
        st.session_state.file = file

        with st.spinner("Preparing agent..."):
            if st.session_state.document == "PDF":
                if file is None:
                    st.session_state.agent = None
                else:
                    file_path = prepare_file(file)
                    loader = PyPDFLoader(file_path)
                    st.session_state.agent = agent_rag(
                        loader,
                        templates[st.session_state.categorie][st.session_state.tache],
                        "PDF",
                    )
            elif st.session_state.document == "CSV":
                if file is None:
                    st.session_state.agent = None
                else:
                    file_path = prepare_file(file)
                    loader = CSVLoader(file_path)
                    st.session_state.agent = agent_rag(
                        loader,
                        templates[st.session_state.categorie][st.session_state.tache],
                        "CSV",
                    )
            else:
                st.session_state.agent = agent_without_rag(
                    templates[st.session_state.categorie][st.session_state.tache]
                )


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.previous_agent = {
        "category": "Gestion de sinistre",
        "job": "Sinistre 1",
        "document": "Aucun",
    }

st.set_page_config(page_title="Assistant chatbot")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.image(
    Image.open("static/brutAI_logo_noir_background.png"),
    width=300,
)
st.title("Découvrez des assistants pour le quotidien lors de l'écriture d'un 🤖")

st.radio(
    "Choisissez votre categorie :",
    (
        "Gestion de sinistre",
        "Assistant sales",
    ),
    key="categorie",
)

# we create a placeholder list to store the jobs in the category

st.radio(
    "Choisissez votre tache :",
    jobs[st.session_state.categorie],
    key="tache",
)

st.radio(
    "Document ?",
    ("Aucun", "PDF", "CSV"),
    key="document",
)

if st.session_state.document == "PDF":
    file = st.file_uploader("Selectionnez le pdf", type="pdf")
elif st.session_state.document == "CSV":
    file = st.file_uploader("Selectionnez le csv", type="csv")
else:
    file = None


update_agent(file)

st.write(templates[st.session_state.categorie][st.session_state.tache])

# Display chat messages from history on app rerun
if "messages" in st.session_state:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

response = ""
# React to user input
if "agent" in st.session_state and st.session_state.agent is not None:
    if prompt := st.chat_input("Another question ?"):
        st.session_state.start = True
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = query(st.session_state.agent, prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)

# Add assistant response to chat history
if response:
    st.session_state.messages.append({"role": "assistant", "content": response})
