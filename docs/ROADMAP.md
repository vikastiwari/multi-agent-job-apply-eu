# Product Roadmap: Multi-Agent Job Apply

## Completed Phases
- [x] **Phase 1: Minimum Viable Product (Complete)**
  - Basic CLI interface.
  - Integration with Gemini 2.5 Flash via CrewAI.
  - Integrated Jina Reader API for intelligent web scraping and bypassing complex DOMs.
  - PDF generation and SMTP email dispatch capabilities.
  - Built `SMTPEmailTool` for automated dispatch.
- [x] **Phase 2: Custom Tooling Integration**
  - Integrated Firecrawl API for intelligent web scraping.
  - Built `MarkdownToPDFTool` using `pdfkit`.
  - Built `SMTPEmailTool` for automated dispatch.
- [x] **Phase 3: RAG-Powered Cover Letters (Complete)**
  - Integrated LanceDB for ephemeral in-memory vector search.
  - Built `CompanyContextRAGTool` using DuckDuckGo and Jina Reader to scrape company engineering blogs.
  - Cover Letter agent autonomously synthesizes core values into applications.

## Upcoming Phases (Current Focus: Europe Job Hunt)
- [ ] **Phase 4: Sourcing & Queueing Infrastructure (Hunter Agent)**
  - Implement a continuously running Hunter Agent that polls the EURES network and LinkedIn via Apify/Camoufox.
  - Implement a message-broker (Redis/RabbitMQ) so the Hunter can asynchronously feed the Evaluation Crew.
- [ ] **Phase 5: Voice AI Interview Prep Module**
  - Create a sub-800ms latency voice pipeline using WebRTC (LiveKit).
  - Use the scraped Job Description and Tailored Resume to conduct live, spoken mock interviews for European HR screenings.
- [ ] **Phase 6: Web Dashboard**
  - Migrate away from the CLI to a React/Vite dashboard to track hundreds of sent applications.
