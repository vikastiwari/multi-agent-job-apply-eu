# UI/UX Design Strategy: Multi-Agent Job Apply

## 1. Current State: Multi-Terminal CLI Ecosystem
As of Phase 4, the application has evolved from a single synchronous script to a distributed CLI ecosystem.

### Key CLI UX Features:
- **Asynchronous Workflows:** The user can start the `hunter.py` daemon in one terminal to continuously source jobs, run the `worker.py` daemon in another to process them, and open `reviewer.py` whenever they have free time to approve applications.
- **Reviewer Dashboard:** The `reviewer.py` script provides a clean text-based dashboard that pops pending applications, displays the synthesized Cover Letter and metadata, and allows quick `yes`/`no`/`skip` interactions.
- **Verbose Agent Logging:** Inside the worker terminal, CrewAI's `verbose=True` is enabled. The user can watch the LLM's thought process, including the real-time DuckDuckGo searches and semantic insights retrieved by the RAG tool.
- **Directory Organization:** Outputs are automatically sorted into clean folders: `output/<Company_Name>/`.

## 2. Future Vision: The Application Tracker Dashboard
As we scale to applying for hundreds of jobs across Europe, the CLI will become insufficient. We will eventually build a full-stack dashboard.

### Planned Web UX:
- **Kanban Board Layout:** Columns for `New Leads`, `Scraping`, `Needs Review (Dry Run)`, `Applied`, and `Interviewing`.
- **Side-by-Side Review:** When reviewing a Dry Run, the UI will display the original Job Description on the left, and the tailored PDF resume on the right for easy comparison.
- **One-Click Dispatch:** A simple "Approve & Send" button in the UI that triggers the SMTP email tool in the background.
- **Aesthetic:** Clean, glassmorphic, enterprise styling mirroring our previous Swarm Dashboard work.

### Phase 5: LiveKit Playground UI
For the Mock Interview module, we utilize the hosted **LiveKit Agents Playground** (https://agents-playground.livekit.io).
*   **Input**: The user inputs their `LIVEKIT_URL` and `LIVEKIT_API_KEY`.
*   **Interaction**: The user presses "Connect" and speaks into their microphone. A visual audio waveform provides feedback that the HR agent is listening and responding.

### Phase 6: Full Web Dashboard (Upcoming)
