import streamlit as st
import time
import threading
# from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# https://discuss.streamlit.io/t/concurrency-with-streamlit/29500/6
# https://discuss.streamlit.io/t/does-streamlit-is-running-on-a-single-threaded-development-server-by-default-or-not/9898
# https://gist.github.com/tvst/fa33b9dcb58040cbcb0ea376146d4e8c
# nicegui 
# Shiny


class App:
    def __init__(self):
        self.models = ["Mistral", "Llama2", "GPT 3.5"]
        # self.external_data_sources = ["Confluence", "Sharepoint"]
        self.external_data_sources = []
        self.query = ""
        self.model = None
        self.data_source = None
        self.processingSource = False

    def _renderAddExternalSourcesSection(self):
        possible_sources = ["Confluence", "Sharepoint"]
        sourceToLoad = None
        if (len(self.external_data_sources) == 0):
            st.warning(
                "Add External Sources. You have no external sources to query from.")
        placeholder = st.empty()
        expander = placeholder.expander("Add External Sources")
        upload_form = expander.form('upload_form', border=False)
        sourceToLoad = upload_form.radio(
            "Here from where you can add sources:",
            [item for item in possible_sources if item not in self.external_data_sources],
            captions=["Data from Confluence spaces", "Data from Sharepoint"])
        submitBtn = upload_form.form_submit_button("Add Source")
        if submitBtn:
            self.processingSource = True
        if (self.processingSource is True):
            if (len(self.external_data_sources) == len(possible_sources)):
                placeholder.empty()
            with st.spinner(f"Processing {sourceToLoad} data..."):
                self.external_data_sources.append(sourceToLoad)
                self.processingSource = False
                st.rerun()

    def render(self):
        if len(self.external_data_sources) != 2:
            self._renderAddExternalSourcesSection()
        col1, col2 = st.columns(2)
        self.model = col1.selectbox("Choose a model", self.models)
        self.data_source = col2.selectbox(
            "Choose a data source", self.external_data_sources)
        st.title(
            f"Test {self.model} LLM on your own data from {self.data_source}!")
        st.write(
            f'Select a model and start chatting. To test the model against your own data, insert a url or upload a document.')
        prompt = st.chat_input(placeholder='Enter your question:')
        chatContainer = st.container()
        st.markdown('''
            <style>
                [data-testid="element-container"] + [data-testid=stVerticalBlockBorderWrapper] > div > [data-testid="stVerticalBlock"] {
                    max-height: 650px !important;
                    overflow-y: auto !important;
                }
            </style>''', unsafe_allow_html=True)
        if prompt:
            self.query = prompt
            self.submit(chatContainer)

    def submit(self, chatContainer):
        with chatContainer:
            with st.chat_message("user"):
                st.write("Hello 👋")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")
            with st.chat_message("ai"):
                st.write("Hello 👋 back!")

    @property
    def selected_values_and_query(self):
        return self.model, self.data_source, self.query
