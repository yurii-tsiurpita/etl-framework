import streamlit as st
from etl.etl import Etl
from typing import Union, TypedDict, Literal
from confluence.typed_dicts.confluence_config import ConfluenceConfig
from ai_assistant.ai_assistant import AiAssistant
from langchain_core.messages import AIMessage, HumanMessage
from common.utils.stream_text import stream_text
import os
from confluence.confluence_service import ConfluenceService
from streamlit.delta_generator import DeltaGenerator
from etl.constants.etl_constants import CONFLUENCE_CHROMA_NAME
import shutil
#
# from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
# https://discuss.streamlit.io/t/concurrency-with-streamlit/29500/6
# https://discuss.streamlit.io/t/does-streamlit-is-running-on-a-single-threaded-development-server-by-default-or-not/9898
# https://gist.github.com/tvst/fa33b9dcb58040cbcb0ea376146d4e8c
# nicegui
# Shiny


class UserDataForConfluenceEtl(TypedDict):
    sourceUrl: str
    userNameOnSource: str
    apiKey: str
    selectedSpaces: list[str]


class UserDataForSharepointEtl(TypedDict):
    clientId: str
    documentLibraryId: str
    clientSecret: str

# TODO add multiselect for spaces
# TODO handle source change in chat
# TODO handle reimport in chat
    
# TODO Figma: access token, project id, (get_files_data) files = spaces
# TODO file lock presentation
# TODO info for the presentation


