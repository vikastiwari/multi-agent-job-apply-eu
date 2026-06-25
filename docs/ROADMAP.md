# Product Roadmap: Multi-Agent Job Apply

## Completed Phases
- [x] **Phase 1: Core Agent Orchestration**
  - Configured CrewAI with Gemini 2.5 Flash.
  - Created sequential agent workflows (Scraper -> Evaluator -> Tailor -> Writer).
- [x] **Phase 2: Custom Tooling Integration**
  - Integrated Firecrawl API for intelligent web scraping.
  - Built `MarkdownToPDFTool` using `pdfkit`.
  - Built `SMTPEmailTool` for automated dispatch.
- [x] **Phase 3: Safety & Logic**
  - Implemented the GO/NO-GO evaluation check.
  - Implemented Human-in-the-Loop (HITL) Dry Run mode to prevent accidental email dispatch.

## Upcoming Phases (Current Focus: Europe Job Hunt)
- [ ] **Phase 4: EU-Optimized Resume Formatting**
  - Ensure the base resume and the PDF generator adhere strictly to European CV standards (e.g., Europass layout, ATS-friendly designs).
- [ ] **Phase 5: Automated LinkedIn Sourcing**
  - Build a lead-generation agent that queries LinkedIn or European job boards for roles matching specific criteria, feeding them directly into the pipeline.
- [ ] **Phase 6: Interview Preparation Module**
  - Create a new CrewAI agent that reads the tailored resume and the job description to generate a list of likely interview questions and mock answers.
- [ ] **Phase 7: Web Dashboard**
  - Migrate away from the CLI to a React/Vite dashboard to track hundreds of sent applications, similar to our Enterprise Swarm architecture.
