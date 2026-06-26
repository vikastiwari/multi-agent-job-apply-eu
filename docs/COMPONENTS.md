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
- **`resume_tailor_agent`:** Rewrites the base markdown resume to highlight keyword matches strictly adhering to European standards.
- **`cover_letter_agent`:** Equipped with the `CompanyContextRAGTool` to retrieve semantic insights about a company and draft highly contextualized cover letters.
- **`execution_agent`:** Equipped with `MarkdownToPDFTool` and `SMTPEmailTool` to handle final logistics.

## 3. Task Definitions (`tasks.py`)
- **Role:** Maps specific, actionable prompts to agents.
- **Responsibilities:** Defines the exact expected output format (e.g., instructing the Evaluator to end its output strictly with "Decision: GO", or instructing the Writer to use LanceDB insights).

## 4. Custom Tools (`tools/`)
- **`JinaReaderScraperTool`:** A custom CrewAI `BaseTool` that calls the Jina Reader API.
- **`CompanyContextRAGTool`:** Uses DuckDuckGo, Jina Reader, Gemini Embeddings, and LanceDB to perform deep semantic searches on a target company for cover letter generation.
- **`MarkdownToPDFTool`:** Uses `fpdf2` to render the agent's markdown string into a styled PDF file.
- **`SMTPEmailTool`:** Constructs a MIME multipart email (text body + PDF attachment) and dispatches it via SMTP.
