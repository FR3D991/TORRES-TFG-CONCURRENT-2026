# Creació d'una arquitectura web per fer consultes concurrents a ChatGpt, DeepSeek i LlaMa

**Grau en Enginyeria Sistemes de Telecomunicació (EETAC - UPC)**

---

## Introducció
Aquest projecte neix de la necessitat d'optimitzar la interacció amb diversos Large Language Models (LLMs) de forma simultània. L'objectiu és dissenyar i implementar una arquitectura web capaç de gestionar consultes concurrents, permetent una comparativa tècnica en temps real quant a latència, qualitat de resposta i consum de recursos.

## Objectius Tècnics
- **Arquitectura Asíncrona:** Implementació d'un backend amb **FastAPI** i `asyncio` per minimitzar el temps d'espera total en realitzar múltiples peticions API en paral·lel.
- **Interfície Comparativa:** Desenvolupament d'un frontend amb **Streamlit** per a l'anàlisi visual de dades i mètriques de rendiment.
- **Benchmarking de LLMs:** Integració de models propietaris (OpenAI) i Open Source (DeepSeek, Llama 3) per avaluar el seu rendiment en entorns corporatius.
- **Sostenibilitat:** Estudi de l'eficiència energètica associada a cada model per promoure un ús responsable de la IA.

## Stack Tecnològic
- **Llenguatge:** Python 3.10+
- **Backend:** FastAPI, Uvicorn, HTTPX (peticions asíncrones).
- **Frontend:** Streamlit.
- **Gestió de Projecte:** GitHub Projects (Metodologia Agile/Kanban).

## Estructura del Repositori
- `/backend`: Lògica de l'API i integració amb els proveïdors de LLM.
- `/frontend`: Codi del client web i visualització de gràfics.
- `/docs`: Documentació técnica i esquemes d'arquitectura.

---
*Autor: Freddy Joel Torres Cabrera* *Tutora: Maria Dolors Royo Vallés* *Data de lliurament (dipòsit): 08/07/2026*