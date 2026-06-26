import pytest
import os
from unittest.mock import patch, MagicMock

@patch('reviewer.QueueManager')
def test_reviewer_no_jobs(mock_qm_class):
    mock_qm = MagicMock()
    mock_qm_class.return_value = mock_qm
    mock_qm.pop_review.return_value = None
    
    import reviewer
    reviewer.main()
    
    mock_qm.mark_review_done.assert_not_called()

@patch('reviewer.QueueManager')
@patch('reviewer.os.path.exists')
def test_reviewer_missing_file(mock_exists, mock_qm_class):
    mock_exists.side_effect = lambda x: False if "email_dry_run.txt" in str(x) else True
    
    mock_qm = MagicMock()
    mock_qm_class.return_value = mock_qm
    mock_qm.pop_review.return_value = {
        'id': 1, 'company_name': 'A', 'url': 'B', 'output_dir': 'C', 'email': 'D'
    }
    
    import reviewer
    reviewer.main()
    
    mock_qm.mark_review_done.assert_called_with(1, status='failed_missing_files')

@patch('reviewer.QueueManager')
@patch('reviewer.os.path.exists')
@patch('reviewer.open')
@patch('builtins.input')
@patch('reviewer.SMTPEmailTool')
def test_reviewer_send(mock_smtp, mock_input, mock_open, mock_exists, mock_qm_class):
    mock_exists.return_value = True
    mock_input.return_value = "yes"
    
    mock_file = mock_open.return_value.__enter__.return_value
    mock_file.read.return_value = "To: x@y.com\nSubject: Hello\n\nBody1\nBody2\nAttachment: /path/file.pdf"
    
    mock_qm = MagicMock()
    mock_qm_class.return_value = mock_qm
    mock_qm.pop_review.return_value = {
        'id': 1, 'company_name': 'A', 'url': 'B', 'output_dir': 'C', 'email': 'D'
    }
    
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value = mock_smtp_instance
    mock_smtp_instance._run.return_value = "Sent"
    
    import reviewer
    with patch.dict('os.environ', {"DRY_RUN": "True"}):
        reviewer.main()
        assert os.environ["DRY_RUN"] == "False"
        
    mock_smtp_instance._run.assert_called_with(
        to_email="x@y.com",
        subject="Hello",
        body="Body1\nBody2",
        attachment_path="/path/file.pdf"
    )
    mock_qm.mark_review_done.assert_called_with(1, status='sent')

@patch('reviewer.QueueManager')
@patch('reviewer.os.path.exists')
@patch('reviewer.open')
@patch('builtins.input')
def test_reviewer_skip(mock_input, mock_open, mock_exists, mock_qm_class):
    mock_exists.return_value = True
    mock_input.return_value = "skip"
    mock_file = mock_open.return_value.__enter__.return_value
    mock_file.read.return_value = "Test content"
    
    mock_qm = MagicMock()
    mock_qm_class.return_value = mock_qm
    mock_qm.pop_review.return_value = {
        'id': 1, 'company_name': 'A', 'url': 'B', 'output_dir': 'C', 'email': 'D'
    }
    
    import reviewer
    reviewer.main()
    
    mock_qm.mark_review_done.assert_called_with(1, status='pending')

@patch('reviewer.QueueManager')
@patch('reviewer.os.path.exists')
@patch('reviewer.open')
@patch('builtins.input')
def test_reviewer_reject(mock_input, mock_open, mock_exists, mock_qm_class):
    mock_exists.return_value = True
    mock_input.return_value = "no"
    mock_file = mock_open.return_value.__enter__.return_value
    mock_file.read.return_value = "Test content"
    
    mock_qm = MagicMock()
    mock_qm_class.return_value = mock_qm
    mock_qm.pop_review.return_value = {
        'id': 1, 'company_name': 'A', 'url': 'B', 'output_dir': 'C', 'email': 'D'
    }
    
    import reviewer
    reviewer.main()
    
    mock_qm.mark_review_done.assert_called_with(1, status='rejected')
