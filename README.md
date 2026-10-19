# 🔍 Data Pipeline Detective

> **Autonomous multi-agent system powered by LangGraph and Groq for real-time data pipeline anomaly detection, cognitive root-cause diagnostics, impact analysis, self-healing SQL remediation, and preventative data contracts.**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203-f55036.svg)](https://groq.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg?logo=scikitlearn)](https://scikit-learn.org/)
[![TailwindCSS](https://img.shields.io/badge/UI-TailwindCSS-38B2AC.svg?logo=tailwind-css)](https://tailwindcss.com/)

---

## 📖 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
  - [Workflow Diagram](#workflow-diagram)
  - [Agent Interaction Sequence](#agent-interaction-sequence)
- [Multi-Agent Roster](#-multi-agent-roster)
- [Technology Stack](#-technology-stack)
- [Repository Structure](#-repository-structure)
  - [Diagrammatic Architecture](#diagrammatic-architecture)
  - [Directory Tree](#directory-tree)
- [Step-by-Step Setup & Installation](#-step-by-step-setup--installation)
  - [Prerequisites](#prerequisites)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Create & Activate Virtual Environment](#2-create--activate-virtual-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Configure Environment Variables](#4-configure-environment-variables)
  - [5. Run the Application](#5-run-the-application)
- [Usage Guide](#-usage-guide)
  - [Web Interface](#web-interface)
  - [REST API Endpoint](#rest-api-endpoint)
- [Roadmap & Evaluation](#-roadmap--evaluation)
- [License](#-license)

---

## 🌟 Overview

Modern data pipelines fail silently. Inadvertent upstream schema mutations, duplicated batch ingestion windows, unexpected null injections, and subtle distribution shifts cascade into downstream data lakes. The consequences are severe: poisoned analytics dashboards, silent ML feature drift, inaccurate financial calculations, and broken automated decision engines.

**Data Pipeline Detective** is an autonomous, cognitive diagnostic and self-healing platform designed to monitor, triage, and repair data pipelines before corruption infects downstream consumers. 

Powered by **LangGraph** multi-agent orchestration, **Groq high-speed LLM inference**, **Scikit-learn Isolation Forest**, and a **FastAPI** backend, the system operates as an intelligent on-call data reliability engineer:
1. **Profiles & Audits**: Inspects incoming CSV payloads for schema fidelity, duplicate records, null frequency, and statistical distributions.
2. **Detects Unsupervised Outliers**: Discovers multi-dimensional statistical anomalies using Isolation Forests that deterministic rules miss.
3. **Reasoning Engine (Groq LLM)**: Synthesizes technical profile metrics and anomaly patterns into human-readable engineering root-cause analyses and executive-level business risk assessments.
4. **Conditional Self-Healing**: Dynamically evaluates pipeline health (`has_issues`). If anomalies or corruption are detected, it generates targeted SQL remediation scripts (using window functions and `COALESCE`) and simulates the repair in-memory to validate data recovery.
5. **Smart Bypass**: If the dataset is pristine, the system automatically bypasses remediation and validation nodes, saving compute and eliminating false alarms.
6. **Preventative Enforcement**: Generates strict, type-annotated **Pydantic Data Contracts** (`extra = 'forbid'`) to enforce schema guardrails at ingestion boundaries.

---

## ⚡ Key Features

- **Automated Data Profiling**: Instantly computes dataset dimensions, duplicate row counts, per-column null percentages, inferred data types, and five-number numerical distribution summaries.
- **Unsupervised ML Anomaly Detection**: Trains an in-memory Scikit-learn **Isolation Forest** (`contamination=0.05`) across numerical attributes to isolate multivariate outliers and distribution drift.
- **Cognitive LLM Diagnostics (Groq & Llama 3)**: Leverages `ChatGroq` (`langchain-groq`) for near-instantaneous reasoning that synthesizes technical anomalies into:
  - **Root-Cause Diagnoses**: Precise engineering failure hypotheses (e.g., failed deduplication, unhandled upstream null bursts, schema drift).
  - **Downstream Impact Assessments**: Concrete business risk translations (dashboard inflation, machine learning feature degradation, billing discrepancy risks).
- **Intelligent Conditional Routing**: Employs LangGraph conditional edge routing (`route_after_diagnostic`). Pristine datasets skip straight to contract generation, while degraded datasets trigger automated remediation and validation pipelines.
- **Self-Healing SQL Remediation**: Produces deterministic SQL queries utilizing Common Table Expressions (CTEs) with Window Functions (`ROW_NUMBER() OVER(PARTITION BY ... ORDER BY (SELECT NULL))`) for partition-based deduplication and `COALESCE` statements for missing value imputation.
- **In-Memory Simulation & Validation**: Simulates data cleansing transformations in memory using Pandas to guarantee the proposed fix reconciles records, removes duplicates, and sanitizes null values before warehouse deployment.
- **Preventative Pydantic Data Contracts**: Automatically derives strongly-typed Pydantic validation schemas with `extra = 'forbid'` and optionality flags to reject ill-formed data payloads at the API or streaming ingestion layer.
- **Graceful Fallback Mechanism**: Built-in resilience ensures that even if external LLM APIs experience rate-limiting or network timeouts, deterministic heuristic diagnostics are provided without breaking the pipeline.
- **Interactive Dark-Mode Dashboard**: Sleek web interface rendered with Tailwind CSS and Lucide icons featuring live Groq engine status indicators, progress bars, metric summary cards, and one-click code copy tools.

---

## 🏗️ System Architecture

Data Pipeline Detective is engineered as a layered, stateful multi-agent system:

1. **Presentation Layer**: A single-page web dashboard (`frontend/index.html`) built with Tailwind CSS, Lucide Icons, and vanilla JavaScript for drag-and-drop file ingestion, asynchronous polling, metric visualization, and code copying.
2. **API & Service Layer**: A high-performance **FastAPI** ASGI server (`main.py`) running on **Uvicorn**. Manages asynchronous multipart uploads, isolated temporary sandbox files, state initialization, and automatic file cleanup.
3. **Agent Orchestration Layer**: A compiled **LangGraph** `StateGraph` (`Agents/graph.py`) passing a centralized `PipelineState` (`Agents/state.py`) through modular agent nodes with dynamic conditional branching (`route_after_diagnostic`).
4. **Cognitive & Machine Learning Layer**:
   - **Groq LLM Engine**: Fast inference via `ChatGroq` powering deep diagnostic reasoning and business impact translation.
   - **Isolation Forest**: Scikit-learn unsupervised model identifying multi-dimensional numeric outliers.
   - **Pandas Data Engine**: In-memory profiling, metric aggregation, and validation simulation.

---

### Workflow Diagram

```mermaid
flowchart TD
    subgraph Client ["Presentation & Ingestion Layer"]
        UI["Web Dashboard<br/>(Tailwind CSS / Lucide)"]
        API_CALL["REST API Client<br/>(POST /api/investigate)"]
    end

    subgraph Server ["FastAPI Service Layer (main.py)"]
        UPLOAD["File Handler &<br/>Temp Sandbox Storage"]
        STATE_INIT["Initialize PipelineState"]
        CLEANUP["Sandbox File Cleanup"]
        RESPONSE["JSON State Response"]
    end

    subgraph LangGraph ["LangGraph Multi-Agent Orchestration (Agents/graph.py)"]
        START_NODE(["Start"]) --> AG1["1. Profiler Agent<br/>(Agents/profiler.py)"]
        AG1 --> AG2["2. Anomaly Detection Agent<br/>(Agents/anomaly.py - Isolation Forest)"]
        AG2 --> AG3["3. Diagnostic Reasoning Agent<br/>(Agents/diagnostic.py - Groq LLM)"]
        
        AG3 --> DECISION{"has_issues?"}
        
        DECISION -->|"Yes (Issues Found)"| AG4["4. SQL Remediation Agent<br/>(Agents/sql_fix.py)"]
        AG4 --> AG5["5. Validation Agent<br/>(Agents/validation.py)"]
        AG5 --> AG6["6. Data Contract Agent<br/>(Agents/contract.py)"]
        
        DECISION -->|"No (Pristine Data)"| AG6
        
        AG6 --> END_NODE(["End"])
    end

    UI -->|Upload CSV| UPLOAD
    API_CALL -->|Multipart CSV| UPLOAD
    UPLOAD --> STATE_INIT
    STATE_INIT --> START_NODE
    END_NODE --> CLEANUP
    CLEANUP --> RESPONSE
    RESPONSE -->|Display Diagnostics & Fixes| UI
    RESPONSE -->|Return Diagnostic JSON| API_CALL
```

---

### Agent Interaction Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as Data Engineer / Client
    participant API as FastAPI (main.py)
    participant State as PipelineState
    participant Profiler as Profiler Agent
    participant Anomaly as Anomaly Agent (Isolation Forest)
    participant GroqDiag as Diagnostic Agent (Groq LLM)
    participant Router as Conditional Router
    participant SQLFix as SQL Fix Agent
    participant Val as Validation Agent
    participant Contract as Data Contract Agent

    User->>API: POST /api/investigate (CSV payload)
    API->>API: Save payload to isolated temp file
    API->>State: Initialize state with file_path
    
    API->>Profiler: Execute profiler_node
    Profiler-->>State: Record row_count, duplicates, null_counts, dtypes
    
    API->>Anomaly: Execute anomaly_node
    Anomaly-->>State: Fit Isolation Forest, record anomaly_count & percentage
    
    API->>GroqDiag: Execute diagnostic_node (Groq ChatGroq API)
    Note over GroqDiag: Evaluates issues & synthesizes<br/>Root-Cause + Downstream Impact
    GroqDiag-->>State: Record diagnosis & has_issues flag
    
    API->>Router: route_after_diagnostic(state)
    
    alt Issues Detected (has_issues == True)
        Router->>SQLFix: Execute sql_fix_node
        SQLFix-->>State: Generate corrective SQL (Window CTE + COALESCE)
        
        Router->>Val: Execute validation_node
        Val-->>State: Run in-memory simulation, record cleaned metrics
        
        Router->>Contract: Execute contract_node
        Contract-->>State: Generate Pydantic schema with extra='forbid'
    else Data is Clean (has_issues == False)
        Router->>Contract: Bypass SQL & Validation -> Execute contract_node
        Contract-->>State: Generate preventative Pydantic schema
    end
    
    API->>API: Clean up temporary file
    API-->>User: Return complete PipelineState (JSON / UI Dashboard)
```

---

## 🤖 Multi-Agent Roster

| Agent / Node | Module File | Function Name | Role & Core Capability |
| :--- | :--- | :--- | :--- |
| **Profiler Agent** | [`Agents/profiler.py`](file:///c:/Users/pranj/DataPipelineDetective/Agents/profiler.py) | `profiler_node` | Reads raw CSV data, measures row dimensions, identifies duplicate records, counts nulls per column, infers pandas data types, and extracts numerical statistical summaries. |
| **Anomaly Agent** | [`Agents/anomaly.py`](file:///c:/Users/pranj/DataPipelineDetective/Agents/anomaly.py) | `anomaly_node` | Fits an unsupervised **Isolation Forest** (`contamination=0.05`, `random_state=42`) on numerical features to capture non-linear, multi-attribute outliers. |
| **Diagnostic Reasoning Agent** | [`Agents/diagnostic.py`](file:///c:/Users/pranj/DataPipelineDetective/Agents/diagnostic.py) | `diagnostic_node` | Evaluates if defects exist (`has_issues`), queries the **Groq LLM Engine** (`ChatGroq`) to synthesize root causes and business consequences, and provides a deterministic heuristic fallback. |
| **SQL Fix Agent** | [`Agents/sql_fix.py`](file:///c:/Users/pranj/DataPipelineDetective/Agents/sql_fix.py) | `sql_fix_node` | *Conditionally triggered.* Synthesizes corrective SQL queries incorporating window function CTEs (`ROW_NUMBER() OVER(PARTITION BY ...)`) for deduplication and `COALESCE` statements for null imputation. |
| **Validation Agent** | [`Agents/validation.py`](file:///c:/Users/pranj/DataPipelineDetective/Agents/validation.py) | `validation_node` | *Conditionally triggered.* Simulates the data repair pipeline in-memory via Pandas, producing reconciliation metrics (initial rows, final rows, duplicates removed, remaining nulls). |
| **Data Contract Agent** | [`Agents/contract.py`](file:///c:/Users/pranj/DataPipelineDetective/Agents/contract.py) | `contract_node` | Constructs a production-ready Pydantic v2 schema (`BaseModel`) with `extra = 'forbid'` and type annotations (`Optional[...]`) to lock ingestion boundaries against upstream schema drift. |

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Core Runtime** | [Python 3.10+](https://www.python.org/) | Base programming language environment |
| **Agent Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) | Cyclic & acyclic stateful multi-agent graph with conditional branching |
| **Cognitive / LLM Engine** | [Groq API](https://groq.com/) via [langchain-groq](https://github.com/langchain-ai/langchain) | Ultra-fast LLM inference for root-cause synthesis and business risk analysis |
| **Machine Learning** | [Scikit-learn](https://scikit-learn.org/) | Isolation Forest algorithm for unsupervised multivariate anomaly detection |
| **Data Engine & Profiling** | [Pandas](https://pandas.pydata.org/) | Dataset profiling, statistical summaries, and in-memory validation simulation |
| **Data Contracts** | [Pydantic v2](https://docs.pydantic.dev/) | Strongly typed data contracts and schema guardrails (`extra='forbid'`) |
| **Web Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance asynchronous REST API backend |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org/) | Production-ready ASGI server supporting hot-reloading |
| **Config & Secrets** | [python-dotenv](https://github.com/theskumar/python-dotenv) | Automated `.env` file environment variable loading |
| **Frontend UI** | HTML5, JavaScript, [Tailwind CSS](https://tailwindcss.com/) | Modern, responsive dark-mode diagnostic dashboard |
| **Iconography** | [Lucide Icons](https://lucide.dev/) | Semantic SVG icons for status badges and diagnostic cards |

---

## 📁 Repository Structure

### Diagrammatic Architecture

```mermaid
graph TD
    Root["📁 DataPipelineDetective/"]
    
    Root --> Agents["📁 Agents/<br/><i>LangGraph Multi-Agent Module</i>"]
    Root --> Eval["📁 evaluation/<br/><i>Benchmarking & Test Suite</i>"]
    Root --> Frontend["📁 frontend/<br/><i>Tailwind Dashboard Assets</i>"]
    Root --> Core["⚙️ Core Entrypoints & Config"]

    Agents --> A1["profiler.py<br/><i>Schema & Null Profiler</i>"]
    Agents --> A2["anomaly.py<br/><i>Isolation Forest Anomaly Agent</i>"]
    Agents --> A3["diagnostic.py<br/><i>Groq Cognitive LLM Reasoner</i>"]
    Agents --> A4["graph.py & state.py<br/><i>StateGraph & Conditional Router</i>"]
    Agents --> A5["sql_fix.py<br/><i>Window CTE Remediation</i>"]
    Agents --> A6["validation.py<br/><i>Pandas In-Memory Simulation</i>"]
    Agents --> A7["contract.py<br/><i>Pydantic v2 Guardrails</i>"]

    Eval --> E1["evaluation_agent.py<br/><i>Automated Test Harness</i>"]
    Eval --> E2["test_cases/<br/><i>Sample CSV Edge Cases</i>"]

    Frontend --> F1["index.html<br/><i>Single-Page App (Tailwind / Lucide)</i>"]

    Core --> C1["main.py<br/><i>FastAPI Server & REST API</i>"]
    Core --> C2[".env<br/><i>GROQ_API_KEY Config</i>"]
    Core --> C3["requirements.txt<br/><i>Python Dependencies</i>"]
```

### Directory Tree

```text
DataPipelineDetective/
├── Agents/                        # LangGraph Multi-Agent Module
│   ├── __init__.py                # Package initialization
│   ├── anomaly.py                 # Outlier detection using Scikit-Learn Isolation Forest
│   ├── contract.py                # Pydantic data contract generator with type mapping
│   ├── diagnostic.py              # Groq LLM diagnostic & business impact reasoning agent
│   ├── graph.py                   # LangGraph workflow builder with conditional routing
│   ├── profiler.py                # Schema, null, and duplicate profiler
│   ├── sql_fix.py                 # Corrective SQL remediation generator (CTE + COALESCE)
│   ├── state.py                   # Shared PipelineState TypedDict definition
│   └── validation.py              # In-memory remediation simulation & validation agent
├── evaluation/                    # Pipeline benchmarking and evaluation suite
│   ├── evaluation_agent.py        # Automated test harness for agent accuracy (in-progress)
│   └── test_cases/                # Sample test datasets and edge cases
├── frontend/                      # Static dashboard assets
│   └── index.html                 # Single-page dashboard UI (Tailwind CSS + Lucide)
├── .env                           # Environment configuration (GROQ_API_KEY)
├── .gitignore                     # Git ignore rules
├── main.py                        # FastAPI application entrypoint & API routing
├── requirements.txt               # Python package dependencies
└── README.md                      # Comprehensive project documentation
```

---

## 🚀 Step-by-Step Setup & Installation

### Prerequisites

Ensure the following tools are available on your system:
- **Python 3.10** or higher (`python --version`)
- **Git** (`git --version`)
- **Groq API Key**: Obtain a free API key from [Groq Console](https://console.groq.com/) for cognitive LLM diagnostics.

---

### 1. Clone Repository

```bash
git clone https://github.com/PJ-21-code/DataPipelineDetective.git
cd DataPipelineDetective
```

---

### 2. Create & Activate Virtual Environment

#### Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If script execution is restricted on Windows PowerShell, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

#### Windows (Command Prompt):
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

#### macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the project root directory and add your Groq API key:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

> [!NOTE]
> If `GROQ_API_KEY` is not provided, the system seamlessly engages its built-in fallback engine to provide heuristic diagnostic reports without crashing.

---

### 5. Run the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Once launched, navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 💻 Usage Guide

### Web Interface

1. Navigate to **[http://localhost:8000](http://localhost:8000)**.
2. Select a pipeline CSV file under **Upload Corrupted CSV Pipeline Log**.
3. Click **Dispatch Agents**.
4. The system streams the file through the LangGraph multi-agent team:
   - **LLM Diagnostic & Impact Reasoning Card**: Displays Groq-synthesized root-cause analysis and business consequence estimations.
   - **Metric Snapshot Bar**: Highlights total rows, duplicates found, ML outliers flagged, and in-memory validation status (`SUCCESS` or `BYPASSED`).
   - **Proposed SQL Remediation**: Shows partition-based deduplication CTEs and null coalescing scripts with a one-click copy button.
   - **Pydantic Prevention Contract**: Displays strict, copy-ready Python schema guardrails to enforce at ingestion.

---

### REST API Endpoint

Integrate Data Pipeline Detective directly into data orchestrators (Airflow, Dagster, Prefect) or CI/CD pipelines.

#### Endpoint: `POST /api/investigate`
- **Content-Type**: `multipart/form-data`
- **Parameter**: `file` (a valid `.csv` file)

#### Example using `cURL`:
```bash
curl -X POST "http://localhost:8000/api/investigate" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@pipeline_sample.csv"
```

#### Example JSON Response:
```json
{
  "file_path": "C:\\Users\\...\\tmp_abc123.csv",
  "profile": {
    "row_count": 1000,
    "duplicate_rows": 45,
    "null_counts": {
      "user_id": 0,
      "amount": 250,
      "timestamp": 0
    },
    "dtypes": {
      "user_id": "int64",
      "amount": "float64",
      "timestamp": "object"
    },
    "numeric_summary": { ... }
  },
  "anomaly": {
    "anomaly_count": 12,
    "percentage": 1.2,
    "message": "Detected 12 statistical outliers (1.2% of dataset)."
  },
  "diagnosis": "1. **Root-Cause Diagnosis**: Found 45 duplicate rows indicating a breakdown in ingestion-level idempotency or deduplication windows. Column 'amount' exhibits 25.0% null values, suggesting upstream schema mutation or unhandled network dropouts. Isolation Forest identified 12 statistical outliers.\n\n2. **Downstream Business Impact**: Analytics dashboards tracking revenue will experience distortion from duplicated records. Machine learning models depending on 'amount' will suffer from feature nullification or skewed inference results.",
  "has_issues": true,
  "database_fix": "WITH ranked_data AS (\n    SELECT *,\n           ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY (SELECT NULL)) as rn\n    FROM raw_pipeline_data\n)\nSELECT user_id, COALESCE(amount, 'DEFAULT_VALUE') AS amount, timestamp\nFROM ranked_data\nWHERE rn = 1;",
  "validation": {
    "status": "SUCCESS",
    "initial_rows": 1000,
    "final_rows": 955,
    "duplicates_removed": 45,
    "remaining_nulls": 0,
    "message": "Validation passed successfully. Removed 45 duplicates and sanitized null records."
  },
  "data_contract": "from pydantic import BaseModel\nfrom typing import Optional\nfrom datetime import datetime\n\nclass IngestionDataContract(BaseModel):\n    user_id: int\n    amount: Optional[float]\n    timestamp: str\n\n    class Config:\n        extra = 'forbid'  # Blocks upstream schema drift"
}
```

---

## 🔮 Roadmap & Evaluation

- [x] **Core Multi-Agent Architecture**: Stateful LangGraph workflow with dynamic conditional routing (`route_after_diagnostic`).
- [x] **Groq Cognitive Reasoning Engine**: Real-time LLM-powered root-cause diagnosis and business risk assessment via `langchain-groq`.
- [x] **Isolation Forest Outlier Detection**: Unsupervised multi-attribute anomaly isolation with Scikit-learn.
- [x] **Automated SQL Remediation**: Self-healing window function CTEs and null coalesce clauses.
- [x] **In-Memory Validation**: Pandas-based simulation verifying row reconciliation and duplicate/null resolution.
- [x] **Preventative Data Contracts**: Automated Pydantic v2 schema generation with `extra = 'forbid'`.
- [x] **Interactive Dashboard**: Modern dark-slate UI with live metrics and one-click code copying.
- [ ] **Automated Evaluation Suite (`evaluation/evaluation_agent.py`)**: Quantitative benchmarking harness measuring diagnostic precision and remediation accuracy across synthetic dirty datasets.
- [ ] **Data Warehouse Connectors**: Direct integrations with Snowflake, BigQuery, and Databricks.
- [ ] **dbt Model & Test Generation**: Export remediation queries directly as dbt `.sql` models and `.yml` schema tests.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](file:///c:/Users/pranj/DataPipelineDetective/LICENSE) for details.
