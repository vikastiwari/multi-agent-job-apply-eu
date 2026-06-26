import pytest
import os
import sqlite3
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, mock_open

# We must set up the DB before importing api
from queue_manager import QueueManager

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_path = os.path.join(tmp_path, "test_jobs.db")
    os.environ["DB_PATH"] = db_path
    
    # Initialize DB
    qm = QueueManager(db_path)
    
    # Insert some dummy data
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO evaluation_queue (url, status) VALUES ('http://test.com', 'pending')")
        cursor.execute("INSERT INTO review_queue (company_name, url, output_dir, email, status) VALUES ('TestCo', 'http://test.com', 'output/TestCo', 'test@test.com', 'pending')")
        conn.commit()
        
    yield db_path
    
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def client(setup_test_db):
    # Mock QueueManager instantiation inside api module
    with patch('api.QueueManager') as mock_qm:
        mock_qm.return_value.db_path = setup_test_db
        mock_qm.return_value.mark_review_done = QueueManager(setup_test_db).mark_review_done
        from api import app, qm
        qm.db_path = setup_test_db # ensure the global qm uses the test db
        yield TestClient(app)

def test_get_jobs(client):
    response = client.get("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert len(data["evaluation"]) == 1
    assert data["evaluation"][0]["url"] == "http://test.com"
    assert len(data["review"]) == 1
    assert data["review"][0]["company_name"] == "TestCo"

def test_get_job_review_not_found(client):
    response = client.get("/api/jobs/999/review")
    assert response.status_code == 404

@patch("api.os.path.exists")
@patch("builtins.open", new_callable=MagicMock)
def test_get_job_review_found(mock_open, mock_exists, client):
    mock_exists.return_value = True
    
    # Mock reading pdf
    mock_file = MagicMock()
    mock_file.read.return_value = b"PDF_CONTENT"
    
    # Text read mock
    mock_text_file = MagicMock()
    mock_text_file.read.return_value = "Text Content"
    
    # Map open return based on args
    def open_side_effect(*args, **kwargs):
        if "pdf" in args[0]:
            return MagicMock(__enter__=lambda _: mock_file, __exit__=lambda *x: None)
        return MagicMock(__enter__=lambda _: mock_text_file, __exit__=lambda *x: None)
        
    mock_open.side_effect = open_side_effect

    response = client.get("/api/jobs/1/review")
    assert response.status_code == 200
    data = response.json()
    assert data["job"]["company_name"] == "TestCo"
    assert data["job_description"] == "Text Content"
    assert data["email_draft"] == "Text Content"
    assert "UERGX0NPTlRFTlQ=" in data["resume_pdf_base64"] # Base64 for PDF_CONTENT

def test_approve_job_not_found(client):
    response = client.post("/api/jobs/999/approve")
    assert response.status_code == 404

@patch("api.os.path.exists")
def test_approve_job_missing_draft(mock_exists, client):
    mock_exists.return_value = False
    response = client.post("/api/jobs/1/approve")
    assert response.status_code == 400

@patch("api.os.path.exists")
@patch("api.SMTPEmailTool")
@patch("builtins.open", new_callable=MagicMock)
def test_approve_job_success(mock_open, mock_smtp_class, mock_exists, client):
    mock_exists.return_value = True
    
    email_draft = "To: hr@test.com\nSubject: App\n\nBody Line 1\nAttachment: path.pdf"
    
    mock_text_file = MagicMock()
    mock_text_file.read.return_value = email_draft
    mock_open.return_value.__enter__.return_value = mock_text_file
    
    mock_smtp_instance = MagicMock()
    mock_smtp_instance._run.return_value = "Email sent"
    mock_smtp_class.return_value = mock_smtp_instance
    
    response = client.post("/api/jobs/1/approve")
    assert response.status_code == 200
    
    mock_smtp_instance._run.assert_called_once_with(to_email="hr@test.com", subject="App", body="Body Line 1", attachment_path="path.pdf")
    
    # verify DB updated
    with sqlite3.connect(os.environ["DB_PATH"]) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM review_queue WHERE id = 1")
        assert cursor.fetchone()[0] == "sent"

def test_reject_job_not_found(client):
    response = client.post("/api/jobs/999/reject")
    assert response.status_code == 404

def test_reject_job_success(client):
    response = client.post("/api/jobs/1/reject")
    assert response.status_code == 200
    
    # verify DB updated
    with sqlite3.connect(os.environ["DB_PATH"]) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM review_queue WHERE id = 1")
        assert cursor.fetchone()[0] == "rejected"
