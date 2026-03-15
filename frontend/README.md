# FRONTEND - INTERACTIVE LLM COMPARATOR (STREAMLIT)

**This directory contains the client-side user interface, responsible for capturing user queries, handling API communications, and visualizing comparative performance metrics in real-time.**

---

## Introduction
The main objective of this frontend is to provide a dashboard to interact with the asynchronous backend.
The key is that it translates raw JSON data from the API into text columns and interactive charts, allowing users to eeasily evaluate each LLM's latency and response quality without needing to analyse the raw data.


## Key Technical Features
- UI Framework: **Streamlit** chosen for its rapid prototyping capabilities and native Python integration.
- Synchronous to Asynchronous Bridge: Uses the `requests` library to send POST for the FastAPI backend. It implements `st.spinner` to provide visual feedback and manage user experience during the concurrent waiting times.
- Data Validation: **Pydantic** models such as `QueryRequest` and `ModelResponse`to ensure stric typing for inputs and outputs.
- Mocking Layer (Current Status): To validate that the BackEnd works propertly without API costs, the system currently runs in "Simulation Mode". It generates synthetic time response and token counts using `random.uniform()` to simulate real-world network conditions.