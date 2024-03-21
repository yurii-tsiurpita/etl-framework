import streamlit as st
from etl.etl import Etl
from confluence.typed_dicts.confluence_config import ConfluenceConfig
from ai_assistant.ai_assistant import AiAssistant
from langchain_core.messages import AIMessage, HumanMessage
from common.utils.stream_text import stream_text
import os
from etl.constants.etl_constants import CONFLUENCE_CHROMA_NAME
import shutil
from confluence.confluence_service import ConfluenceService
#
# from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
# https://discuss.streamlit.io/t/concurrency-with-streamlit/29500/6
# https://discuss.streamlit.io/t/does-streamlit-is-running-on-a-single-threaded-development-server-by-default-or-not/9898
# https://gist.github.com/tvst/fa33b9dcb58040cbcb0ea376146d4e8c
# nicegui
# Shiny


class App:
    def __init__(self):
        self.spaces = []
        self.fetched_spaces = []
        self.external_data_sources = []
        self.data_source = None
        self.processingSource = False
        self.confluence_etl = None
        self.chat_container = None
        # self._initAiAssistantAndSources()

    def _initAiAssistantAndSources(self):
        confluence_etl: Etl = self.confluence_etl
        if os.path.isdir("./data/confluence_chroma"):
            self.external_data_sources.append("Confluence")
        elif os.path.isdir("./data/sharepoint_chroma"):
            self.external_data_sources.append("Sharepoint")
        self.chroma = confluence_etl.getChroma()
        self.confluence_assistant = AiAssistant(self.chroma)

    def _performETL(self, sourceUrl: str, userNameOnSource: str, apiKey: str, selectedSpace: str):
        spacesList: list[str] = [next(filter(lambda space: space.name == selectedSpace, self.fetched_spaces), None).key]
        print(f"Spaces List: {spacesList}")
        if selectedSpace == 'All':
            spacesList = list(map(lambda space: space.key, self.fetched_spaces))
        etlConfig: ConfluenceConfig = {
            'url': sourceUrl,
            'username': userNameOnSource,
            'api_key': apiKey,
        }
        self.confluence_etl = Etl(etlConfig)
        self.confluence_etl.execute(spaceKeys=spacesList)

    def _getSpaces(self, sourceUrl: str, userNameOnSource: str, apiKey: str):
        spaces = ConfluenceService({
            'url': sourceUrl,
            'username': userNameOnSource,
            'api_key': apiKey,
        }).getSpacesData()
        self.fetched_spaces = spaces
        self.spaces = list(map(lambda space: space.name, spaces))
        self.spaces.append('All')
        st.rerun()

    def _isAiAssistantAvailable(self) -> bool:
        return self.confluence_etl != None and len(self.external_data_sources) != 0

    def _isReadyToLoadSource(self, sourceUrl: str, userNameOnSource: str, apiKey: str, selectedSpace: str) -> bool:
        return ((sourceUrl != '' and sourceUrl != None)
                and (userNameOnSource != '' and userNameOnSource != None)
                and (apiKey != '' and apiKey != None)
                and (selectedSpace != '' and selectedSpace != None))

    def _isReadyToLoadSpace(self, sourceUrl: str, userNameOnSource: str, apiKey: str) -> bool:
        return ((sourceUrl != '' and sourceUrl != None)
                and (userNameOnSource != '' and userNameOnSource != None)
                and (apiKey != '' and apiKey != None))

    def _renderAddExternalSourcesSection(self):
        possible_sources = ["Confluence", "Sharepoint"]
        sourceToLoad = None
        if (len(self.external_data_sources) == 0):
            st.warning(
                "Add External Sources. You have no external sources to query from.")
        placeholder = st.empty()
        expander = placeholder.expander("Add External Sources")
        upload_container = expander.container()
        col1, col2 = upload_container.columns(2)
        sourceToLoad = col1.radio(
            "Here from where you can add sources:",
            possible_sources,
            captions=["Data from Confluence spaces", "Data from Sharepoint"])
        sourceUrl = col2.text_input(
            "Enter the URL of the source you want to add", placeholder="https://example.com")
        userNameOnSource = col2.text_input(
            "Enter your username for the source", placeholder="john@doe.ai")
        apiKey = col2.text_input(
            "Enter your API key for the source", placeholder="e.g. QAWehqwj11keu13", type="password")
        selectedSpace = col2.selectbox(
            "Load spaces before choosing", self.spaces)
        # buttons
        loadSpacesBtn = upload_container.button(
            "Load Spaces", disabled=not self._isReadyToLoadSpace(sourceUrl, userNameOnSource, apiKey))
        if loadSpacesBtn:
            self._getSpaces(sourceUrl, userNameOnSource, apiKey)
        submitBtn = upload_container.button("Add Source", disabled=not self._isReadyToLoadSource(
            sourceUrl, userNameOnSource, apiKey, selectedSpace))
        if submitBtn:
            if (sourceToLoad == "Confluence"):
                self.processingSource = True
                self._performETL(sourceUrl, userNameOnSource,
                                 apiKey, selectedSpace)
                self._initAiAssistantAndSources()
        if (self.processingSource is True):
            if (len(self.external_data_sources) == len(possible_sources)):
                placeholder.empty()
            with st.spinner(f"Processing {sourceToLoad} data..."):
                self.processingSource = False
                st.rerun()

    def render(self):
        st.set_page_config(page_title='AI Assistant', page_icon='🤖')
        if len(self.external_data_sources) != 2:
            self._renderAddExternalSourcesSection()
        col1, col2 = st.columns(2)
        self.data_source = col1.selectbox(
            "Choose a data source", self.external_data_sources)
        st.title(
            f"Test GPT 3.5 LLM on your own data from {self.data_source or ':gray[[select source above]]'}!")
        st.write(
            f'Select a source and start chatting. To test the model against your own data, insert a url and credentials.')
        # Chat
        prompt = st.chat_input(
            placeholder='Enter your question:', disabled=not self._isAiAssistantAvailable())
        st.markdown('''
            <style>
                [data-testid="element-container"] + [data-testid=stVerticalBlockBorderWrapper] > div > [data-testid="stVerticalBlock"] {
                    max-height: 650px !important;
                    overflow-y: auto !important;
                }
            </style>''', unsafe_allow_html=True)
        chatContainer = st.container()
        for message in st.session_state.chat_history:
            if isinstance(message, AIMessage):
                with chatContainer.chat_message('ai'):
                    st.write(message.content)
            elif isinstance(message, HumanMessage):
                with chatContainer.chat_message('user'):
                    st.write(message.content)
        if prompt and prompt != '':
            st.session_state.chat_history.append(HumanMessage(content=prompt))
            chatContainer.chat_message('user').write(prompt)
            self.submit(prompt, chatContainer)

    def submit(self, prompt: str, chatContainer):
        response = chatContainer.chat_message('ai').write_stream(
            stream_text(self.confluence_assistant.answer(
                prompt, st.session_state.chat_history))
        )
        st.session_state.chat_history.append(AIMessage(content=response))
