import pytest
from unittest.mock import patch, MagicMock

@patch('builtins.input')
@patch('main.Crew')
@patch('main.JobApplicationAgents')
@patch('main.JobApplicationTasks')
@patch('main.os.makedirs')
@patch('main.os.path.exists')
@patch('main.open')
def test_main_execution_go_send(mock_open, mock_exists, mock_makedirs, mock_tasks, mock_agents, mock_crew, mock_input):
    mock_exists.return_value = True
    mock_input.side_effect = [
        "https://example.com",
        "Test Company",
        "test@example.com",
        "yes"
    ]
    
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    
    mock_eval_result = MagicMock()
    mock_eval_result.raw = "Decision: GO"
    mock_crew_instance.kickoff.return_value = mock_eval_result
    
    import main
    with patch.dict('os.environ', {"GEMINI_API_KEY": "fake_key"}):
        main.main()
        
    assert mock_crew_instance.kickoff.call_count >= 2

@patch('builtins.input')
@patch('main.Crew')
@patch('main.JobApplicationAgents')
@patch('main.JobApplicationTasks')
@patch('main.os.makedirs')
@patch('main.os.path.exists')
@patch('main.open')
def test_main_execution_go_abort(mock_open, mock_exists, mock_makedirs, mock_tasks, mock_agents, mock_crew, mock_input):
    mock_exists.return_value = True
    mock_input.side_effect = [
        "https://example.com",
        "Test Company",
        "test@example.com",
        "no"
    ]
    
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    
    mock_eval_result = MagicMock()
    mock_eval_result.raw = "Decision: GO"
    mock_crew_instance.kickoff.return_value = mock_eval_result
    
    import main
    with patch.dict('os.environ', {"GEMINI_API_KEY": "fake_key"}):
        main.main()

@patch('builtins.input')
@patch('main.Crew')
@patch('main.os.makedirs')
@patch('main.os.path.exists')
@patch('main.open')
def test_main_execution_no_go(mock_open, mock_exists, mock_makedirs, mock_crew, mock_input):
    mock_exists.return_value = True
    mock_input.side_effect = [
        "https://example.com",
        "Test Company",
        "test@example.com"
    ]
    
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    
    mock_eval_result = MagicMock()
    # str(mock_eval_result) needs to contain Decision: NO-GO, so we patch __str__
    mock_eval_result.__str__.return_value = "Decision: NO-GO"
    mock_crew_instance.kickoff.return_value = mock_eval_result
    
    import main
    with patch.dict('os.environ', {"GEMINI_API_KEY": "fake_key"}):
        main.main()
        
    assert mock_crew_instance.kickoff.call_count == 1

@patch('builtins.input')
@patch('main.os.path.exists')
def test_main_execution_missing_resume(mock_exists, mock_input):
    # Only return False for base_resume.md, True for everything else (like .env)
    mock_exists.side_effect = lambda x: False if x == "base_resume.md" else True
    mock_input.side_effect = ["url", "company", "email"]
    
    import main
    main.main()
