# Component Specifications: Multi-Agent Job Apply

## 1. Orchestration (`main.py`)
- **Role:** The application entry point.
- **Responsibilities:** 
  - Loads `.env` configurations.
  - Prompts the user for initial context (URL, Company, Email).
  - Instantiates Phase 1 (Evaluation) and Phase 2 (Execution) Crews.
  - Handles the GO/NO-GO conditional logic.

## 2. AI Agents (`agents.py`)
Defines the personas, goals, and backstories for the Swarm.
- **`scraper_agent`:** Equipped with the `JinaReaderScraperTool` to extract clean job postings.
- **`evaluator_agent`:** Analyzes fit (Base Resume vs Job Description).
- **`resume_tailor_agent`:** Rewrites the base markdown resume to highlight keyword matches.
- **`cover_letter_agent`:** Drafts the email body/cover letter.
- **`execution_agent`:** Equipped with `MarkdownToPDFTool` and `SMTPEmailTool` to handle final logistics.

## 3. Task Definitions (`tasks.py`)
- **Role:** Maps specific, actionable prompts to agents.
- **Responsibilities:** Defines the exact expected output format (e.g., instructing the Evaluator to end its output strictly with "Decision: GO").

## 4. Custom Tools (`tools/`)
- **`JinaReaderScraperTool`:** A custom CrewAI `BaseTool` that calls the Jina Reader API.
- **`MarkdownToPDFTool`:** Uses `pdfkit` and `wkhtmltopdf` to render the agent's markdown string into a styled PDF file.
- **`SMTPEmailTool`:** Constructs a MIME multipart email (text body + PDF attachment) and dispatches it via SMTP.
