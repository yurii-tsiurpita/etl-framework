from typing import cast
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st
load_dotenv()
from frontend.main import App

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = cast(
        list[AIMessage | HumanMessage],
        [AIMessage(
            content='Hello, my name is Trinity. I am Confluence chatbot assistant. How can I help you?')]
    )

if "my_instance" not in st.session_state:
    st.session_state.my_instance = App()
st.session_state.my_instance.render()
