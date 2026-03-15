# BACKEND - ASYNCHRONOUS REST API (FASTAPI)

**This directory contains the core server logic, responsible for managing high-concurrency requests, data validation, and perfect integration with LLM providers (OpenAI, DeepSeek and Llamma)**

---

## Introduction
The main objective of this backend is to drive all the requests to different AI providers such as ChatGPT, DeepSeek and Llama3 simultaneously.
The key is that instead of waiting for one model to finish before starting the next, the system uses **Asymchronous Programming** to give results in parallel.


## Key Technical Features
- Asynchronous Architecture: FastAPI choosed for high throughput and async support.
- Concurrency: Implements `asyncio.gather` to use multiple model requests at once. The total response time is determined by the slowest model, not the sum of all the latencies.
- Data Validation: **Pydantic** models such as `QueryRequest` and `ModelResponse`to ensure stric typing for inputs and outputs.
- Mocking Layer (Current Status): To validate that the BackEnd works propertly without API costs, the system currently runs in "Simulation Mode". It generates synthetic time response and token counts using `random.uniform()` to simulate real-world network conditions.

---

## Bibliography

- Asyncio (Asynchronous I/O): Allows the server to not block while it waits the LLM's response:
    https://docs.python.org/3/library/asyncio.html

- OS: Allows the server read systems variable:
    https://docs.python.org/3/library/os.html

- Random: Used at the Mocking phase, it generates numbers randomly to simulate time response:
    https://docs.python.org/3/library/random.html

- FastAPI: Principal Framework to create the API and define the endpoints:
    https://fastapi.tiangolo.com

- CORS (Cross-Origin Resource Sharing) Middleware: Allows Backend-Frontend communication:
    https://fastapi.tiangolo.com/tutorial/cors/

-Pyndatic: Strict validation data:
    https://docs.pydantic.dev/latest/api/base_model/

-Python-dotenv: Load credentials from .env
    https://pypi.org/project/python-dotenv/