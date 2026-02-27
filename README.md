# 🌊 AI-Driven Disaster Response System

An end-to-end AI-powered emergency response simulation platform designed to detect flood events and orchestrate optimized response planning using multi-modal data fusion, deterministic planning logic, and multi-agent orchestration.

This system simulates real-world flood scenarios and demonstrates how AI can assist decision-makers during disasters through structured planning, geospatial reasoning, and measurable performance metrics.

---

## 🎯 Project Objective

To build a reproducible, explainable, and evaluation-driven disaster response system that:

* Detects flood events using multi-source synthetic data
* Generates affected area GeoJSON outputs
* Prioritizes distress reports intelligently
* Allocates resources efficiently
* Plans safe routes avoiding hazards
* Produces operational dispatch plans
* Generates Situation Reports (SITREP)
* Evaluates response effectiveness with metrics
* Provides a replayable simulation dashboard

This system is a **decision-support tool**, not a replacement for authorities.

---

## 🏗️ System Architecture

The system follows a layered backend-first architecture:

```
Synthetic Data → Detection & Fusion → FloodEvent →
Deterministic Planning Engine → Multi-Agent Orchestration →
Evaluation → Streamlit Dashboard
```

### Core Components

1. **Synthetic Data Engine**

   * Weather stream (rainfall, river level)
   * Social distress reports
   * Satellite flood polygons
   * Ground truth generation for evaluation

2. **Flood Detection & Fusion**

   * Rule-based risk scoring
   * Multi-modal evidence fusion
   * Confidence scoring (0–1)
   * Severity classification (1–5)
   * GeoJSON affected area output

3. **Deterministic Planning Engine**

   * Urgency scoring
   * Geographic clustering
   * Resource allocation
   * Shelter assignment
   * Route planning using NetworkX
   * Risk assessment

4. **Multi-Agent Orchestrator (LangGraph)**

   * Triage Agent
   * Clustering Agent
   * Resource Agent
   * Routing Agent
   * Medical Agent
   * Command Agent
   * RAG-enhanced SITREP generation

5. **Evaluation Module**

   * Detection precision & recall
   * Response time estimation
   * Urgent-case coverage %
   * Resource utilization rate
   * Fairness distribution
   * Route safety score

6. **Streamlit Dashboard**

   * Scenario selector
   * Map visualization (GeoJSON)
   * Timeline replay
   * Agent decision panel
   * Metrics display
   * SITREP export

---

## 📂 Project Structure

```
disaster-response-system/
│
├── backend/
│   ├── synthetic/
│   ├── detection/
│   ├── planning/
│   ├── agents/
│   ├── simulation/
│   ├── evaluation/
│   ├── schemas/
│   └── api/
│
├── dashboard/        # Streamlit UI
├── data/             # Scenarios + knowledge base
├── tests/
├── run_demo.py
└── requirements.txt
```

All modules output structured JSON for interoperability and evaluation.

---

## 🚀 How to Run

### 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd disaster-response-system
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure OpenAI API

Create `.env` file:

```
OPENAI_API_KEY=your_key_here
```

---

## ▶ Run Backend Demo (CLI)

```bash
python run_demo.py --scenario S3 --seed 42
```

Outputs:

* FloodEvent JSON
* Affected GeoJSON
* Evidence references
* Response plan
* Evaluation metrics

---

## 🖥️ Run Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard Features:

* Scenario selection
* Map visualization
* Agent decision breakdown
* Metrics panel
* SITREP generation
* Timeline replay

---

## 🧪 Available Scenarios

* S1: No flood (false positive test)
* S2: Flash flood
* S3: River flood (slow expansion)
* S4: Social misinformation
* S5: Medical-heavy emergency
* S6: Missing satellite evidence

All scenarios are reproducible using deterministic seeds.

---

## 📊 Evaluation Metrics

The system measures:

* Detection accuracy
* Response coverage of high-urgency cases
* Average response time estimate
* Resource utilization rate
* Route hazard avoidance
* Fairness across geographic clusters

This ensures measurable intelligence rather than a static demo.

---

## 🔒 Design Principles

* Deterministic core logic
* Structured data contracts (Pydantic)
* Explainable fusion logic
* Transparent agent reasoning
* GeoJSON everywhere
* Reproducible simulation
* Evaluation-first design

---

## 🧠 Technology Stack

* Python 3.10+
* FastAPI
* Pydantic
* Shapely
* NetworkX
* LangGraph / LangChain
* OpenAI API
* Chroma (Vector DB)
* Streamlit

---

## 🎬 Demo Flow

1. Select scenario
2. Simulate multi-stream ingestion
3. Detect flood event
4. Generate affected area polygon
5. Produce response plan
6. View dispatch decisions
7. Inspect metrics
8. Export SITREP

---

## 📌 Future Extensions

* Real-world data ingestion
* Integration with OpenStreetMap
* Cyclone & earthquake scenarios
* Real-time streaming pipeline
* Multi-region scaling

---

## 👨‍💻 Author

Capstone Project – AI-Driven Disaster Response Simulation
Designed as a research-grade emergency decision-support system.

---

