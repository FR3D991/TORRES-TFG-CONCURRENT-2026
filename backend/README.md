# BACKEND - ASYNCHRONOUS REST API (FASTAPI)

This directory contains the core server logic, responsible for managing high-concurrency requests, data validation, and seamless integration with multiple LLM providers (OpenAI, DeepSeek, NVIDIA, and Llama).

---

## Introduction

The main objective of this backend is to route incoming user prompts to different AI providers simultaneously. Instead of waiting for one model to finish before starting the next (synchronous blocking), the system leverages **Asynchronous Programming** to execute inferences in parallel, minimizing the total waiting time for the end user.

## Key Technical Features

* **Asynchronous Architecture:** FastAPI was chosen for its high throughput, native async support, and ASGI standard compliance.
* **Concurrency:** Implements `asyncio.gather()` to dispatch multiple model requests at once. The total network response time is determined by the slowest model, not the sum of all latencies.
* **Streaming & Telemetry:** Uses `httpx.AsyncClient` to read Server-Sent Events (SSE) in real-time, allowing the system to calculate precise telemetric data such as the Time To First Token (TTFT).
* **Data Validation:** Utilizes Pydantic models (e.g., `QueryRequest` and `ModelResponse`) to ensure strict typing for inputs and outputs.
* **Graceful Degradation (Mocking Layer):** The system features a fallback mechanism. If an API key is missing or a network authorization error (HTTP 401) occurs, the generic API handler automatically degrades to a "Simulation Mode" (Mock API), generating synthetic time responses and token counts using `random.uniform()` to keep the application running without crashing.

## Core Endpoints

* `GET /` : Health check endpoint to verify the API status.
* `POST /generate` : The main routing endpoint. It receives a JSON payload containing the user's prompt and a list of target models, and returns an array of telemetric responses.

## Bibliography & Documentation

* **Asyncio (Asynchronous I/O):** Allows the server to remain unblocked while waiting for LLM responses. [Python Docs](https://docs.python.org/3/library/asyncio.html)
* **OS:** Enables the server to read environment variables dynamically. [Python Docs](https://docs.python.org/3/library/os.html)
* **Random:** Used in the Mocking phase to generate synthetic time variables simulating real-world network conditions. [Python Docs](https://docs.python.org/3/library/random.html)
* **FastAPI:** The principal framework used to create the REST API and define the asynchronous endpoints. [FastAPI Docs](https://fastapi.tiangolo.com)
* **CORS Middleware:** Allows secure Backend-Frontend Cross-Origin communication. [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
* **Pydantic:** Enforces strict data validation and serialization. [Pydantic Docs](https://docs.pydantic.dev/latest/api/base_model/)
* **Python-dotenv:** Loads credentials from local `.env` files, maintaining security by keeping API Keys out of version control. [PyPI](https://pypi.org/project/python-dotenv/)