import os
from dotenv import load_dotenv
from crewai import Crew, Process

from agents import JobApplicationAgents
from tasks import JobApplicationTasks

def main():
    # Load environment variables
    load_dotenv()
    
    print("==========================================")
    print("Multi-Agent Job Application System")
    print("Powered by CrewAI + GCP Vertex AI (Gemini)")
    print("==========================================\n")
    
    job_url = input("Enter the target Job URL: ")
    company_name = input("Enter the Company Name (for folder organization): ")
    recipient_email = input("Enter the recruiter/application email (if known, or 'test@example.com'): ")
    
    # Setup Output Directory
    import re
    safe_company_name = re.sub(r'[^A-Za-z0-9_\-\.]+', '_', company_name.strip())
    output_dir = os.path.join("output", safe_company_name)
    os.makedirs(output_dir, exist_ok=True)
    os.environ["OUTPUT_DIR"] = output_dir
    
    # Load Base Resume
    resume_path = "base_resume.md"
    if not os.path.exists(resume_path):
        print(f"Error: {resume_path} not found. Please create one.")
        return
        
    with open(resume_path, "r", encoding="utf-8") as f:
        base_resume_content = f.read()

    # Initialize Agents and Tasks
    agents = JobApplicationAgents()
    tasks = JobApplicationTasks()
    
    scraper = agents.scraper_agent()
    evaluator = agents.evaluator_agent()
    tailor = agents.resume_tailor_agent()
    writer = agents.cover_letter_agent()
    executor = agents.execution_agent()
    
    task_scrape = tasks.scrape_job_task(scraper, job_url)
    task_evaluate = tasks.evaluate_job_task(evaluator, base_resume_content)
    
    print("\n[Phase 1] Scraping and Evaluating...")
    
    # Phase 1 Crew
    eval_crew = Crew(
        agents=[scraper, evaluator],
        tasks=[task_scrape, task_evaluate],
        process=Process.sequential,
        verbose=True,
        max_rpm=10
    )
    
    eval_result = str(eval_crew.kickoff())
    print("\n--- Evaluation Result ---")
    print(eval_result)
    
    if "Decision: NO-GO" in eval_result:
        print("\n[System] Evaluation resulted in NO-GO. Aborting application process.")
        return
        
    print("\n[System] Evaluation resulted in GO. Proceeding to HITL Dry Run Generation...\n")
    
    print("[System] Proceeding...")
    
    # We must explicitly force Dry Run for the safety check (HITL)
    os.environ["DRY_RUN"] = "True"
    
    task_tailor = tasks.tailor_resume_task(tailor, base_resume_content)
    task_writer = tasks.write_cover_letter_task(writer, company_name)
    task_execute = tasks.execute_application_task(executor, recipient_email, output_dir)
    
    # Provide the context of previous tasks to subsequent tasks
    task_tailor.context = [task_scrape]
    task_writer.context = [task_scrape, task_tailor]
    task_execute.context = [task_writer, task_tailor]
    
    # Phase 2 Crew
    exec_crew = Crew(
        agents=[tailor, writer, executor],
        tasks=[task_tailor, task_writer, task_execute],
        process=Process.sequential,
        verbose=True,
        max_rpm=10
    )
    
    exec_crew.kickoff()
    
    print("\n==========================================")
    print("HITL / DRY RUN COMPLETE")
    print(f"Please check the '{output_dir}' folder for:")
    print("1. tailored_resume.pdf")
    print("2. email_dry_run.txt")
    print("==========================================")
    
    proceed = input("\nDo you want to actually SEND this application? (yes/no): ")
    if proceed.lower() in ['yes', 'y']:
        print("\n[System] Sending application...")
        os.environ["DRY_RUN"] = "False"
        
        # We just need to rerun the execution task with the tools enabled
        # The executor agent will use the context from before
        final_crew = Crew(
            agents=[executor],
            tasks=[task_execute],
            process=Process.sequential,
            max_rpm=10
        )
        final_crew.kickoff()
        print("\n[System] Application sent successfully!")
    else:
        print("\n[System] Application aborted by user.")

if __name__ == "__main__": # pragma: no cover
    main()
