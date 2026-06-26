# UI/UX Design Strategy: Multi-Agent Job Apply

## 1. Current State: CLI Interface
Currently, the application runs entirely in the terminal. The UX is focused on developer efficiency and logging visibility.

### Key CLI UX Features:
- **Clear Prompts:** The user is asked linearly for the Job URL, Company Name, and Recruiter Email.
- **Verbose Agent Logging:** CrewAI's `verbose=True` is enabled. The user can watch the LLM's thought process, including the real-time DuckDuckGo searches and semantic insights retrieved by the RAG tool.
- **Directory Organization:** Outputs are automatically sorted into clean folders: `output/<Company_Name>/`.

## 2. Future Vision: The Application Tracker Dashboard
As we scale to applying for hundreds of jobs across Europe, the CLI will become insufficient. We will eventually build a full-stack dashboard.

### Planned Web UX:
- **Kanban Board Layout:** Columns for `New Leads`, `Scraping`, `Needs Review (Dry Run)`, `Applied`, and `Interviewing`.
- **Side-by-Side Review:** When reviewing a Dry Run, the UI will display the original Job Description on the left, and the tailored PDF resume on the right for easy comparison.
- **One-Click Dispatch:** A simple "Approve & Send" button in the UI that triggers the SMTP email tool in the background.
- **Aesthetic:** Clean, glassmorphic, enterprise styling mirroring our previous Swarm Dashboard work.
