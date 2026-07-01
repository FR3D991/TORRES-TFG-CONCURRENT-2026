# LIBRARIES, THIRD-PARTY FRAMEWORKS AND TOOLS
import streamlit as st
import requests
import pandas as pd
import time

# FRONTEND configuration
st.set_page_config(page_title="TFG: Sistema d'Avaluació Telemàtica LLMs", layout="wide")

st.title("Creació d'una arquitectura web per fer consultes concurrents a la família GPT, DeepSeek i LlaMa")
st.subheader("Plataforma de Monitorització: Avaluació Concurrent i Mode Explotació")

# SESSION STATE
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

# CACHE with time to live 12 hours
@st.cache_data(show_spinner=False, ttl=43200)
def fetch_telemetric_data(prompt, models_list):
    payload = {"prompt": prompt, "models": models_list}
    response = requests.post("http://127.0.0.1:8000/generate", json=payload)
    response.raise_for_status()
    return response.json()


# LLMs models
cataleig_models = [
    # Locals
    "[LOCAL] Llama 3 (Meta)",
    "[LOCAL] DeepSeek Coder",
    "[LOCAL] DeepSeek LLM",
    # PAYMENT CLOUD MODELS
    "[CLOUD-PRO] ChatGPT-3.5 Turbo (OpenAI)",
    "[CLOUD-PRO] DeepSeek (API Oficial)",
    # FREE CLOUD MODELS
    "[CLOUD-FREE] Owl Alpha (OpenRouter)",
    "[CLOUD-NVIDIA] Llama 3.1 8B (NIM)",
]

