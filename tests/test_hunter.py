import pytest
from unittest.mock import patch, MagicMock

@patch('builtins.input')
@patch('hunter.Crew')
@patch('hunter.JobApplicationAgents')
@patch('hunter.JobApplicationTasks')
@patch('hunter.QueueManager')
@patch('hunter.time.sleep', return_value=None)
def test_hunter_main_loop(mock_sleep, mock_qm, mock_tasks, mock_agents, mock_crew, mock_input):
    mock_input.return_value = "query"
    
    mock_qm_instance = MagicMock()
    mock_qm.return_value = mock_qm_instance
    mock_qm_instance.push_evaluation.side_effect = [True, False] # Test new and duplicate
    
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    
    mock_result = MagicMock()
    mock_result.__str__.return_value = '["https://example.com/1", "https://example.com/2"]'
    mock_crew_instance.kickoff.return_value = mock_result
    
    import hunter
    
    # Remove mock_sleep side_effect as it is not needed
    hunter.main()
    assert mock_crew_instance.kickoff.call_count == 1
    assert mock_qm_instance.push_evaluation.call_count == 2
    
@patch('builtins.input')
@patch('hunter.Crew')
@patch('hunter.JobApplicationAgents')
@patch('hunter.JobApplicationTasks')
@patch('hunter.QueueManager')
def test_hunter_main_bad_json(mock_qm, mock_tasks, mock_agents, mock_crew, mock_input):
    mock_input.return_value = "" # test default query fallback
    
    mock_qm_instance = MagicMock()
    mock_qm.return_value = mock_qm_instance
    
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    
    mock_result = MagicMock()
    mock_result.__str__.return_value = 'Not a JSON list'
    mock_crew_instance.kickoff.return_value = mock_result
    
    import hunter
    hunter.main()
    
    assert mock_qm_instance.push_evaluation.call_count == 0

@patch('builtins.input')
@patch('hunter.Crew')
def test_hunter_main_exception(mock_crew, mock_input):
    mock_input.return_value = "query"
    
    mock_crew_instance = MagicMock()
    mock_crew.return_value = mock_crew_instance
    mock_crew_instance.kickoff.side_effect = Exception("Mock Crew Error")
    
    import hunter
    hunter.main()
