#LIBRARIES, THIRD-PARTY FRAMEWORKS AND TOOLS
import streamlit as st
import requests
import pandas as pan

#Interface configuration
st.set_page_config(page_title="TFG: Comparador LLMs", layout="wide")

st.title("Arquitecura de Consultas Concurrents a Inteligencias Artificials")
st.subheader("Evaluació de rendiment: ChatGPT vs DeepSeek vs Llama")
st.subheader("Versió: 0.1.0 // Fet per Freddy Joel Torres Cabrera")

#INPUT 
with st.container():
    query = st.text_area("Introdueix la consulta per als models:", placeholder="Ej: Explica'm les caracteristiques d'una antena YAGI...")

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        enviar = st.button("Fer Consulta", type="primary")

st.divider()

#Communication
if enviar and query:
    with st.spinner("Solicitant respostes en paral·lel..."):
        try:
            payload = {"prompt": query, "models": ["ChatGPT", "DeepSeek", "Llama3"]} #Preparation: Define the data packs (JSON)
            response = requests.post("http://127.0.0.1:8000/generate", json=payload) #Petition: Send a POST to the Backend (port 8000)

            if response.status_code==200:
                resultados=response.json()

                cols = st.columns(len(resultados)) #Visualization: Create columns to compare the results

                chart_data = [] #Graphic

                for i, res in enumerate(resultados):
                    with cols[i]:
                        st.info(f"**{res['model_name']}**")
                        st.write(res['response_text'])

                        st.metric("Latencia", f"{res['latency']}s")

                        chart_data.append({
                            "Model": res['model_name'],
                            "Latencia (s)": res['latency']
                        })
                
                st.divider() #Graphic: Time response comparation
                st.subheader("Comparativa de Latencia ($t_{res}$)")
                df = pan.DataFrame(chart_data)
                st.bar_chart(df, x="Model", y="Latencia (s)")

            else:
                st.error(f"Error en el servidor: {response.status_code}")
        except Exception as e:
            st.error(f"No s'ha pogut connectar amb el backend: {e}")
elif enviar:
    st.warning("Sis plau, escriu una consulta primer.")

