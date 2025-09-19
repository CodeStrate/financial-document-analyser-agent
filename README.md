# Financial Document Analyzer Agent - Base App (Enhanced)

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

This project is an AI-powered system that analyzes financial documents (such as quarterly earnings reports) to provide a comprehensive summary, investment advice, and a risk assessment. It uses **CrewAI** to orchestrate a team of specialized AI agents, **FastAPI** for API interaction, and a **Redis + Celery job queue** for scalable asynchronous processing.

This repository is the improved and stable version of the base assignment codebase, with bugs fixed, prompts refined, and extended with concurrency features.

---

## Table of Contents

1. [Key Features](#key-features)
2. [Bugs Squashed](#bugs-squashed)
3. [Technology Stack](#technology-stack)
4. [Setup and Installation](#setup-and-installation)
5. [Usage](#usage)
6. [API Reference](#api-reference)

---

## Key Features

* **AI Agent Orchestration**: CrewAI manages specialized agents for document analysis, investment advice, and risk assessment.
* **Summarizer Agent**: Aggregates results from all previous agents into one consolidated summary.
* **Robust PDF Parsing**: Custom CrewAI tool for extracting text from PDF documents.
* **Job Queue with Redis + Celery**: Long-running tasks are executed asynchronously, allowing concurrent analysis jobs and improved scalability.
* **RESTful API**: FastAPI-based endpoints for job submission and status/result retrieval.

---

## Bugs Squashed

During development, several issues were identified and resolved:

* **Dependency Conflicts**: `requirements.txt` had severe version mismatches (notably with `opentelemetry`, `google` packages, and `onnxruntime`).

  * **Fix**: Adjusted versions compatible with `crewai==1.30.0`.

* **Broken Custom Tools**: PDF parser was incorrectly implemented.

  * **Fix**: Proper inheritance from `crewai.tools.BaseTool`, correct `_run` method, and integration of `PyPDFium2Loader` from `langchain-community`. Also fixed incorrect `SerperDevTool` import.

* **LLM Initialization Errors**: Agents were not receiving models correctly. Also Agent import was wrong its `crewai.agent` not `crewai.agents`.

  * **Fix**: Used `LLM` class from `crewai` with proper env var configuration; fixed `tools=` vs. `tool=` bug.

* **Workflow Execution Issues**: `run_crew` was not properly passing agents/tasks, and `kickoff()` lacked file\_path handling.

  * **Fix**: Ensured full workflow with contextual passing across agents.

* **Prompt & Task Quality**: Agents’ roles, goals, and tasks were previously written as sarcastic jokes, leading to hallucinations and poor outputs.

  * **Fix**: Rewritten as professional, structured roles with explicit objectives. Outputs now cascade logically (financial → investment → risk).

* **Redundant Logic Removed**: `Verifier` agent and unused tools were eliminated since their responsibilities overlapped with other agents, reducing unnecessary complexity.



## Technology Stack

* **AI Framework**: [CrewAI](https://www.crewai.com/)
* **LLM**: OpenAI GPT-4o (or any compatible model)
* **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/)
* **PDF Parsing**: [PyPDFium2](https://pypdfium2.readthedocs.io/en/stable/)
* **Job Queue**: Redis + Celery


## Job Data Persistence

In addition to Redis for managing background task queues, the system uses **SQLite** as a lightweight relational database to store job metadata and results. This ensures job information is persisted beyond the in-memory lifecycle of Redis and can be queried reliably.

**What gets stored in SQLite**
Each job entry contains:

* `job_id` (UUID4) – unique identifier for the analysis job
* `job_status` – current state (`in queue`, `processing`, `completed`, `failed`)
* `job_created_at` – timestamp when job was created
* `job_updated_at` – timestamp when job last updated
* `job_result` – final structured result (analysis, recommendations, risk, summary)

**Why SQLite?**

* Simple setup, no additional infrastructure required
* Data persists between restarts
* Portable: the database file (`jobs.db`) can be inspected or migrated easily

**Configuration**

* Database file: `jobs.db` (default, configurable via env variable `JOB_DB_PATH`)
* Access Layer: Python `sqlite3` module with simple CRUD operations for job records


## Setup and Installation

### Prerequisites

* Python 3.13+
* Git
* OpenAI (or Gemini, Anthropic) API Key - depending on what you want to use.
* Serper API Key
* Redis Server

---

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/CodeStrate/financial-document-analyser-agent.git
   cd financial-document-analyser-agent
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3.13 -m venv venv
   source venv/bin/activate   # Linux / macOS
   .\venv\Scripts\activate    # Windows PowerShell
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Redis**

   * **Ubuntu/Debian**

     ```bash
     sudo apt update
     sudo apt install redis-server
     sudo systemctl enable redis-server
     sudo systemctl start redis-server
     ```
   * **macOS (Homebrew)**

     ```bash
     brew install redis
     brew services start redis
     ```
   * **Windows**
     Download from [Memurai](https://www.memurai.com/) or [Redis for Windows port](https://github.com/microsoftarchive/redis/releases).
     Then run:

     ```powershell
     redis-server.exe
     ```

5. **Configure environment variables**

   ```env
   OPENAI_API_KEY="sk-..."
   SERPER_API_KEY="a20..."
   REDIS_URL="redis://localhost:6379/0"
   ```

6. **Run the FastAPI server**

   ```bash
   python main.py
   ```

7. **Start the Celery worker**

   ```bash
   celery -A celery_jobs.analysis_worker worker --loglevel=info --pool=solo --concurrency=1
   ```

---

## Usage

Submit a document and check job status via API.

### 1. Submit a document for analysis

```bash
http POST http://localhost:8000/analyze file@data/quarterly_report.pdf query="Provide a detailed analysis, recommendation, and risk assessment."
```

**Response**

```json
{
    "status": "success",
    "message": "Analysis Job created and submitted.",
    "job_id": "Job_c0b12a64-324c-4fbb-8a22-36e7c2b2f9a4",
    "file_processed": "quarterly_report.pdf"
}
```
---

## API Reference

### `POST /analyze`

Uploads a financial document and queues it for analysis. The job metadata is inserted into the **SQLite database** immediately after submission.

**Request Body**:

* `file` (file) – required, PDF file
* `query` (string) – optional, custom analysis request

**Success Response (200 OK):**

```json
{
    "status": "success",
    "message": "Analysis Job created and submitted.",
    "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "file_processed": "quarterly_report.pdf"
}
```

* `job_id` → UUID4 stored in the SQLite database
* `file_processed` → original filename

---

### `GET /status/{job_id}`

Retrieves the **current status and results** of a specific job. All data is fetched from the **SQLite database**, which is updated by Celery workers as jobs progress.

**Path Parameter**:

* `job_id` (string, `Job_UUID4`) – required

**Response while processing (200 OK):**

```json
{
    "job_id": "Job_a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "job_status": "Processing",
    "job_created_at": "2025-09-19T10:15:30",
    "job_updated_at": "2025-09-19T10:16:12",
    "job_result": null
}
```

**Response when complete (200 OK):**

```json
{
    "job_id": "Job_c0b12a64-324c-4fbb-8a22-36e7c2b2f9a4",
    "job_status": "Completed",
    "job_created_at": "2025-09-19T10:20:00Z",
    "job_updated_at": "2025-09-19T10:22:45Z",
    "job_result": "Overall financials improved with YoY growth...",
}
```

**Response if not found (404 Not Found):**

```json
{
    "detail": "Job with Job_c0b12a64-324c-4fbb-8a22-36e7c2b2f9a4 doesn't exist."
}
```
