import pytest
import os
import sqlite3
from queue_manager import QueueManager

@pytest.fixture
def temp_db():
    db_path = "test_jobs.db"
    qm = QueueManager(db_path=db_path)
    yield qm
    if os.path.exists(db_path):
        os.remove(db_path)

def test_push_and_pop_evaluation(temp_db):
    url = "https://example.com/job"
    
    # Push new url
    assert temp_db.push_evaluation(url) == True
    # Push duplicate url
    assert temp_db.push_evaluation(url) == False
    
    # Pop from queue
    job = temp_db.pop_evaluation()
    assert job is not None
    job_id, popped_url = job
    assert popped_url == url
    
    # Next pop should be None
    assert temp_db.pop_evaluation() is None
    
    # Mark done
    temp_db.mark_evaluation_done(job_id)

def test_push_and_pop_review(temp_db):
    company = "Test Co"
    url = "https://example.com/job"
    out_dir = "output/Test_Co"
    email = "test@example.com"
    
    temp_db.push_review(company, url, out_dir, email)
    
    job = temp_db.pop_review()
    assert job is not None
    assert job['company_name'] == company
    assert job['url'] == url
    assert job['output_dir'] == out_dir
    assert job['email'] == email
    
    assert temp_db.pop_review() is None
    
    temp_db.mark_review_done(job['id'])
