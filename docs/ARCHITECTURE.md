# Multi-Agent Job Apply: Architectural Design Document

## 1. Executive Summary
The **Multi-Agent Job Apply** system is an automated, AI-driven workflow built with Python and **CrewAI**. It leverages Google's **Vertex AI (Gemini 2.5 Flash)** to analyze job postings, evaluate candidate fit, and auto-generate tailored application materials (Resume PDF and Cover Letter). 

## 2. System Architecture
The architecture is split into two distinct sequential phases to prevent hallucinated applications and ensure human oversight.

```mermaid
graph TD;
    User([User CLI Input]) --> Main[Orchestrator: main.py]
    
    subgraph Phase 1: Evaluation Crew
        Main --> Scraper[Scraper Agent]
        Scraper -.->|Jina Reader API| Website[Job Board URL]
        Scraper --> Evaluator[Evaluator Agent]
        Evaluator -.->|Compare| BaseResume[(base_resume.md)]
    end
    
    Evaluator -->|Decision: GO / NO-GO| Check{Is it a Match?}
    Check -->|NO-GO| Abort[Terminate Process]
    
    subgraph Phase 2: Execution Crew
        Check -->|GO| Tailor[Resume Tailor Agent]
        Tailor --> Writer[Cover Letter Writer]
        
        subgraph Semantic Context
            Writer -.->|Search DDG + Jina| CompanyWeb[Company Blog]
            CompanyWeb --> LanceDB[(LanceDB Vector DB)]
            LanceDB -.->|Context Injection| Writer
        end
        
        Writer --> Executor[Application Dispatcher]
        
        Executor -.->|wkhtmltopdf| PDF[tailored_resume.pdf]
        Executor -.->|SMTP| Email[Recruiter Inbox]
    end
    
    Executor --> OutputDir[Local Output Directory]
```

## 3. Core Architectural Decisions

## High-Level Architecture (Phase 4)

The system consists of three independent async components communicating via a SQLite-backed Message Broker (`queue_manager.py`):

1.  **Hunter Daemon (`hunter.py`)**: Runs continuously, querying job boards (e.g., via `duckduckgo-search`), and extracting job URLs. It pushes these into the `evaluation_queue`.
2.  **Worker Daemon (`worker.py`)**: Continuously polls the `evaluation_queue`. When a job URL is found, it runs the `eval_crew`. If the evaluation is "Decision: GO", it runs the `exec_crew` in DRY-RUN mode. Successful dry-runs are pushed to the `review_queue`.
3.  **Reviewer CLI (`reviewer.py`)**: A Human-In-The-Loop terminal dashboard. Pops jobs from the `review_queue`, presents the drafted email/PDF to the user, and physically dispatches the `SMTPEmailTool` if approved.

### Sub-System: The CrewAI Engine

Within the Worker and Hunter daemons, we orchestrate the following Agents:

-   **Hunter Agent** (Sourcing phase)
-   **Scraper Agent** (Evaluation phase)
-   **Evaluator Agent** (Evaluation phase)
-   **Tailor Agent** (Execution phase)
-   **Writer Agent** (Execution phase)
-   **Executor Agent** (Execution phase), `CompanyContextRAGTool`) wrap complex logic so the CrewAI agents only need to know *what* to do, not *how* to do it. The RAG tool specifically utilizes ephemeral, in-memory **LanceDB** to perform high-speed semantic searches on scraped company data to inject deep organizational alignment into cover letters.

## 4. Scalability & Deployment
Currently designed as a local CLI tool. Future architectures may involve migrating this into a fastAPI backend with a React UI for managing hundreds of concurrent applications.
