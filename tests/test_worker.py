import pytest
from unittest.mock import patch, MagicMock

@patch('worker.Crew')
@patch('worker.JobApplicationAgents')
@patch('worker.JobApplicationTasks')
@patch('worker.os.makedirs')
def test_worker_process_job_go(mock_makedirs, mock_tasks, mock_agents, mock_crew):
    mock_qm = MagicMock()
    
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    
    mock_eval_result = MagicMock()
    mock_eval_result.__str__.return_value = "Decision: GO"
    
    mock_exec_result = MagicMock()
    mock_exec_result.__str__.return_value = "Success"
    
    mock_crew_instance.kickoff.side_effect = [mock_eval_result, mock_exec_result]
    
    from worker import process_job
    with patch.dict('os.environ', {"GEMINI_API_KEY": "fake"}):
        process_job(1, "https://company.com/job", mock_qm, "Resume")
        
    assert mock_crew_instance.kickoff.call_count == 2
    mock_qm.push_review.assert_called_once()
    mock_qm.mark_evaluation_done.assert_called_with(1, status='completed')

@patch('worker.Crew')
@patch('worker.JobApplicationAgents')
@patch('worker.JobApplicationTasks')
def test_worker_process_job_no_go(mock_tasks, mock_agents, mock_crew):
    mock_qm = MagicMock()
    
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    
    mock_eval_result = MagicMock()
    mock_eval_result.__str__.return_value = "Decision: NO-GO"
    
    mock_crew_instance.kickoff.return_value = mock_eval_result
    
    from worker import process_job
    with patch.dict('os.environ', {"GEMINI_API_KEY": "fake"}):
        process_job(2, "https://company.com/job", mock_qm, "Resume")
        
    assert mock_crew_instance.kickoff.call_count == 1
    mock_qm.push_review.assert_not_called()
    mock_qm.mark_evaluation_done.assert_called_with(2, status='rejected')

@patch('worker.Crew')
@patch('worker.JobApplicationAgents')
@patch('worker.JobApplicationTasks')
def test_worker_process_job_exception(mock_tasks, mock_agents, mock_crew):
    mock_qm = MagicMock()
    
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    mock_crew_instance.kickoff.side_effect = Exception("Mock Eval Error")
    
    from worker import process_job
    with patch.dict('os.environ', {"GEMINI_API_KEY": "fake"}):
        process_job(3, "https://company.com/job", mock_qm, "Resume")
        
    mock_qm.mark_evaluation_done.assert_called_with(3, status='failed')

@patch('worker.os.path.exists')
@patch('worker.QueueManager')
def test_worker_main_no_resume(mock_qm, mock_exists):
    mock_exists.side_effect = lambda x: False if x == "base_resume.md" else True
    
    import worker
    worker.main()
    
    mock_qm.return_value.pop_evaluation.assert_not_called()

def test_extract_company_name_from_url_unknown():
    import worker
    # Test fallback
    assert worker.extract_company_name_from_url("http://localhost") == "UnknownCompany"
    # Test exception fallback
    assert worker.extract_company_name_from_url(None) == "UnknownCompany"

@patch('worker.os.path.exists')
@patch('worker.QueueManager')
@patch('worker.open')
@patch('worker.process_job')
@patch('worker.time.sleep')
def test_worker_main_loop(mock_sleep, mock_process, mock_open, mock_qm_class, mock_exists):
    mock_exists.side_effect = lambda x: False if x == ".env" else True
    
    mock_qm = MagicMock()
    mock_qm_class.return_value = mock_qm
    mock_qm.pop_evaluation.side_effect = [(1, "url"), None]
    
    mock_sleep.side_effect = Exception("Break Loop")
    
    import worker
    try:
        worker.main()
    except Exception as e:
        if str(e) == "Break Loop":
            pass
            
    mock_process.assert_called_once_with(1, "url", mock_qm, mock_open.return_value.__enter__.return_value.read.return_value)
