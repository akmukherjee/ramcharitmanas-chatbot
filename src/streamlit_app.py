from dotenv import load_dotenv
import sys
import os
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion import ingest
from retrievers import retrieval
from responder import response_generation

load_dotenv()
st.set_page_config(
    page_title="Ramcharitmanas Answer Bot",
    page_icon="images/tulsidas.jpg",  # Use your custom image
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600&display=swap');

.main-header {
    text-align: center;
    margin-bottom: 1rem;
    margin-top: -1rem;
}

/* Main Title */
.title-line-1 {
    font-family: 'Cinzel', serif;
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #800000, #DAA520, #D2691E, #800000);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 2px;
    line-height: 1;
    word-spacing: 4px;
    display: inline-block;
}

/* Subtitle */
.title-line-2 {
    font-family: 'Cinzel', serif;
    font-size: 2.2rem;
    font-weight: 600;
    background: linear-gradient(90deg, #2F4F4F, #DAA520, #2F4F4F);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 1.5px;
    line-height: 1;
    display: inline-block;
}

/* Reduce overall padding */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
}

/* Chat message styling */
.stChatMessage, .stChatMessage p, .stChatMessage div {
    font-family: 'Crimson Text', serif !important;
    font-size: 1.1rem !important;
    line-height: 1.6 !important;
    color: #4B3832 !important;
}

/* Highlight any verse text (if marked with a .verse class) */
.verse {
    color: #800000;
    font-weight: 600;
    font-size: 1.15rem;
}
</style>
""",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("images/ramcharitmanas.jpg", width=500)

    # header markdown call

    st.markdown(
        '<h1 class="main-header"><span class="title-line-1">Ramcharitmanas Answer Bot</span></h1>',
        unsafe_allow_html=True,
    )

prompt = st.chat_input("Enter your Ramcharitmanas related question here")

# Initializing retriever once per session
if "retriever" not in st.session_state:
    retriever = retrieval.get_retriver()
    st.session_state["retriever"] = retriever

# Initializing messages array empty array
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# for display of chat history
for message in st.session_state["messages"]:
    if message["role"] == "RC-Bot":
        st.chat_message(message["role"], avatar="🕉️").write(message["content"])
    else:
        st.chat_message(message["role"], avatar="🙏").write(message["content"])

if prompt:
    retriever = st.session_state["retriever"]
    with st.spinner("Getting a response ..."):
        response = response_generation.get_validated_response(
            retriever=retriever, question=prompt
        )
        st.chat_message("user", avatar="🙏").write(prompt)
        st.chat_message("RC-Bot", avatar="🕉️").write(response)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "RC-Bot", "content": response})
