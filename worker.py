import os
import re
import time
from dotenv import load_dotenv
from crewai import Crew, Process

from agents import JobApplicationAgents
from tasks import JobApplicationTasks
from queue_manager import QueueManager

def extract_company_name_from_url(url: str) -> str:
    # A simple heuristic to get a company name from a URL or just use a default
    # For a real system, you might want the scraper agent to return this.
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        parts = domain.split('.')
        if len(parts) >= 2:
            return parts[-2].capitalize()
        return "UnknownCompany"
    except:
        return "UnknownCompany"

def process_job(job_id: int, job_url: str, qm: QueueManager, base_resume_content: str):
    print(f"\n==========================================")
    print(f"[Worker] Processing Job ID: {job_id} | URL: {job_url}")
    print(f"==========================================\n")
    
    agents = JobApplicationAgents()
    tasks = JobApplicationTasks()
    
    scraper = agents.scraper_agent()
    evaluator = agents.evaluator_agent()
    tailor = agents.resume_tailor_agent()
    writer = agents.cover_letter_agent()
    executor = agents.execution_agent()
    
    task_scrape = tasks.scrape_job_task(scraper, job_url)
    task_evaluate = tasks.evaluate_job_task(evaluator, base_resume_content)
    
    # Phase 1
    eval_crew = Crew(
        agents=[scraper, evaluator],
        tasks=[task_scrape, task_evaluate],
        process=Process.sequential,
        verbose=True,
        max_rpm=10
    )
    
    try:
        eval_result = str(eval_crew.kickoff())
        print("\n--- Evaluation Result ---")
        print(eval_result)
        
        if "Decision: NO-GO" in eval_result:
            print(f"[Worker] Evaluation resulted in NO-GO for job {job_id}. Discarding.")
            qm.mark_evaluation_done(job_id, status='rejected')
            return
            
        print(f"[Worker] Evaluation resulted in GO. Proceeding to Dry Run Phase 2...")
        
        # We need a company name for output dir
        company_name = extract_company_name_from_url(job_url)
        safe_company_name = re.sub(r'[^A-Za-z0-9_\-\.]+', '_', company_name.strip())
        output_dir = os.path.join("output", safe_company_name)
        os.makedirs(output_dir, exist_ok=True)
        os.environ["OUTPUT_DIR"] = output_dir
        
        # We also need a generic email since we don't have human input
        # The writer agent should find it, or we use a fallback
        recipient_email = "recruiter@" + safe_company_name.lower() + ".com"
        
        os.environ["DRY_RUN"] = "True"
        
        task_tailor = tasks.tailor_resume_task(tailor, base_resume_content)
        task_writer = tasks.write_cover_letter_task(writer, company_name)
        task_execute = tasks.execute_application_task(executor, recipient_email, output_dir)
        
        task_tailor.context = [task_scrape]
        task_writer.context = [task_scrape, task_tailor]
        task_execute.context = [task_writer, task_tailor]
        
        exec_crew = Crew(
            agents=[tailor, writer, executor],
            tasks=[task_tailor, task_writer, task_execute],
            process=Process.sequential,
            verbose=True,
            max_rpm=10
        )
        
        exec_crew.kickoff()
        
        # If successful, push to review queue
        qm.push_review(company_name, job_url, output_dir, recipient_email)
        qm.mark_evaluation_done(job_id, status='completed')
        
        print(f"[Worker] Successfully processed job {job_id} and queued for review.")
        
    except Exception as e:
        print(f"[Worker] Error processing job {job_id}: {e}")
        qm.mark_evaluation_done(job_id, status='failed')

def main():
    load_dotenv()
    qm = QueueManager()
    
    resume_path = "base_resume.md"
    if not os.path.exists(resume_path):
        print(f"Error: {resume_path} not found. Please create one.")
        return
        
    with open(resume_path, "r", encoding="utf-8") as f:
        base_resume_content = f.read()

    print("[Worker] Waiting for jobs in the evaluation queue...")
    
    while True:
        job = qm.pop_evaluation()
        if job:
            job_id, job_url = job
            process_job(job_id, job_url, qm, base_resume_content)
        else:
            time.sleep(5)

if __name__ == "__main__":
    main()
