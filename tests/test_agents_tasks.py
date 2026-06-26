import pytest
from agents import JobApplicationAgents
from tasks import JobApplicationTasks

@pytest.fixture
def agents_instance():
    return JobApplicationAgents()

@pytest.fixture
def tasks_instance():
    return JobApplicationTasks()

def test_scraper_agent_creation(agents_instance):
    agent = agents_instance.scraper_agent()
    assert agent.role == 'Senior Data Extractor'
    assert 'Jina Reader' in agent.tools[0].name

def test_evaluator_agent_creation(agents_instance):
    agent = agents_instance.evaluator_agent()
    assert agent.role == 'Talent Acquisition Matcher'

def test_tailor_agent_creation(agents_instance):
    agent = agents_instance.resume_tailor_agent()
    # Verify European compliance instructions are present in backstory
    assert 'Europass' in agent.backstory
    assert 'Anabin Listed: H+' in agent.backstory

def test_evaluate_job_task(tasks_instance, agents_instance):
    agent = agents_instance.evaluator_agent()
    task = tasks_instance.evaluate_job_task(agent, "Base Resume Content")
    
    # Verify EU Blue Card €45,934.20 check is present in task description
    assert '€45,934.20' in task.description

def test_tailor_resume_task(tasks_instance, agents_instance):
    agent = agents_instance.resume_tailor_agent()
    task = tasks_instance.tailor_resume_task(agent, "Base Resume Content")
    
    # Verify single-column markdown requirement is present
    assert 'single-column layout' in task.description
    assert 'Base Resume Content' in task.description

def test_cover_letter_agent_creation(agents_instance):
    agent = agents_instance.cover_letter_agent()
    assert agent.role == 'Corporate Communications Specialist'
    assert len(agent.tools) == 1
    assert agent.tools[0].name == 'Company Context RAG Tool'

def test_write_cover_letter_task(tasks_instance, agents_instance):
    agent = agents_instance.cover_letter_agent()
    task = tasks_instance.write_cover_letter_task(agent, "Acme Corp")
    
    assert 'Acme Corp' in task.description
    assert 'Company Context RAG Tool' in task.description
