# Web Architecture for Concurrent LLM Querying: ChatGPT, DeepSeek, and Llama

**Bachelor's Degree in Telecommunications Systems Engineering (EETAC - UPC)**

---

## Introduction
This project addresses the need to streamline interacionts with multiple Large Language Models (LLMs) simultaneously. **The main goal is to design and build a web architecture capable of handling concurrent queries, enabling real-time technical comparison regarding latency, response quality, and resource usage.**

## Technical Objectives
- **Asynchronous Architecture:** Implementing a backend using **FastAPI** and `asyncio` to minimize total wait times when executing parallel API requests.
- **Comparison Interface:** Developing a **Streamlit** frontend for visual data analysis and performance metrics.
- **LLMs Benchmarking:** Integrating both propietary (OpenAI) and Open Source (DeepSeek, Llama 3) models to evaluate ther performance in corporate environments.
- **Sustainability:** Analyzing the energy efficiency associated with each model to encourage responsible AI usage.

## Tech Stack
- **Language:** Python 3.10+
- **Backend:** FastAPI, Uvicorn, HTTPX (async requests).
- **Frontend:** Streamlit.
- **Project Management:** GitHub Projects (Agile/Kanban methodology).

## Repository Structure
- `/backend`: API logic and LLM provider integrations.
- `/frontend`: Web client code and chart visualization.
- `/docs`: Technical documentation and architecture diagrams.

---
*Author: Freddy Joel Torres Cabrera* *Tutor: Maria Dolors Royo Vallés* *Delivery date (deposit): 08/07/2026*