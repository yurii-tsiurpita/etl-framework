# import streamlit as st
# from frontend.main import App

# if "my_instance" not in st.session_state:
#   st.session_state.my_instance = App()
# st.session_state.my_instance.render()

from typing import cast
from dotenv import load_dotenv
from ai_assistant.ai_assistant import AiAssistant
from common.utils.stream_text import stream_text
from etl.etl import Etl
from etl.typed_dicts.etl_config import EtlConfig
from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st

load_dotenv()

st.set_page_config(page_title='AI Assistant', page_icon='🤖')
st.title('AI Assistant')

etlConfig: EtlConfig = {
  'url': '',
  'username': '',
  'api_key': '',
  'space_key': '',
}

confluence_etl = Etl(etlConfig)
# confluence_etl.execute()

chroma = confluence_etl.getChroma()
confluence_assistant = AiAssistant(chroma)

if 'chat_history' not in st.session_state:
  st.session_state.chat_history = cast(
    list[AIMessage | HumanMessage],
    [AIMessage(content='Hello, my name is Trinity. I am Confluence chatbot assistant. How can I help you?')]
  )

for message in st.session_state.chat_history:
  if isinstance(message, AIMessage):
    with st.chat_message('AI'):
      st.write(message.content)
  elif isinstance(message, HumanMessage):
    with st.chat_message('Human'):
      st.write(message.content)

user_message = st.chat_input('Type your message here...')

if user_message is not None and user_message != '':
  st.session_state.chat_history.append(HumanMessage(content=user_message))

  with st.chat_message('Human'):
    st.markdown(user_message)

  with st.chat_message('AI'):
    response = st.write_stream(
      stream_text(confluence_assistant.answer(user_message, st.session_state.chat_history))
    )

  st.session_state.chat_history.append(AIMessage(content=response))
