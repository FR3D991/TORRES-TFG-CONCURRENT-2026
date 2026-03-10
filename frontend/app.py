#LIBRARIES, THIRD-PARTY FRAMEWORKS AND TOOLS
import streamlit as st
import requests
import pandas as pan

#Interface configuration
st.set_page_config(page_title="TFG: Comparador LLMs", layout="wide")

st.title("Arquitecura de Consultas Concurrentes a Inteligencias Artificiales")
st.subheader("Evaluación de rendimiento: ChatGPT vs DeepSeek vs Llama")
st.subheader("Versión: 0.1.0 // Hecho por Freddy Torres Cabrera")

#INPUT 
with st.container():
    query = st.text_area("Introduzca la consulta para los modelos:", placeholder="Ej: Explica las caracteristicas de una antena YAGI...")

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        enviar = st.button("Realizar Consulta", type="primary")

st.divider()