class App:
    def __init__(self):
        self.spaces = []
        self.fetched_spaces = []
        self.external_data_sources = []
        self.data_source = None
        self.processingSource: bool = False
        self.confluence_etl: Union[Etl, None] = None
        self._initAiAssistantAndSources()

    def _checkImportedData(self) -> None:
        if os.path.isdir("./data/confluence_chroma"):
            if "Confluence" not in self.external_data_sources:
                self.external_data_sources.append("Confluence")
        elif os.path.isdir("./data/sharepoint_chroma"):
            if "Sharepoint" not in self.external_data_sources:
                self.external_data_sources.append("Sharepoint")

    def _initAiAssistantAndSources(self, selectedSource: Literal["Confluence", "Sharepoint"] = "Confluence") -> None:
        self._checkImportedData()
        if self.confluence_etl == None:
            self.confluence_etl = Etl({})
        confluence_etl: Etl = self.confluence_etl
        if os.path.isdir("./data/confluence_chroma"):
            self.chroma = confluence_etl.getChroma()
            self.confluence_assistant = AiAssistant(self.chroma)

    def _performETL(self, selectedSource: Literal["Confluence", "Sharepoint"],
                    userDataForConfluence: UserDataForConfluenceEtl = {},
                    userDataForSharepoint: UserDataForSharepointEtl = {}) -> None:
        if selectedSource == "Confluence":
            sourceUrl = userDataForConfluence['sourceUrl']
            userNameOnSource = userDataForConfluence['userNameOnSource']
            apiKey = userDataForConfluence['apiKey']
            selectedSpaces = userDataForConfluence['selectedSpaces']
            selectedSpacesKeys = []
            if "All" in selectedSpaces:
                selectedSpacesKeys = list(map(lambda space: space.key, self.fetched_spaces))
            else:
                for space in self.fetched_spaces:
                    if (space.name in selectedSpaces):
                        selectedSpacesKeys.append(space.key)
            print(f"Selected spaces keys: {selectedSpacesKeys}")
            etlConfig: ConfluenceConfig = {
                'url': sourceUrl,
                'username': userNameOnSource,
                'api_key': apiKey,
            }
            self.confluence_etl = Etl(etlConfig)
            self.confluence_etl.execute(spaceKeys=selectedSpacesKeys)
        elif selectedSource == "Sharepoint":
            print("Sharepoint ETL not implemented yet")

    def _getSpaces(self, sourceUrl: str, userNameOnSource: str, apiKey: str) -> None:
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

    def _isReadyToLoadSource(self, userData: dict[str, str | None]) -> bool:
        if 'sourceUrl' in userData:
            sourceUrl = userData['sourceUrl']
            userNameOnSource = userData['userNameOnSource']
            apiKey = userData['apiKey']
            selectedSpaces = userData['selectedSpaces']
            return ((sourceUrl != '' and sourceUrl != None)
                    and (userNameOnSource != '' and userNameOnSource != None)
                    and (apiKey != '' and apiKey != None)
                    and (len(selectedSpaces) != 0 and selectedSpaces != None))
        elif 'clientId' in userData:
            clientId = userData['clientId']
            documentLibraryId = userData['documentLibraryId']
            clientSecret = userData['clientSecret']
            return ((clientId != '' and clientId != None)
                    and (documentLibraryId != '' and documentLibraryId != None)
                    and (clientSecret != '' and clientSecret != None))

    def _isReadyToLoadSpace(self, sourceUrl: str, userNameOnSource: str, apiKey: str) -> bool:
        return ((sourceUrl != '' and sourceUrl != None)
                and (userNameOnSource != '' and userNameOnSource != None)
                and (apiKey != '' and apiKey != None))

    def _renderAddExternalSourcesSection(self) -> None:
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
        # Inputs Confluence
        sourceUrl = None
        userNameOnSource = None
        apiKey = None
        selectedSpaces = None
        loadSpacesBtn = None
        # Inputs Sharepoint
        clientId = None
        documentLibraryId = None
        clientSecret = None
        if (sourceToLoad == "Confluence"):
            sourceUrl = col2.text_input(
                "Enter the URL of the source you want to add", placeholder="https://example.com")
            userNameOnSource = col2.text_input(
                "Enter your username for the source", placeholder="john@doe.ai")
            apiKey = col2.text_input(
                "Enter your API key for the source", placeholder="e.g. QAWehqwj11keu13", type="password")
            #  remade to multiple select
            selectedSpaces = col2.multiselect(
                "Load spaces before choosing", options=self.spaces)
            loadSpacesBtn = upload_container.button(
                "Load Spaces", disabled=not self._isReadyToLoadSpace(sourceUrl, userNameOnSource, apiKey))
        elif (sourceToLoad == "Sharepoint"):
            self.spaces = []
            clientId = col2.text_input(
                "Enter the client ID of the source you want to add", placeholder="e.g. 12345678-1234-1234-1234-1234567890ab")
            documentLibraryId = col2.text_input(
                "Enter the document library ID for the source", placeholder="e.g. 12345678-1234-1234-1234-1234567890ab")
            clientSecret = col2.text_input(
                "Enter your client secret for the source", placeholder="e.g. QAWehqwj11keu13", type="password")

        if loadSpacesBtn:
            self._getSpaces(sourceUrl, userNameOnSource, apiKey)
        if sourceToLoad == "Confluence":
            dictionaryToPassToSubmitBtn = {
                'sourceUrl': sourceUrl,
                'userNameOnSource': userNameOnSource,
                'apiKey': apiKey,
                'selectedSpaces': selectedSpaces
            }
        else:
            dictionaryToPassToSubmitBtn = {
                'clientId': clientId,
                'documentLibraryId': documentLibraryId,
                'clientSecret': clientSecret
            }
        submitBtn = upload_container.button(
            "Add Source", disabled=not self._isReadyToLoadSource(userData=dictionaryToPassToSubmitBtn))
        if submitBtn:
            if (sourceToLoad == "Confluence"):
                self.processingSource = True
                self._performETL(userDataForConfluence={
                    'sourceUrl': sourceUrl,
                    'userNameOnSource': userNameOnSource,
                    'apiKey': apiKey,
                    'selectedSpaces': selectedSpaces
                }, selectedSource="Confluence")
                self._initAiAssistantAndSources(selectedSource="Confluence")
            elif (sourceToLoad == "Sharepoint"):
                self.processingSource = True
                self._performETL(userDataForSharepoint={
                    'clientId': clientId,
                    'documentLibraryId': documentLibraryId,
                    'clientSecret': clientSecret
                }, selectedSource="Sharepoint")
                self._initAiAssistantAndSources(selectedSource="Confluence")
        if (self.processingSource is True):
            if (len(self.external_data_sources) == len(possible_sources)):
                placeholder.empty()
            with st.spinner(f"Processing {sourceToLoad} data..."):
                self.processingSource = False
                st.rerun()

    def render(self) -> None:
        st.set_page_config(page_title='AI Assistant', page_icon='🤖')
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

    def submit(self, prompt: str, chatContainer) -> None:
        response = chatContainer.chat_message('ai').write_stream(
            stream_text(self.confluence_assistant.answer(
                prompt, st.session_state.chat_history))
        )
        st.session_state.chat_history.append(AIMessage(content=response))