# 3 tabs for the interface
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
        st.caption("Realitzem auditoria concurrent a diferents models depenent si es tracta d'una versió local o en núvol.")
    
    with st.container():
        query = st.text_area("Introdueix la consulta:", placeholder="Ex: Explica'm les Antenes YAGI...", disabled=st.session_state.is_processing or chat_active)
        
        selected_models = st.multiselect(
            "Models:", 
            cataleig_models, 
            default=["[LOCAL] Llama 3 (Meta)", "[CLOUD-PRO] ChatGPT-3.5 Turbo (OpenAI)", "[CLOUD-FREE] Owl Alpha (OpenRouter)"], 
            disabled=st.session_state.is_processing or chat_active
        )

        col_btn, col_unlock = st.columns([1, 3])
        with col_btn:
            enviar = st.button("Realitzar consulta", type="primary", disabled=st.session_state.is_processing or chat_active)
        with col_unlock:
            if st.session_state.is_processing:
                if st.button("Forçar Desbloqueig"):
                    st.session_state.is_processing = False
                    st.rerun()

    st.divider()

    # Error handling and telemetry results
    if enviar:

        if not query.strip():
            st.warning(" Si us plau, introdueix una consulta a la caixa de text abans d'enviar.")
            
        elif not selected_models:
            st.warning(" Selecciona com a mínim un model del catàleg.")
            
        else:
            st.session_state.is_processing = True
            with st.status(f"Iniciant auditoria per a {len(selected_models)} models...", expanded=True) as status:
                st.write("Realitzant les consultes...")
                for model in selected_models:
                    st.write(f"{'[Local] -' if 'Local' in model else '[Cloud] -'} **{model}**: Preparant inferència...")
                
                import time 
                try:
                    start_ui_time = time.time()
                    
                    st.session_state.audit_results = fetch_telemetric_data(query, selected_models)
                    
                    total_ui_time = time.time() - start_ui_time
                    
                    if total_ui_time < 0.5:
                        missatge = f" RECUPERAT DEL CACHÉ ({total_ui_time:.3f} s). Has estalviat processament!"
                        status.update(label=missatge, state="complete", expanded=False)
                        st.success("**Sostenibilitat Activada:** Aquesta consulta ja s'havia fet. S'ha recuperat la dada de la memòria cau sense gastar recursos computacionals.")
                    else:
                        missatge = f"Completat (Petició real a xarxa: {total_ui_time:.3f} s)"
                        status.update(label=missatge, state="complete", expanded=False)
                        
                except Exception as e:
                    status.update(label="Error de xarxa", state="error")
                    st.error(str(e))

            st.session_state.is_processing = False

    # Display telemetry results if available
    if st.session_state.audit_results and not st.session_state.is_processing:
        cols = st.columns(len(st.session_state.audit_results))
        metrics_list = []
        for i, res in enumerate(st.session_state.audit_results):
            with cols[i]:
                st.info(f"**{res['model_name']}**")
                st.write(res['response_text'])
                st.metric("Latència Total", f"{res['latency']} s")
                st.metric("TTFT", f"{res['ttft']} s")
                st.metric("Volum (Tokens)", f"{res['token_count']}")
                
                nom_grafica = res['model_name'].split("]")[-1].strip()

                metrics_list.append({
                    "Model": nom_grafica, 
                    "Latència Total (s)": res['latency'], 
                    "TTFT (s)": res['ttft'], 
                    "Volum (Tokens)": res['token_count']
                })
        
        st.divider()
        st.subheader("Anàlisi Comparativa del Rendiment Telemàtic")
        df_metrics = pd.DataFrame(metrics_list)
        
        tab_ttft, tab_lat, tab_vol = st.tabs([
            " Temps de Retard (TTFT)", 
            " Latència Total", 
            " Volum de Tokens"
        ])
        
        with tab_ttft:
            st.markdown("**Mètrica:** Temps d'establiment i primera resposta útil.")
            st.bar_chart(df_metrics, x="Model", y="TTFT (s)", height=400)
            
        with tab_lat:
            st.markdown("**Mètrica:** Temps total de la transacció telemàtica.")
            st.bar_chart(df_metrics, x="Model", y="Latència Total (s)", height=400)
            
        with tab_vol:
            st.markdown("**Mètrica:** Càrrega útil processada (Payload).")
            st.bar_chart(df_metrics, x="Model", y="Volum (Tokens)", height=400)

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
            dades_reset_callback()
            st.rerun()

        st.divider()

        c_chat, c_telemetry = st.columns([2, 1])
        
        with c_chat:
            chat_box = st.container(height=500)
            
            with chat_box:
                for m in st.session_state.messages:
                    with st.chat_message(m["role"]): 
                        st.write(m["content"])

            if prompt := st.chat_input("Envia un missatge..."):
                
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_box:
                    with st.chat_message("user"):
                        st.write(prompt)
                    
                    with st.chat_message("assistant"):
                        with st.spinner("L'IA està pensant la resposta..."):
                            try:
                                response = requests.post(
                                    "http://127.0.0.1:8000/generate", 
                                    json={"prompt": prompt, "models": [selected_chat_model]}
                                )
                                response.raise_for_status()
                                dades = response.json()
                                
                                text_resposta = dades[0]["response_text"]
                                latency = dades[0].get("latency", 0.0)
                                ttft = dades[0].get("ttft", 0.0)
                                
                                st.write(text_resposta)
                                
                                st.session_state.messages.append({"role": "assistant", "content": text_resposta})
                                
                                st.session_state.turn_counter += 1
                                st.session_state.telemetry_history.append({
                                    "Torn": f"Torn {st.session_state.turn_counter}",
                                    "Latència Total (s)": latency,
                                    "TTFT (s)": ttft
                                })
                                
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error de connexió: {e}")
                                if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                                    st.session_state.messages.pop()

        with c_telemetry:
            st.markdown("#### Monitoratge Telemàtic")
            if st.session_state.telemetry_history:
                df_telemetry = pd.DataFrame(st.session_state.telemetry_history)
                st.line_chart(df_telemetry, x="Torn", y=["Latència Total (s)", "TTFT (s)"])
            else:
                st.info("Envía missatges al xat per començar a registrar i monitoritzar la degradació de les mètriques en temps real.")

