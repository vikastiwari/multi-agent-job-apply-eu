import pytest
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock

# We must mock livekit imports because they might require binary wheels or C-extensions during test loading
sys.modules['livekit'] = MagicMock()
sys.modules['livekit.agents'] = MagicMock()
sys.modules['livekit.agents.pipeline'] = MagicMock()
sys.modules['livekit.plugins'] = MagicMock()

from interview import main, entrypoint

@patch('interview.cli.run_app')
@patch('interview.sys.argv', ['interview.py', '--company', 'TestCompany'])
def test_interview_main(mock_run_app):
    main()
    assert os.environ.get("INTERVIEW_COMPANY") == "TestCompany"
    mock_run_app.assert_called_once()

@pytest.mark.asyncio
@patch('interview.os.path.exists')
@patch('builtins.open', new_callable=MagicMock)
@patch('interview.VoicePipelineAgent')
@patch('interview.silero')
@patch('interview.google')
async def test_interview_entrypoint(mock_google, mock_silero, mock_agent_class, mock_open, mock_exists):
    # Setup mocks
    mock_exists.return_value = True
    
    mock_file = MagicMock()
    mock_file.read.return_value = "Mocked File Content"
    mock_open.return_value.__enter__.return_value = mock_file
    
    os.environ["INTERVIEW_COMPANY"] = "TestCompany"
    
    mock_ctx = AsyncMock()
    mock_ctx.room = MagicMock()
    
    mock_agent_instance = AsyncMock()
    mock_agent_class.return_value = mock_agent_instance
    
    await entrypoint(mock_ctx)
    
    # Verify connections and agent start
    mock_ctx.connect.assert_called_once()
    mock_agent_instance.start.assert_called_once_with(mock_ctx.room)
    mock_agent_instance.say.assert_called_once()
    
    # Verify the correct prompt was sent to Say
    say_arg = mock_agent_instance.say.call_args[0][0]
    assert "Hello, I am the HR recruiter for TestCompany." in say_arg
