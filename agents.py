import os
from crewai import Agent, LLM

from tools.scraper_tool import FirecrawlScraperTool
from tools.pdf_tool import MarkdownToPDFTool
from tools.email_tool import SMTPEmailTool

def get_llm():
    # Initialize Google AI Studio LLM.
    # Requires GEMINI_API_KEY to be set in your environment.
    return LLM(
        model="gemini/gemini-2.5-flash-lite",
        temperature=0.2
    )

class JobApplicationAgents():
    def __init__(self):
        self.llm = get_llm()

    def scraper_agent(self):
        return Agent(
            role='Senior Data Extractor',
            goal='Extract the full job description, requirements, and application contact details from a given URL.',
            backstory='An expert web scraper who specializes in finding job postings and extracting clean markdown content from complex websites.',
            tools=[FirecrawlScraperTool()],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def evaluator_agent(self):
        return Agent(
            role='Talent Acquisition Matcher',
            goal='Evaluate a job description against a base resume and decide if it is a good match.',
            backstory='A seasoned technical recruiter. You ruthlessly evaluate whether a candidate has a realistic chance at a job based on their resume. You output "Decision: GO" or "Decision: NO-GO".',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def resume_tailor_agent(self):
        return Agent(
            role='Expert Resume Writer',
            goal='Rewrite and tailor a base markdown resume to highlight skills relevant to a specific job description while strictly adhering to European standards.',
            backstory="A professional resume consultant who specializes in the European tech market. You know exactly how to bypass ATS systems. You strictly format resumes according to Europass guidelines. You always ensure the candidate's exact Date of Birth is clearly stated to maximize Chancenkarte points. You explicitly map all language skills to the CEFR scale (e.g., English C1). CRITICAL: You must explicitly append the exact phrase 'Anabin Listed: H+ / ZAB Statement of Comparability' beneath the education section to clear German Opportunity Card requirements. You ONLY output valid markdown.",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def cover_letter_agent(self):
        return Agent(
            role='Corporate Communications Specialist',
            goal='Write a highly compelling, personalized cover letter and email body for a job application.',
            backstory='An expert copywriter. You know how to be professional, enthusiastic, and concise. You write emails that recruiters actually want to read.',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def execution_agent(self):
        return Agent(
            role='Application Dispatcher',
            goal='Convert the final tailored markdown resume to PDF, and send the final application email.',
            backstory='A detail-oriented assistant who ensures the final PDF looks good and the email is sent to the correct address.',
            tools=[MarkdownToPDFTool(), SMTPEmailTool()],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