# ==========================================
# TAB 3
# ==========================================
with tab3:
    st.markdown("## Documentació i Arquitectura del TFG")
    
    # 1. Project Information
    col1, col2 = st.columns(2)
    with col1:
        st.info("### Autor i Projecte")
        st.write("**Estudiant:** Freddy Joel Torres Cabrera")
        st.write("**Titulació:** Grau en Enginyeria de Sistemes de Telecomunicació (GRE ENG SIS TELECOMUN)")
        st.write("**Universitat:** UPC - EETAC (Castelldefels)")
        st.write("**Tutora:** Dolors Royo Vallés")
    
    with col2:
        st.success("### Versió del Programari")
        st.write("**Versió Actual:** 3.1.1 (Release Candidate)")
        st.write("**Estat:** Prototip d'auditoria telemàtica")
        st.write("**Data de l'última compilació:** Juny 2026")

    st.divider()

    # 2. Objectives
    st.markdown("### Context: La Desfragmentació dels LLMs")
    st.write("""
    Actualment, l'ecosistema de la Intel·ligència Artificial pateix una forta **fragmentació**. Existeixen desenes de proveïdors (OpenAI, Meta, Google, DeepSeek) amb formats d'API, temps de resposta i estructures de dades totalment diferents. Aquesta arquitectura neix per donar solució a aquesta desfragmentació, creant una capa d'abstracció unificada que permet interactuar amb qualsevol model sota un mateix estàndard.
    """)

    st.markdown("#### Objectius Específics del Projecte")
    st.markdown("""
    * **Backend Asíncron:** Dissenyar i implementar una arquitectura utilitzant el framework FastAPI per evitar el bloqueig del fil d'execució (*I/O Bound*).
    * **Integració Interoperable:** Connectar les APIs de tres proveïdors representatius del mercat sota un mateix orquestrador.
    * **Interfície Analítica:** Desenvolupar un *frontend* interactiu que permeti visualitzar mètriques clau com el TTFT i la latència total en temps real.
    * **Benchmarking Comparatiu:** Avaluar l'eficiència computacional i de xarxa de cada model sota les mateixes condicions d'estrès telemàtic.
    * **Escalabilitat Modular:** Fer l'arquitectura escalable de forma que sigui tècnicament àgil i senzill afegir noves APIs o models locals en el futur.
    """)

    st.divider()

   # 3. Architecture Diagram
    st.markdown("### Diagrama de l'Arquitectura Telemàtica")
    st.caption("Aquest diagrama professional representa el flux de dades asíncron, dividint la infraestructura en topologies locals (Edge) i externes (Cloud) i mostrant com s'extrauen les mètriques telemàtiques.")
    
    try:
        st.image('arquitectura.svg', use_container_width=True)
    except:
        st.warning("El fitxer 'arquitectura.svg' no s'ha trobat al directori de treball.")
    
    st.markdown("#### Descripció del Flux de Dades (Pas a Pas)")
    st.write("""
    L'arquitectura opera mitjançant un cicle de vida altament optimitzat per a la concurrència i la telemetria:
    
    * **1. Petició Inicial:** El client (Streamlit) envia el *prompt* i la llista de models desitjats en format JSON cap al *Gateway* de l'orquestrador FastAPI.
    * **2 i 3. Estratègia de Sostenibilitat (Caché):** Abans d'establir connexions de xarxa, el sistema valida la consulta contra la Memòria Cau. Si hi ha un *Hit* (3a), es recuperen les dades instantàniament, aconseguint un estalvi energètic i computacional del 100%. Si és un *Miss* (3b), la petició avança cap a l'enrutador.
    * **4. Enrutament Asíncron (Streaming):** FastAPI, evitant el bloqueig del fil d'execució (*I/O bound*), distribueix les peticions en paral·lel. S'ataquen tant nodes **Edge** (execució local on-premise sense dependència externa) com nodes **Cloud** (diferenciant entre APIs comercials estables i passarel·les gratuïtes de rendiment variable).
    * **5. Retorn i Monitoratge:** A mesura que els models retornen la informació (*HTTP Streaming*), el Gestor de Mètriques del backend intercepta els paquets per calcular el **TTFT** (capturant el *timestamp* del primer token) i acumula la càrrega per mesurar la latència total.
    * **6 i 7. Consolidació:** Finalment, l'orquestrador actualitza la memòria cau amb els nous resultats i emet un JSON unificat cap al Frontend, permetent la visualització simultània de les respostes de llenguatge natural i les gràfiques de degradació telemàtica.
    """)

    # 4. Technology Stack and Libraries
    st.markdown("### Stack Tecnològic i Llibreries")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Frontend (Client)**")
        st.code("""
- Streamlit (UI Framework)
- Pandas (Estructuració de dades)
- Requests (Peticions HTTP síncrones)
- Time (Cronometratge de UX)
        """)
    with c2:
        st.markdown("**Backend (Orquestrador)**")
        st.code("""
- FastAPI (Framework REST asíncron)
- HTTPX (Streaming asíncron de xarxa)
- AsyncIO (Gestió de concurrència)
- Uvicorn (Servidor ASGI)
        """)
    with c3:
        st.markdown("**Dades i Seguretat**")
        st.code("""
- Pydantic (Validació de models de dades)
- Json (Parseig de paquets de xarxa)
- Python-dotenv (Gestió de variables d'entorn)
        """)

    st.divider()

    # 5. Telemetry Metrics
    st.markdown("### Monitoratge de Mètriques Telemàtiques")
    st.write("La plataforma llegeix el flux de dades (*streaming*) per avaluar tres paràmetres crítics de rendiment xarxa/còmput:")
    
    col_met1, col_met2, col_met3 = st.columns(3)
    with col_met1:
        st.markdown("**1. TTFT (Time To First Token)**")
        st.write("Temps fins a rebre el primer paquet útil. Ajuda a diferenciar la latència de xarxa de l'establiment de connexió.")
        st.latex(r"TTFT = T_{primer\_paquet} - T_{enviament\_peticio}")
    
    with col_met2:
        st.markdown("**2. Latència Total**")
        st.write("Temps des de l'emissió del *prompt* fins al tancament de la connexió TCP/flux de dades.")
        st.latex(r"Lat\grave{e}ncia_{Total} = T_{final} - T_{enviament\_peticio}")

    with col_met3:
        st.markdown("**3. Volum de Càrrega (Tokens)**")
        st.write("Mida del *Payload* (càrrega útil) rebut. Clau per calcular el *Throughput* (tokens/segon).")

    st.divider()

    # 6. Sostenibility and Green Computing
    st.markdown("### Sostenibilitat i Eficiència Computacional (Green Computing)")
    st.success("**Estratègia de Memoization (Caché Temporal)**")
    st.write("""
    L'execució de models generatius suposa un alt consum energètic. Per minimitzar la petjada de carboni i optimitzar l'ús de xarxa, aquesta plataforma integra un **patró de memòria cau (Caché)**.
    
    Mitjançant la detecció de patrons recurrents (*Time To Live* de 12 hores), l'arquitectura intercepta consultes idèntiques. Quan s'identifica una redundància, el sistema denega la petició externa i retorna els resultats des de la memòria RAM local. Aquest *Zero-Compute Response* suposa un estalvi del 100% en ample de banda i consum computacional.
    """)
    
    with st.expander("Línies futures d'investigació i escalabilitat"):
        st.markdown("""
        L'arquitectura actual estableix una base sòlida per a la inferència de text, però el seu disseny modular permet plantejar les següents evolucions tecnològiques:
        
        * **Caché Semàntic i Sostenibilitat:** Implementació d'un enrutador basat en bases de dades vectorials per avaluar la intenció del missatge, reduint el consum energètic en consultes parafrasejades (actuant com un 'Jutge IA').
        * **Integració RAG (Retrieval-Augmented Generation):** Ampliació del *payload* per admetre la ingesta d'arxius pesats (ex: conjunts de dades `.csv`, *logs* de xarxa o bases de codi completes). El sistema vectoritzaria aquests documents per permetre a l'IA auditar infraestructures o revisar codi de manera contextual sense saturar la finestra de tokens.
        * **Analítica Avançada i Big Data:** Aplicació d'algorismes de *Machine Learning* clàssic (com KNN o *clustering*) sobre les dades telemàtiques recollides, permetent fer anàlisi predictiva, detecció d'anomalies i classificació d'esdeveniments en entorns d'alta disponibilitat.
        """)