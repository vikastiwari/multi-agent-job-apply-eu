# Component Specifications: Multi-Agent Job Apply

## 1. Orchestration (Phase 4 Async Architecture)
Instead of a single `main.py`, orchestration is now split into three standalone daemons connected by a SQLite Message Broker (`queue_manager.py`):
- **`hunter.py`:** A proactive daemon that polls job boards using DuckDuckGo search and pushes URLs to the `evaluation_queue`.
- **`worker.py`:** The backend consumer. It pops URLs from the `evaluation_queue`, orchestrates the CrewAI Phase 1 (Evaluation) and Phase 2 (Execution) agents, and pushes successful drafts to the `review_queue`.
- **`reviewer.py`:** The CLI Human-In-The-Loop dashboard. It pops from the `review_queue` and allows the user to approve or reject staged applications before dispatch.

### Real-Time Voice Module

* **`interview.py`**: A LiveKit WebRTC worker script. When executed (`python interview.py --company <Name>`), it loads the candidate's tailored resume and the job description, connecting to a LiveKit room to act as an HR Recruiter for a real-time mock interview.

## 2. AI Agents (`agents.py`)
Defines the personas, goals, and backstories for the Swarm.
- **`hunter_agent`:** Proactively sources jobs using advanced search queries (DuckDuckGo Dorks) to uncover hidden opportunities.
- **`scraper_agent`:** Equipped with the `JinaReaderScraperTool` to extract clean job postings.
- **`evaluator_agent`:** Analyzes fit (Base Resume vs Job Description).
- **`resume_tailor_agent`:** Rewrites the base markdown resume to highlight keyword matches strictly adhering to European standards.
- **`cover_letter_agent`:** Equipped with the `CompanyContextRAGTool` to retrieve semantic insights about a company and draft highly contextualized cover letters.
- **`execution_agent`:** Equipped with `MarkdownToPDFTool` and `SMTPEmailTool` to handle final logistics.

## 3. Task Definitions (`tasks.py`)
- **Role:** Maps specific, actionable prompts to agents.
- **Responsibilities:** Defines the exact expected output format (e.g., instructing the Evaluator to end its output strictly with "Decision: GO", or instructing the Writer to use LanceDB insights).

## 4. Custom Tools (`tools/`)
- **`JobSearchTool`:** Uses `duckduckgo-search` (DDGS) to programmatically search platforms like LinkedIn and EURES for job links.
- **`JinaReaderScraperTool`:** A custom CrewAI `BaseTool` that calls the Jina Reader API.
- **`CompanyContextRAGTool`:** Uses DuckDuckGo, Jina Reader, Gemini Embeddings, and LanceDB to perform deep semantic searches on a target company for cover letter generation.
- **`MarkdownToPDFTool`:** Uses `fpdf2` to render the agent's markdown string into a styled PDF file.
- **`SMTPEmailTool`:** Constructs a MIME multipart email (text body + PDF attachment) and dispatches it via SMTP.
