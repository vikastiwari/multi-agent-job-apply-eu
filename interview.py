import os
import sys
import argparse
from dotenv import load_dotenv

from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import google, silero

load_dotenv()

async def entrypoint(ctx: JobContext):
    company_name = os.getenv("INTERVIEW_COMPANY", "Unknown")
    
    # Read context files
    output_dir = os.path.join("output", company_name)
    job_desc_path = os.path.join(output_dir, "job_description.md")
    resume_path = os.path.join(output_dir, "tailored_resume.md")
    
    job_desc = "Unknown"
    if os.path.exists(job_desc_path):
        with open(job_desc_path, "r", encoding="utf-8") as f:
            job_desc = f.read()
            
    resume = "Unknown"
    if os.path.exists(resume_path):
        with open(resume_path, "r", encoding="utf-8") as f:
            resume = f.read()

    system_prompt = (
        f"You are a strict but professional Technical HR Recruiter for {company_name} in Europe. "
        f"You are conducting a live voice mock interview. "
        f"Here is the Job Description:\n{job_desc}\n\n"
        f"Here is the Candidate's Resume:\n{resume}\n\n"
        f"Your goal is to evaluate their fit. Ask one question at a time. "
        f"Keep your responses short, conversational, and under 3 sentences."
    )

    initial_ctx = llm.ChatContext().append(
        role="system",
        text=system_prompt,
    )

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Initialize VoicePipelineAgent with Google plugins
    # We use Google STT, Google Gemini LLM, Google TTS, and Silero VAD
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=google.STT(),
        llm=google.LLM(),
        tts=google.TTS(),
        chat_ctx=initial_ctx,
    )

    agent.start(ctx.room)
    
    # Wait for the user to connect to the room before speaking
    # Livekit SDK automatically handles track subscriptions
    await agent.say(f"Hello, I am the HR recruiter for {company_name}. Let's begin the interview. Could you start by introducing yourself?", allow_interruptions=True)

def main():
    parser = argparse.ArgumentParser(description="LiveKit Mock Interviewer")
    parser.add_argument("--company", type=str, required=True, help="The safe company name directory in output/")
    
    args, unknown = parser.parse_known_args()
    os.environ["INTERVIEW_COMPANY"] = args.company
    
    # Rebuild sys.argv for LiveKit's internal CLI parser
    sys.argv = [sys.argv[0]] + unknown
    
    # Start the LiveKit Worker
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

if __name__ == "__main__": # pragma: no cover
    main()
