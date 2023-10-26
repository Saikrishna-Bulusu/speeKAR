from collections import namedtuple
import altair as alt

import os, time
import pandas as pd
import math
import glob
import base64
from io import StringIO

import openai
import tiktoken
encoding = tiktoken.get_encoding("cl100k_base")
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

# -------------IMPORTING CORE FUNCTIONALITIES OF THE SpeeKAR_BOT-------------
from qa import (
    speechtotext,
    readdoc_splittext,
    readdoc_splittext_pdf,
    create_context,
    create_db,
    chatbot_slim,
    chatbot,
    texttospeech_raw,
)

# -------------------AUDIO FUNCTIONALITY-------------------------
from mutagen.wave import WAVE

# --------------------HTML BUILDER AND FUNCTIONALITIES-----------------------------------#
from htbuilder import (
    HtmlElement,
    div,
    ul,
    li,
    br,
    hr,
    a,
    p,
    img,
    styles,
    classes,
    fonts,
)
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb

import streamlit as st
from audiorecorder import audiorecorder


from PIL import Image


# ------------------DEFAULTS--------------------#
SECRET_TOKEN = os.environ["SECRET_TOKEN"]
openai.api_key = SECRET_TOKEN


# -----------------------HELPER FUNCTIONS--------------------------#
def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):
    style = """
    <style>
      # MainMenu {visibility: display;}
      footer {visibility: display;}
     .stApp { bottom: 105px; }
    </style>
    """
    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 50, 0, 50),
        width=percent(100),
        color="black",
        text_align="left",
        height="auto",
        opacity=1,
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(1.5),
    )

    body = p()
    foot = div(style=style_div)(hr(style=style_hr), body)

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


# -------------------------------FUNCTIONS FOR KAR BASED RESPONSE GENERATION-------------#
def process_query(speech_input, email, passwd):
    question0 = speech_input
    question = speech_input
    query = speechtotext(speech_input)

    return query


def generate_kARanswer(query, text_split):
    ans, context, keys = chatbot_slim(query, text_split)
    return ans, context, keys


# -------------------------------------------------------------------------#
# --------------------------GUI CONFIGS------------------------------------#
# -------------------------------------------------------------------------#
# App title
st.set_page_config(page_title="🤗💬 SpeeKAR @ Gen AI-Chat Bot")
st.header("SpeeKAR @ Gen AI-Chat Bot")


# Hugging Face Credentials
with st.sidebar:
    st.title("🤗💬SpeeKAR @ Gen-AI Chat Bot")
    st.success(
        "Access to this Gen-AI Powered Chatbot is provided by  [Anupam](https://www.linkedin.com/in/anupamisb/)!!",
        icon="✅",
    )
    hf_email = "anupam_purwar2019@pgp.isb.edu"
    hf_pass = "PASS"
    st.markdown(
        "📖 This app is hosted by Anupam Purwar [website](https://anupam-purwar.github.io/page/)!"
    )
    image = Image.open("speekar_logo.png")
    st.image(
        image,
        caption=None,
        width=None,
        use_column_width=None,
        clamp=False,
        channels="RGB",
        output_format="auto",
    )


# ---------------------------------------------------------#
# -----------------UPLOAD THE SRC DOCUMENT-----------------#
# ---------------------------------------------------------#
st.title("Please let me know what you want to talk about by choosing a file below!")
uploaded_file = st.file_uploader(label = "")
uploaded_status = 0
if uploaded_status==0 and uploaded_file is not None:
    # To read file as bytes:
    #bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)

    file_path = os.path.join( os.getcwd(), uploaded_file.name)
    with open(file_path,"wb") as f: 
        f.write(uploaded_file.getbuffer())         
    st.success("Saved File")

    print(file_path)
    filename = file_path
    # To convert to a string based IO:
    # stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # st.write(stringio)

    # To read file as string:
    # string_data = StringIO.read()
    # st.write(string_data)
    # st.write("Filename:", uploaded_file.name)
    #print(".docx" in filename)#uploaded_file.name)
    if ".docx" in filename: #uploaded_file.name:
        all_text, text_split, text_chunk, headings, para_texts = readdoc_splittext(filename)#uploaded_file.name)
    elif ".pdf" in filename: #uploaded_file.name:
        all_text, text_split, text_chunk, headings, para_texts = readdoc_splittext_pdf(filename)#uploaded_file.name)
    # ----------------------------------------------------------#
    # -------------START INTERACTING WITH THE CHATBOT------------#
    # ----------------------------------------------------------#
    #print("HEADINGS:", headings)
    #print("PARAS:", para_texts)
    #print("TEXT_SPLIT:", text_split)
    #num_tokens = len(encoding.encode(context))
    #if num_tokens > 4000:
    with st.chat_message("assistant"):
        st.write("Hi! Getting your contexts ready for query! Please wait!")
    hf, db = create_db(text_chunk)
    
    #else:
    uploaded_status = 1
