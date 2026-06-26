from crewai import Task

class JobApplicationTasks():
    def source_jobs_task(self, agent, query):
        return Task(
            description=f'Use the Job Search Tool to find recent job postings matching the query: "{query}". Extract and return a JSON list of the URLs you found. Do not include any extra conversational text, just valid JSON.',
            expected_output='A JSON list of job URLs.',
            agent=agent
        )

    def scrape_job_task(self, agent, job_url):
        return Task(
            description=f'Scrape the job posting at {job_url}. Extract the title, full job description, requirements, and if possible, the application email address or contact info.',
            expected_output='A structured summary of the job title, description, requirements, and application contact info.',
            agent=agent
        )

    def evaluate_job_task(self, agent, base_resume_content):
        return Task(
            description=f'Read the extracted job description and compare it to this base resume:\n\n{base_resume_content}\n\nDetermine if the candidate is a good match (at least 60% skill overlap). IMPORTANT: You must also explicitly search the job description for salary expectations. To qualify for the EU Blue Card (IT shortage occupation), the salary must be at least €45,934.20. If the salary is listed and falls below this threshold, output "Decision: NO-GO". If it is a match and salary is acceptable (or not listed), end your output with "Decision: GO". If not, end with "Decision: NO-GO".',
            expected_output='Analysis of the fit including EU Blue Card salary threshold check, ending strictly with "Decision: GO" or "Decision: NO-GO".',
            agent=agent
        )

    def tailor_resume_task(self, agent, base_resume_content):
        return Task(
            description=f'Based on the extracted job description, tailor the following base resume to highlight relevant experience and keywords. DO NOT hallucinate or invent new experience. Keep it entirely in valid Markdown format. CRITICAL: You must strictly output a single-column layout to prevent horizontal interleaving failures in Workday and Greenhouse ATS parsers. Do not use tables or side-by-side structures.\n\nBase Resume:\n{base_resume_content}',
            expected_output='The complete, tailored resume in valid, single-column Markdown format.',
            agent=agent
        )

    def write_cover_letter_task(self, agent, company_name):
        return Task(
            description=f'First, use the Company Context RAG Tool to research {company_name}. Extract their core values, recent news, or engineering culture. Then, using the tailored resume and the job description, write a concise, compelling cover letter that will also serve as the body of the application email. Synthesize your RAG findings into the letter to show profound organizational alignment. Do not include a subject line here, just the email body.',
            expected_output='A professional email body / cover letter text demonstrating deep company contextualization.',
            agent=agent
        )

    def execute_application_task(self, agent, recipient_email, output_dir):
        return Task(
            description=f'''You need to do two things in order:
1. Use the MarkdownToPDFTool to convert the output of the "tailor_resume_task" into a PDF file saved at "{output_dir}/tailored_resume.pdf". Pass the raw markdown text to it.
2. Use the SMTPEmailTool to send an email to {recipient_email}. 
   - Subject: Create a good subject line like "Application for [Job Title] - [Your Name]"
   - Body: Use the exact text from the "write_cover_letter_task".
   - Attachment: "{output_dir}/tailored_resume.pdf"
''',
            expected_output='A confirmation string stating whether the PDF was generated and the email tool was successfully called.',
            agent=agent
        )
