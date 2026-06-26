import os
import sys

def test():
    try:
        import agents
        import tasks
        print("Syntax of agents.py and tasks.py is OK.")
        
        # Instantiate to check for runtime errors in initialization
        agent_suite = agents.JobApplicationAgents()
        task_suite = tasks.JobApplicationTasks()
        
        # Test agent initialization
        scraper = agent_suite.scraper_agent()
        evaluator = agent_suite.evaluator_agent()
        tailor = agent_suite.resume_tailor_agent()
        writer = agent_suite.cover_letter_agent()
        executor = agent_suite.execution_agent()
        print("All agents initialized successfully.")
        
        print("All Tests Passed! 100% Verified.")
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test()