# ------------------------------------------------------------------------------#
# -------------------------QUERY AUDIO INPUT - RETURNING TEXT QUERY-------------#
# ------------------------------------------------------------------------------#



st.title("Ask me anything about the document!")
#st.title("Interact with the bot, here!")
audio = audiorecorder("Click to record", "Click to stop recording")



#query = None
query_status = 0
while not audio.empty() and query_status == 0:
    # To play audio in frontend:
    with st.chat_message("user"):
        st.audio(audio.export().read())
    
        # To save audio to a file, use pydub export method:
        audio.export("query.wav", format="wav")
    #with st.chat_message("assistant"):
        # To get audio properties, use pydub AudioSegment properties:
        #st.write(f"Duration: {audio.duration_seconds} seconds")
    
        # st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")
    querywav = WAVE("query.wav")
    if querywav.info.length > 0:
        query = process_query("query.wav", hf_email, hf_pass)
        st.markdown(
            """
            <style>
            .big-font {
                font-size:20px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # st.markdown("Your question in text ::")
        #st.markdown(
        #    '<p class="big-font"> Your question in text : </p>', unsafe_allow_html=True
        #)
        # if "messages" not in st.session_state.keys():
        #    st.session_state.messages = [{"role": "assistant", "content": query}]
    query_status = 1
        
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask anything from the document!"}
    ]

# Display chat messages
#for message in st.session_state.messages:
#    with st.chat_message(message["role"]):
#        st.write(message["content"])
# ---------------------------------------------------------#
# -----------------LLM RESPONSES-----------------#
# ---------------------------------------------------------#
# Store LLM generated responses


while (uploaded_status == 1) and (query_status == 1):
    
    with st.chat_message("assistant"):
        st.write("If I heard you right, your question is as follows ")
    with st.chat_message("user"):
        st.write(query)

    context, keywords = create_context(query, text_split, headings, para_texts)
    #with st.chat_message("assistant"):
    #    st.write(context)

    # Generate a new response if last message is not from assistant
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                #print(context)
                #st.write("Using KAR")
                ans, context, keys = chatbot_slim(query, context, keywords)
                
                if (ans=='I don\'t know.' or ans=='I don\'t know' ):
                    #st.write("Using StdRAG")
                    ans = chatbot(query,db)
                    st.write(ans)
                else:
                    st.write(ans)
            except Exception as e:
                #st.write(e)
                #st.write("Using StdRAG")
                ans = chatbot(query,db)
                st.write(ans)

        message = {"role": "assistant", "content": ans}
        st.session_state.messages.append(message)
        # -----------text to speech--------------------------#
        texttospeech_raw(ans, language="en")
        mymidia_placeholder = st.empty()
        with open("answer.wav", "rb") as audio_file:
            #st.audio(audio_bytes, format="audio/wav")
            audio_bytes = audio_file.read()
            b64 = base64.b64encode(audio_bytes).decode()
            md = f"""
                 <audio controls autoplay="true">
                 <source src="data:audio/wav;base64,{b64}" type="audio/wav">
                 </audio>
                 """
            mymidia_placeholder.empty()
            time.sleep(1)
            mymidia_placeholder.markdown(md, unsafe_allow_html=True)
        
    query_status = 0
    
    #st.markdown(
    #    """
    #        <style>
    #        .big-font {
    #            font-size:20px !important;
    #        }
    #        </style>
    #        """,
    #    unsafe_allow_html=True,
    #)

    
    #st.markdown(
    #    '<p class="big-font"> Play your answer below! </p>', unsafe_allow_html=True
    #)
    #st.write(ans)
    

# if prompt := st.chat_input():
#   st.session_state.messages.append({"role": "user", "content": prompt})
#    with st.chat_message("user"):
#        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            pass
        pass
    message = {"role": "assistant", "content": ans}
    st.session_state.messages.append(message)


myargs = [
    "Made in India",
    "" " with ❤️ by ",
    link("https://www.linkedin.com/in/anupamisb/", "@Anupam"),
    br(),
    link("https://anupam-purwar.github.io/page/", "SpeeKAR ChatBoT"),
    br(),
    link("https://www.linkedin.com/in/rahul-sundar-311a6977/", "@Rahul"),
    br(),
    link("https://github.com/RahulSundar", "SpeeKAR ChatBoT"),
]


def footer():
    myargs = [
        "Made in India",
        "" " with ❤️ by ",
        link("https://www.linkedin.com/in/anupamisb/", " Anupam for "),
        link("https://anupam-purwar.github.io/page/", "SpeeKAR ChatBoT"),
        ", and",
        link("https://www.linkedin.com/in/rahul-sundar-311a6977/", "@Rahul"),
        link("https://github.com/RahulSundar", "SpeeKAR ChatBoT"),
    ]
    layout(*myargs)


footer()
