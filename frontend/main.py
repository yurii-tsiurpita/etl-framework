import streamlit as st

class App:
    def __init__(self):
        self.models = ["Mistral", "Llama2", "GPT 3.5"]
        self.external_data_sources = ["Confluence", "Sharepoint"]
        self.models = ["Mistral", "Llama2", "GPT 3.5"]
        self.external_data_sources = ["Confluence", "Sharepoint"]
        self.query = ""
        self.model = None
        self.data_source = None

    def render(self):
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
            submitted = st.form_submit_button('Submit')
            if submitted:
                self.query = text
                self.submit()

    def submit(self):
        pass

    @property
    def selected_values_and_query(self):
        return self.model, self.data_source, self.query
