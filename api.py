import os
import sqlite3
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from queue_manager import QueueManager
from tools.email_tool import SMTPEmailTool

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

qm = QueueManager()

@app.get("/api/jobs")
def get_jobs():
    jobs = {
        "evaluation": [],
        "review": []
    }
    with sqlite3.connect(qm.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM evaluation_queue")
        for row in cursor.fetchall():
            jobs["evaluation"].append(dict(row))
            
        cursor.execute("SELECT * FROM review_queue")
        for row in cursor.fetchall():
            jobs["review"].append(dict(row))
            
    return jobs

@app.get("/api/jobs/{job_id}/review")
def get_job_review(job_id: int):
    with sqlite3.connect(qm.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM review_queue WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = dict(row)
    output_dir = job["output_dir"]
    
    # Read files
    try:
        with open(os.path.join(output_dir, "job_description.md"), "r", encoding="utf-8") as f:
            job_desc = f.read()
    except FileNotFoundError: # pragma: no cover
        job_desc = "Not found"
        
    try:
        with open(os.path.join(output_dir, "email_dry_run.txt"), "r", encoding="utf-8") as f:
            email_draft = f.read()
    except FileNotFoundError: # pragma: no cover
        email_draft = "Not found"
        
    resume_path = os.path.join(output_dir, "tailored_resume.pdf")
    resume_b64 = None
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            resume_b64 = base64.b64encode(f.read()).decode("utf-8")
            
    return {
        "job": job,
        "job_description": job_desc,
        "email_draft": email_draft,
        "resume_pdf_base64": resume_b64
    }

@app.post("/api/jobs/{job_id}/approve")
def approve_job(job_id: int):
    with sqlite3.connect(qm.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM review_queue WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = dict(row)
    output_dir = job["output_dir"]
    
    dry_run_path = os.path.join(output_dir, "email_dry_run.txt")
    if not os.path.exists(dry_run_path):
        raise HTTPException(status_code=400, detail="Missing email_dry_run.txt")
        
    with open(dry_run_path, "r", encoding="utf-8") as f:
        email_content = f.read()
        
    lines = email_content.split('\n')
    to_email = lines[0].replace("To: ", "").strip()
    subject = lines[1].replace("Subject: ", "").strip()
    
    body_lines = []
    attachment_path = ""
    for line in lines[3:]:
        if line.startswith("Attachment:"):
            attachment_path = line.replace("Attachment: ", "").strip()
        else:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()
    
    # Actually send email
    os.environ["DRY_RUN"] = "False"
    tool = SMTPEmailTool()
    try:
        result = tool._run(to_email=to_email, subject=subject, body=body, attachment_path=attachment_path)
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))
        
    qm.mark_review_done(job_id, status="sent")
    return {"status": "success", "result": result}

@app.post("/api/jobs/{job_id}/reject")
def reject_job(job_id: int):
    # Ensure job exists first
    with sqlite3.connect(qm.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM review_queue WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
        
    qm.mark_review_done(job_id, status="rejected")
    return {"status": "success"}

if __name__ == "__main__": # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
