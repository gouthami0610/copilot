import streamlit as st
import requests

mathmark = st.number_input("Enter math marks")
scimark = st.number_input("Enter sci marks")
engmark = st.number_input("Enter eng marks")
marks = [mathmark, scimark, engmark]

if st.button("Predict result"):
    response = requests.post("http://localhost:8000/predict", json={"marks": marks})
    if response.status_code == 200:
        result = response.json().get("prediction")
        if result == 1:
            st.success("Passed")
        else:
            st.error("Fail")
    else:
        st.error(f"API returned status code {response.status_code}")
