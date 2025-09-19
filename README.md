# Financial Document Analyzer Agent - Base App Debugged

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

This project is an AI-powered system that analyzes financial documents (such as quarterly earnings reports) to provide a comprehensive summary, investment advice, and a risk assessment. It uses **CrewAI** to orchestrate a team of specialized AI agents and a **FastAPI** server for interaction.

This repository is the improved and stable version of the base assignment codebase, with bugs fixed and prompts refined without bonus features.

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
* **Robust PDF Parsing**: Custom CrewAI tool for extracting text from PDF documents.
* **RESTful API**: FastAPI-based interface for document submission and result retrieval.

---

## Bugs Squashed

During development, several issues were identified and fixed:

* **Dependency Conflicts**: `requirements.txt` had too many versioning issues especially with `opentelemetry`, `google` packages and `onnxruntime`
    - Fix: Made sure to use appropriate package versions w.r.t. `crewai==1.30.0`.
* **Broken Custom Tools**: Fixed PDF parsing tool by properly inheriting from `crewai.tools.BaseTool` for proper format, implementing `_run` method for tool execution and integrating `PyPDFium2Loader` from `langchain-community`. As well as fixed `SerperDevTool` import (was `serper_dev_tool`)
* **LLM Initialization**: Corrected agent LLM initialization (llm=llm) with `LLM` class from `crewai` (so we can easily switch AI providers as well as models) and environment variable configuration. Also tools were passed incorrectly to the agents, that was fixed. (was `tools=` not `tool=`)
* **Crew Running Problems**: `run_crew` in `main` was not passing all agents and tasks in the workflow also it didn't get file_path in `kickoff()`. Fixed by adding them.

### Inefficient Prompting Fixes and Removal of Redundant Code
* **Problem 1** : The Agents' role, backstory and goals were sarcastic jokes or satire at worst. It lead to hallucination at best and undesirable output at worst.
  - Fix : The role, goals and backstory were properly defined to position each agent as a serious professional. So now each Agent carries a persona or a character it plays that leads to quality output.

* **Problem 2** : The tasks were also poorly written, like hyperbolic jokes with no clear directive, the task assignment also needed fixing, as it was wrong. Also no context sharing between agents so no agent had knowledge towards its task from the previous.
  - Fix : Defined structured tasks with a clear output format in mind while passing the output from one task to the next. eg. `financial_analysis_task` forms the context for `investment_analysis_task` and the both tasks formed the context for the `risk_assessment_task` for the best response.
 
* **Redundant Code Removed** : `Verifier` Agent and its subsequent task was removed from the codebase as it wasn't influencing the Agent's response and it's objective was already fulfilled by the `financial_analyst` Agent and task. It wasn't logically to add this overhead which might have caused confusion for the LLM. Also tools for `investment_analysis` and `risk_assessment` were also removed since they weren't doing anything extra that the Agents could not on their own reasoning and supplied WebSearch tools.

---

## Technology Stack

* **AI Framework**: [CrewAI](https://www.crewai.com/)
* **LLM**: OpenAI GPT-4o (or any compatible model)
* **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/)
* **PDF Parsing**: [PyPDFium2](https://pypdfium2.readthedocs.io/en/stable/)

---

## Setup and Installation

### Prerequisites

* Python 3.13+
* Git
* OpenAI API Key

---

### Steps

1. Clone the repository:

   ```powershell
   git clone https://github.com/CodeStrate/financial-document-analyser-agent.git
   cd financial-document-analyser-agent
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

   or in Linux
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```env
   OPENAI_API_KEY="sk-..."
   SERPER_API_KEY="a20..."
   ```

5. Run the FastAPI server:

   ```powershell
   python main.py
   ```

---

## Usage

Submit a document and check results through the API.

### 1. Submit a document for analysis

```bash
http POST http://localhost:8000/analyze file@data/quarterly_report.pdf query="Provide a detailed analysis, recommendation, and risk assessment."
```

---

## API Reference

### `POST /analyze`

Uploads a financial document and starts analysis.

**Request Body**:

* `file` (file) – required, PDF file
* `query` (string) – optional

**Response**:

```json
{
      "status": "success",
      "query": "User query",
      "analysis": "Agent response",
      "file_processed": "file_name"
}
```
