import streamlit as st
from frontend.main import App

if "my_instance" not in st.session_state:
  st.session_state.my_instance = App()
st.session_state.my_instance.render()
