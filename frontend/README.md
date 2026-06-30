# FRONTEND - ANALYTICAL INTERFACE (STREAMLIT)

This directory contains the client-side web application. It acts as the visual and interactive layer of the architecture, allowing users to perform concurrent audits of Large Language Models (LLMs) and monitor network telemetry in real-time.

---

## Introduction

The frontend is designed to translate complex asynchronous backend processes into an intuitive User Experience (UX). Built entirely in Python using the Streamlit framework, it eliminates the need for traditional HTML/JS/CSS stacks while providing industrial-grade data visualization. It serves a dual purpose: a testing benchmarking tool (Phase 1) and an interactive deployment environment (Phase 2).

## Key Technical Features

* **Reactive UI (Streamlit):** Enables rapid prototyping and deployment of data-driven web applications. The interface re-renders dynamically based on session states (`st.session_state`), ensuring no data is lost during user interaction.
* **Real-Time Telemetry (Pandas & Line Charts):** Parses the JSON responses from the FastAPI backend and structures the telemetric data (TTFT and Total Latency) into Pandas DataFrames, rendering live line charts to monitor service degradation.
* **Green Computing (Memoization):** Implements the `@st.cache_data` decorator with a 12-hour Time To Live (TTL). This caching mechanism prevents identical requests from triggering new backend and API computations, effectively reducing GPU load, API costs, and network bandwidth by 100% on redundant queries.
* **Asynchronous UX:** Utilizes native loading states (`st.spinner` and `st.status`) to prevent UI freezing (silent fails) while waiting for the backend's `httpx` concurrent responses.

## Core Interface Components

The application is structured into three main tabs for logical separation of concerns:

1. **Benchmarking & Auditing (Fase 1):** The control panel to select multiple models (Edge and Cloud) and send a unified prompt to analyze their concurrent response metrics.
2. **Interactive Chat Deployment (Fase 2):** A production-like environment for a selected optimal model. It features a continuous chat interface paired with a live telemetry graph that updates per conversation turn.
3. **Architecture Documentation (Fase 3):** An embedded technical documentation tab explaining the asynchronous topology, metric formulas (TTFT), and the Green Computing caching strategy.

## Bibliography & Documentation

* **Streamlit:** The core UI framework for building the interactive web app. [Streamlit Docs](https://docs.streamlit.io/)
* **Pandas:** Used for structuring the telemetry history into DataFrames for accurate chart rendering. [Pandas Docs](https://pandas.pydata.org/docs/)
* **Requests:** Synchronous HTTP library used by the client to communicate with the local FastAPI backend. [Requests Docs](https://requests.readthedocs.io/en/latest/)
* **Time:** Python's built-in library utilized for frontend-side chronometry and cache hit detection. [Python Time Docs](https://docs.python.org/3/library/time.html)