import streamlit as st
import requests
import pandas as pd

# FRONTEND configuration
st.set_page_config(page_title="TFG: Sistema d'Auditoria Telemàtica LLMs", layout="wide")

st.title("Creació d'una arquitectura web per fer consultes concurrents a ChatGpt, DeepSeek i LlaMa")
st.subheader("Plataforma de Monitorització: Auditoria Concurrent i Mode Explotació")

# -SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "telemetry_history" not in st.session_state:
    st.session_state.telemetry_history = []
if "turn_counter" not in st.session_state:
    st.session_state.turn_counter = 0
if "audit_results" not in st.session_state:
    st.session_state.audit_results = None
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

chat_active = len(st.session_state.messages) > 0

# -CACHE with time to live 12 hours
@st.cache_data(show_spinner=False, ttl=43200)
def fetch_telemetric_data(prompt, models_list):
    payload = {"prompt": prompt, "models": models_list}
    response = requests.post("http://127.0.0.1:8000/generate", json=payload)
    response.raise_for_status()
    return response.json()

# -LLMs models
cataleig_models = [
    "Llama 3 (Local - Meta)",
    "DeepSeek Coder (Local)",
    "DeepSeek LLM (Local - General)",
    "DeepSeek Cloud (API Oficial)",
    "ChatGPT-3.5 Turbo (OpenAI)",
    "ChatGPT-4o (OpenAI)",
    "Claude 3.5 Sonnet (Anthropic)",
    "Gemini 1.5 Pro (Google)"
]

# -3 tabs for the interface
tab1, tab2, tab3 = st.tabs([
    "Fase 1: Auditoria Concurrent", 
    "Fase 2: Mode Explotació", 
    "Fase 3: Documentació i Arquitectura"
])

# ==========================================
# TAB 1
# ==========================================
with tab1:
    st.markdown("### Banc de Proves Concurrent")
    if chat_active:
        st.error("**Bloqueig per Seguretat (Prevenció OOM):** Out Of Memory. Hi ha un xat actiu a la Fase 2. Reinicia la sessió i neteja la memòria per poder fer nous Benchmarks.")
    else:
        st.caption("Avaluació comparativa de latències en entorns concurrents.")
    
    with st.container():
        query = st.text_area("Introdueix la consulta:", placeholder="Ex: Explica'm les Antenes YAGI...", disabled=st.session_state.is_processing or chat_active)
        selected_models = st.multiselect("Models:", cataleig_models, default=["Llama 3 (Local - Meta)", "ChatGPT-3.5 Turbo (OpenAI)"], disabled=st.session_state.is_processing or chat_active)

        col_btn, col_unlock = st.columns([1, 3])
        with col_btn:
            enviar = st.button("Realitzar consulta", type="primary", disabled=st.session_state.is_processing or chat_active)
        with col_unlock:
            if st.session_state.is_processing:
                if st.button("Forçar Desbloqueig"):
                    st.session_state.is_processing = False
                    st.rerun()

    st.divider()

    if enviar and query:
        if not selected_models:
            st.warning("Selecciona com a mínim un model.")
        else:
            st.session_state.is_processing = True
            with st.status(f"Iniciant auditoria per a {len(selected_models)} models...", expanded=True) as status:
                st.write("Realitzant les consultes...")
                for model in selected_models:
                    st.write(f"{'[En Local] -' if 'Local' in model else '[Amb Cloud] -'} **{model}**: Preparant inferència...")
                try:
                    st.session_state.audit_results = fetch_telemetric_data(query, selected_models)
                    status.update(label="Completat!", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="Error de xarxa", state="error")
                    st.error(str(e))
            st.session_state.is_processing = False

    if st.session_state.audit_results and not st.session_state.is_processing:
        cols = st.columns(len(st.session_state.audit_results))
        metrics_list = []
        for i, res in enumerate(st.session_state.audit_results):
            with cols[i]:
                st.info(f"**{res['model_name']}**")
                st.write(res['response_text'])
                st.metric("Latència Total", f"{res['latency']} s")
                st.metric("TTFT", f"{res['ttft']} s")
                metrics_list.append({"Model": res['model_name'], "Latència Total (s)": res['latency'], "TTFT (s)": res['ttft'], "Volum (Tokens)": res['token_count']})
        
        df_metrics = pd.DataFrame(metrics_list)
        c1, c2, c3 = st.columns(3)
        with c1: st.bar_chart(df_metrics, x="Model", y="TTFT (s)")
        with c2: st.bar_chart(df_metrics, x="Model", y="Latència Total (s)")
        with c3: st.bar_chart(df_metrics, x="Model", y="Volum (Tokens)")

# ==========================================
# TAB 2
# ==========================================

