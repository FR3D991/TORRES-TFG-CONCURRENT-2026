import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="TFG: Comparador LLMs", layout="wide")

st.title("Arquitectura de Consultes Concurrents a Intel·ligències Artificials")
st.subheader("Avaluació de rendiment: ChatGPT vs DeepSeek vs Llama")
st.subheader("Versió: 0.2.0 // Fet per Freddy Joel Torres Cabrera")

# CACHE CONFIGURATION
@st.cache_data(show_spinner=False)
def fetch_llm_responses(prompt, selected_models):
    payload = {"prompt": prompt, "models": selected_models}
    response = requests.post("http://127.0.0.1:8000/generate", json=payload)
    response.raise_for_status()
    return response.json()

# INPUT & MODEL SELECTION
if "custom_models" not in st.session_state:
    st.session_state.custom_models = [] #Innitialitzation of the memory if it does not exist

with st.container():
    query = st.text_area("Introdueix la consulta per als models:", placeholder="Ex: Explica'm les característiques d'una antena YAGI...")
    
    # NEW system to input new models
    col_input, col_add = st.columns([3, 1])
    with col_input:
        new_model = st.text_input("Vols testejar un altre model? (Es simularà automàticament)", placeholder="Ex: Claude 3.5, Gemini...")
    with col_add:
        st.write("") 
        st.write("")
        if st.button("Afegir Model a la llista"):
            if new_model and new_model not in st.session_state.custom_models and new_model not in ["ChatGPT", "DeepSeek", "Llama3"]:
                st.session_state.custom_models.append(new_model)
                st.rerun()

    available_models = ["ChatGPT", "DeepSeek", "Llama3"] + st.session_state.custom_models
    selected_models = st.multiselect("Selecciona els models a consultar:", available_models, default=available_models)

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        enviar = st.button("Fer Consulta Principal", type="primary")

st.divider()

# COMMUNICATION
if enviar and query:
    if not selected_models:
        st.warning("Si us plau, selecciona com a mínim un model.")
    else:
        with st.spinner("Sol·licitant respostes en paral·lel..."):
            try:
                # The function is cached. If the prompt and models are identical to a previous run, it loads instantly.
                resultados = fetch_llm_responses(query, selected_models)

                cols = st.columns(len(resultados))
                chart_data = []

                for i, res in enumerate(resultados):
                    with cols[i]:
                        st.info(f"**{res['model_name']}**")
                        st.write(res['response_text'])
                        st.metric("Latència", f"{res['latency']} s")

                        chart_data.append({
                            "Model": res['model_name'],
                            "Latència (s)": res['latency']
                        })
                
                st.divider()
                st.subheader("Comparativa de Latència (t_res)")
                df = pd.DataFrame(chart_data)
                st.bar_chart(df, x="Model", y="Latència (s)")

            except Exception as e:
                st.error(f"Error de connexió amb el backend: {e}")
elif enviar:
    st.warning("Si us plau, escriu una consulta primer.")