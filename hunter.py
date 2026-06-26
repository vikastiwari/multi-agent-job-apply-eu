import os
import json
import time
from dotenv import load_dotenv
from crewai import Crew, Process

from agents import JobApplicationAgents
from tasks import JobApplicationTasks
from queue_manager import QueueManager

def main():
    load_dotenv()
    print("==========================================")
    print("Hunter Agent Daemon: Sourcing Jobs...")
    print("==========================================\n")
    
    # Daemon mode: use a fixed query or read from environment variable
    query = os.environ.get("HUNTER_QUERY", 'site:linkedin.com/jobs "Software Engineer" "Germany"')
    
    agents = JobApplicationAgents()
    tasks = JobApplicationTasks()
    qm = QueueManager()
    
    hunter = agents.hunter_agent()
    task_source = tasks.source_jobs_task(hunter, query)
    
    crew = Crew(
        agents=[hunter],
        tasks=[task_source],
        process=Process.sequential,
        verbose=True
    )
    
    print(f"\n[Hunter] Searching for: {query}\n")
    
    try:
        result = crew.kickoff()
        result_text = str(result)
        
        # Try to parse the result as JSON list of URLs
        try:
            # Often LLMs wrap JSON in markdown block like ```json ... ```
            import re
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                urls = json.loads(json_match.group(0))
            else:
                urls = json.loads(result_text)
                
            if isinstance(urls, list):
                for url in urls:
                    if isinstance(url, str) and url.startswith('http'):
                        if qm.push_evaluation(url):
                            print(f"[Queue] Added new job: {url}")
                        else:
                            print(f"[Queue] Skipped duplicate job: {url}")
        except json.JSONDecodeError:
            print("[Error] Hunter output was not valid JSON.")
            print(f"Raw Output:\n{result_text}")
    except Exception as e:
        print(f"[Error] Hunter failed: {e}")

if __name__ == "__main__": # pragma: no cover
    while True:
        main()
        # Sleep for a bit before searching again to avoid rate limits
        print("\n[Hunter] Sleeping for 60 seconds before next scan...")
        time.sleep(60)
