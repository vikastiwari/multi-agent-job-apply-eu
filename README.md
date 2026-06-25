# Multi-Agent Job Application System

A powerful, automated Multi-Agent Job Application workflow powered by **CrewAI** and **GCP Vertex AI (Gemini)**. This system streamlines your job hunting by taking a job URL, scraping the requirements, evaluating your fit, automatically tailoring your resume, drafting a personalized cover letter, and even sending out the application via email on your behalf—all with Human-in-the-Loop (HITL) approval.

## 🚀 Features

- **Automated Web Scraping:** Uses Jina Reader API to cleanly extract markdown from job URLs, bypassing complex DOM structures.
- **Smart Fit Evaluation:** Evaluates the scraped job description against your base resume to determine a GO/NO-GO decision.
- **Resume Tailoring:** If it's a good fit, the AI tailors a single-column markdown resume (EU compliant) and automatically converts it to a professional PDF using `fpdf2`.
- **Cover Letter Generation:** Drafts a highly personalized cover letter based on the job requirements and your background.
- **Human-in-the-Loop (HITL) Safety:** Generates the materials and saves them in a local "Dry Run" output folder organized by company name for your review before taking action.
- **Automated Email Dispatch:** Approving the Dry Run prompts the system to automatically email your tailored resume and cover letter directly to the recruiter.

## 🧰 Tech Stack & Tools

- **Language:** Python 3.9+
- **Agent Orchestration:** CrewAI
- **LLM Provider:** Google Vertex AI (Gemini 2.5 Flash) via LiteLLM
- **Extraction:** Jina Reader API
- **PDF Generation:** `fpdf2`
- **Testing:** `pytest` (100% Core Code Coverage)

## 🛠️ Prerequisites

Before you start, ensure you have the following installed:
1. **Python 3.9+**
2. API Key for **Gemini** (Google AI Studio / Vertex AI).
3. An App Password for your SMTP email provider (e.g., Gmail) to dispatch applications.

## 💻 Installation

1. **Clone or Download the Project:**
   ```bash
   git clone <repository_url>
   cd "MultiAgent Job Apply"
   ```

2. **Create and Activate a Virtual Environment (Optional but Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

1. **Environment Variables:**
   Rename `.env.example` to `.env` and fill in your details:
   ```env
   # Google AI Studio / Vertex AI settings
   GEMINI_API_KEY="your_gemini_api_key_here"

   # SMTP Email Settings (for sending applications)
   SMTP_SERVER="smtp.gmail.com"
   SMTP_PORT="465"
   SENDER_EMAIL="your_email@gmail.com"
   SENDER_APP_PASSWORD="your_app_password_here"
   
   # Execution Mode
   DRY_RUN=True
   ```

2. **Prepare Your Resume:**
   There is a file named `base_resume.md` in the root directory. Paste your standard, comprehensive resume into this file using Markdown format. The AI will use this as the master reference when tailoring applications.

## ▶️ Usage

Run the main application script:

```bash
python main.py
```

### The Workflow:

1. **Input Information:** The script will prompt you for:
   - `Target Job URL`
   - `Company Name` (used to organize your output files)
   - `Recruiter Email` (if known; otherwise you can use a test email or leave it out if the system is configured to just generate docs)
2. **Phase 1 (Scrape & Evaluate):** The agents will scrape the URL and decide if it's a "GO" or "NO-GO" based on your `base_resume.md`.
3. **Phase 2 (Tailor & Draft):** If "GO", the system tailors the resume, drafts an email/cover letter, and saves them locally.
4. **Review (HITL):** Go to the generated folder `output/<Company_Name>` to review your `tailored_resume.pdf` and `email_dry_run.txt`.
5. **Dispatch:** The console will ask if you want to proceed. Type `yes` to send the email automatically, or `no` to abort.

## 🗂️ Project Structure

- `main.py`: The entry point that orchestrates the CrewAI process.
- `agents.py`: Defines the personalized AI agents (Scraper, Evaluator, Tailor, Writer, Executor).
- `tasks.py`: Outlines the specific tasks assigned to each agent.
- `tools/`: Contains custom Python tools for PDF generation, sending emails, and scraping.
- `output/`: Auto-generated folder where tailored resumes and draft emails are stored per company.
- `requirements.txt`: Python package dependencies.
- `base_resume.md`: Your master resume in Markdown format.

## 🤝 Contributing
Feel free to submit issues, fork the repository, and send pull requests.

## 📝 License
This project is open-source and available under the MIT License.
