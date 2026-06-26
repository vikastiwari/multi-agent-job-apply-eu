# Communication Strategy: Multi-Agent Job Apply

This document outlines how data flows between the user, the AI agents, and external APIs.

## 1. External API Communication
- **LLM Provider:** Google Vertex AI (Gemini 2.5 Flash). Agents communicate securely via the CrewAI LLM wrapper using the `GEMINI_API_KEY`. It is also used to generate embeddings for semantic search.
- **Web Scraping:** Jina Reader API. The `Scraper Agent` makes HTTP requests to `r.jina.ai` to extract clean markdown from job portals.
- **RAG Sourcing:** DuckDuckGo Search API. The `CompanyContextRAGTool` queries DuckDuckGo for company blogs/about pages, parses them via Jina, and stores embeddings locally in an ephemeral **LanceDB** instance.
- **Email Delivery:** SMTP (Simple Mail Transfer Protocol). The `Application Dispatcher` uses Python's native `smtplib` and `ssl` to communicate securely over port 465 to Gmail/Outlook servers using an App Password.

## 2. System-Level Queue Communication
With Phase 4, processes no longer run synchronously.
- **Message Broker (`jobs.db`):** A local SQLite database acts as the communication bus between the Hunter daemon, Worker daemon, and Reviewer CLI.
- **Queue Flow:** `hunter.py` -> `evaluation_queue` -> `worker.py` -> `review_queue` -> `reviewer.py`

## 3. Inter-Agent Communication (Context Passing)
Inside the `worker.py` daemon, CrewAI tasks run sequentially. The output of one task becomes the context for the next.

- **Phase 1 Context:** The Scraper Agent's output (Job Description Markdown) is implicitly passed to the Evaluator Agent.
- **Phase 2 Context Injection:** We explicitly link tasks to pass context forward.
  ```python
  task_tailor.context = [task_scrape]
  task_writer.context = [task_scrape, task_tailor]
  task_execute.context = [task_writer, task_tailor]
  ```
  This ensures the Cover Letter Writer knows *both* what the job is, and what the tailored resume looks like, avoiding inconsistencies.

## 4. Human-Machine Interaction
- **Input:** The `hunter.py` daemon prompts for search queries. The `reviewer.py` dashboard prompts for `yes`, `no`, or `skip` decisions on pending applications.
- **Output:** File system I/O. Agents write their final deliverables to `output/<company_name>/`. The Reviewer reads these to present them to the user.
