import pytest
import os
from unittest.mock import patch, MagicMock
from tools.email_tool import SMTPEmailTool

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": "465",
        "SENDER_EMAIL": "test@example.com",
        "SENDER_APP_PASSWORD": "password123",
        "DRY_RUN": "False"
    }):
        yield

def test_email_tool_dry_run():
    with patch.dict(os.environ, {"DRY_RUN": "True"}):
        tool = SMTPEmailTool()
        # Create a dummy file
        with open("test_dummy.pdf", "w") as f:
            f.write("dummy")
            
        result = tool._run("recipient@example.com", "Test Subject", "Test Body", "test_dummy.pdf")
        
        assert "Dry run successful" in result
        os.remove("test_dummy.pdf")

def test_email_tool_live(mock_env, mocker):
    mock_smtp = mocker.patch("smtplib.SMTP_SSL")
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    tool = SMTPEmailTool()
    
    with open("test_dummy2.pdf", "w") as f:
        f.write("dummy")
        
    result = tool._run("recipient@example.com", "Test Subject", "Test Body", "test_dummy2.pdf")
    
    assert "Successfully sent email" in result
    mock_server.login.assert_called_once_with("test@example.com", "password123")
    mock_server.send_message.assert_called_once()
    
    os.remove("test_dummy2.pdf")
