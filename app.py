import streamlit as st

file = st.file_uploader(label='master')

if file:
  if st.button("Save"):
    st.write('ok')
