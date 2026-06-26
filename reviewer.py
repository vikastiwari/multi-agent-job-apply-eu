import os
import time
from dotenv import load_dotenv

from queue_manager import QueueManager
from tools.email_tool import SMTPEmailTool

def main():
    load_dotenv()
    qm = QueueManager()
    
    print("==========================================")
    print("Reviewer Dashboard")
    print("==========================================\n")
    
    job = qm.pop_review()
    if not job:
        print("No applications pending review.")
        return
        
    job_id = job['id']
    company = job['company_name']
    url = job['url']
    output_dir = job['output_dir']
    
    print(f"Company: {company}")
    print(f"URL: {url}")
    print(f"Output Directory: {output_dir}")
    print("-" * 40)
    
    dry_run_path = os.path.join(output_dir, "email_dry_run.txt")
    if not os.path.exists(dry_run_path):
        print(f"Error: {dry_run_path} not found.")
        qm.mark_review_done(job_id, status='failed_missing_files')
        return
        
    with open(dry_run_path, "r", encoding="utf-8") as f:
        email_content = f.read()
        
    print(email_content)
    print("-" * 40)
    
    # Optional: Open the PDF for the user (Windows specific via WSL, or generic)
    # Using python's generic os.system might not work in WSL to open GUI.
    
    proceed = input("\nDo you want to actually SEND this application? (yes/no/skip): ")
    if proceed.lower() in ['yes', 'y']:
        print("\n[System] Sending application...")
        os.environ["DRY_RUN"] = "False"
        
        # Parse the email content back into components
        lines = email_content.split('\n')
        to_email = lines[0].replace("To: ", "").strip()
        subject = lines[1].replace("Subject: ", "").strip()
        
        # Body starts after line 2 until the last line (Attachment)
        body_lines = []
        attachment_path = ""
        for line in lines[3:]:
            if line.startswith("Attachment:"):
                attachment_path = line.replace("Attachment: ", "").strip()
            else:
                body_lines.append(line)
        body = "\n".join(body_lines).strip()
        
        tool = SMTPEmailTool()
        result = tool._run(to_email=to_email, subject=subject, body=body, attachment_path=attachment_path)
        print(f"[System] Email Result: {result}")
        
        qm.mark_review_done(job_id, status='sent')
    elif proceed.lower() in ['skip', 's']:
        print("\n[System] Skipping. Returning to queue.")
        qm.mark_review_done(job_id, status='pending')
    else:
        print("\n[System] Application rejected.")
        qm.mark_review_done(job_id, status='rejected')

if __name__ == "__main__": # pragma: no cover
    main()
