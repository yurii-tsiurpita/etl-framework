import streamlit as st
from etls.confluence_etl.confluence_etl import ConfluenceEtl
from etls.figma_etl.figma_etl import FigmaEtl
from etls.constants.etl_constants import CONFLUENCE_CHROMA_NAME, FIGMA_CHROMA_NAME
from typing import Union, TypedDict, Literal
from confluence.classes.confluence_config import ConfluenceConfig
from ai_assistants.confluence_ai_assistant.confluence_ai_assistant import ConfluenceAiAssistant
from ai_assistants.figma_ai_assistant.figma_ai_assistant import FigmaAiAssistant
from langchain_core.messages import AIMessage, HumanMessage
from common.utils.stream_text import stream_text
import os
from confluence.confluence_service import ConfluenceService
from figma.figma_service import FigmaService

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


class UserDataForFigmaEtl(TypedDict):
    figmaAccessToken: str
    selectedFigmaFiles: list[str]

# TODO handle source change in chat
# TODO change chat bot first message
# TODO handle reimport in chat
# TODO Figma: access token, project id, (get_files_data) files = spaces

# TODO add multiselect for spaces -> Done
# TODO file lock presentation -> Done
# TODO info for the presentation -> Done


class App:
    def __init__(self):
        self.spaces = []
        self.fetched_spaces = []
        self.figma_pages = []
        self.fetched_figma_pages = []
        self.external_data_sources = []
        self.data_source = None
        self.etl_instance: Union[ConfluenceEtl, FigmaEtl, None] = None
        self._initAiAssistantAndSources()

    def _checkImportedData(self) -> None:
        if os.path.isdir(f"./data/{CONFLUENCE_CHROMA_NAME}"):
            if "Confluence" not in self.external_data_sources:
                self.external_data_sources.append("Confluence")
        if os.path.isdir("./data/sharepoint_chroma"):
            if "Sharepoint" not in self.external_data_sources:
                self.external_data_sources.append("Sharepoint")
        if os.path.isdir(f"./data/{FIGMA_CHROMA_NAME}"):
            if "Figma" not in self.external_data_sources:
                self.external_data_sources.append("Figma")

    # TODO fix this
    def _initAiAssistantAndSources(self, selectedSource: Literal["Confluence", "Sharepoint", "Figma"] = "Confluence") -> None:
        self._checkImportedData()
        etlMap = {
            "Confluence": ConfluenceEtl,
            "Figma": FigmaEtl
        }
        etlSourceLocationMap = {
            "Confluence": CONFLUENCE_CHROMA_NAME,
            "Figma": FIGMA_CHROMA_NAME
        }
        aiAssistantMap = {
            "Confluence": ConfluenceAiAssistant,
            "Figma": FigmaAiAssistant
        }
        if self.etl_instance == None:
            self.etl_instance = etlMap[selectedSource]({})
        confluence_etl: ConfluenceEtl = self.etl_instance
        if os.path.isdir(f"./data/{etlSourceLocationMap[selectedSource]}"):
            self.chroma = confluence_etl.getChroma()
            self.confluence_assistant = aiAssistantMap[selectedSource](self.chroma)

    def _performETL(self, selectedSource: Literal["Confluence", "Sharepoint", "Figma"],
                    userData: Union[UserDataForConfluenceEtl, UserDataForFigmaEtl]) -> None:
        if selectedSource == "Confluence":
            sourceUrl = userData['sourceUrl']
            userNameOnSource = userData['userNameOnSource']
            apiKey = userData['apiKey']
            selectedSpaces = userData['selectedSpaces']
            selectedSpacesKeys = []
            if "All" in selectedSpaces:
                selectedSpacesKeys = list(
                    map(lambda space: space.key, self.fetched_spaces))
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
            self.etl_instance = ConfluenceEtl(etlConfig)
            self.etl_instance.execute(spaceKeys=selectedSpacesKeys)
        elif selectedSource == "Sharepoint":
            print("Sharepoint ETL not implemented yet")
        elif selectedSource == "Figma":
            figmaAccessToken = userData['figmaAccessToken']
            selectedFigmaFiles = userData['selectedFigmaFiles']
            selectedFigmaFilesKeys = []
            for file in self.fetched_figma_pages:
                if (file.name in selectedFigmaFiles):
                    selectedFigmaFilesKeys.append(file.key)
            self.etl_instance = FigmaEtl(figma_access_token=figmaAccessToken)
            self.etl_instance.execute(fileKeys=selectedFigmaFilesKeys)

    def _getSpaces(self, sourceUrl: str, userNameOnSource: str, apiKey: str) -> None:
        spaces = ConfluenceService(confluenceConfig={
            'url': sourceUrl,
            'username': userNameOnSource,
            'api_key': apiKey,
        }).getSpacesData()
        self.fetched_spaces = spaces
        self.spaces = list(map(lambda space: space.name, spaces))
        self.spaces.append('All')
        st.rerun()

    def _getFigmaFiles(self, figmaAccessToken: str, figmaProjectId: str) -> None:
        files = FigmaService(figmaConfig={
            'access_token': figmaAccessToken,
            'project_id': figmaProjectId,
        }).getFilesData()
        self.fetched_figma_pages = files
        self.figma_pages = list(map(lambda file: file.name, files))
        print(f"Figma pages: {self.figma_pages}")
        st.rerun()

    def _isAiAssistantAvailable(self) -> bool:
        return self.etl_instance != None and len(self.external_data_sources) != 0

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
        elif 'figmaAccessToken' in userData:
            figmaAccessToken = userData['figmaAccessToken']
            selectedFigmaFiles = userData['selectedFigmaFiles']
            return ((figmaAccessToken != '' and figmaAccessToken != None)
                    and (len(selectedFigmaFiles) != 0 and selectedFigmaFiles != None))

    def _isReadyToLoadSpace(self, sourceUrl: str, userNameOnSource: str, apiKey: str) -> bool:
        return ((sourceUrl != '' and sourceUrl != None)
                and (userNameOnSource != '' and userNameOnSource != None)
                and (apiKey != '' and apiKey != None))

    def _isReadyToLoadFigmaFiles(self, figmaAccessToken: str, figmaProjectId: str) -> bool:
        return ((figmaAccessToken != '' and figmaAccessToken != None)
                and (figmaProjectId != '' and figmaProjectId != None))

    def _renderAddExternalSourcesSection(self) -> None:
        possible_sources = ["Confluence", "Sharepoint", "Figma"]
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
            captions=["Data from Confluence spaces", "Data from Sharepoint", "Data from Figma pages"])
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
        # Inputs Figma
        figmaAccessToken = None
        figmaProjectId = None
        loadFigmaFilesBtn = None
        selectedFigmaFiles = None
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
        elif (sourceToLoad == "Figma"):
            self.spaces = []
            figmaProjectId = col2.text_input(
                "Enter the project ID for the source", placeholder="e.g. 123456789")
            figmaAccessToken = col2.text_input(
                "Enter the access token of the source you want to add", placeholder="e.g. QAWehqwj11keu13", type="password")
            selectedFigmaFiles = col2.multiselect(
                "Load files before choosing", options=self.figma_pages)
            loadFigmaFilesBtn = upload_container.button(
                "Load Figma Files", disabled=not self._isReadyToLoadFigmaFiles(figmaAccessToken, figmaProjectId))

        if loadSpacesBtn:
            self._getSpaces(sourceUrl, userNameOnSource, apiKey)
        elif loadFigmaFilesBtn:
            self._getFigmaFiles(figmaAccessToken, figmaProjectId)
        if sourceToLoad == "Confluence":
            dictionaryToPassToSubmitBtn = {
                'sourceUrl': sourceUrl,
                'userNameOnSource': userNameOnSource,
                'apiKey': apiKey,
                'selectedSpaces': selectedSpaces
            }
        elif sourceToLoad == "Sharepoint":
            dictionaryToPassToSubmitBtn = {
                'clientId': clientId,
                'documentLibraryId': documentLibraryId,
                'clientSecret': clientSecret
            }
        elif sourceToLoad == "Figma":
            dictionaryToPassToSubmitBtn = {
                'figmaAccessToken': figmaAccessToken,
                'selectedFigmaFiles': selectedFigmaFiles
            }
        submitBtn = upload_container.button(
            "Add Source", disabled=not self._isReadyToLoadSource(userData=dictionaryToPassToSubmitBtn))
        if submitBtn:
            self._performETL(userData=dictionaryToPassToSubmitBtn,
                             selectedSource=sourceToLoad)
            self._initAiAssistantAndSources(selectedSource=sourceToLoad)

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
