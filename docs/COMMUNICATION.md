# Communication Strategy: Multi-Agent Job Apply

This document outlines how data flows between the user, the AI agents, and external APIs.

## 1. External API Communication
- **LLM Provider:** Google Vertex AI (Gemini 2.5 Flash). Agents communicate securely via the CrewAI LLM wrapper using the `GEMINI_API_KEY`.
- **Web Scraping:** Jina Reader API. The `Scraper Agent` makes HTTP requests to `r.jina.ai` to bypass anti-bot protections and extract clean markdown from job portals, ensuring complex DOM structures are navigated effectively.
- **Email Delivery:** SMTP (Simple Mail Transfer Protocol). The `Application Dispatcher` uses Python's native `smtplib` and `ssl` to communicate securely over port 465 to Gmail/Outlook servers using an App Password.

## 2. Inter-Agent Communication (Context Passing)
In CrewAI, tasks run sequentially (in our current configuration). The output of one task becomes the context for the next.

- **Phase 1 Context:** The Scraper Agent's output (Job Description Markdown) is implicitly passed to the Evaluator Agent.
- **Phase 2 Context Injection:** We explicitly link tasks to pass context forward.
  ```python
  task_tailor.context = [task_scrape]
  task_writer.context = [task_scrape, task_tailor]
  task_execute.context = [task_writer, task_tailor]
  ```
  This ensures the Cover Letter Writer knows *both* what the job is, and what the tailored resume looks like, avoiding inconsistencies.

## 3. Human-Machine Interaction
- **Input:** Standard CLI `input()` prompts for Job URL, Company Name, and Recruiter Email.
- **Output:** File system I/O. Agents write their final deliverables to `output/<company_name>/`.
