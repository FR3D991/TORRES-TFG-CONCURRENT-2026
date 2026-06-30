# Advanced Technical Documentation & Architectural Foundations

This directory contains the engineering specifications, topological diagrams, and the theoretical telecommunications framework that underpin the design of this concurrent testbench for network operations.

---

## 1. Asynchronous Telematic Data Flow (Step-by-Step)

Based on the unified topological diagram of the system (`arquitectura.svg`), the lifecycle of an audit transaction is formally broken down into the following 7 network stages:

1. **Transaction Initiation (HTTP POST):** The user enters a prompt into the reactive Streamlit interface. The frontend serializes the data and issues an asynchronous `HTTP POST` request with a unified JSON payload to the FastAPI orchestrator's `/generate` endpoint.
2. **Interception and Cache Validation:** The FastAPI *Gateway* receives the request and immediately routes it to the Sustainability management module (*Memoization Layer*). The system calculates a unique cryptographic hash combining the prompt string and the list of selected models.
3. **Redundancy Resolution (Hit vs. Miss):**
   * **3a. Cache Hit (100% Savings):** If the hash already exists in memory with a Time To Live (TTL) of less than 12 hours, the software denies any external request, retrieves the data at local RAM bus speeds, and sends the information directly to the charting module without generating any network or compute overhead.
   * **3b. Cache Miss:** If the resource is not registered, backend telemetry timers are initialized, and the request is forwarded to the Model Router.
4. **Concurrent Multiplexing via HTTP Stream:** The FastAPI router utilizes `asyncio.gather()` and the non-blocking `httpx.AsyncClient` to open multiple network sockets simultaneously. Parallel requests are dispatched to the **Edge** scenario (Ollama running on local VRAM) and the **Cloud** scenario (divided between high-performance production environments like NVIDIA NIM / OpenAI and variable-performance free gateways like OpenRouter).
5. **Data Stream Reading (Server-Sent Events):** Both external and local servers respond by opening text streaming connections. The backend receives data packets as tokens are generated. The *Metrics Manager* reads the stream without blocking the main thread, capturing the exact timestamp of the first data frame for each model.
6. **State Consolidation and Persistence:** Once the streaming connections for all models are closed (TCP transaction finalized), the orchestrator collects the final timestamp, the total volume of tokens received from the payload, and stores the result in the cache for future queries.
7. **Unified Client Return:** FastAPI responds to the Streamlit frontend with a unified JSON grouping all the analyzed model responses along with their telemetric numerical matrices. Streamlit instantly renders the natural language responses and draws the time-evolution line charts.

---

## 2. Theoretical Foundations of Telecommunications and Computing

To understand the necessity of this architecture, the project resolves a classic bottleneck in data transmission and distributed application links:

### A. The I/O Bound Blocking Problem
In a traditional synchronous backend (like Flask), when an HTTP request is made to a cloud model, the server's execution thread "freezes" waiting for the provider's response. If the user requests to audit 3 models simultaneously, the total wait time is the linear sum of the latencies:

$$\text{Total Latency} = T_{\text{Model 1}} + T_{\text{Model 2}} + T_{\text{Model 3}}$$

This architecture utilizes an **Event-Driven Asynchronous Model (Event Loop)** powered by FastAPI and AsyncIO. Requests are delegated to the operating system in a non-blocking manner. Therefore, the total system time is no longer determined by the sum of the factors, but depends exclusively on the slowest model (the telematic bottleneck):

$$\text{Total Latency} = \max(T_{\text{Model 1}}, T_{\text{Model 2}}, T_{\text{Model 3}})$$

### B. Performance Metrics in Large Language Networks
The telematic performance of an Artificial Intelligence model cannot be measured solely by the total time. Three key industrial metrics have been defined:

* **TTFT (Time To First Token):** This is the most critical network metric. It measures the channel propagation time plus the initial server computation time (loading context into the GPU). It is calculated as the difference between the arrival of the first useful text line from the *SSE Stream* and the initial request:
  $$\text{TTFT} = T_{\text{first packet}} - T_{\text{request sent}}$$
* **Total Latency:** Total time required to close the stream connection from the original emission:
  $$\text{Total Latency} = T_{\text{connection closed}} - T_{\text{request sent}}$$
* **Throughput (Tokens per second):** Net transmission speed of the artificial intelligence's useful information payload, calculated by dividing the processed packet (token) count by the net generation time:
  $$\text{Throughput} = \frac{\text{Total Payload (Tokens)}}{\text{Total Latency} - \text{TTFT}}$$

---

## 3. Topological Node Analysis: Edge vs. Cloud

One of the engineering objectives of this project is to compare two completely opposing compute distribution network topologies:

| Telematic Feature | Edge Scenario (Local - Ollama) | Cloud Scenario (NVIDIA NIM / OpenAI) | Alternative Cloud Scenario (Free OpenRouter) |
| :--- | :--- | :--- | :--- |
| **Channel Latency (RTT)** | Almost zero (Localhost / VRAM Bus) | High (Depends on internet routes / Traffic) | Variable (Saturation due to third-party dependency) |
| **Processing Time** | Determined by local Hardware (GPU/VRAM) | Extremely fast (Dedicated H100 Servers) | Very slow (Free priority queues) |
| **Transmission Cost** | Free and unlimited | Billed by Payload Volume (Tokens) | Free (Subject to *Rate Limits*) |
| **Metadata Format** | Standard, clean strings | Strict OpenAPI compliance | Format modifications / Risk of security injections |
| **Data Privacy** | Maximum (In-house / Ideal for a NOC) | Vulnerable (Data sent to external servers) | Low (Unknown third-party gateways) |

---
*This engineering documentation has been formalized as part of the final project for the Bachelor's Degree in Telecommunications Systems Engineering at EETAC-UPC.*