with tab2:
    st.markdown("### Entorn de Desplegament i Explotació de Model Únic")
    
    if st.session_state.is_processing:
        st.error("**Sistema Bloquejat:** L'arquitectura està processant actualment consultes concurrents massives a la Fase 1. Si us plau, espera que l'auditoria finalitzi per evitar la saturació del bus del sistema.")
    else:
        st.caption("Un cop analitzades les mètriques de la Fase 1, selecciona el model òptim per iniciar una sessió interactiva. L'arquitectura monitoritzarà la degradació del rendiment telemàtic.")

        def dades_reset_callback():
            st.session_state.messages = []
            st.session_state.telemetry_history = []
            st.session_state.turn_counter = 0

        selected_chat_model = st.selectbox(
            "Escull el model d'explotació:", 
            cataleig_models,
            key="selector_model_actiu",
            on_change=dades_reset_callback
        )
        
        if st.button("Reiniciar Sessió i Netejar Memòria"):
            st.session_state.messages = []
            st.session_state.telemetry_history = []
            st.session_state.turn_counter = 0
            st.rerun()

        st.divider()

        c_chat, c_telemetry = st.columns([2, 1])
        
        with c_chat:
            if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
                st.warning("Connexió interrompuda detectada.")
            
            chat_box = st.container(height=500)
            with chat_box:
                for m in st.session_state.messages:
                    with st.chat_message(m["role"]): st.write(m["content"])

            if q := st.chat_input("Envia un missatge..."):
                st.session_state.messages.append({"role": "user", "content": q})
                st.session_state.turn_counter += 1
                with chat_box:
                    with st.chat_message("user"): st.write(q)
                    with st.chat_message("assistant"):
                        try:
                            response = requests.post("http://127.0.0.1:8000/generate", json={"prompt": q, "models": [selected_chat_model]})
                            response.raise_for_status()
                            r = response.json()[0]
                            
                            st.write(r["response_text"])
                            st.session_state.messages.append({"role": "assistant", "content": r["response_text"]})
                            st.session_state.telemetry_history.append({"Torn": f"T {st.session_state.turn_counter}", "Latència Total (s)": r["latency"], "TTFT (s)": r["ttft"]})
                            st.rerun()
                            
                        except Exception as e:
                            # Let's see the error Timeout (codi 500/504)
                            st.error(f"Error de connexió amb el servidor: {e}")
                            
                            if st.session_state.messages[-1]["role"] == "user":
                                st.session_state.messages.pop()
                                st.session_state.turn_counter -= 1
        with c_telemetry:
            if st.session_state.telemetry_history:
                st.line_chart(pd.DataFrame(st.session_state.telemetry_history), x="Torn", y=["Latència Total (s)", "TTFT (s)"])

# ==========================================
# TAB 3
# ==========================================
with tab3:
    st.markdown("## Detalls Tècnics de la Infraestructura")
    
    # 1. Informació del Projecte
    col1, col2 = st.columns(2)
    with col1:
        st.info("### Autor i Projecte")
        st.write("**Estudiant:** Freddy Joel Torres Cabrera")
        st.write("**Titulació:** Grau en Enginyeria de Sistemes de Telecomunicació (GRE ENG SIS TELECOMUN)")
        st.write("**Universitat:** UPC - EETAC (Escola d'Enginyeria de Telecomunicació i Aeroespacial de Castelldefels)")
        st.write("**Tutora i Supervisora:** Dolors Royo Vallés")
    
    with col2:
        st.success("### Versió del Programari")
        st.write("**Versió Actual:** 3.1.0 (Release Candidate)")
        st.write("**Estat:** Prototip d'auditoria funcional")
        st.write("**Data de l'última compilació:** Juny 2026")

    st.divider()

    # Diagram of the architecture
    st.markdown("### Diagrama de l'Arquitectura Telemàtica Concurrent")
    st.caption("Aquest diagrama professional representa el flux de dades asíncron, dividint la infraestructura en topologies locals (Edge) i externes (Cloud) i mostrant com s'extrauen les mètriques telemàtiques.")
    st.image('arquitectura.png', use_container_width=True)
    
    st.divider()

    # Stack technology used 
    st.markdown("### Stack Tecnològic Utilitzat")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**Llenguatge**")
        st.code("Python 3.10+")
    with c2:
        st.markdown("**Backend Asíncron**")
        st.code("FastAPI / AsyncIO")
    with c3:
        st.markdown("**Interfície d'Usuari**")
        st.code("Streamlit")
    with c4:
        st.markdown("**Clients de Xarxa**")
        st.code("HTTPX (Streaming)")

    st.divider()

    # 4. Explication of the TTFT metric
    st.markdown("### Mesura de la Mètrica TTFT (Time To First Token)")
    st.write("""
    Aquesta arquitectura utilitza una lectura de flux de dades (*streaming*) per detectar el moment exacte en què arriba el primer paquet de dades útil. 
    A nivell telemàtic, el **TTFT** es calcula com:
    """)
    st.latex(r"TTFT = T_{primer\_paquet} - T_{enviament\_peticio}")
    st.write("""
    Aquesta mètrica és fonamental per diferenciar la latència de xarxa (Cloud) de la latència de càrrega de models a la memòria VRAM (Edge).
    """)