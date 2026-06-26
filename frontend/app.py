import streamlit as st
import requests
import pandas as pd

# FRONTEND configuration
st.set_page_config(page_title="TFG: Sistema d'Auditoria Telemàtica LLMs", layout="wide")

st.title("Arquitectura de Consultes Concurrents a Intel·ligències Artificials")
st.subheader("Plataforma de Monitorització: Auditoria Concurrent i Mode Explotació")
st.subheader("Versió: 1.0.0 // Desenvolupat per Freddy Joel Torres Cabrera")

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "telemetry_history" not in st.session_state:
    st.session_state.telemetry_history = []
if "turn_counter" not in st.session_state:
    st.session_state.turn_counter = 0

# CACHE with time to live 12 hours
@st.cache_data(show_spinner=False, ttl=43200)
def fetch_telemetric_data(prompt, models_list):
    payload = {"prompt": prompt, "models": models_list}
    response = requests.post("http://127.0.0.1:8000/generate", json=payload)
    response.raise_for_status()
    return response.json()

# LLMs models
cataleig_models = [
    "Llama 3 (Local - Meta)",
    "DeepSeek Coder (Local)",
    "ChatGPT-3.5 Turbo (OpenAI)",
    "ChatGPT-4o (OpenAI)",
    "Claude 3.5 Sonnet (Anthropic)",
    "Gemini 1.5 Pro (Google)"
]

# Differents tabs
tab1, tab2 = st.tabs(["Fase 1: Auditoria Concurrent (Benchmarks)", "Fase 2: Mode Explotació (Xat en Viu i Monitorització de mètriques)"])

# TAB 1: ASYNC auditory
with tab1:
    st.markdown("### Banc de Proves")
    st.caption("Aquesta fase permet llançar consultes massives en paral·lel per avaluar de manera comparativa els temps de resposta de diferents LLMs (evaluar diferents tipologies).")
    
    with st.container():
        query = st.text_area(
            "Introdueix la consulta:", 
            placeholder="Ex: Explica'm les caràcteristiques de les antenes YAGI...",
            key="audit_query"
        )
        
        selected_models = st.multiselect(
            "Selecciona els models:",
            cataleig_models,
            default=["Llama 3 (Local - Meta)", "ChatGPT-3.5 Turbo (OpenAI)", "DeepSeek Coder (Local)"],
            key="audit_models"
        )

        col_btn, _ = st.columns([1, 3])
        with col_btn:
            enviar = st.button("Realitzar consulta", type="primary")

    st.divider()

    if enviar and query:
        if not selected_models:
            st.warning("Si us plau, selecciona com a mínim un model de la llista per poder realitzar la comparativa.")
        else:
            with st.spinner("Relitzant consulta als diferents LLMs i messurant les seves mètriques..."):
                try:
                    resultados = fetch_telemetric_data(query, selected_models)
                    cols = st.columns(len(resultados))
                    metrics_list = []

                    for i, res in enumerate(resultados):
                        with cols[i]:
                            st.info(f"**{res['model_name']}**")
                            st.write(res['response_text'])
                            st.metric("Latència Total", f"{res['latency']} s")
                            st.metric("Time To First Token (TTFT)", f"{res['ttft']} s")
                            st.caption(f"Volum: {res['token_count']} tokens processats")

                            metrics_list.append({
                                "Model": res['model_name'],
                                "Latència Total (s)": res['latency'],
                                "TTFT (s)": res['ttft']
                            })
                    
                    st.divider()
                    st.subheader("Anàlisi Comparativa del Rendiment Telemàtic")
                    df_metrics = pd.DataFrame(metrics_list)
                    
                    col_graph1, col_graph2 = st.columns(2)
                    with col_graph1:
                        st.markdown("**Temps de Retard fins al Primer Token (TTFT)**")
                        st.bar_chart(df_metrics, x="Model", y="TTFT (s)")
                    with col_graph2:
                        st.markdown("**Temps de Resposta de la Latència Total**")
                        st.bar_chart(df_metrics, x="Model", y="Latència Total (s)")

                except Exception as e:
                    st.error(f"Error crític en establir connexió amb la infraestructura del backend: {e}")
    elif enviar:
        st.warning("El camp de text no pot estar buit. Si us plau, redacta una consulta telemàtica vàlida.")

# TAB 2: Real-time chat
with tab2:
    st.markdown("### Entorn de Desplegament i Explotació de Model Únic")
    st.caption("Un cop analitzades les mètriques de la Fase 1, selecciona el model òptim per iniciar una sessió interactiva. L'arquitectura monitoritzarà la degradació del rendiment telemàtic a mesura que creix el context de la conversa.")

    selected_chat_model = st.selectbox("Escull el model:", cataleig_models)
    
    if st.button("Reiniciar Sessió"):
        st.session_state.messages = []
        st.session_state.telemetry_history = []
        st.session_state.turn_counter = 0
        st.rerun()

    st.divider()

    col_chat, col_telemetry = st.columns([2, 1])

    with col_chat:
        st.markdown("#### Canals de Comunicació (Xat)")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if chat_query := st.chat_input("Envia un missatge..."):
            
            with st.chat_message("user"):
                st.write(chat_query)
            st.session_state.messages.append({"role": "user", "content": chat_query})
            st.session_state.turn_counter += 1

            with st.chat_message("assistant"):
                with st.spinner("Preguntant al model..."):
                    try:
                        payload = {"prompt": chat_query, "models": [selected_chat_model]}
                        response = requests.post("http://127.0.0.1:8000/generate", json=payload)
                        response.raise_for_status()
                        backend_data = response.json()[0] # Agafem l'únic model sol·licitat

                        st.write(backend_data["response_text"])
                        st.session_state.messages.append({"role": "assistant", "content": backend_data["response_text"]})

                        st.session_state.telemetry_history.append({
                            "Torn": f"Torn {st.session_state.turn_counter}",
                            "Latència Total (s)": backend_data["latency"],
                            "TTFT (s)": backend_data["ttft"]
                        })
                        
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error de xarxa en el canal d'explotació: {e}")

    with col_telemetry:
        st.markdown("#### Monitorització de la Red en Temps Real")
        st.caption("Evolució temporal del comportament dels paquets segons el volum històric de la conversa.")
        
        if st.session_state.telemetry_history:
            df_history = pd.DataFrame(st.session_state.telemetry_history)
            
            st.markdown("**Evolució de les Latències del Canal ($t_{res}$ i $TTFT$)**")
            st.line_chart(df_history, x="Torn", y=["Latència Total (s)", "TTFT (s)"])
            
            last_metric = st.session_state.telemetry_history[-1]
            st.metric("Última Latència Registrada", f"{last_metric['Latència Total (s)']} s")
            st.metric("Últim TTFT Registrat", f"{last_metric['TTFT (s)']} s")
        else:
            st.info("Inicia la comunicació al xat per començar a capturar telemetria del canal de transmissió.")