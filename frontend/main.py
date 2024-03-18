import streamlit as st
import time
import threading
# from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# https://discuss.streamlit.io/t/concurrency-with-streamlit/29500/6
# https://discuss.streamlit.io/t/does-streamlit-is-running-on-a-single-threaded-development-server-by-default-or-not/9898
# https://gist.github.com/tvst/fa33b9dcb58040cbcb0ea376146d4e8c


class App:
    def __init__(self):
        self.models = ["Mistral", "Llama2", "GPT 3.5"]
        # self.external_data_sources = ["Confluence", "Sharepoint"]
        self.external_data_sources = []
        self.query = ""
        self.model = None
        self.data_source = None
        self.processingSource = False

    def _processSourceUpload(self, source):
        self.processingSource = True

    def _renderAddExternalSourcesSection(self):
        possible_sources = ["Confluence", "Sharepoint"]
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
            self._processSourceUpload(sourceToLoad)
        if (self.processingSource is True):
            placeholder.empty()
            return

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
        with st.form('my_form'):
            text = st.text_area('Enter your question:', '')
            submitted = st.form_submit_button(
                'Submit', disabled=len(self.external_data_sources) == 0)
            if submitted:
                self.query = text
                self.submit()

    def submit(self):
        pass

    @property
    def selected_values_and_query(self):
        return self.model, self.data_source, self.query
